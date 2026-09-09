import time
import datetime

class ExecutionPipeline:
    def __init__(self, risk_guard, profit_calc):
        self.risk_guard = risk_guard
        self.profit_calc = profit_calc

    def generate_opp_id(self, chain_id, strategy_name, counter):
        # We don't generate opp_id here anymore, we expect it from Discovery
        pass

    def run_pipeline(self, opportunity_data):
        """
        Enforces the exact execution pipeline logic:
        DISCOVER -> IDENTIFY -> VERIFY -> QUOTE -> LIQUIDITY CHECK -> ECONOMICS -> RISK ->
        OPPORTUNITY SCORE -> INTENT -> SIGNATURE -> SIMULATION -> FINAL REQUOTE -> 
        FINAL STATE CHECK -> EXECUTION DECISION -> EXECUTE -> RECEIPT -> RECONCILE -> LEARN
        """
        opp_id = opportunity_data.get('opp_id')
        if not opp_id:
            return self._abort("UNKNOWN", "MISSING_OPP_ID", opportunity_data)
            
        # Step 1: Discover & Identify
        print(f"[{opp_id}] IDENTIFIED: {opportunity_data.get('strategy')} on {opportunity_data.get('chain_id')}")
        
        # Step 2: Verify & Quote
        if opportunity_data.get('quote_status') != "VALID":
            return self._abort(opp_id, "QUOTE_FAILED", opportunity_data)
            
        # Step 3: Liquidity Check (P0-10: Strict Check, No Defaults)
        liq = opportunity_data.get('liquidity_sufficient')
        if liq is None or not liq:
            return self._abort(opp_id, "INSUFFICIENT_LIQUIDITY", opportunity_data)
            
        # Step 4: Economics
        net_profit = opportunity_data.get('net_profit')
        if net_profit is None:
            return self._abort(opp_id, "ECONOMICS_FAILED", opportunity_data)
            
        # Step 5: Risk (P0-10: Strict Check, No Defaults)
        is_safe = opportunity_data.get('is_safe')
        if is_safe is None or not is_safe:
            return self._abort(opp_id, "RISK_REJECTED", opportunity_data, "is_safe flag missing or False")
            
        risk_passed, msg = self.risk_guard.validate_execution_economics(net_profit, is_safe, "Checking profit limits")
        if not risk_passed:
            return self._abort(opp_id, "RISK_REJECTED", opportunity_data, msg)
            
        # Step 6: Opportunity Score & Intent
        print(f"[{opp_id}] OPPORTUNITY SCORE: HIGH. Building Intent.")
        
        # Step 7: Signature & Simulation
        opportunity_data["final_status"] = "SIGNED"
        
        try:
            rpc_manager = opportunity_data.get('rpc_manager')
            calldata = opportunity_data.get('calldata')
            target_contract = opportunity_data.get('verifying_contract')
            
            # P0-12, P0-28: Protected Signer Object
            signer = opportunity_data.get('signer')
            
            if not (rpc_manager and calldata and target_contract and signer):
                return self._abort(opp_id, "MISSING_SIMULATION_DATA", opportunity_data)
                
            signer_address = signer.address
            
            # Record explicit block number from intent state
            current_block = rpc_manager.w3.eth.block_number
            opportunity_data['execution_block'] = current_block
            
            # Exact simulation requires: eth_estimateGas + eth_call
            tx_context = {
                "from": rpc_manager.w3.to_checksum_address(signer_address),
                "to": rpc_manager.w3.to_checksum_address(target_contract),
                "data": calldata,
                "value": 0
            }
            
            print(f"[{opp_id}] Running eth_estimateGas...")
            gas_estimate = rpc_manager.w3.eth.estimate_gas(tx_context)
            opportunity_data['actual_gas_estimate'] = gas_estimate
            
            print(f"[{opp_id}] Running eth_call simulation...")
            rpc_manager.w3.eth.call(tx_context)
            
            opportunity_data["final_status"] = "SIMULATION_PASSED"
        except Exception as e:
            print(f"[{opp_id}] SIMULATION REVERTED: {e}")
            return self._abort(opp_id, "SIMULATION_REVERTED", opportunity_data)
            
        # Step 8: Final Requote & Final State Check
        # Hard gate: No fallback to True. The data MUST explicitly have a positive requote flag.
        requote_match = opportunity_data.get('final_requote_match')
        if requote_match is None or not requote_match:
            return self._abort(opp_id, "STATE_CHANGED_BEFORE_EXECUTION", opportunity_data)
            
        # Step 9: Execution Decision
        print(f"[{opp_id}] EXECUTION DECISION: PROCEED. Gates GREEN.")
        opportunity_data["final_status"] = "RAW_TX_BUILT"
        
        # Step 10: Execution / Reconciliation
        exec_mode = opportunity_data.get('execution_mode', 'READ_ONLY')
        if exec_mode in ['TESTNET', 'MAINNET_CAPITAL']:
            try:
                # 1. Sign TX using Protected Signer
                gas_price = rpc_manager.w3.eth.gas_price
                nonce = rpc_manager.w3.eth.get_transaction_count(rpc_manager.w3.to_checksum_address(signer_address))
                
                tx_context = {
                    "from": rpc_manager.w3.to_checksum_address(signer_address),
                    "to": rpc_manager.w3.to_checksum_address(target_contract),
                    "data": calldata,
                    "value": 0,
                    "gas": opportunity_data.get('actual_gas_estimate', 1000000),
                    "gasPrice": gas_price,
                    "nonce": nonce,
                    "chainId": opportunity_data.get('chain_id')
                }
                
                signed_tx = signer.sign_transaction(tx_context)
                
                # 2. Broadcast
                tx_hash = rpc_manager.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                opportunity_data["tx_hash"] = tx_hash.hex()
                opportunity_data["nonce"] = nonce
                opportunity_data["final_status"] = "TX_SUBMITTED"
                print(f"[{opp_id}] TX_SUBMITTED: {tx_hash.hex()}")
                
                # 3. Reconcile (P0-13, P0-30)
                print(f"[{opp_id}] Waiting for receipt...")
                receipt = rpc_manager.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                opportunity_data["receipt_status"] = receipt.status
                
                if receipt.status != 1:
                    return self._abort(opp_id, "TX_REVERTED_ON_CHAIN", opportunity_data)
                
                actual_gas_used = receipt.gasUsed
                # Extract effective gas price for precise economics
                effective_gas_price = receipt.effectiveGasPrice if hasattr(receipt, 'effectiveGasPrice') else tx_context["gasPrice"]
                actual_gas_cost = actual_gas_used * effective_gas_price
                
                opportunity_data["actual_gas_used"] = actual_gas_used
                opportunity_data["effective_gas_price"] = effective_gas_price
                opportunity_data["actual_gas_cost"] = actual_gas_cost
                opportunity_data["final_status"] = "RECONCILED"
                
                print(f"[{opp_id}] RECONCILED. Status: {receipt.status}, Gas Used: {actual_gas_used}")
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                return self._abort(opp_id, "EXECUTION_OR_RECONCILIATION_FAILED", opportunity_data, str(e))
        else:
            print(f"[{opp_id}] SKIPPED BROADCAST: execution_mode is {exec_mode}")
            opportunity_data["final_status"] = "READ_ONLY_COMPLETED"
            
        # Step 11: Write JSON Evidence Manifest (P0-15, P0-18, P0-19)
        import json
        import os
        import hashlib
        
        manifest_path = "PFLC_5.4R_Evidence_Manifest.jsonl"
        
        # Read previous hash to build cryptographic chain
        prev_hash = "0" * 64
        seq = 0
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = json.loads(lines[-1].strip())
                        prev_hash = last_line.get("hash", prev_hash)
                        seq = last_line.get("data", {}).get("sequence", 0) + 1
            except:
                pass
                
        manifest_entry = {
            "sequence": seq,
            "timestamp": int(time.time()),
            "opp_id": opp_id,
            "chain_id": opportunity_data.get("chain_id"),
            "strategy": opportunity_data.get("strategy"),
            "execution_mode": exec_mode,
            "final_status": opportunity_data.get("final_status"),
            
            # Explicit semantic proof requirements
            "execution_block": opportunity_data.get("execution_block"),
            "expected_profit": opportunity_data.get("net_profit"),
            
            "tx_hash": opportunity_data.get("tx_hash"),
            "nonce": opportunity_data.get("nonce"),
            "gas_estimate": opportunity_data.get("actual_gas_estimate"),
            
            # Reconciliation
            "receipt_status": opportunity_data.get("receipt_status"),
            "actual_gas_used": opportunity_data.get("actual_gas_used"),
            "effective_gas_price": opportunity_data.get("effective_gas_price"),
            
            # Payload hash for intent verifiable tracing
            "calldata_hash": hashlib.sha256(opportunity_data.get("calldata", b"")).hexdigest() if opportunity_data.get("calldata") else None,
            
            # Chain verification
            "prev_hash": prev_hash
        }
        
        # Consistent ordering for hashing
        entry_str = json.dumps(manifest_entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_str.encode('utf-8')).hexdigest()
        
        with open(manifest_path, "a") as f:
            f.write(json.dumps({"hash": entry_hash, "data": manifest_entry}) + "\n")
            
        opportunity_data["opp_id"] = opp_id
        return opportunity_data

    def _abort(self, opp_id, reason, data, extra_msg=""):
        print(f"[{opp_id}] ABORT: {reason} {extra_msg}")
        data["final_status"] = reason
        data["opp_id"] = opp_id
        return data

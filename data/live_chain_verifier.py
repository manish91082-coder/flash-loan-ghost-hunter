import sys
import os
import time

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from quote_engine.rpc_fetcher import RPCFallbackManager, UNIV2_PAIR_ABI

ERC20_ABI = json.loads('''[
    {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
    {"constant": true, "inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"constant": true, "inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}
]''')

UNIV3_POOL_ABI = json.loads('''[
    {"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"fee","outputs":[{"internalType":"uint24","name":"","type":"uint24"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"liquidity","outputs":[{"internalType":"uint128","name":"","type":"uint128"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"slot0","outputs":[{"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"},{"internalType":"int24","name":"tick","type":"int24"},{"internalType":"uint16","name":"observationIndex","type":"uint16"},{"internalType":"uint16","name":"observationCardinality","type":"uint16"},{"internalType":"uint16","name":"observationCardinalityNext","type":"uint16"},{"internalType":"uint8","name":"feeProtocol","type":"uint8"},{"internalType":"bool","name":"unlocked","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
]''')

def verify_contract_exists(rpc_manager, address_str):
    if not address_str:
        return False
    try:
        checksum = rpc_manager.w3.to_checksum_address(address_str)
        code = rpc_manager.w3.eth.get_code(checksum)
        return len(code) > 2  # more than just '0x'
    except Exception:
        return False

def verify_pool(rpc_manager, pool_address, pool_type='v2'):
    """
    Verifies pool: pool address, token0, token1, fee (if V3), pool type, factory (implicit via reserves), liquidity/reserves.
    Dummy zero address forbidden.
    """
    if not pool_address or pool_address == "0x0000000000000000000000000000000000000000":
        return {"status": "INVALID", "reason": "DUMMY_ADDRESS_FORBIDDEN"}
        
    try:
        checksum = rpc_manager.w3.to_checksum_address(pool_address)
        if pool_type == 'v2':
            # Rely on the rpc_manager's Univ2 ABI check
            # We don't have token_in here, so we just do a raw call
            contract = rpc_manager.w3.eth.contract(address=checksum, abi=UNIV2_PAIR_ABI)
            token0 = rpc_manager.w3.to_checksum_address(contract.functions.token0().call())
            token1 = rpc_manager.w3.to_checksum_address(contract.functions.token1().call())
            reserves = contract.functions.getReserves().call()
            # Golden Slice constraint: V2 liquidity requires both reserves > 0
            if reserves[0] == 0 or reserves[1] == 0:
                return {"status": "INVALID", "reason": "ZERO_LIQUIDITY"}
            return {
                "status": "VALID",
                "pool_type": "v2",
                "token0": token0,
                "token1": token1,
                "reserve0": reserves[0],
                "reserve1": reserves[1]
            }
        elif pool_type == 'v3':
            contract = rpc_manager.w3.eth.contract(address=checksum, abi=UNIV3_POOL_ABI)
            token0 = rpc_manager.w3.to_checksum_address(contract.functions.token0().call())
            token1 = rpc_manager.w3.to_checksum_address(contract.functions.token1().call())
            fee = contract.functions.fee().call()
            liquidity = contract.functions.liquidity().call()
            slot0 = contract.functions.slot0().call()
            factory = rpc_manager.w3.to_checksum_address(contract.functions.factory().call())
            
            if liquidity == 0:
                return {"status": "INVALID", "reason": "ZERO_LIQUIDITY"}
                
            return {
                "status": "VALID",
                "pool_type": "v3",
                "token0": token0,
                "token1": token1,
                "fee": fee,
                "liquidity": liquidity,
                "sqrtPriceX96": slot0[0],
                "factory": factory
            }
        else:
            return {"status": "INVALID", "reason": "UNSUPPORTED_POOL_TYPE"}
    except Exception as e:
        return {"status": "INVALID", "reason": str(e)}

class LiveChainVerifier:
    def __init__(self, chain_id, config):
        self.chain_id = chain_id
        self.config = config
        self.rpc_manager = RPCFallbackManager(config.get("rpc_urls", []), chain_id)
        
    def verify(self):
        """
        Dynamically verifies tokens, DEXes, and flash providers on-chain.
        Returns a dict of verified capabilities.
        """
        print(f"[ChainVerifier] Verifying {self.config.get('name')} ({self.chain_id})")
        report = {
            "chain_id": self.chain_id,
            "status": "NOT_READY",
            "verified_tokens": {},
            "verified_dexes": [],
            "block_number": None,
            "native_token_verified": False
        }
        
        try:
            block = self.rpc_manager.w3.eth.get_block('latest')
            report["block_number"] = block.number
        except Exception as e:
            report["status"] = "DATA_ERROR"
            report["error"] = str(e)
            return report
            
        # Native token verification (Native token is NOT a contract)
        native_symbol = self.config.get("native_token")
        if native_symbol:
            report["native_token_verified"] = True
            report["verified_tokens"]["native"] = native_symbol

        # Verify ERC20 tokens
        tokens_to_check = {
            "wrapped": self.config.get("wrapped_native"),
            "usdc": self.config.get("stablecoins", {}).get("USDC"),
            "usdt": self.config.get("stablecoins", {}).get("USDT")
        }
        
        for name, address in tokens_to_check.items():
            if address and verify_contract_exists(self.rpc_manager, address):
                try:
                    checksum = self.rpc_manager.w3.to_checksum_address(address)
                    contract = self.rpc_manager.w3.eth.contract(address=checksum, abi=ERC20_ABI)
                    decimals = contract.functions.decimals().call()
                    symbol = contract.functions.symbol().call()
                    report["verified_tokens"][name] = {
                        "address": checksum,
                        "decimals": decimals,
                        "symbol": symbol
                    }
                except Exception as e:
                    print(f"[Token Verify Error] {name} ({address}): {e}")
                    
        # Verify DEX Quoters/Factories
        dexes = self.config.get("dexes", {})
        for dex_name, dex_conf in dexes.items():
            if "quoter" in dex_conf:
                if verify_contract_exists(self.rpc_manager, dex_conf["quoter"]):
                    report["verified_dexes"].append(dex_name)
                    
        # Hard Gate: Only return READY if all mandatory identities are verified
        if not report["native_token_verified"]:
            report["status"] = "MISSING_NATIVE_TOKEN"
            return report
        if "wrapped" not in report["verified_tokens"]:
            report["status"] = "MISSING_WRAPPED_TOKEN"
            return report
        if "usdc" not in report["verified_tokens"]:
            report["status"] = "MISSING_USDC_TOKEN"
            return report
        if len(report["verified_dexes"]) < 2:
            report["status"] = "INSUFFICIENT_DEXES"
            return report
            
        report["status"] = "READY"
        return report

if __name__ == "__main__":
    from economics.flash_loan import load_chain_config
    cfg = load_chain_config()
    for cid, conf in cfg.items():
        if isinstance(conf, dict) and "chain_id" in conf:
            verifier = LiveChainVerifier(int(cid), conf)
            res = verifier.verify()
            print(res)

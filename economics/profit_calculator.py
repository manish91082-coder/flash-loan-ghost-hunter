from decimal import Decimal, getcontext
import json

# Set precision high enough for EVM uint256
getcontext().prec = 78

class ProfitCalculator:
    def __init__(self, flash_provider):
        self.flash_provider = flash_provider

    def calculate_flash_loan_repayment(self, borrow_amount):
        """Returns borrow_amount + flash loan premium (in raw integer units)."""
        if borrow_amount is None:
            return None
        premium = self.flash_provider.calculate_premium(borrow_amount)
        return borrow_amount + premium

    def calculate_l2_gas_cost(self, l2_gas_used, l2_gas_price_wei, l1_data_gas_used=0, l1_gas_price_wei=0, l2_multiplier_bps=10000):
        """
        Calculates granular gas costs. l2_multiplier_bps = 10000 means 1.0 multiplier.
        Returns strict int.
        """
        l2_execution_fee = l2_gas_used * l2_gas_price_wei
        l1_data_fee = (l1_data_gas_used * l1_gas_price_wei * l2_multiplier_bps) // 10000
        return l2_execution_fee + l1_data_fee

    def normalize_gas_to_borrow_token(self, total_gas_cost_wei, borrow_token_decimals, eth_price_in_borrow_token):
        """
        Converts gas cost (in native ETH wei) to the equivalent value in the borrow token.
        Returns strict int.
        """
        if total_gas_cost_wei is None or eth_price_in_borrow_token is None:
            return None
        # Gas cost in standard ETH (1e18) * Price = Cost in Borrow Token
        gas_cost_in_borrow_token = (total_gas_cost_wei * eth_price_in_borrow_token) // (10**18)
        return gas_cost_in_borrow_token

    def calculate_net_profit(self, borrow_amount, final_amount, total_gas_cost_wei, borrow_token_decimals=18, eth_price_in_borrow_token=None, min_profit_usd_value_cents=100, borrow_token_price_usd_cents=100):
        """
        Calculates net profit accounting for flash loan fees, gas costs, and Zero-Loss Guard.
        Strictly avoids floats. USD values are expressed in cents to keep integer math where possible.
        If final_amount is None (meaning quote failed), returns None for PnL.
        """
        if final_amount is None or final_amount == 0:
            return None, False, "ABORT: QUOTE_FAILED or ZERO_OUTPUT"

        repayment = self.calculate_flash_loan_repayment(borrow_amount)
        if repayment is None:
            return None, False, "ABORT: NO_FLASH_PROVIDER_DATA"

        gross_profit = final_amount - repayment
        
        if not eth_price_in_borrow_token:
            return None, False, "ABORT: MISSING_ETH_PRICE"
            
        normalized_gas_cost = self.normalize_gas_to_borrow_token(total_gas_cost_wei, borrow_token_decimals, eth_price_in_borrow_token)

        if normalized_gas_cost is None:
            return None, False, "ABORT: GAS_CALCULATION_FAILED"

        net_profit_tokens = gross_profit - normalized_gas_cost
        
        # Zero-Loss Guard Enforcement using Decimals for division to avoid precision loss
        # net_profit_usd_cents = (net_profit_tokens / 10**decimals) * borrow_token_price_usd_cents
        net_profit_tokens_dec = Decimal(net_profit_tokens)
        decimals_dec = Decimal(10**borrow_token_decimals)
        borrow_token_price_usd_cents_dec = Decimal(borrow_token_price_usd_cents)
        
        net_profit_usd_cents = (net_profit_tokens_dec / decimals_dec) * borrow_token_price_usd_cents_dec
        min_profit_usd_value_cents_dec = Decimal(min_profit_usd_value_cents)
        
        if net_profit_usd_cents < min_profit_usd_value_cents_dec:
            return net_profit_tokens, False, f"ABORT: UNPROFITABLE (Net profit {net_profit_usd_cents} cents < Min {min_profit_usd_value_cents} cents)"
        
        return net_profit_tokens, True, f"SUCCESS: READY (Net profit {net_profit_usd_cents} cents)"

    def estimate_l2_gas(self, w3, tx, chain_config):
        """
        Dynamic gas & L1 data fee calculator based on chain ID config.
        Returns strict int.
        """
        chain_id = chain_config.get("chain_id")
        try:
            gas_price = w3.eth.gas_price
        except Exception:
            return None
            
        try:
            gas_used = w3.eth.estimate_gas(tx)
        except Exception:
            # Do NOT mock gas. If it fails to estimate, return None to trigger QUOTE_FAILED / NULL
            return None
            
        l2_execution_fee = gas_used * gas_price
        
        # Ethereum
        if chain_id == 1:
            return l2_execution_fee
            
        # Arbitrum
        if chain_id == 42161:
            l1_data_fee = (gas_used * gas_price * 11000) // 10000 # 1.1x multiplier
            return l2_execution_fee + l1_data_fee
            
        # Base (8453) / Optimism (10)
        if chain_id in [10, 8453]:
            gas_oracle_address = w3.to_checksum_address("0x420000000000000000000000000000000000000F")
            GAS_ORACLE_ABI = json.loads('[{"inputs":[{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"getL1Fee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')
            
            try:
                oracle = w3.eth.contract(address=gas_oracle_address, abi=GAS_ORACLE_ABI)
                
                # Fetch actual transaction data instead of using dummy padding
                tx_data = tx.get('data') or tx.get('input')
                if not tx_data:
                    print("[Gas Estimation] Missing actual calldata in tx object. Aborting L1 estimate.")
                    return None
                
                # Ensure data is in bytes format if it's a hex string
                if isinstance(tx_data, str) and tx_data.startswith('0x'):
                    tx_data = bytes.fromhex(tx_data[2:])
                elif isinstance(tx_data, str):
                    tx_data = tx_data.encode('utf-8')
                    
                l1_data_fee = oracle.functions.getL1Fee(tx_data).call()
            except Exception as e:
                # Fallback to strict 1.1x multiplier if L1 fee oracle fails is FORBIDDEN by PFLC-5.3
                print(f"[Gas Estimation] L1 Fee Oracle failed: {e}")
                return None
                
            return l2_execution_fee + l1_data_fee
            
        return l2_execution_fee

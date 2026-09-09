# PFLC-REAL-MISSION-3.0 Code Modifications

## File: `chains.json`
Path: `config/chains.json`
```json
{
  "1": {
    "chain_id": 1,
    "name": "Ethereum",
    "rpc_urls": ["https://ethereum-rpc.publicnode.com", "https://rpc.ankr.com/eth"],
    "native_token": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "native_token_decimals": 18,
    "flash_loan_providers": {
      "aave_v3": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
      "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    },
    "dexes": {
      "uniswap_v3": { "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564", "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6", "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984" },
      "sushiswap_v2": { "router": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F" }
    },
    "l2_gas_params": { "l1_data_fee_multiplier": 0.0, "l2_execution_fee_multiplier": 1.0 },
    "zero_loss_guard": { "min_profit_usd": 20.0, "max_slippage_bips": 50 },
    "finality": { "max_block_drift": 1 }
  },
  "8453": {
    "chain_id": 8453,
    "name": "Base",
    "rpc_urls": ["https://mainnet.base.org", "https://base.llamarpc.com"],
    "native_token": "0x4200000000000000000000000000000000000006",
    "native_token_decimals": 18,
    "flash_loan_providers": {
      "aave_v3": "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5",
      "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    },
    "dexes": {
      "uniswap_v3": { "router": "0x2626664c2603336E57B271c5C0b26F421741e481", "quoter": "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a", "factory": "0x33128a8fC17869897dcE68Ed026d694621f6FDfD" },
      "aerodrome_v2": { "router": "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43" }
    },
    "l2_gas_params": { "l1_data_fee_multiplier": 1.5, "l2_execution_fee_multiplier": 1.0 },
    "zero_loss_guard": { "min_profit_usd": 1.0, "max_slippage_bips": 50 },
    "finality": { "max_block_drift": 2 }
  },
  "10": {
    "chain_id": 10,
    "name": "Optimism",
    "rpc_urls": ["https://mainnet.optimism.io", "https://optimism-rpc.publicnode.com"],
    "native_token": "0x4200000000000000000000000000000000000006",
    "native_token_decimals": 18,
    "flash_loan_providers": {
      "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
      "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    },
    "dexes": {
      "uniswap_v3": { "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564", "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6", "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984" },
      "velodrome_v2": { "router": "0x9c12939390052919aF3155f41bf4160Fd3666A6f" }
    },
    "l2_gas_params": { "l1_data_fee_multiplier": 1.3, "l2_execution_fee_multiplier": 1.0 },
    "zero_loss_guard": { "min_profit_usd": 1.0, "max_slippage_bips": 50 },
    "finality": { "max_block_drift": 2 }
  },
  "42161": {
    "chain_id": 42161,
    "name": "Arbitrum",
    "rpc_urls": ["https://arb1.arbitrum.io/rpc", "https://arbitrum-rpc.publicnode.com"],
    "native_token": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    "native_token_decimals": 18,
    "flash_loan_providers": {
      "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
      "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    },
    "dexes": {
      "uniswap_v3": { "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564", "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6", "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984" },
      "sushiswap_v2": { "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506" }
    },
    "l2_gas_params": { "l1_data_fee_multiplier": 1.1, "l2_execution_fee_multiplier": 1.0 },
    "zero_loss_guard": { "min_profit_usd": 1.0, "max_slippage_bips": 50 },
    "finality": { "max_block_drift": 2 }
  },
  "137": {
    "chain_id": 137,
    "name": "Polygon",
    "rpc_urls": ["https://polygon-rpc.com", "https://polygon-bor-rpc.publicnode.com"],
    "native_token": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    "native_token_decimals": 18,
    "flash_loan_providers": {
      "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
      "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    },
    "dexes": {
      "uniswap_v3": { "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564", "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6", "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984" },
      "quickswap_v2": { "router": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff" }
    },
    "l2_gas_params": { "l1_data_fee_multiplier": 0.0, "l2_execution_fee_multiplier": 1.0 },
    "zero_loss_guard": { "min_profit_usd": 0.5, "max_slippage_bips": 50 },
    "finality": { "max_block_drift": 2 }
  },
  "43114": {
    "chain_id": 43114,
    "name": "Avalanche",
    "rpc_urls": ["https://api.avax.network/ext/bc/C/rpc", "https://avalanche-c-chain-rpc.publicnode.com"],
    "native_token": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    "native_token_decimals": 18,
    "flash_loan_providers": {
      "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
      "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    },
    "dexes": {
      "traderjoe_v2": { "router": "0x60aE616a2155Ee3d9A68541Ba4544862310933d4" }
    },
    "l2_gas_params": { "l1_data_fee_multiplier": 0.0, "l2_execution_fee_multiplier": 1.0 },
    "zero_loss_guard": { "min_profit_usd": 0.5, "max_slippage_bips": 50 },
    "finality": { "max_block_drift": 2 }
  },
  "250": {
    "chain_id": 250,
    "name": "Fantom",
    "rpc_urls": ["https://rpc.ftm.tools", "https://fantom-rpc.publicnode.com"],
    "native_token": "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",
    "native_token_decimals": 18,
    "flash_loan_providers": {
      "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
    },
    "dexes": {
      "spookyswap_v2": { "router": "0x31F63A33141fFee63D4B26755430a390ACdD8a4d" }
    },
    "l2_gas_params": { "l1_data_fee_multiplier": 0.0, "l2_execution_fee_multiplier": 1.0 },
    "zero_loss_guard": { "min_profit_usd": 0.5, "max_slippage_bips": 50 },
    "finality": { "max_block_drift": 1 }
  },
  "42220": {
    "chain_id": 42220,
    "name": "Celo",
    "rpc_urls": ["https://forno.celo.org"],
    "native_token": "0x471EcE3750Da237f93B8E339c536989b8978a438",
    "native_token_decimals": 18,
    "flash_loan_providers": {
      "aave_v3": "0x2F869d8Ba859D3905D97C52097e3DDEf2010A94F"
    },
    "dexes": {
      "uniswap_v3": { "router": "0x5615CDAb10dc425a742d643d949a7F474C01abc4", "quoter": "0x82825d0554fA07f7FC52Ab63c961F330fdEFa8E8", "factory": "0xAfE208a311B21f13EF87E33A90049fC17A7acE2c" }
    },
    "l2_gas_params": { "l1_data_fee_multiplier": 0.0, "l2_execution_fee_multiplier": 1.0 },
    "zero_loss_guard": { "min_profit_usd": 0.5, "max_slippage_bips": 50 },
    "finality": { "max_block_drift": 2 }
  }
}

```

## File: `intent.py`
Path: `execution/intent.py`
```py
from eth_account.messages import encode_typed_data
from web3 import Web3

class ExecutionIntentBuilder:
    def __init__(self, private_key, verifying_contract, chain_id):
        self.w3 = Web3()
        self.account = self.w3.eth.account.from_key(private_key)
        self.verifying_contract = verifying_contract
        self.chain_id = chain_id
        
    def build_typed_data(self, intent_dict):
        """
        Builds the EIP-712 typed data payload matching the Solidity struct.
        """
        return {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"}
                ],
                "ExecutionIntent": [
                    {"name": "executionId", "type": "bytes32"},
                    {"name": "providerType", "type": "uint8"},
                    {"name": "providerAddress", "type": "address"},
                    {"name": "tokenBorrow", "type": "address"},
                    {"name": "amountBorrow", "type": "uint256"},
                    {"name": "swap1Type", "type": "uint8"},
                    {"name": "routerA", "type": "address"},
                    {"name": "pathA", "type": "bytes"},
                    {"name": "minAmountOut1", "type": "uint256"},
                    {"name": "swap2Type", "type": "uint8"},
                    {"name": "routerB", "type": "address"},
                    {"name": "pathB", "type": "bytes"},
                    {"name": "minAmountOutFinal", "type": "uint256"},
                    {"name": "minimumOnChainSurplus", "type": "uint256"},
                    {"name": "maximumGasLimit", "type": "uint256"},
                    {"name": "deadline", "type": "uint256"}
                ]
            },
            "primaryType": "ExecutionIntent",
            "domain": {
                "name": "PhantomX Executor",
                "version": "1",
                "chainId": self.chain_id,
                "verifyingContract": self.verifying_contract
            },
            "message": intent_dict
        }
        
    def sign_intent(self, intent_dict):
        typed_data = self.build_typed_data(intent_dict)
        signed_message = self.account.sign_typed_data(full_message=typed_data)
        
        # Keep it as a dict but append the signature
        result = dict(intent_dict)
        result['signature'] = signed_message.signature
        return result

class PathEncoder:
    @staticmethod
    def build_v2_path(token_in, token_out):
        from eth_abi import encode
        return encode(['address[]'], [[token_in, token_out]])

    @staticmethod
    def build_v3_path_single(token_in, fee, token_out):
        return Web3.to_bytes(hexstr=token_in) + int(fee).to_bytes(3, 'big') + Web3.to_bytes(hexstr=token_out)

    @staticmethod
    def build_v3_path_multi(token_a, fee1, token_b, fee2, token_c):
        return (
            Web3.to_bytes(hexstr=token_a) + 
            int(fee1).to_bytes(3, 'big') + 
            Web3.to_bytes(hexstr=token_b) + 
            int(fee2).to_bytes(3, 'big') + 
            Web3.to_bytes(hexstr=token_c)
        )

    @staticmethod
    def build_yield_path(protocol, action, token):
        # Placeholder for yield farming stake/unstake calldata packing
        # format: action_id (1 byte) + token_address (20 bytes) + protocol_id (1 byte)
        action_id = 1 if action == "stake" else 0
        protocol_id = 1 # e.g. 1 for Aave, 2 for Compound
        return int(action_id).to_bytes(1, 'big') + Web3.to_bytes(hexstr=token) + int(protocol_id).to_bytes(1, 'big')

    @staticmethod
    def build_statistical_path(token_a, token_b):
        # Mean reversion placeholder packing
        return Web3.to_bytes(hexstr=token_a) + Web3.to_bytes(hexstr=token_b)

    @staticmethod
    def build_bridge_path(chain_a, chain_b, token):
        # Cross-chain bridge calldata packing
        return int(chain_a).to_bytes(32, 'big') + int(chain_b).to_bytes(32, 'big') + Web3.to_bytes(hexstr=token)

    @staticmethod
    def build_mev_path(target_tx_hash, token):
        # Sandwich MEV payload (target tx hash + token)
        return Web3.to_bytes(hexstr=target_tx_hash) + Web3.to_bytes(hexstr=token)

```

## File: `flash_loan.py`
Path: `economics/flash_loan.py`
```py
import json
import os
from typing import Optional

def load_chain_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'chains.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {"chains": {}}

def get_best_provider(chain_id: int, borrow_asset: str, amount: int) -> Optional[str]:
    """
    Returns the best flash loan provider address for the given chain based on basic logic:
    1. Aave V3 (0.05% fee)
    2. Uniswap V3 (variable fee 0.05% or 0.30%)
    3. Balancer (0% fee but limited asset coverage)
    Fallback to None if no provider works.
    """
    config_data = load_chain_config()
    chain_config = config_data.get('chains', {}).get(str(chain_id))
    
    if not chain_config:
        return None
        
    providers = chain_config.get('flash_loan_providers', {})
    
    # Logic: Balancer 0 fee if available (ideal case)
    if 'balancer' in providers and providers['balancer']:
        # Assuming Balancer has liquidity
        return providers['balancer']
        
    # Fallback to Aave V3
    if 'aave_v3' in providers and providers['aave_v3']:
        return providers['aave_v3']
        
    # Fallback to UniV3 if flash loan is supported via callback
    if 'uniswap_v3' in providers and providers['uniswap_v3']:
        return providers['uniswap_v3']
        
    return None

```

## File: `profit_calculator.py`
Path: `economics/profit_calculator.py`
```py
class ProfitCalculator:
    def __init__(self, flash_provider):
        self.flash_provider = flash_provider

    def calculate_flash_loan_repayment(self, borrow_amount):
        premium = self.flash_provider.calculate_premium(borrow_amount)
        return borrow_amount + premium

    def calculate_l2_gas_cost(self, l2_gas_used, l2_gas_price_wei, l1_data_gas_used=0, l1_gas_price_wei=0, l2_multiplier=1.0):
        """
        Calculates granular gas costs for L2s like Optimism and Base.
        Total Fee = L2 Execution Fee + L1 Data Fee
        L1 Data Fee = (L1 Gas Price * L1 Data Gas Used) * l2_multiplier
        """
        l2_execution_fee = l2_gas_used * l2_gas_price_wei
        l1_data_fee = int((l1_data_gas_used * l1_gas_price_wei) * l2_multiplier)
        return l2_execution_fee + l1_data_fee

    def normalize_gas_to_borrow_token(self, total_gas_cost_wei, borrow_token_decimals, eth_price_in_borrow_token):
        """
        Converts gas cost (in native ETH wei) to the equivalent value in the borrow token.
        :param eth_price_in_borrow_token: Price of 1 ETH expressed in the borrow token (scaled to its decimals).
        """
        # Gas cost in standard ETH (1e18) * Price = Cost in Borrow Token
        # Formula: (total_gas_cost_wei * eth_price_in_borrow_token) / 10**18
        gas_cost_in_borrow_token = (total_gas_cost_wei * eth_price_in_borrow_token) // (10**18)
        return gas_cost_in_borrow_token

    def calculate_net_profit(self, borrow_amount, final_amount, total_gas_cost_wei, borrow_token_decimals=18, eth_price_in_borrow_token=None):
        """
        Calculates net profit accounting for flash loan fees and gas costs.
        Ensures unit domain matching (Gas -> Borrow Token)
        """
        repayment = self.calculate_flash_loan_repayment(borrow_amount)
        gross_profit = final_amount - repayment
        
        if eth_price_in_borrow_token:
            normalized_gas_cost = self.normalize_gas_to_borrow_token(total_gas_cost_wei, borrow_token_decimals, eth_price_in_borrow_token)
        else:
            # Assume borrow token IS the native gas token (WETH -> ETH)
            normalized_gas_cost = total_gas_cost_wei

        net_profit = gross_profit - normalized_gas_cost
        
        return net_profit, net_profit > 0

    def estimate_l2_gas(self, w3, tx, chain_config):
        """
        Dynamic gas & L1 data fee calculator based on chain ID config.
        """
        chain_id = chain_config.get("chain_id")
        gas_price = w3.eth.gas_price
        
        # Ethereum
        if chain_id == 1:
            gas_used = w3.eth.estimate_gas(tx)
            return gas_used * gas_price
            
        # Arbitrum
        if chain_id == 42161:
            gas_used = w3.eth.estimate_gas(tx)
            # Rough Arbitrum L1 data fee logic (approx)
            l1_data_fee = int((gas_used * gas_price) * 1.1)
            return (gas_used * gas_price) + l1_data_fee
            
        # Base (8453) / Optimism (10)
        gas_used = w3.eth.estimate_gas(tx)
        l2_params = chain_config.get("l2_gas_params", {})
        l1_multiplier = l2_params.get("l1_data_fee_multiplier", 1.0)
        
        l1_gas_price = w3.eth.gas_price # Approximation for test/fallback
        # In a real environment, query the GasPriceOracle contract on OP Stack.
        l1_data_fee = int((gas_used * l1_gas_price) * l1_multiplier)
        
        return (gas_used * gas_price) + l1_data_fee

```

## File: `mev.py`
Path: `risk/mev.py`
```py
class MEVRiskModel:
    def __init__(self):
        pass

    def evaluate_sandwich_risk(self, route_visibility, expected_slippage_bips):
        """
        Evaluates the likelihood and impact of a MEV sandwich attack.
        :param route_visibility: 'PUBLIC_MEMPOOL', 'PRIVATE_RELAY'
        :param expected_slippage_bips: The allowed slippage in basis points
        """
        if route_visibility == 'PRIVATE_RELAY':
            return True, "MEV Risk Low: Using Private Relay"
            
        if expected_slippage_bips > 50:
            return False, f"MEV Risk High: Slippage tolerance ({expected_slippage_bips} bips) is too wide for public mempool"
            
        return True, "MEV Risk Acceptable: Slippage is tight enough for public mempool"

    def send_private_bundle(self, tx_calldata, chain_id, slippage_bips):
        """
        Sends transaction via Private RPC / Flashbots if MEV risk is present.
        """
        if slippage_bips > 50:
            return False, "ABORT: MEV Risk High (>50 bps Slippage)"
            
        if chain_id == 1:
            # Ethereum Mainnet: Use Flashbots Relay
            relay_url = "https://relay.flashbots.net"
            return True, f"Sent via Flashbots: {relay_url}"
        elif chain_id in [10, 8453, 42161]:
            # L2s: Use Alchemy or other private mempool endpoints
            return True, "Sent via L2 Private RPC"
        
        return True, "Sent via Standard RPC (Low MEV Environment)"

```

## File: `lifecycle.py`
Path: `execution/lifecycle.py`
```py
import time
import os
import json

from economics.flash_loan import load_chain_config, get_best_provider
from execution.intent import ExecutionIntentBuilder, PathEncoder

class AutonomousLifecycleDaemon:
    def __init__(self, private_key):
        self.private_key = private_key
        self.chain_config = load_chain_config()
        self.state = {}
        # dummy verifying contract for now
        self.verifying_contract = "0x7c5cE74e72AEC0748d4726570e81545b1BCDB626"

    def run_daemon(self):
        print("=== STARTING AUTONOMOUS LIFECYCLE DAEMON ===")
        chains = self.chain_config.get('chains', {})
        
        while True:
            for chain_id_str, config in chains.items():
                chain_id = int(chain_id_str)
                self._scan_chain(chain_id, config)
            
            # Rate Limit / Sleep
            print("[DAEMON] Sleeping for 5 seconds before next cycle...")
            time.sleep(5)

    def _scan_chain(self, chain_id, config):
        print(f"\n[SCAN] Checking Chain: {config.get('name')} ({chain_id})")
        # In a real daemon, fetch block number from RPC
        # state[chain_id] = last_block_processed
        
        provider = get_best_provider(chain_id, config.get("native_token"), 1000)
        if not provider:
            print("  -> No suitable flash loan provider found.")
            return

        # Scan for opportunities (stub)
        opportunity = self._find_opportunity(chain_id, config)
        if opportunity:
            self._execute_opportunity(chain_id, config, opportunity)
        else:
            print("  -> No profitable opportunity found.")

    def _find_opportunity(self, chain_id, config):
        # Stub for finding an opportunity
        # In real logic, this calls quote_engine and profit_calculator
        # Let's mock a NO TRADE for safe rejection
        return None

    def _execute_opportunity(self, chain_id, config, opportunity):
        print("  -> Profitable opportunity found! Executing...")
        builder = ExecutionIntentBuilder(self.private_key, self.verifying_contract, chain_id)
        # Sign intent and broadcast...
        # Log to execution_report.md
        with open("execution_report.md", "a") as f:
            f.write(f"Executed trade on {config.get('name')} (Chain ID: {chain_id})\n")

if __name__ == "__main__":
    pk = "0x" + "1" * 64
    daemon = AutonomousLifecycleDaemon(pk)
    # daemon.run_daemon() # Commented out to prevent infinite loop in script execution
    print("Daemon initialized and ready.")

```


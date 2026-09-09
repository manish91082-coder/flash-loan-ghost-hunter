import json
import time
from web3 import Web3
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
import random

# Minimal ABI for Uniswap V2 Pair to fetch reserves
UNIV2_PAIR_ABI = json.loads('''[
    {
        "constant": true,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]''')

UNIV2_ROUTER_ABI = json.loads('''[
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]''')

class RPCFallbackManager:
    def __init__(self, rpc_urls, chain_id=1):
        """
        Manages multiple RPC URLs with exponential backoff and rate limiting.
        """
        self.rpc_urls = rpc_urls
        self.chain_id = chain_id
        self.current_rpc_index = 0
        self.w3 = self._connect_current_rpc()
        
    def _connect_current_rpc(self):
        url = self.rpc_urls[self.current_rpc_index]
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10}))
        # Inject POA middleware for networks like Optimism/Base
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # PROVIDER CHAIN SAFETY: strict verification
        try:
            returned_chain = w3.eth.chain_id
            if returned_chain != self.chain_id:
                raise Exception(f"PROVIDER_CHAIN_MISMATCH: Expected {self.chain_id}, got {returned_chain}")
        except Exception as e:
            raise Exception(f"RPC Connection/Validation Failed: {e}")
            
        return w3
        
    def _rotate_rpc(self):
        self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_urls)
        print(f"Rotating RPC to: {self.rpc_urls[self.current_rpc_index]}")
        self.w3 = self._connect_current_rpc()

    def execute_with_fallback(self, func, *args, **kwargs):
        """
        Executes a Web3 function with exponential backoff across multiple RPC providers.
        """
        max_retries_per_rpc = 3
        base_delay = 1.0
        
        for _ in range(len(self.rpc_urls)):
            for attempt in range(max_retries_per_rpc):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_str = str(e).lower()
                    if "execution reverted" in error_str or "contract" in error_str or "no data" in error_str:
                        # This is a legitimate on-chain failure, not an infrastructure issue.
                        raise
                        
                    print(f"RPC Error on {self.rpc_urls[self.current_rpc_index]}: {e}")
                    
                    if any(x in error_str for x in ["429", "401", "403", "500", "502", "503", "max retries exceeded", "timeout", "too many requests"]):
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"Rate limited/Connection Error. Backing off for {delay:.2f}s...")
                        time.sleep(delay)
                    else:
                        break
            
            self._rotate_rpc()
            
        raise Exception("All RPCs failed. Execution aborted.")

    def _internal_get_univ2_reserves(self, pair_address, token_in_address, block_identifier='latest'):
        checksum_pair = self.w3.to_checksum_address(pair_address)
        checksum_token_in = self.w3.to_checksum_address(token_in_address)
        
        contract = self.w3.eth.contract(address=checksum_pair, abi=UNIV2_PAIR_ABI)
        token0 = contract.functions.token0().call(block_identifier=block_identifier)
        reserves = contract.functions.getReserves().call(block_identifier=block_identifier)
        
        r0 = reserves[0]
        r1 = reserves[1]
        
        # Also return the block number and timestamp
        block = self.w3.eth.get_block(block_identifier)
        block_number = block.number
        block_timestamp = block.timestamp
        
        if checksum_token_in == token0:
            return r0, r1, block_number, block_timestamp
        else:
            return r1, r0, block_number, block_timestamp

    def get_univ2_reserves(self, pair_address, token_in_address, block_identifier='latest'):
        """
        Fetches exact reserves for a UniV2 pair and aligns them with token_in, returning state block and timestamp.
        :return: (reserve_in, reserve_out, block_number, block_timestamp)
        """
        return self.execute_with_fallback(self._internal_get_univ2_reserves, pair_address, token_in_address, block_identifier)

    def _internal_get_univ2_amounts_out(self, router_address, amount_in, path, block_identifier='latest'):
        checksum_router = self.w3.to_checksum_address(router_address)
        checksum_path = [self.w3.to_checksum_address(p) for p in path]
        
        contract = self.w3.eth.contract(address=checksum_router, abi=UNIV2_ROUTER_ABI)
        amounts = contract.functions.getAmountsOut(amount_in, checksum_path).call(block_identifier=block_identifier)
        
        block = self.w3.eth.get_block(block_identifier)
        return {
            "amountOut": amounts[-1],
            "block_number": block.number,
            "block_timestamp": block.timestamp
        }
        
    def get_univ2_amounts_out(self, router_address, amount_in, path, block_identifier='latest'):
        return self.execute_with_fallback(self._internal_get_univ2_amounts_out, router_address, amount_in, path, block_identifier)
            
    def _internal_get_univ3_quote(self, quoter_address, token_in, token_out, amount_in, fee, block_identifier='latest'):
        checksum_quoter = self.w3.to_checksum_address(quoter_address)
        UNIV3_QUOTER_ABI = json.loads('''[{"inputs":[{"components":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"internalType":"struct IQuoterV2.QuoteExactInputSingleParams","name":"params","type":"tuple"}],"name":"quoteExactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceX96After","type":"uint160"},{"internalType":"uint32","name":"initializedTicksCrossed","type":"uint32"},{"internalType":"uint256","name":"gasEstimate","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]''')
        contract = self.w3.eth.contract(address=checksum_quoter, abi=UNIV3_QUOTER_ABI)
        
        params = (
            self.w3.to_checksum_address(token_in),
            self.w3.to_checksum_address(token_out),
            amount_in,
            fee,
            0
        )
        
        # call the contract; might fail if pool doesn't exist or not enough liquidity
        request_time = time.time()
        result = contract.functions.quoteExactInputSingle(params).call(block_identifier=block_identifier)
        
        block = self.w3.eth.get_block(block_identifier)
        current_time = time.time()
        
        # Quote age is based on block timestamp
        block_timestamp = block.timestamp
        block_age_seconds = int(current_time - block_timestamp)
        quote_age_ms = block_age_seconds * 1000
        
        return {
            "amountOut": result[0],
            "sqrtPriceX96After": result[1],
            "gasEstimate": result[3],
            "block_number": block.number,
            "block_timestamp": block_timestamp,
            "quote_age_ms": quote_age_ms,
            "block_age_seconds": block_age_seconds
        }

    def get_univ3_quote(self, quoter_address, token_in, token_out, amount_in, fee, block_identifier='latest'):
        return self.execute_with_fallback(self._internal_get_univ3_quote, quoter_address, token_in, token_out, amount_in, fee, block_identifier)

    def get_gas_price(self):
        """Returns current gas price in wei"""
        return self.execute_with_fallback(lambda: self.w3.eth.gas_price)
        
    def _internal_get_univ3_twap(self, factory_address, tokenA, tokenB, fee, seconds_ago, block_identifier='latest'):
        checksum_factory = self.w3.to_checksum_address(factory_address)
        FACTORY_ABI = json.loads('''[{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint24","name":"","type":"uint24"}],"name":"getPool","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]''')
        factory = self.w3.eth.contract(address=checksum_factory, abi=FACTORY_ABI)
        
        tokenA = self.w3.to_checksum_address(tokenA)
        tokenB = self.w3.to_checksum_address(tokenB)
        
        pool_address = factory.functions.getPool(tokenA, tokenB, fee).call(block_identifier=block_identifier)
        if pool_address == "0x0000000000000000000000000000000000000000":
            raise Exception("POOL_DOES_NOT_EXIST")
            
        POOL_ABI = json.loads('''[{"inputs":[{"internalType":"uint32[]","name":"secondsAgos","type":"uint32[]"}],"name":"observe","outputs":[{"internalType":"int56[]","name":"tickCumulatives","type":"int56[]"},{"internalType":"uint160[]","name":"secondsPerLiquidityCumulativeX128s","type":"uint160[]"}],"stateMutability":"view","type":"function"}]''')
        pool = self.w3.eth.contract(address=pool_address, abi=POOL_ABI)
        
        # Will revert with "OLD" if the oracle doesn't have enough cardinality
        result = pool.functions.observe([seconds_ago, 0]).call(block_identifier=block_identifier)
        return result
        
    def get_univ3_twap(self, factory_address, tokenA, tokenB, fee, seconds_ago=300, block_identifier='latest'):
        return self.execute_with_fallback(self._internal_get_univ3_twap, factory_address, tokenA, tokenB, fee, seconds_ago, block_identifier)

    def _internal_get_aave_reserve_data(self, pool_address, token_address, block_identifier='latest'):
        checksum_pool = self.w3.to_checksum_address(pool_address)
        checksum_token = self.w3.to_checksum_address(token_address)
        
        # We attempt to call getReserveData on the Pool
        # ABI for Aave V3 Pool getReserveData
        POOL_ABI = json.loads('''[{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveData","outputs":[{"components":[{"internalType":"uint256","name":"configuration","type":"uint256"},{"internalType":"uint128","name":"liquidityIndex","type":"uint128"},{"internalType":"uint128","name":"currentLiquidityRate","type":"uint128"},{"internalType":"uint128","name":"variableBorrowIndex","type":"uint128"},{"internalType":"uint128","name":"currentVariableBorrowRate","type":"uint128"},{"internalType":"uint128","name":"currentStableBorrowRate","type":"uint128"},{"internalType":"uint40","name":"lastUpdateTimestamp","type":"uint40"},{"internalType":"uint16","name":"id","type":"uint16"},{"internalType":"address","name":"aTokenAddress","type":"address"},{"internalType":"address","name":"stableDebtTokenAddress","type":"address"},{"internalType":"address","name":"variableDebtTokenAddress","type":"address"},{"internalType":"address","name":"interestRateStrategyAddress","type":"address"},{"internalType":"uint128","name":"accruedToTreasury","type":"uint128"},{"internalType":"uint128","name":"unbacked","type":"uint128"},{"internalType":"uint128","name":"isolationModeTotalDebt","type":"uint128"}],"internalType":"struct DataTypes.ReserveData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"}]''')
        pool = self.w3.eth.contract(address=checksum_pool, abi=POOL_ABI)
        
        # This will revert if the address isn't an Aave Pool or token isn't supported
        result = pool.functions.getReserveData(checksum_token).call(block_identifier=block_identifier)
        return result
        
    def get_aave_reserve_data(self, pool_address, token_address, block_identifier='latest'):
        return self.execute_with_fallback(self._internal_get_aave_reserve_data, pool_address, token_address, block_identifier)

    def _internal_get_layerzero_version(self, endpoint_address, block_identifier='latest'):
        checksum_endpoint = self.w3.to_checksum_address(endpoint_address)
        
        # We attempt to call defaultSendVersion() on the LayerZero Endpoint
        ENDPOINT_ABI = json.loads('''[{"inputs":[],"name":"defaultSendVersion","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"}]''')
        endpoint = self.w3.eth.contract(address=checksum_endpoint, abi=ENDPOINT_ABI)
        
        result = endpoint.functions.defaultSendVersion().call(block_identifier=block_identifier)
        return result
        
    def get_layerzero_version(self, endpoint_address, block_identifier='latest'):
        return self.execute_with_fallback(self._internal_get_layerzero_version, endpoint_address, block_identifier)

    def check_websocket_mempool(self):
        """
        Genuinely attempt to connect to the WSS equivalent of the current HTTP RPC
        to subscribe to the pending transactions mempool.
        """
        current_url = self.rpc_urls[self.current_rpc_index]
        if current_url.startswith("http://"):
            wss_url = current_url.replace("http://", "ws://")
        elif current_url.startswith("https://"):
            wss_url = current_url.replace("https://", "wss://")
        else:
            raise Exception("INVALID_RPC_SCHEMA_FOR_WSS")
            
        # Attempt to create a WebsocketProvider. This will throw if it can't connect,
        # or if the provider rejects WSS connections.
        try:
            ws_provider = Web3.WebsocketProvider(wss_url, websocket_timeout=2)
            # Just instantiating doesn't always connect immediately in older web3.py versions,
            # so we explicitly check connected status if available.
            if hasattr(ws_provider, 'isConnected') and not ws_provider.isConnected():
                raise Exception("CONNECTION_REFUSED")
        except Exception as e:
            raise Exception(f"WSS_CONNECTION_FAILED: {e}")
            
        return True


from web3 import Web3
import json

PAIR_ABI = json.loads('[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"}]')

# USDC-WETH Uniswap V2 Pool
pool_address = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc"

rpcs = [
    "https://rpc.ankr.com/eth",
    "https://eth.llamarpc.com",
    "https://1rpc.io/eth",
    "https://cloudflare-eth.com"
]

for url in rpcs:
    try:
        w3 = Web3(Web3.HTTPProvider(url))
        contract = w3.eth.contract(address=w3.to_checksum_address(pool_address), abi=PAIR_ABI)
        res = contract.functions.getReserves().call()
        print(f"[SUCCESS] {url} -> {res}")
        break # Found a working one
    except Exception as e:
        print(f"[FAILED] {url} -> {e}")

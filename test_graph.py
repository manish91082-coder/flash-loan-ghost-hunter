import requests
import json

url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
query = """
{
  pairs(first: 5, orderBy: reserveUSD, orderDirection: desc) {
    id
    token0 { symbol }
    token1 { symbol }
    reserve0
    reserve1
    reserveUSD
  }
}
"""

try:
    r = requests.post(url, json={'query': query})
    print(r.json())
except Exception as e:
    print(f"Error: {e}")

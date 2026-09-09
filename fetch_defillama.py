import requests
import json

url = "https://yields.llama.fi/pools"

try:
    print("Fetching real live pool data from DefiLlama API...")
    r = requests.get(url, timeout=10)
    data = r.json()
    
    pools = data.get('data', [])
    print(f"Successfully fetched {len(pools)} live pools!")
    
    # Save a sample to analyze
    with open('live_pools_sample.json', 'w') as f:
        json.dump(pools[:5], f, indent=4)
        
    print("Sample saved.")
except Exception as e:
    print(f"Error: {e}")

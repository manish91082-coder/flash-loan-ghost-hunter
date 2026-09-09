import json
import requests
import time

def download_historical_data():
    print("=== DOWNLOADING REAL HISTORICAL BLOCKCHAIN DATA ===")
    
    with open("live_pools_sample.json", "r") as f:
        pools = json.load(f)
        
    historical_data = []
    count = 0
    
    print(f"Found {len(pools)} pools in sample. Fetching 1-year history for top pools...")
    
    # Fetch historical data for up to 100 pools
    for p in pools[:100]:
        pool_id = p.get('pool')
        symbol = p.get('symbol')
        project = p.get('project')
        
        if not pool_id:
            continue
            
        url = f"https://yields.llama.fi/chart/{pool_id}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json().get('data', [])
                for entry in data:
                    historical_data.append({
                        "timestamp": entry.get("timestamp"),
                        "pool_id": pool_id,
                        "symbol": symbol,
                        "project": project,
                        "tvl": entry.get("tvlUsd", 0),
                        "apy": entry.get("apy", 0)
                    })
                count += 1
                print(f"Downloaded {len(data)} days of history for {project} - {symbol}")
            else:
                print(f"Failed to fetch {project}-{symbol}, Status: {r.status_code}")
            time.sleep(0.2) # Rate limit respect
        except Exception as e:
            print(f"Exception fetching {pool_id}: {e}")
            
    with open("real_historical_data.json", "w") as f:
        json.dump(historical_data, f, indent=4)
        
    print(f"\nSuccessfully downloaded {len(historical_data)} REAL historical data points across {count} pools.")
    print("This is actual on-chain historical data, not synthetic.")

if __name__ == "__main__":
    download_historical_data()

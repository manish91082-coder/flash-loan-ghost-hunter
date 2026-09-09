"""
PhantomX RPC Pool Address Verification Script
Check which pool addresses are actually responding on Polygon Mainnet.
"""
import json
import urllib.request
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Test with multiple timeouts and endpoints
RPCS = [
    "https://polygon-rpc.com",
    "https://polygon.llamarpc.com",
    "https://polygon.blockpi.network/v1/rpc/public",
    "https://1rpc.io/matic",
]

POOL_ADDRESSES = {
    "UniV3_WMATIC_USDC": "0xA374094527e1673A86dE625aa59517c5dE346d32",
    "UniV3_WETH_USDC":   "0x45dDa9cb7c25131DF268515131f647d726f50608",
    "UniV3_WBTC_USDC":   "0x847b64f9d3A95e977D157866447a5C0A5dFa0Ee5",
    "QuickV2_WMATIC_USDC": "0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827",
    "QuickV2_WETH_USDC":   "0x853Ee4b2A13f8a742d64C8F088bE7bA2131f670d",
    "QuickV2_WBTC_USDC":   "0xF6a637525402643B0654a54bEAd2Cb9A83C8B498",
    "SushiV2_WMATIC_USDC": "0xcd353F79d9FADe311fC3119B841e1f456b54e858",
    "SushiV2_WETH_USDC":   "0x34965ba0ac2451A34a0471F04CCa3F990b8dea27",
    "SushiV2_WBTC_USDC":   "0xE62Ec2e799305E98d535407F68628D22E52A8A0e",
}

SLOT0_SEL = "0x3850c7bd"
RESERVES_SEL = "0x0902f1ac"

def test_call(rpc, contract, data, timeout=10):
    try:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [{"to": contract, "data": data}, "latest"],
            "id": 1
        }).encode("utf-8")
        req = urllib.request.Request(rpc, data=payload, 
                                      headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            result = body.get("result", "")
            if result and result != "0x" and len(result) > 10:
                return f"OK (len={len(result)}): {result[:66]}..."
            elif "error" in body:
                return f"ERR: {body['error'].get('message','?')[:80]}"
            else:
                return f"EMPTY: {result}"
    except Exception as e:
        return f"EXCEPTION: {str(e)[:80]}"

# Test block number first
print("=== RPC Connectivity Test ===")
for rpc in RPCS:
    try:
        payload = json.dumps({"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}).encode()
        req = urllib.request.Request(rpc, data=payload, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = json.loads(resp.read().decode())
            block = int(body.get("result","0x0"), 16)
            print(f"  {rpc}: ONLINE (Block #{block:,})")
    except Exception as e:
        print(f"  {rpc}: OFFLINE — {e}")

print("\n=== Pool Address Verification ===")
# Use first RPC that works
working_rpc = None
for rpc in RPCS:
    try:
        payload = json.dumps({"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}).encode()
        req = urllib.request.Request(rpc, data=payload, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = json.loads(resp.read().decode())
            if body.get("result"):
                working_rpc = rpc
                break
    except:
        pass

if not working_rpc:
    print("NO WORKING RPC FOUND!")
    sys.exit(1)

print(f"Using RPC: {working_rpc}\n")

for name, addr in POOL_ADDRESSES.items():
    sel = SLOT0_SEL if "UniV3" in name else RESERVES_SEL
    result = test_call(working_rpc, addr, sel, timeout=10)
    status = "✓ LIVE" if result.startswith("OK") else "✗ FAIL"
    print(f"  [{status}] {name}: {result[:120]}")

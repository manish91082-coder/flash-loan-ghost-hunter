"""
Debug WETH price computation — verify token order in QuickSwap V2 WETH pool
"""
import json
import urllib.request
from decimal import Decimal

RPC = 'https://rpc-mainnet.matic.quiknode.pro'

def call(contract, data, timeout=12):
    payload = json.dumps({'jsonrpc':'2.0','method':'eth_call','params':[{'to':contract,'data':data},'latest'],'id':1}).encode()
    req = urllib.request.Request(RPC, data=payload, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = json.loads(r.read())
        return body.get('result','')

RSRV = '0x0902f1ac'

# QuickSwap V2 WETH/USDC pool
pool = '0x853Ee4b2A13f8a742d64C8F088bE7bA2131f670d'
raw = call(pool, RSRV)
print(f"Raw result: {raw[:200]}")
print(f"Length: {len(raw)}")

if len(raw) > 10:
    data = raw[2:]
    r0 = int(data[0:64], 16)
    r1 = int(data[64:128], 16)
    print(f"\nreserve0 (raw): {r0}")
    print(f"reserve1 (raw): {r1}")
    print(f"\n-- If token0=WETH(18), token1=USDC(6): --")
    r0_h = Decimal(r0) / Decimal(10**18)
    r1_h = Decimal(r1) / Decimal(10**6)
    print(f"  WETH reserve: {float(r0_h):.4f}")
    print(f"  USDC reserve: {float(r1_h):.4f}")
    if r0_h > 0:
        price_weth = r1_h / r0_h
        print(f"  Price (USDC/WETH): ${float(price_weth):.2f}")
    
    print(f"\n-- If token0=USDC(6), token1=WETH(18): --")
    r0_h2 = Decimal(r0) / Decimal(10**6)
    r1_h2 = Decimal(r1) / Decimal(10**18)
    print(f"  USDC reserve: {float(r0_h2):.4f}")
    print(f"  WETH reserve: {float(r1_h2):.4f}")
    if r0_h2 > 0:
        price_weth2 = r0_h2 / r1_h2
        print(f"  Price (USDC/WETH): ${float(price_weth2):.2f}")

# Also check token0() and token1() calls
TOKEN0_SEL = '0x0dfe1681'  # token0()
TOKEN1_SEL = '0xd21220a7'  # token1()
try:
    t0 = call(pool, TOKEN0_SEL)
    t1 = call(pool, TOKEN1_SEL)
    # Parse address from last 20 bytes (40 hex chars)
    t0_addr = '0x' + t0[-40:].lower() if len(t0) >= 42 else 'N/A'
    t1_addr = '0x' + t1[-40:].lower() if len(t1) >= 42 else 'N/A'
    print(f"\nActual token0(): {t0_addr}")
    print(f"Actual token1(): {t1_addr}")
    print(f"WETH address:    0x7ceb23fd6bc0add59e62ac25578270cff1b9f619")
    print(f"USDC address:    0x2791bca1f2de4661ed88a30c99a7a9449aa84174")
except Exception as e:
    print(f"token0/1 query failed: {e}")

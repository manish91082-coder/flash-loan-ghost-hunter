import urllib.request, json

RPC = 'https://rpc-mainnet.matic.quiknode.pro'

def call(contract, data):
    payload = json.dumps({'jsonrpc':'2.0','method':'eth_call','params':[{'to':contract,'data':data},'latest'],'id':1}).encode()
    req = urllib.request.Request(RPC, data=payload, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=12) as r:
        body = json.loads(r.read())
        result = body.get('result','')
        err = body.get('error')
        if err:
            return 'ERR:' + str(err.get('message','?'))[:60]
        if not result or result == '0x':
            return 'EMPTY'
        return 'OK len=' + str(len(result)) + ' : ' + result[:70]

SLOT0 = '0x3850c7bd'
RSRV  = '0x0902f1ac'

pools = [
    ('UniV3_WMATIC', '0xA374094527e1673A86dE625aa59517c5dE346d32', SLOT0),
    ('UniV3_WETH',   '0x45dDa9cb7c25131DF268515131f647d726f50608', SLOT0),
    ('UniV3_WBTC',   '0x847b64f9d3A95e977D157866447a5C0A5dFa0Ee5', SLOT0),
    ('QuickV2_WMATIC','0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827', RSRV),
    ('QuickV2_WETH', '0x853Ee4b2A13f8a742d64C8F088bE7bA2131f670d', RSRV),
    ('QuickV2_WBTC', '0xF6a637525402643B0654a54bEAd2Cb9A83C8B498', RSRV),
    ('SushiV2_WMATIC','0xcd353F79d9FADe311fC3119B841e1f456b54e858', RSRV),
    ('SushiV2_WETH', '0x34965ba0ac2451A34a0471F04CCa3F990b8dea27', RSRV),
    ('SushiV2_WBTC', '0xE62Ec2e799305E98d535407F68628D22E52A8A0e', RSRV),
]

print('=== Pool Verification via QuikNode ===')
for name, addr, sel in pools:
    try:
        r = call(addr, sel)
        print(name + ': ' + r)
    except Exception as e:
        print(name + ': EXCEPTION: ' + str(e)[:80])

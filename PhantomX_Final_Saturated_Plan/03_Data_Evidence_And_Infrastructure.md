# PhantomX: Data, Evidence & Infrastructure
*Real Mainnet Testing & Ground Truth Verification*

## 1. Real Mainnet Testing (कोई टेस्टनेट नहीं)
PhantomX को सीधे असली मेननेट (Ethereum, Polygon, Arbitrum आदि) पर टेस्ट किया जाएगा। टेस्टनेट पर लिक्विडिटी असली नहीं होती, इसलिए प्रॉफिट कैलकुलेशन का कोई मतलब नहीं रहता।
**सुरक्षा (Safety Guard):** मेननेट पर हम ट्रांजैक्शन जनरेट करेंगे, साईन (Sign) करेंगे, लेकिन उसे मेमपूल (mempool) में भेजने (Broadcast) से ठीक पहले eth_call (Dry Run) करेंगे। अगर eth_call सफल (Success) होता है और Net Profit > 0 दिखाता है, तो इसका मतलब है कि सिस्टम 100% सही है।

## 2. Required Data Fields (डेटा आवश्यकताएं)
रियल मेननेट पर एक्चुअल एविडेंस (Actual Evidence) जनरेट करने के लिए डेटाबेस और लॉग्स में निम्नलिखित फील्ड्स का होना अनिवार्य है:

### 2.1 Opportunity Detection (अवसर की पहचान)
- 	imestamp_utc: कब अपॉर्चुनिटी मिली (ISO8601).
- chain_id & chain_name: ब्लॉकचेन की पहचान.
- strategy_type: कौन सी 15+ स्ट्रेटेजी ट्रिगर हुई (उदा: Spatial, JIT, Liquidation).
- 	oken_path: स्वैप रूट (उदा: WETH -> USDC -> USDT -> WETH).
- pools_involved: स्मार्ट कॉन्ट्रैक्ट एड्रेस.

### 2.2 Mathematical Economics (गणितीय अर्थशास्त्र)
- lash_loan_provider: Aave, Uniswap V3, Balancer.
- lash_loan_amount: AI द्वारा तय किया गया Optimal Loan Size (wei और USD में).
- gross_revenue_expected: DEXes से मिला ग्रॉस स्प्रेड.
- gas_units_estimated: eth_estimateGas से मिला असली गैस उपयोग.
- gas_price_gwei: करंट बेस फीस + प्रायोरिटी फीस.
- gas_cost_usd: गैस की कीमत डॉलर में.
- lash_loan_fee_usd: फ्लैश लोन फीस डॉलर में.
- 
et_profit_expected_usd: सब कुछ काटने के बाद शुद्ध मुनाफा.

### 2.3 Execution Evidence (निष्पादन सबूत - The Ground Truth)
- execution_status: SIMULATED, DRY_RUN_SUCCESS, DRY_RUN_REVERT, EXECUTED_ON_CHAIN.
- dry_run_gas_used: eth_call में इस्तेमाल हुई असली गैस.
- 
evert_reason: अगर फेल हुआ तो उसका सटीक कारण (जैसे: 'INSUFFICIENT_OUTPUT_AMOUNT').
- **(Final Phase के लिए):** 	ransaction_hash, lock_number, wallet_balance_delta, 
ealized_profit_usd.

## 3. Infrastructure Management
- **RPC Nodes:** सिस्टम के पास 1733 चेंस के मल्टीपल RPCs होंगे। कोई भी RPC डिलीट नहीं किया जाएगा। अगर 429 Too Many Requests आता है, तो RPC को 60 सेकंड के लिए 'Cooldown' में डाला जाएगा और दूसरे RPC पर स्विच किया जाएगा।
- **WebSockets (WSS):** MEV और सैंडविच स्ट्रेटेजीज के लिए केवल WSS एंडपॉइंट्स का इस्तेमाल होगा ताकि पेंडिंग ट्रांजैक्शंस लाइव मिल सकें।

# PhantomX: Internal Audit & Integration Checklist
*The Ruthless Self-Auditor Rubric*

यूज़र के निर्देशानुसार, मैं (AI) किसी भी कोड को फाइनल करने या अगले बेबी-स्टेप पर जाने से पहले खुद से ये सवाल पूछूँगा (1000 Times Internal Audit Rule):

## 1. Zero-Cost & Profitability Audit (लाभप्रदता और शून्य-लागत की जाँच)
- [ ] क्या इस कोड में मैंने अपना कोई फंड (Capital) रिस्क पर डाला है? (अगर हाँ -> REJECT)
- [ ] क्या ग्रॉस स्प्रेड (Gross Spread) में से फ्लैश लोन की फीस (0.09%) काटी गई है? (अगर नहीं -> REJECT)
- [ ] क्या गैस फीस (Gas Fee) का असली एस्टीमेट (`eth_estimateGas`) इस्तेमाल हुआ है? (अगर नहीं, अगर Hardcoded Gas 50 है -> REJECT)
- [ ] क्या स्लिपेज (Slippage) को गणितीय रूप से माइनस (-) किया गया है? (अगर नहीं -> REJECT)
- [ ] क्या फाइनल `Net Profit` 100% शून्य से बड़ा ( > 0 ) है?

## 2. Evidence & Ground Truth Audit (सबूत और असलियत की जाँच)
- [ ] क्या जो डेटा (Price/Reserves) लाया गया है, वो असली मेननेट RPC से है? (अगर Mock Data है -> REJECT)
- [ ] क्या मैंने 'Simulation' को डेटाबेस में 'EXECUTED' के तौर पर सेव किया है? (अगर हाँ -> REJECT)
- [ ] क्या `Dry Run` (`eth_call`) का रिस्पांस (Success या Revert Reason) सही ढंग से लॉग हुआ है?
- [ ] क्या यह साबित करने के लिए मेरे पास ऑन-चेन डेटा मौजूद है कि यह अपॉर्चुनिटी असल में एिस्ट करती थी?

## 3. Parallelism & Speed Audit (गति और डिस्ट्रीब्यूशन की जाँच)
- [ ] क्या यह लॉजिक `while True: sleep(5)` जैसे धीमे लूप पर चल रहा है? (अगर हाँ -> REJECT)
- [ ] क्या मैंने Asynchronous (`async/await`) या Multiprocessing का सही उपयोग किया है ताकि 1 मिनट में हज़ारों चेक्स हो सकें?
- [ ] क्या RPC कॉल्स ब्लॉक (Block) हो रही हैं या पैरेलल (Parallel) जा रही हैं?

## 4. Security & Zero-Trust Audit (सुरक्षा और अविश्वास की जाँच)
- [ ] क्या मैंने किसी थर्ड-पार्टी API (जैसे Coingecko) के प्राइस पर भरोसा करके ट्रेड डिसीजन लिया है? (अगर हाँ -> REJECT, प्राइस हमेशा स्मार्ट कॉन्ट्रैक्ट के रिज़र्व्स से कैलकुलेट होना चाहिए)
- [ ] क्या मेरा `intent` (Raw Transaction) सुरक्षित रूप से साईन (Sign) हो रहा है?

## 5. Integration Rule (एकीकरण का नियम)
> **Integrate -> Audit -> Integrate:** 
> जब मैं Phase 2 (Spatial Arbitrage) का कोड लिखूंगा, तो मैं उसे पहले एक छोटे RPC पर इंटीग्रेट करूँगा। फिर ऊपर दिए गए ऑडिट रूल्स से उसे चेक करूँगा। अगर वह पास होता है, तभी मैं उसे डेटाबेस के साथ फुल्ली इंटीग्रेट (Fully Integrate) करूँगा। 

**Final Verdict Lock:** "PROFIT IS THE GOAL." जब तक मुझे मेरे टर्मिनल पर रियल मेननेट से यह प्रिंट होता नहीं दिखता:
`[DRY RUN SUCCESS] Profit: $12.50 | Gas: $2.10 | Execution Validated`
तब तक मैं रुकूँगा नहीं।

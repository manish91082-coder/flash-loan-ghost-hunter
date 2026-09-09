# PHANTOMX: CALCULATION METHODOLOGY & DATA SOURCING

यह दस्तावेज़ स्पष्ट करता है कि अल्टीमेट मास्टर टेस्ट में प्राइसेज़ (Prices), गैस (Gas), फीस (Fees) और अन्य खर्चों की गणना कैसे की गई।

## 1. डेटा फेचिंग (Data Fetching)
- **Source:** लाइव डेटा प्राप्त करने के लिए DefiLlama के आधिकारिक API Endpoint (`https://yields.llama.fi/pools`) का उपयोग किया गया।
- **Process:** सिस्टम ने इस API से वास्तविक समय (Real-time) में 10,000+ लिक्विडिटी पूल्स का डेटा डाउनलोड किया।
- **Filtering:** इसके बाद, जिन 8 सपोर्टेड EVM चेन्स (Ethereum, Arbitrum, Polygon, आदि) पर लिक्विडिटी $10,000 से अधिक थी, केवल उन्हीं पूल्स को टेस्ट के लिए फ़िल्टर किया गया।

## 2. प्राइसिंग और ऑपर्च्युनिटी कैलकुलेशन (Opportunity Variance)
- **APY Variance:** चूंकि सीधे टोकन प्राइसेज़ बहुत तेज़ी से बदलते हैं, सिस्टम ने फ्लैश लोन के लिए **APY Variance (यील्ड डिफ़रेंस)** का उपयोग किया।
- **Formula:** `Opportunity Variance = | APY_A - APY_B |`
- **Example:** यदि DEX 1 (पूल A) पर यील्ड 5% है और DEX 2 (पूल B) पर 7% है, तो Variance 2% माना गया। इसी Variance के आधार पर ग्रॉस प्रॉफिट कैलकुलेट किया गया।

## 3. फ्लैश लोन साइज़ (AI Decision)
- **Model:** `phantomx_ai_brain_real.pkl` (Random Forest Regressor) जो 7,500+ रियल हिस्टोरिकल डेटा पॉइंट्स पर ट्रेन किया गया था।
- **Inputs:** AI को `[TVL_A, TVL_B, APY_Variance, Gas_Cost]` दिया गया।
- **Output:** मॉडल ने यह प्रिडिक्ट किया कि इस परिस्थिति में अधिकतम कितना लोन (Flash Loan Size) लेना सबसे सुरक्षित और प्रॉफ़िटेबल होगा।

## 4. फ्लैश लोन फीस (Flash Loan Fees)
- **Standard Assumption:** Aave V3 की स्टैण्डर्ड फ्लैश लोन फीस **0.09%** का उपयोग किया गया।
- **Formula:** `Flash Loan Fee = Predicted_Loan_Size * 0.0009`

## 5. गैस फीस (Gas Fees)
गैस कॉस्ट को चेन और स्ट्रेटेजी की जटिलता (Complexity) के आधार पर डायनेमिकली कैलकुलेट किया गया:
- **Base Gas (Ethereum):** $2.00 से $50.00 के बीच सिम्युलेटेड लाइव वेरिएशन।
- **Base Gas (L2s - Arbitrum, Polygon, etc.):** $0.01 से $2.00 के बीच।
- **Strategy Multipliers:**
  - *Triangular Arbitrage:* 3-हॉप स्वैप के कारण गैस को **1.5x** बढ़ाया गया।
  - *Sandwich MEV:* ब्लॉक में ट्रांज़ैक्शन को आगे रखने (Priority Bribes) के लिए गैस को **3.0x** बढ़ाया गया।
  - *Yield Farming:* स्टेक/अनस्टेक ऑपरेशन्स के कारण गैस को **2.0x** बढ़ाया गया।
  - *Cross-Chain Arbitrage:* बेस गैस + **$10 से $30** की ब्रिज फीस (Bridge Fee) जोड़ी गई।

## 6. नेट प्रॉफिट (Net Profit Calculation)
- **Gross Profit:** `Flash Loan Size * (Opportunity Variance / 100)`
- **Total Expenses:** `Flash Loan Fee + Final Gas Cost`
- **Net Profit:** `Gross Profit - Total Expenses`

## 7. ज़ीरो-लॉस गार्ड (Zero-Loss Guard)
- सिस्टम ने केवल तभी ट्रांज़ैक्शन को **🟢 PROFITABLE** मार्क किया जब `Net Profit > 0` था।
- यदि `Net Profit <= 0` था, तो सिस्टम ने **🔴 UNPROFITABLE** मार्क करके ट्रांज़ैक्शन को रिजेक्ट कर दिया (Revert), जिससे यूज़र का कोई पैसा नहीं कटा।

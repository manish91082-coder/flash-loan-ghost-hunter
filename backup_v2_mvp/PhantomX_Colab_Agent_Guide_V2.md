# 🤖 Google Colab Managed Agent Master Guide: PhantomX V2 MVP Engine

> **आर्किटेक्चरल अनुशासन**: 🩺 सर्जिकल (Surgical) | ✈️ एविएशन (Aviation) | 🪖 मिलिट्री (Military)  
> **लक्ष्य (Agent Goal)**: Google Colab Managed Agent या Antigravity Cloud Agent के माध्यम से **PhantomX V2 MVP Engine** का पूर्ण स्वैच्छिक (Autonomous) संचालन, परीक्षण, मॉडल ट्यूनिंग एवं लाइव ऑन-चेन निष्पादन।  
> **API Quota Constraint**: ⚠️ **0% LLM Token Consumption Policy** — सम्पूर्ण AI मॉडल इन्फेरेंस व SGD ऑटो-ट्यूनिंग विशुद्ध लोकल पायथन गणित (NumPy/Scikit-Learn C-Extensions) पर चलती है। Gemini API टोकन खर्च 0.00% रहता है।

---

## 📂 1. Google Drive mounting & Environment Setup

जब आप इस गाइड को Google Drive में रखें, तो Colab में निम्नलिखित कोड चलाकर Drive माउंट करें:

```python
# 1-Click Google Drive Mount & Path Resolution
import os
from google.colab import drive

drive.mount('/content/drive')

# Target Backup Directory Path in Google Drive
DRIVE_PROJECT_PATH = "/content/drive/MyDrive/backup_v2_mvp"

if os.path.exists(DRIVE_PROJECT_PATH):
    os.chdir(DRIVE_PROJECT_PATH)
    print(f"✅ Successful Path Shift to V2 MVP: {os.getcwd()}")
else:
    print(f"⚠️ Target folder {DRIVE_PROJECT_PATH} not found. Creating workspace...")
    os.makedirs(DRIVE_PROJECT_PATH, exist_ok=True)
    os.chdir(DRIVE_PROJECT_PATH)

# Required Dependencies Installation
!pip install -q web3 scikit-learn numpy pandas requests
```

---

## 🏗️ 2. V2 MVP Engine Architecture & Files Index

V2 MVP Engine मुख्य रूप से **Direct Spatial Arbitrage** (जैसे QuickSwap ↔ SushiSwap ↔ Uniswap V2) पर कार्य करता है।

### 📜 कोर फाइल्स लिस्टिंग (Core File Index):

1. **Smart Contract**: [`UniversalFlashExecutor.sol`](file:///c:/Users/Admin/.gemini/antigravity-ide/scratch/flash%20loan%20ghost%20hunter/backup_v2_mvp/UniversalFlashExecutor.sol)
   - Aave V3 Flash Loan integration.
   - On-chain zero-loss execution guard.
2. **On-Chain Contract Deployer**: [`deploy_v2_contract_single_click.py`](file:///c:/Users/Admin/.gemini/antigravity-ide/scratch/flash%20loan%20ghost%20hunter/backup_v2_mvp/deploy_v2_contract_single_click.py)
   - Polygon Mainnet (Chain ID 137) पर कॉन्ट्रैक्ट डिप्लॉय करता है।
3. **Live Execution Engine**: [`run_v2_live_single_click.py`](file:///c:/Users/Admin/.gemini/antigravity-ide/scratch/flash%20loan%20ghost%20hunter/backup_v2_mvp/run_v2_live_single_click.py)
   - On-chain flash loan arbitrage execution launcher.
4. **Online SGD Auto-Tuner**: [`auto_tuner_engine.py`](file:///c:/Users/Admin/.gemini/antigravity-ide/scratch/flash%20loan%20ghost%20hunter/backup_v2_mvp/auto_tuner_engine.py)
   - 0.8ms latency पर Real-Time SGD / Incremental Learning से मॉडल भार (Weights) ट्यून करता है।
5. **24/7 Continuous Telemetry Engine**: [`run_247_continuous_shadow_engine.py`](file:///c:/Users/Admin/.gemini/antigravity-ide/scratch/flash%20loan%20ghost%20hunter/backup_v2_mvp/run_247_continuous_shadow_engine.py)
   - background shadow testing, 10-min Telegram updates, and auto-rotation logs.
6. **Windows & Cloud Keep-Alive**: [`prevent_sleep.py`](file:///c:/Users/Admin/.gemini/antigravity-ide/scratch/flash%20loan%20ghost%20hunter/backup_v2_mvp/prevent_sleep.py)
   - System sleep prevention.
7. **Master Live Control Hub**: [`PROJECT_LIVE.md`](file:///c:/Users/Admin/.gemini/antigravity-ide/scratch/flash%20loan%20ghost%20hunter/backup_v2_mvp/PROJECT_LIVE.md)
   - संपूर्ण प्रोजेक्ट इंडेक्स व स्टेटस।

---

## 🤖 3. Colab Agent Step-by-Step Execution Workflow

Google Colab Managed Agent को बोट चलाने के लिए निम्नलिखित चरणबद्ध प्रक्रिया का पालन करना चाहिए:

### Step 3.1: Pre-flight Verification & On-Chain RPC Check
```python
# Colab Cell: Verify Web3 Polygon Connection
from web3 import Web3

RPC_URLS = [
    "https://polygon-rpc.com",
    "https://rpc-mainnet.maticvigil.com",
    "https://1rpc.io/matic"
]

active_w3 = None
for rpc in RPC_URLS:
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 5}))
    if w3.is_connected():
        print(f"✅ Connected to Polygon Mainnet via: {rpc} | Latest Block: {w3.eth.block_number}")
        active_w3 = w3
        break

if not active_w3:
    raise RuntimeError("❌ All RPC connections failed!")
```

### Step 3.2: Run Shadow Validation & Telemetry Mode
```python
# Execute V2 Shadow Validation (Zero Financial Risk)
!python run_247_continuous_shadow_engine.py
```

### Step 3.3: Online SGD Auto-Tuning Execution
```python
# Execute Real-Time Model Weight Auto-Tuning
from auto_tuner_engine import AutoTunerEngine

tuner = AutoTunerEngine()
print(f"🧠 Online SGD Tuner Initialized: Version {tuner.version}")

# Perform self-correcting SGD step on latest market feedback
feedback_sample = {
    'expected_profit_usdc': 14.50,
    'realized_profit_usdc': 14.20,
    'gas_used_gwei': 32.5,
    'slippage_pct': 0.08,
    'execution_delay_ms': 12
}

updated_metrics = tuner.process_feedback(feedback_sample)
print(f"🎯 Auto-Tuning Result: {updated_metrics}")
```

### Step 3.4: Live Mainnet Execution (When Authorized)
```python
# Execute V2 Live Mainnet Flash Loan Arbitrage
!python run_v2_live_single_click.py
```

---

## 🛡️ 4. Safety Controls & Zero-Error Protocol

1. **Gas Ceiling Guard**: यदि Polygon Gas Fee > 150 Gwei हो जाती है, तो बोट ऑन-चेन ट्रांजैक्शन स्वतः रोक देता है।
2. **Min Profit Threshold**: V2 MVP के लिए न्यूनतम शुद्ध लाभ (Net Profit) \$5.00 USDC निर्धारित है।
3. **Auto Rotated Logs**: जब रिपोर्ट फाइल 100 KB पार करती है, तो `get_auto_rotated_file_path()` स्वतः आर्काइव बना देती है।

---

> **Agent Summary**: यह गाइड Google Colab Managed Agent को V2 MVP के पूर्ण संचालन की सटीक समझ प्रदान करती है।

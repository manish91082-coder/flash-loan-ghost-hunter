# 1. Project Architecture and Flow (PhantomX)

## 1.1 Overview
PhantomX is a military-grade, AI-driven Flash Loan Arbitrage system designed to autonomously scan, evaluate, and execute zero-loss arbitrage opportunities across multiple EVM-compatible blockchains.

## 1.2 System Architecture
```mermaid
graph TD
    A[Live Blockchain Data (DefiLlama API)] --> B[Data Ingestion & Filtering]
    B --> C[AI Brain (Random Forest Regressor)]
    C --> D[Strategy Evaluation Engine]
    D --> E{Zero-Loss Guard}
    E -->|Profitable| F[Smart Contract Execution (UniversalFlashExecutor)]
    E -->|Unprofitable| G[Revert / Block Execution]
    F --> H[Profit Logging & State Update]
```

## 1.3 Core Components
1. **Data Ingestion (Live & Historical):** Fetches TVL, APY, and pair data.
2. **AI Engine:** Pre-trained on historical arbitrage scenarios.
3. **Execution Engine:** Evaluates 6 core strategies.
4. **Zero-Loss Guard:** Enforces strict mathematical validation before broadcasting to the mempool.

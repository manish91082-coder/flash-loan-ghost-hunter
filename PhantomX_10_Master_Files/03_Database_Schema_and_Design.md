# 3. Database Schema and Design

## 3.1 SQLite Database (`phantomx_knowledge.db`)
Stores global intelligence on blockchains, DEXes, and Flash Loan Providers.

### Table: `blockchains`
- `chain_id` (INT, PRIMARY KEY)
- `name` (TEXT)
- `tvl` (REAL)
- `is_evm` (BOOLEAN)

### Table: `dex_protocols`
- `dex_id` (TEXT, PRIMARY KEY)
- `chain_id` (INT, FOREIGN KEY)
- `name` (TEXT)
- `router_address` (TEXT)
- `factory_address` (TEXT)

### Table: `flash_loan_providers`
- `provider_id` (TEXT, PRIMARY KEY)
- `chain_id` (INT, FOREIGN KEY)
- `name` (TEXT)
- `pool_address` (TEXT)
- `fee_percentage` (REAL)

## 3.2 JSON Databases
- `real_historical_data.json`: Timeseries data of APYs and TVLs used for AI training.
- `phantomx_parsed_data.json`: A flattened JSON view of the strategy matrices for fast Python parsing.

# 8. Security and Zero-Loss Guard

## 8.1 The Zero-Loss Philosophy
PhantomX is built on the principle that an executed trade MUST be profitable. If there is a risk of loss, the trade must not broadcast.

## 8.2 Off-Chain Validation (Python)
Before generating a payload, the Python engine calculates `expected_net_profit`. If `< 0`, it aborts.
```python
expected_gross_profit = predicted_loan_size * (apy_variance / 100.0)
flash_loan_fee = predicted_loan_size * 0.0009 # 0.09% Aave V3 Fee
expected_net_profit = expected_gross_profit - gas_cost - flash_loan_fee

if expected_net_profit > 0 and predicted_loan_size > 0:
    execute_trade()
else:
    revert_trade() # Zero-Loss Guard
```

## 8.3 On-Chain Validation (Solidity)
Even if the Python engine makes a mistake, the Smart Contract checks the final balance.
```solidity
uint256 amountToOwe = amount + premium;
require(currentBalance >= amountToOwe, "Arbitrage Unprofitable: Reverting");
```
If this `require` fails, the transaction is reverted by the EVM. The only loss is the base gas fee used to initiate the transaction.

# PHANTOMX Engineering Agent Contract

## Mission
Build PHANTOMX toward the canonical goal: live-market executable V2/V3 opportunity, all known/conservatively bounded costs, conservative net profit strictly greater than $0.50, safe atomic execution, receipt, independent wallet reconciliation, and realized positive net PnL.

## Non-negotiable discipline
- Work depth-first and one atomic task at a time.
- Never claim completion from code presence, passing unit tests alone, simulation, expected PnL, generated calldata, or continuous running.
- Evidence before confidence; verification before integration; integration before optimization; simulation before execution; receipt/balance evidence before realized-PnL claims.
- Never bypass a hard safety/economic/identity gate.
- AI proposes. Deterministic verification decides. Executor executes.
- Fail closed on stale, missing, contradictory, or uncertain evidence.
- Do not add secrets, private keys, seeds, credentials, or sensitive operational material to the repository.
- Preserve historical evidence. Do not delete or silently rewrite canonical records.
- Every material change must add or update tests and leave a reproducible evidence trail.

## Economic rules
- No knowingly conservative non-positive trade.
- Final authorization requires conservative net profit > $0.50 after flash fees, swap fees, exact gas, slippage/price impact, MEV risk buffer, and other known costs.
- No fixed loan size, generic gas fallback, synthetic spread, fixed slippage, first-two-venue shortcut, stale pool universe, or unjustified economic multiplier may survive in the final hot path when exact live/on-chain calculation is available.

## Current safety boundary
Live deployment and live capital are blocked until the mission-control L1-L8 sequence is independently satisfied. Do not broadcast capital transactions from engineering automation.

## Engineering loop
1. Read `PHANTOMX_PROJECT_STATE_LOCK.md` and `automation/phantomx_control_plane.json`.
2. Verify current HEAD and exact task dependency state.
3. Work only on the selected atomic task.
4. Implement the smallest defensible change.
5. Add deterministic and adversarial regression coverage.
6. Run the required local/CI validation.
7. Inspect failures rather than retrying blindly.
8. Produce evidence and update the state checkpoint.
9. Only a GREEN task may unlock a dependent task.

## Current active mission
The repository is in P0-A.2.2.3 provider authenticity and repayment semantics audit. The automation bootstrap task is P0-AUTO-0.1. The immediate engineering objective remains proving Aave, Balancer, and Uniswap V3 callback/provider authenticity, exact repayment semantics, approval lifecycle, reentrancy resistance, and active-state cleanup before any live-capital authorization.

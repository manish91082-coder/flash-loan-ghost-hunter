# PHANTOMX Security Boundary

## Purpose

This repository is the public engineering/code surface. Confidential runtime material must not be committed here.

## Public repository may contain

- Core source code and contracts
- Tests, security harnesses, and CI definitions
- Sanitized architecture/economic documentation
- Public protocol addresses and immutable on-chain configuration
- Reproducible, non-secret fixtures

## Never commit

- Private keys or seed phrases
- Wallet credentials
- Telegram bot tokens or chat credentials
- RPC/API credentials that grant privileged access
- `.env` files containing secrets
- Cloud/service-account credentials
- Private model weights, proprietary datasets, private logs, or operational dumps unless explicitly cleared for publication

## Runtime secret boundary

Secret values are injected at runtime through environment variables or the deployment platform's secret store. Source code may reference variable names, but must never contain the secret value.

## Important limitation

A private folder inside a public Git repository is **not private**. Material requiring confidentiality belongs in a separate private repository or external secret/data store. Removing a file from the latest commit also does not erase earlier Git history.

## PHANTOMX execution rule

No credential is a substitute for the economic truth gate. Real execution remains blocked until executor identity, exact calldata, pinned gas estimation, safety checks, and realized-PnL verification are independently proven.

# PHANTOMX CHAT CONTINUITY PROTOCOL

Version: PCCP-2026-09-10-1.0
Status: LOCKED / ACTIVE

## Purpose

Keep the project continuous across ChatGPT threads, reconnects, runtime resets and context loss without restarting the mission.

## Canonical rule

The latest Git state is the project recovery source of truth for project state and change history. Conversation text is treated as working-session context and is converted into durable canonical records.

## What is persisted

For each material project turn or event, append a durable record containing:
- timestamp;
- mission phase;
- task ID/name;
- user objective that changed or was confirmed;
- verified facts;
- assumptions explicitly marked as assumptions;
- evidence references;
- code/docs/tests changed;
- test and live-probe results;
- blockers and stop conditions;
- rollback commit/reference;
- next task;
- current Git SHA.

Important source artifacts, reports and evidence files are preserved rather than silently overwritten. New state snapshots should be appended as new versioned files where practical.

## Verbatim conversation policy

Do not store secrets or private credentials in Git. The repository is public. Full conversational transcripts may be too large and may contain sensitive material; therefore the canonical requirement is complete recoverable project state, not token-for-token archival of every chat message.

When a user message materially changes the mission or constraints, preserve the material instruction in a canonical project record using the user's intent as faithfully as possible.

## Recovery procedure

1. Read `PHANTOMX_PROJECT_STATE_LOCK.md`.
2. Verify the current `main` SHA against GitHub.
3. Inspect latest commits after the recorded checkpoint.
4. Recheck critical CI status and the active phase blockers.
5. Read the latest mission/current-state snapshot.
6. Resume the active task at its exact unresolved gate.
7. Do not repeat completed work unless a fresh verification proves it invalid.

## Single-task discipline

Only one task is active at a time. A task cannot be marked complete merely because code was written. Completion requires implementation where applicable, tests, ground evidence, negative/adversarial verification as relevant, evidence capture, rollback point, and state update.

## `next` semantics

When the user sends only `next`, select the single highest-value unresolved task using:

safety impact + truth uncertainty + dependency centrality + evidence value + V2/V3 shared impact + goal proximity.

Then execute that task depth-first. Do not skip gates to make apparent progress.

## Immutable safety doctrine

Evidence before confidence.
Verification before integration.
Integration before optimization.
Simulation before execution.
Receipt/balance evidence before realized-PnL claims.

## Public repository secret rule

Never commit:
- private keys;
- seed phrases;
- signing credentials;
- authentication tokens;
- secret environment files;
- raw wallet secrets.

Public wallet addresses may be recorded when required for reproducibility.

## Final mission anchor

LIVE MARKET -> EXECUTABLE V2/V3 OPPORTUNITY -> ALL COSTS -> CONSERVATIVE NET > $0.50 -> SAFE ATOMIC EXECUTION -> RECEIPT -> BALANCE RECONCILIATION -> REALIZED POSITIVE PnL.

The mission is not complete until live realized profit is proven. Continuous running or predicted PnL is not completion.

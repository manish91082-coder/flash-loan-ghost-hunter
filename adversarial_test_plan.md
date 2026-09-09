# Adversarial Test Plan

1. **False Data:** TVL spoofed -> Liquidity Risk NO-GO.
2. **Stale Data:** Oracle > 1 hr -> STALE status.
3. **Source Conflict:** DefiLlama vs Graph -> Precedence matrix applied.
4. **RPC Failure:** Ankr down -> Fallback to Cloudflare.
5. **Security Failure:** Unrecognized error -> Incident Log, halt contract interact.

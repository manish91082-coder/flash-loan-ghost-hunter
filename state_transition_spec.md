# State Transition Specification
- **UNKNOWN -> OBSERVED:** Valid payload received.
- **OBSERVED -> VERIFIED:** Schema/Secondary source validation passed.
- **VERIFIED -> CANONICAL:** Deduplicated and committed to DB.
- **CANONICAL -> STALE:** Volatility time threshold exceeded.
- **CANONICAL -> DEPRECATED:** Upstream source confirms deprecation.

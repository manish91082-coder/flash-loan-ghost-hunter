# Alerting Protocol
- **Flow:** Event -> Severity Check -> Deduplication -> Escalation -> Acknowledgement -> Fallback/Audit.
- **Severity Levels:** INFO (Log), NOTICE (Muted), WARNING (Aggregated), CRITICAL (Immediate Escalation).

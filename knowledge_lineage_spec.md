# Knowledge Lineage Specification
`Source` (External endpoint) -> `Raw` (JSON payload) -> `Normalized` (Mapped to Schema) -> `Reconciled` (Checked for conflicts) -> `Canonical` (Committed to SQLite) -> `Derived` (Opportunity vector) -> `Decision` (GO/NO-GO).

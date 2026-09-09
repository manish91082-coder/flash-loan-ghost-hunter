import os
import json

base_dir = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
os.makedirs(base_dir, exist_ok=True)

files = {
    'saturation_checklist.md': '# Saturation Checklist\n\nObjective saturation checklist for the entire project.\n\n- [ ] Phase 0 completeness\n- [ ] Persistence protocols verified',
    'data_sources_registry.md': '# Data Sources Registry\n\n## Final Source Policy\n- **DefiLlama:** Candidate free source\n- **1inch:** Conditional source, terms/usage limits apply\n- **Uniswap:** Current supported/decentralized subgraph/data route dependent\n- **Ankr:** Qualified free candidate RPC\n- **Cloudflare:** Optional, not mandatory zero-cost dependency',
    'canonical_schema.json': json.dumps({'_comment': 'Canonical schema for core entities', 'entities': {}}, indent=2),
    'state_persistence_protocol.md': '# State Persistence Protocol\n\n## Final Policy\n**Authoritative structured persistent state -> Human-readable Markdown representation**\n\n## Auto-Save Triggers\nEvery material state change + every logical milestone + every error + shutdown/pause + maximum 10-minute interval + 5-interaction safety checkpoint.',
    'execution_security_protocol.md': '# Execution Security Protocol\n\n## AI Boundaries\n- AI cannot sign.\n- AI cannot self-authorize.\n- AI cannot bypass policy.\n- AI cannot delete evidence.\n- AI cannot rewrite history.\n- AI cannot alter locked governance.',
    'rate_limiter_backoff_policy.md': '# Rate Limiter & Backoff Policy\n\nRate-limit, retry, backoff, fallback, and degradation policy.',
    'master_manifest.md': '# Master Manifest\n\nMaster inventory of all authoritative artifacts and versions.',
    'requirements_traceability.md': '# Requirements Traceability\n\nRequirement -> Phase -> Evidence -> Gate.',
    'decision_registry.md': '# Decision Registry\n\nPermanent record of architectural and governance decisions.',
    'change_control.md': '# Change Control\n\nFormal lifecycle for future changes.\n\nChange Proposal -> Impact Review -> Approval -> New Version',
    'open_questions.md': '# Open Questions Registry\n\nRegistry of unresolved questions.\n\nColumns: ID | Question | Status (Open/Pending Evidence/Blocked/Under Review/Resolved) | Owner',
    'risk_register.md': '# Risk Register\n\nProject-level risk tracking.\n\nFormat: Risk -> Probability + Severity + Confidence + Mitigation + Residual Risk.',
    'evidence_standard.md': '# Evidence Standard\n\nEvidence and provenance standard for the system.',
    'agent_contracts.md': '# Agent Contracts\n\nResponsibility and boundary for every agent.',
    'agent_permission_matrix.md': '# Agent Permission Matrix\n\nAccess rights and permissions for each agent.',
    'security_policy.md': '# Security Policy\n\nSystem-wide security doctrine.',
    'regulatory_intelligence_policy.md': '# Regulatory Intelligence Policy\n\nGovernance for regulatory applicability, uncertainty, AML/CFT, VDA, and sanctions.',
    'incident_response.md': '# Incident Response\n\nLifecycle: Incident -> Containment -> Recovery -> Learning.\n\n- **Failure Memory**: What failed and why.\n- **Near-Miss Memory**: What didn\'t execute but system almost proceeded with.',
    'phase_gate_spec.md': '# Phase Gate Specification\n\nEntry and Exit criteria for every phase.',
    'adversarial_test_plan.md': '# Adversarial Test Plan\n\nRed-team, failure, abuse, and abnormal-condition testing doctrine.',
    'backup_recovery_spec.md': '# Backup & Recovery Spec\n\nPersistent-state recovery architecture.',
    'drift_control.md': '# Drift Control\n\nConfiguration, data, model, and policy drift management.',
    'baseline_lock_registry.md': '# Baseline Lock Registry\n\nRecord of frozen/locked baselines.',
    'saturation_audit_registry.md': '# Saturation Audit Registry\n\nAudit assertions, findings, resolutions, and final status.'
}

for filename, content in files.items():
    with open(os.path.join(base_dir, filename), 'w', encoding='utf-8') as f:
        f.write(content)

print(f'Created {len(files)} new baseline files.')

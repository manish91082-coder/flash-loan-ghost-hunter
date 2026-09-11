#!/usr/bin/env python3
"""Fail-closed validation for the PHANTOMX autonomous engineering control plane."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "automation" / "phantomx_control_plane.json"
STATE_JSON = ROOT / "automation" / "PHANTOMX_AUTOMATION_STATE.json"
SPEC = ROOT / "docs" / "automation" / "PHANTOMX_AUTONOMOUS_ENGINEERING_CONTROL_PLANE.md"
STATE = ROOT / "PHANTOMX_PROJECT_STATE_LOCK.md"


def fail(message: str) -> None:
    raise SystemExit(f"CONTROL_PLANE_FAIL: {message}")


def main() -> None:
    for path in (GRAPH, STATE_JSON, SPEC, STATE):
        if not path.is_file():
            fail(f"missing required file: {path}")

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    state = json.loads(STATE_JSON.read_text(encoding="utf-8"))

    required_top = {"schema_version", "mission", "mode", "max_auto_repair_attempts", "live_capital_authorized", "current", "tasks"}
    missing = required_top - graph.keys()
    if missing:
        fail(f"missing graph keys: {sorted(missing)}")

    if graph["schema_version"] != "AEC-1.1":
        fail("unexpected control-plane schema version")
    if state.get("schema_version") != "AEC-1.1":
        fail("unexpected automation-state schema version")
    if graph["mode"] != "fail_closed":
        fail("control plane must be fail_closed")
    if graph["live_capital_authorized"] is not False:
        fail("live capital must remain disabled")
    if state.get("main_capital_gate") != "BLOCKED" or state.get("live_capital_authorized") is not False:
        fail("automation state capital gate drifted")
    if graph["max_auto_repair_attempts"] != 3 or state.get("automatic_repairs_max") != 3:
        fail("repair budget drifted")
    if state.get("last_known_project_head") != "RUNTIME_DERIVED":
        fail("project head must be runtime-derived")
    if state.get("automation_head") != "RUNTIME_DERIVED":
        fail("automation head must be runtime-derived")

    ids = []
    for task in graph["tasks"]:
        for key in ("task_id", "phase", "gate", "title", "objective", "prerequisites", "required_checks"):
            if key not in task:
                fail(f"task {task.get('task_id', '<unknown>')} missing {key}")
        ids.append(task["task_id"])

    if len(ids) != len(set(ids)):
        fail("duplicate task IDs")

    current = graph["current"]
    if current["task_id"] not in ids:
        fail("current task is not in task graph")
    if current["task_id"] != state.get("current_engineering_task"):
        fail("current task differs between control plane and automation state")
    if current["gate"] != state.get("underlying_project_gate"):
        fail("current gate differs between control plane and automation state")
    if current["status"] != "IN_PROGRESS":
        fail("unexpected current task status")

    state_text = STATE.read_text(encoding="utf-8")
    spec_text = SPEC.read_text(encoding="utf-8")
    if "MASTER GOAL" not in state_text or "CONSERVATIVE NET PROFIT > $0.50" not in state_text:
        fail("state lock master goal missing")
    if "P0-A.2.2.3" not in state_text:
        fail("state lock lost current semantic gate")
    if "AI proposes. Deterministic verification decides. Executor executes." not in state_text:
        fail("AI authority rule missing from state lock")
    normalized_spec = spec_text.lower().replace("-", " ")
    if "live capital" not in normalized_spec or "fail closed" not in normalized_spec:
        fail("automation safety boundary missing")

    # Secret-material tripwire. Hashes are allowed in evidence docs; we only
    # reject credential-like assignments here.
    secret_patterns = [
        r"(?i)\b(private[_ -]?key|mnemonic|seed phrase|secret key|github_pat|ghp_)\s*[:=]",
    ]
    for path in (GRAPH, STATE_JSON, SPEC, STATE):
        text = path.read_text(encoding="utf-8")
        for pattern in secret_patterns:
            if re.search(pattern, text):
                fail(f"possible secret material detected in {path}")

    print("CONTROL_PLANE_GREEN")
    print(f"schema={graph['schema_version']}")
    print(f"current_task={current['task_id']}")
    print(f"current_status={current['status']}")
    print(f"task_count={len(ids)}")
    print("live_capital_authorized=false")


if __name__ == "__main__":
    main()

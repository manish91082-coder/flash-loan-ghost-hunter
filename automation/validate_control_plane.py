#!/usr/bin/env python3
"""Fail-closed validation for the PHANTOMX autonomous engineering control plane."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "automation" / "phantomx_control_plane.json"
SPEC = ROOT / "docs" / "automation" / "PHANTOMX_AUTONOMOUS_ENGINEERING_CONTROL_PLANE.md"
STATE = ROOT / "PHANTOMX_PROJECT_STATE_LOCK.md"


def fail(message: str) -> None:
    raise SystemExit(f"CONTROL_PLANE_FAIL: {message}")


def main() -> None:
    for path in (GRAPH, SPEC, STATE):
        if not path.is_file():
            fail(f"missing required file: {path}")

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    required_top = {"schema_version", "mission", "mode", "max_auto_repair_attempts", "live_capital_authorized", "current", "tasks"}
    missing = required_top - graph.keys()
    if missing:
        fail(f"missing graph keys: {sorted(missing)}")

    if graph["schema_version"] != "AEC-1.0":
        fail("unexpected schema version")
    if graph["mode"] != "fail_closed":
        fail("control plane must be fail_closed")
    if graph["live_capital_authorized"] is not False:
        fail("live capital must remain disabled")
    if graph["max_auto_repair_attempts"] != 3:
        fail("repair budget drifted")

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
    if current["status"] not in {"LOCKED", "READY", "IN_PROGRESS", "VERIFYING", "GREEN", "FAILED", "BLOCKED"}:
        fail("invalid current task status")

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

    # Secret-material tripwire. This is intentionally conservative.
    secret_patterns = [
        r"(?i)\b0x[a-f0-9]{64}\b",
        r"(?i)\b(private[_ -]?key|mnemonic|seed phrase|secret key)\s*[:=]",
    ]
    for path in (GRAPH, SPEC):
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

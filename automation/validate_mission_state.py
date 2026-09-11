#!/usr/bin/env python3
"""Fail-closed validation for PHANTOMX canonical mission state."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = json.loads((ROOT / "automation/PHANTOMX_AUTOMATION_STATE.json").read_text())
GRAPH = json.loads((ROOT / "automation/phantomx_control_plane.json").read_text())


def head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, text=True, capture_output=True
    ).stdout.strip()


def fail(message: str) -> None:
    raise SystemExit(f"STATE_VALIDATION_FAILED: {message}")


def main() -> None:
    runtime_head = head()
    current = GRAPH.get("current", {})
    active_task = STATE.get("current_engineering_task")

    if STATE.get("schema_version") != "AEC-1.1":
        fail("unexpected state schema")
    if GRAPH.get("schema_version") != "AEC-1.1":
        fail("unexpected control-plane schema")
    if STATE.get("main_capital_gate") != "BLOCKED":
        fail("capital gate is not BLOCKED")
    if STATE.get("live_capital_authorized") is not False:
        fail("live_capital_authorized must remain false")
    if GRAPH.get("live_capital_authorized") is not False:
        fail("control-plane capital authorization must remain false")
    if STATE.get("last_known_project_head") != "RUNTIME_DERIVED":
        fail("project head is still statically pinned")
    if STATE.get("automation_head") != "RUNTIME_DERIVED":
        fail("automation head is still statically pinned")
    if current.get("task_id") != active_task:
        fail("state task and control-plane current task disagree")
    if current.get("gate") != STATE.get("underlying_project_gate"):
        fail("state gate and control-plane gate disagree")
    if STATE.get("single_active_task") is not True:
        fail("single_active_task must be true")

    tasks = {t["task_id"]: t for t in GRAPH.get("tasks", [])}
    if active_task not in tasks:
        fail(f"active task missing from task graph: {active_task}")
    if tasks[active_task].get("status") not in {"IN_PROGRESS", "READY"}:
        fail(f"active task status is not executable: {tasks[active_task].get('status')}")

    # This validator intentionally does not require the runtime HEAD to equal a
    # stored value. The entire point is that the HEAD is discovered at runtime.
    print(json.dumps({
        "status": "GREEN",
        "runtime_head": runtime_head,
        "active_task": active_task,
        "gate": current.get("gate"),
        "capital_gate": STATE.get("main_capital_gate"),
        "live_capital_authorized": STATE.get("live_capital_authorized"),
    }, indent=2))


if __name__ == "__main__":
    main()

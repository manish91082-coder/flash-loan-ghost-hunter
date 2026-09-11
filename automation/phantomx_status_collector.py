#!/usr/bin/env python3
"""Collect PHANTOMX repository health from GitHub Actions and canonical state.

Deterministic only: no LLM, no live capital, no transaction broadcast.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = os.environ.get("GITHUB_REPOSITORY", "manish91082-coder/flash-loan-ghost-hunter")
ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "automation" / "PHANTOMX_AUTOMATION_STATE.json"
GRAPH_PATH = ROOT / "automation" / "phantomx_control_plane.json"
WATCHED_WORKFLOWS = {
    "PHANTOMX P0-A.1 Executor Lineage",
    "PHANTOMX P0-A.2.1 Executor Conformance",
    "PHANTOMX P0-A Economic Truth Tests",
    "PHANTOMX P0-A Live Polygon Quote Validation",
    "PHANTOMX P0-B Executor Compile",
    "PHANTOMX P0-B Executor Security",
    "Compile PHANTOMX Agentic Workflows",
    "PHANTOMX Autonomous Control Plane",
    "PHANTOMX Mission Driver",
    "PHANTOMX Copilot Auth Smoke Test",
    "PHANTOMX CI Failure Alert",
}


def run_gh(args: list[str]) -> str:
    return subprocess.run(
        ["gh", *args], check=True, text=True, capture_output=True, env=os.environ.copy()
    ).stdout


def main() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))

    workflow_rows = json.loads(run_gh([
        "run", "list", "--repo", REPO, "--limit", "80",
        "--json", "databaseId,name,status,conclusion,headSha,createdAt,updatedAt,url",
    ]))
    watched = [row for row in workflow_rows if row.get("name") in WATCHED_WORKFLOWS]

    conclusions: dict[str, int] = {}
    failures: list[dict[str, Any]] = []
    active: list[dict[str, Any]] = []
    latest_by_workflow: dict[str, dict[str, Any]] = {}
    for row in watched:
        name = row["name"]
        if name not in latest_by_workflow:
            latest_by_workflow[name] = row
        status = row.get("status")
        conclusion = row.get("conclusion")
        key = conclusion if status == "completed" and conclusion else status
        conclusions[key] = conclusions.get(key, 0) + 1
        if status != "completed":
            active.append(row)
        if status == "completed" and conclusion in {"failure", "timed_out", "cancelled", "action_required"}:
            failures.append(row)

    current_status = state["controller_status"]
    capital_gate = state["main_capital_gate"]
    if capital_gate != "BLOCKED":
        verdict = "BLOCKED"
    elif failures:
        verdict = "RED"
    elif current_status in {"FAILED", "BLOCKED"}:
        verdict = "RED"
    elif current_status in {"GREEN"}:
        verdict = "GREEN"
    else:
        verdict = "YELLOW"

    report = {
        "schema_version": "PHS-1.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": REPO,
        "main_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "goal": state["mission_goal"],
        "controller_status": current_status,
        "current_task": state["current_engineering_task"],
        "underlying_gate": state["underlying_project_gate"],
        "live_capital_gate": capital_gate,
        "single_active_task": state["single_active_task"],
        "task_graph_count": len(graph["tasks"]),
        "latest_workflows": latest_by_workflow,
        "workflow_conclusions": conclusions,
        "active_workflows": active,
        "failures": failures,
        "verdict": verdict,
        "notes": [
            "This is an engineering-health verdict, not a realized-PnL verdict.",
            "Live capital remains blocked until the mission-control L1-L8 gates independently authorize it.",
        ],
    }

    Path("phantomx-status.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# PHANTOMX LIVE STATUS",
        "",
        f"**Generated:** {report['generated_at']}",
        f"**Current task:** `{report['current_task']}`",
        f"**Underlying gate:** `{report['underlying_gate']}`",
        f"**Controller:** `{report['controller_status']}`",
        f"**Capital gate:** `{report['live_capital_gate']}`",
        f"**Engineering verdict:** `{report['verdict']}`",
        f"**HEAD:** `{report['main_sha']}`",
        "",
        "## Workflow health",
    ]
    if latest_by_workflow:
        for name, row in sorted(latest_by_workflow.items()):
            conclusion = row.get("conclusion") or row.get("status") or "unknown"
            lines.append(f"- `{name}`: **{conclusion}** (run {row.get('databaseId')})")
    else:
        lines.append("- No watched workflow runs were observed.")

    lines += ["", "## Active runs"]
    if active:
        for row in active:
            lines.append(f"- `{row['name']}`: `{row['status']}` (run {row['databaseId']})")
    else:
        lines.append("- None")

    lines += ["", "## Recent failures"]
    if failures:
        for row in failures[:10]:
            lines.append(f"- `{row['name']}`: `{row.get('conclusion')}` (run {row['databaseId']})")
    else:
        lines.append("- None")

    lines += [
        "",
        "## Safety",
        "- Collector never broadcasts transactions or enables live capital.",
        "- Green engineering status is not realized-PnL proof.",
    ]
    Path("PHANTOMX_STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "current_task": report["current_task"], "failures": len(failures)}, indent=2))


if __name__ == "__main__":
    main()

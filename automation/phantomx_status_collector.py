#!/usr/bin/env python3
"""Deterministic PHANTOMX health collector.

The collector is deliberately AI-free and non-capital. It reads the exact
checked-out HEAD, canonical machine state, task graph, and recent GitHub Actions
runs. Historical failures are retained as evidence but cannot make the current
engineering verdict RED when a newer current-HEAD run supersedes them.
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

# Exact workflow names currently present on main. Missing entries are reported
# rather than silently treated as failures.
WATCHED_WORKFLOWS = {
    "PHANTOMX P0-A.1 Executor Lineage",
    "PHANTOMX P0-A.2.1 Executor Conformance",
    "PHANTOMX P0-A Economic Truth Tests",
    "PHANTOMX P0-A Live Polygon Quote Probe",
    "PHANTOMX P0-B Executor Compile",
    "PHANTOMX P0-B Executor Security",
    "Compile PHANTOMX Agentic Workflows",
    "PHANTOMX Autonomous Control Plane",
    "PHANTOMX Copilot Auth Smoke Test",
    "PHANTOMX Live Status / End-to-End Health",
}

FAIL_CONCLUSIONS = {"failure", "timed_out", "cancelled", "action_required"}


def run_gh(args: list[str]) -> str:
    proc = subprocess.run(
        ["gh", *args],
        check=True,
        text=True,
        capture_output=True,
        env=os.environ.copy(),
    )
    return proc.stdout


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def latest_by_name(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        name = row.get("name")
        if name and name not in latest:
            latest[name] = row
    return latest


def main() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    current_head = git_head()

    workflow_rows = json.loads(
        run_gh([
            "run",
            "list",
            "--repo",
            REPO,
            "--limit",
            "100",
            "--json",
            "databaseId,name,status,conclusion,headSha,createdAt,updatedAt,url,event",
        ])
    )
    available_names = {row.get("name") for row in workflow_rows}
    missing_workflows = sorted(WATCHED_WORKFLOWS - available_names)
    watched = [row for row in workflow_rows if row.get("name") in WATCHED_WORKFLOWS]
    latest = latest_by_name(watched)

    current_head_failures: list[dict[str, Any]] = []
    historical_failures: list[dict[str, Any]] = []
    active_current_head: list[dict[str, Any]] = []

    for row in watched:
        conclusion = row.get("conclusion")
        status = row.get("status")
        is_current_head = row.get("headSha") == current_head
        if status != "completed" and is_current_head:
            active_current_head.append(row)
        if status == "completed" and conclusion in FAIL_CONCLUSIONS:
            if is_current_head:
                current_head_failures.append(row)
            else:
                historical_failures.append(row)

    state_consistency = {
        "current_head": current_head,
        "state_last_known_project_head": state.get("last_known_project_head"),
        "state_automation_head": state.get("automation_head"),
        "runtime_head_fields_not_pinned": (
            state.get("last_known_project_head") == "RUNTIME_DERIVED"
            and state.get("automation_head") == "RUNTIME_DERIVED"
        ),
        "task_matches_graph": any(
            t.get("task_id") == state.get("current_engineering_task")
            and t.get("status") == graph.get("current", {}).get("status")
            for t in graph.get("tasks", [])
        ),
        "capital_fail_closed": state.get("main_capital_gate") == "BLOCKED"
        and graph.get("live_capital_authorized") is False,
    }
    state_consistency["ok"] = all(
        [
            state_consistency["runtime_head_fields_not_pinned"],
            state_consistency["task_matches_graph"],
            state_consistency["capital_fail_closed"],
        ]
    )

    current_status = state.get("controller_status")
    capital_gate = state.get("main_capital_gate")
    if capital_gate != "BLOCKED":
        verdict = "BLOCKED"
    elif not state_consistency["ok"]:
        verdict = "RED"
    elif current_head_failures:
        verdict = "RED"
    elif current_status in {"FAILED", "BLOCKED"}:
        verdict = "RED"
    elif active_current_head:
        verdict = "YELLOW"
    elif current_status == "GREEN":
        verdict = "GREEN"
    else:
        verdict = "YELLOW"

    report = {
        "schema_version": "PHS-1.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": REPO,
        "main_sha": current_head,
        "goal": state["mission_goal"],
        "controller_status": current_status,
        "current_task": state["current_engineering_task"],
        "underlying_gate": state["underlying_project_gate"],
        "live_capital_gate": capital_gate,
        "live_capital_authorized": state.get("live_capital_authorized", False),
        "single_active_task": state.get("single_active_task"),
        "task_graph_count": len(graph.get("tasks", [])),
        "latest_workflows": latest,
        "missing_watched_workflows": missing_workflows,
        "active_current_head": active_current_head,
        "current_head_failures": current_head_failures,
        "historical_failures": historical_failures,
        "state_consistency": state_consistency,
        "verdict": verdict,
        "notes": [
            "Deterministic engineering-health verdict only; not realized-PnL proof.",
            "Historical failures are evidence and remain visible but do not contaminate the current verdict when superseded by a newer current-HEAD result.",
            "Missing workflow names are surfaced explicitly and are not reclassified as execution failures.",
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
        f"**State consistency:** `{state_consistency['ok']}`",
        "",
        "## Current-head workflow health",
    ]
    if latest:
        for name, row in sorted(latest.items()):
            marker = "current-head" if row.get("headSha") == current_head else "historical-head"
            conclusion = row.get("conclusion") or row.get("status") or "unknown"
            lines.append(
                f"- `{name}`: **{conclusion}** (run {row.get('databaseId')}; {marker})"
            )
    else:
        lines.append("- No watched workflow runs were observed.")

    lines += ["", "## Current-head failures"]
    if current_head_failures:
        for row in current_head_failures:
            lines.append(
                f"- `{row['name']}`: `{row.get('conclusion')}` (run {row['databaseId']})"
            )
    else:
        lines.append("- None")

    lines += ["", "## Historical failures (non-current HEAD)"]
    if historical_failures:
        for row in historical_failures[:10]:
            lines.append(
                f"- `{row['name']}`: `{row.get('conclusion')}` (run {row['databaseId']})"
            )
    else:
        lines.append("- None in the sampled run window")

    lines += ["", "## Missing / drifted workflow names"]
    if missing_workflows:
        for name in missing_workflows:
            lines.append(f"- `{name}`")
    else:
        lines.append("- None")

    lines += [
        "",
        "## Safety",
        "- Collector never broadcasts transactions or enables live capital.",
        "- Engineering GREEN is not realized-PnL proof.",
    ]
    Path("PHANTOMX_STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": verdict,
                "current_task": report["current_task"],
                "current_head": current_head,
                "current_head_failures": len(current_head_failures),
                "historical_failures": len(historical_failures),
                "state_consistency": state_consistency["ok"],
                "missing_workflows": len(missing_workflows),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

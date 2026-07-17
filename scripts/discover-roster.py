#!/usr/bin/env python3
"""discover-roster — scan this machine for available coding-agent CLIs.

Part of the sop skill. Run by the orchestrator at task start:

    python3 scripts/discover-roster.py [--probe] [--out roster.json]

Prints a roster JSON (and optionally writes it to --out). The probe list
below is an *extensible detection list*, not a roster: installing a new
agent CLI makes it appear on the next run with zero skill edits. Slot
assignment rules live in references/roster-protocol.md — this script only
reports facts (what exists, what version, whether it responds).

--probe additionally runs a minimal non-interactive call per agent
(timeout 60s) to distinguish "installed" from "actually answering"
(auth expired / provider outage show up here). Agents with no known
non-interactive probe recipe report health "unknown" under --probe.
Without --probe, health is at most "available" (present and reports a
version).

Never prints credentials, tokens, or key material.
"""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import time

# Detection list: executable -> static metadata + how to version/probe it.
# "vendor" is the API provider the CLI fronts by default; multi-provider
# CLIs say "multi" and the orchestrator resolves the active provider from
# the CLI's own config at assignment time.
# "tier" is a coarse capability class of the *default* model behind the CLI:
#   frontier  — top reasoning tier, use for sole-writer / final review
#   balanced  — strong general tier, bulk implementation / first-pass review
#   fast      — cheap+quick tier, scouting, mechanical sweeps
# A CLI that can select models across tiers lists them in "tiers_available".
CANDIDATES = {
    "claude": {
        "vendor": "anthropic",
        "tier": "frontier",
        "tiers_available": ["frontier", "balanced", "fast"],
        "version_args": ["--version"],
        "probe_args": ["-p", "reply with exactly: ok"],
        "background_recipe": "IS_SANDBOX=1 claude --dangerously-skip-permissions",
    },
    "codex": {
        "vendor": "openai",
        "tier": "frontier",
        "tiers_available": ["frontier", "balanced"],
        "version_args": ["--version"],
        "probe_args": ["exec", "--skip-git-repo-check", "reply with exactly: ok"],
        "background_recipe": "codex in a bypass/full-auto approval+sandbox mode (never interactive default)",
    },
    "pi": {
        "vendor": "multi",
        "tier": "balanced",
        "tiers_available": ["frontier", "balanced", "fast"],
        "version_args": ["--version"],
        "probe_args": ["-p", "--no-session", "reply with exactly: ok"],
        "background_recipe": "pi (auto-approves by default)",
    },
    "grok": {
        "vendor": "xai",
        "tier": "frontier",
        "tiers_available": ["frontier", "fast"],
        "version_args": ["--version"],
        "probe_args": ["-p", "reply with exactly: ok"],
        "background_recipe": None,
    },
    "opencode": {
        "vendor": "multi",
        "tier": "balanced",
        "tiers_available": ["frontier", "balanced", "fast"],
        "version_args": ["--version"],
        "probe_args": None,
        "background_recipe": None,
    },
    "omp": {
        "vendor": "multi",
        "tier": "balanced",
        "tiers_available": ["balanced"],
        "version_args": ["--version"],
        "probe_args": None,
        "background_recipe": None,
    },
    "gemini": {
        "vendor": "google",
        "tier": "frontier",
        "tiers_available": ["frontier", "fast"],
        "version_args": ["--version"],
        "probe_args": ["-p", "reply with exactly: ok"],
        "background_recipe": None,
    },
}

VERSION_TIMEOUT = 10
PROBE_TIMEOUT = 60


def run(cmd: list[str], timeout: int) -> tuple[int, str]:
    try:
        p = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out.strip()[:200]
    except subprocess.TimeoutExpired:
        return -1, f"timeout after {timeout}s"
    except OSError as exc:
        return -2, str(exc)[:200]


def discover(do_probe: bool) -> dict:
    agents = []
    for name, meta in CANDIDATES.items():
        path = shutil.which(name)
        if not path:
            continue
        entry = {
            "name": name,
            "path": path,
            "vendor": meta["vendor"],
            "tier": meta["tier"],
            "tiers_available": meta["tiers_available"],
            "background_recipe": meta["background_recipe"],
            "version": None,
            "health": "available",
            "probe_ms": None,
            "notes": [],
        }
        rc, out = run([path, *meta["version_args"]], VERSION_TIMEOUT)
        if rc == 0 and out:
            entry["version"] = out.splitlines()[0][:80]
        else:
            entry["health"] = "degraded"
            entry["notes"].append(f"version check failed: {out}")

        if do_probe and meta["probe_args"] and entry["health"] == "available":
            # Probe through an interactive shell so the agent sees the same
            # profile-provided environment (auth tokens sourced in rc files)
            # that a real dispatched pane gets. A bare subprocess can lack
            # that env and report false degradation.
            probe_cmd = [path, *meta["probe_args"]]
            bash = shutil.which("bash")
            if bash:
                probe_cmd = [bash, "-ic", shlex.join(probe_cmd)]
            t0 = time.monotonic()
            rc, out = run(probe_cmd, PROBE_TIMEOUT)
            entry["probe_ms"] = int((time.monotonic() - t0) * 1000)
            ok_lines = {"ok", "ok."}
            answered = rc == 0 and any(
                line.strip().lower() in ok_lines for line in out.splitlines()
            )
            if not answered:
                entry["health"] = "degraded"
                entry["notes"].append(f"probe failed (rc={rc}): {out[:120]}")
        elif do_probe and not meta["probe_args"]:
            entry["health"] = "unknown"
            entry["notes"].append("no non-interactive probe known; verify manually")

        agents.append(entry)

    return {
        "generated_by": "sop/scripts/discover-roster.py",
        "probed": do_probe,
        "host": "local",
        "agents": agents,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--probe", action="store_true",
                    help="run a live non-interactive probe per agent (slower, catches auth/outage)")
    ap.add_argument("--out", help="also write roster JSON to this path")
    args = ap.parse_args()

    roster = discover(args.probe)
    text = json.dumps(roster, indent=2, ensure_ascii=False)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    if not roster["agents"]:
        print("WARNING: no agent CLIs found on PATH", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

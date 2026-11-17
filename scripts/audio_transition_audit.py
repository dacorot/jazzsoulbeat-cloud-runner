#!/usr/bin/env python3
"""Fail-closed audit for audible gaps in a rendered video."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

SILENCE_RE = re.compile(r"silence_(start|end|duration):\s*([0-9.]+)")


def audit(path: Path, threshold_db: float = -45.0, max_seconds: float = 0.20) -> dict:
    command = [
        "ffmpeg", "-hide_banner", "-vn", "-i", str(path),
        "-af", f"silencedetect=noise={threshold_db}dB:d={max_seconds}",
        "-f", "null", "-",
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    events = [(kind, float(value)) for kind, value in SILENCE_RE.findall(result.stderr)]
    durations = [value for kind, value in events if kind == "duration"]
    failures = [duration for duration in durations if duration > max_seconds]
    report = {
        "file": str(path),
        "silence_threshold_db": threshold_db,
        "max_allowed_silence_seconds": max_seconds,
        "silence_durations_seconds": durations,
        "status": "PASS" if result.returncode == 0 and not failures else "FAIL",
        "failure_reason": "boundary_or_internal_silence_exceeds_limit" if failures else "",
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--threshold-db", type=float, default=-45.0)
    parser.add_argument("--max-seconds", type=float, default=0.20)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = audit(args.video, args.threshold_db, args.max_seconds)
    payload = json.dumps(report, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

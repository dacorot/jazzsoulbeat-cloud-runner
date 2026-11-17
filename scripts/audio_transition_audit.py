#!/usr/bin/env python3
"""Fail-closed audit for audible gaps in a rendered video."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

SILENCE_RE = re.compile(r"silence_(start|end|duration):\s*([0-9.]+)")
STRICT_THRESHOLD_DB = -40.0
WARNING_THRESHOLD_DB = -35.0


def detect(path: Path, threshold_db: float, duration: float) -> list[float]:
    command = [
        "ffmpeg", "-hide_banner", "-vn", "-i", str(path),
        "-af", f"silencedetect=noise={threshold_db}dB:d={duration}",
        "-f", "null", "-",
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    events = [(kind, float(value)) for kind, value in SILENCE_RE.findall(result.stderr)]
    return [value for kind, value in events if kind == "duration"]


def audit(path: Path, max_seconds: float = 0.20) -> dict:
    strict = detect(path, STRICT_THRESHOLD_DB, max_seconds)
    warning = detect(path, WARNING_THRESHOLD_DB, max_seconds)
    failures = [duration for duration in strict if duration > max_seconds]
    return {
        "file": str(path),
        "strict_threshold_db": STRICT_THRESHOLD_DB,
        "warning_threshold_db": WARNING_THRESHOLD_DB,
        "max_allowed_silence_seconds": max_seconds,
        "strict_silence_durations_seconds": strict,
        "low_level_quiet_durations_seconds": warning,
        "status": "PASS" if not failures else "FAIL",
        "failure_reason": "audible_gap_exceeds_limit" if failures else "",
        "warning_reason": "low_level_musical_pause_review" if warning else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--max-seconds", type=float, default=0.20)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = audit(args.video, args.max_seconds)
    payload = json.dumps(report, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

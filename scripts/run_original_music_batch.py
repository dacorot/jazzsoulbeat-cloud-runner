#!/usr/bin/env python3
"""Run a bounded, persistent queue of original music candidates.

Every candidate remains pending human listening. This script only automates
generation, technical validation and state tracking; it never approves or
publishes music.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

GENRES = ("jazz", "soul", "lofi")
TARGET = int(os.getenv("MUSIC_TARGET_PER_GENRE", "100"))
BATCH = max(1, min(int(os.getenv("MUSIC_BATCH_SIZE", "3")), 6))
ROOT = Path("music-production")
STATE = ROOT / "music-batch-state.json"

def load_state():
    if STATE.is_file():
        try:
            data = json.loads(STATE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("counts", {g: 0 for g in GENRES})
                data.setdefault("entries", [])
                return data
        except (OSError, ValueError, TypeError):
            pass
    return {"target_per_genre": TARGET, "counts": {g: 0 for g in GENRES}, "entries": []}

def save(state):
    state["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    state = load_state()
    state["target_per_genre"] = TARGET
    produced = []
    for sequence in range(BATCH):
        eligible = [g for g in GENRES if int(state["counts"].get(g, 0)) < TARGET]
        if not eligible:
            break
        genre = min(eligible, key=lambda g: (int(state["counts"].get(g, 0)), GENRES.index(g)))
        slot = int(state["counts"].get(genre, 0)) + 1
        env = os.environ.copy()
        env.update({"MUSIC_GENRE": genre, "MUSIC_DURATION_SECONDS": os.getenv("MUSIC_DURATION_SECONDS", "240")})
        result = subprocess.run([sys.executable, "-m", "scripts.music_producer_agent"], env=env, timeout=1100)
        report_path = ROOT / "production_report.json"
        report = {}
        if report_path.is_file():
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except (OSError, ValueError, TypeError):
                report = {"status": "invalid_report"}
        qc_exit = 1
        if result.returncode == 0 and report.get("status") == "generated_audio_needs_human_review":
            qc_exit = subprocess.run([
                sys.executable, "-m", "scripts.music_audio_qc",
                "--report", str(report_path),
                "--output", str(ROOT / "TECHNICAL_AUDIO_QA.json"),
            ], timeout=240).returncode
        pre_review_exit = 1
        technical_path = ROOT / "TECHNICAL_AUDIO_QA.json"
        pre_review_path = ROOT / "PRE_REVIEW_GATE.json"
        if qc_exit == 0 and report_path.is_file() and technical_path.is_file():
            pre_review_exit = subprocess.run([
                sys.executable, "-m", "scripts.music_pre_review_gate",
                "--report", str(report_path),
                "--technical-qa", str(technical_path),
                "--output", str(pre_review_path),
            ], timeout=60).returncode
        run_dir = ROOT / "batch" / genre / f"candidate-{slot:03d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        for path in ROOT.glob("generated/*"):
            if path.is_file():
                shutil.move(str(path), run_dir / path.name)
        if report_path.is_file():
            shutil.copy2(report_path, run_dir / "production_report.json")
        qa = ROOT / "TECHNICAL_AUDIO_QA.json"
        if qa.is_file():
            shutil.copy2(qa, run_dir / qa.name)
        pre_review = ROOT / "PRE_REVIEW_GATE.json"
        if pre_review.is_file():
            shutil.copy2(pre_review, run_dir / pre_review.name)
        success = (
            result.returncode == 0
            and qc_exit == 0
            and pre_review_exit == 0
            and report.get("status") == "generated_audio_needs_human_review"
        )
        if success:
            state["counts"][genre] = slot
        entry = {"genre": genre, "slot": slot, "status": report.get("status", "process_failed"),
                 "technical_candidate": success, "run_exit_code": result.returncode,
                 "technical_qa_exit_code": qc_exit,
                 "pre_review_gate_exit_code": pre_review_exit,
                 "path": str(run_dir), "created_at_utc": datetime.now(timezone.utc).isoformat(),
                 "approval": "PENDING_HUMAN_LISTENING"}
        state["entries"].append(entry)
        produced.append(entry)
        save(state)
        if result.returncode != 0 and report.get("status") in {"blocked_free_quota", "blocked_rate_limit"}:
            break
    save(state)
    print(json.dumps({"target_per_genre": TARGET, "counts": state["counts"], "produced": produced,
                      "status": "TARGET_REACHED" if all(v >= TARGET for v in state["counts"].values()) else "IN_PROGRESS"}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

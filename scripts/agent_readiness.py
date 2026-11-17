#!/usr/bin/env python3
"""Run a bounded readiness audit for every local Jazz Soul Beat agent."""
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path


def check(name, fn):
    try:
        result = fn()
        return {"name": name, "status": "PASS", "details": result or {}}
    except Exception as exc:  # noqa: BLE001 - audit must report every lane
        return {"name": name, "status": "FAIL", "details": {"error": str(exc)}}


def audit(root: Path) -> dict:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    image = root / "music-production/visual-review/cafe-library-clean-window-v2-candidate.png"
    ledger = root / "music-production/approval_ledger.json"
    checks = [
        check("visual_motion_agent_contract", lambda: _visual(root, image)),
        check("music_search_policy", lambda: _search(root)),
        check("longform_library_gate", lambda: _library(root, ledger)),
        check("audio_adapters_import", lambda: _imports()),
        check("python_compile", lambda: _compile(root)),
    ]
    return {
        "agent_readiness_version": 1,
        "project": "Jazz Soul Beat",
        "checks": checks,
        "technical_status": "READY" if all(c["status"] == "PASS" for c in checks) else "BLOCKED",
        "publication": "DISABLED",
    }


def _visual(root, image):
    from scripts.visual_motion_agent import create_plan
    plan = create_plan(image)
    assert plan["animated_layers"] == ["coffee_steam"]
    assert plan["camera"] == "locked"
    return {"profile": plan["profile"], "base_image_sha256": plan["base_image_sha256"]}


def _search(root):
    policy = json.loads((root / "config/music_search_policy.json").read_text(encoding="utf-8"))
    assert policy["never_auto_approve"] is True
    assert policy["never_publish"] is True
    assert policy["target_genres"]
    return {"target_genres": policy["target_genres"], "minimum_seconds": policy["minimum_candidate_duration_seconds"]}


def _library(root, ledger):
    from scripts.longform_library_agent import plan
    result = plan(json.loads(ledger.read_text(encoding="utf-8")))
    return {"status": result["status"], "approved_seconds": result["approved_seconds"],
            "missing_seconds": result["missing_seconds"]}


def _imports():
    for module in ("scripts.stable_audio3_producer", "scripts.diffrhythm2_producer",
                   "scripts.music_audio_qc", "scripts.approval_gate", "scripts.production_gate"):
        importlib.import_module(module)
    return {"modules": 5}


def _compile(root):
    result = subprocess.run([sys.executable, "-m", "compileall", "-q", "scripts"],
                            cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "compileall failed")
    return {"directory": "scripts"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root.resolve())
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["technical_status"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())

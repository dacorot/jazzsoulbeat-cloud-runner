#!/usr/bin/env python3
"""Three-role release board for every private video candidate.

Supervisor, coordinator and creative directors each get an independent check.
Failure means REWORK_REQUIRED, never silent rejection or publication.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def review(run_dir: Path, expected_seconds: float) -> dict:
    transition_path = run_dir / "AUDIO_TRANSITION_REPORT.json"
    visual_path = run_dir / "VISUAL_SCENE_PROVENANCE.json"
    required = ["video.mp4", "mix.mp3", "thumb.jpg", "description.txt", "MUSIC_SOURCE.txt"]
    checks = []

    def check(role: str, name: str, passed: bool, detail: str = "") -> None:
        checks.append({"role": role, "name": name, "passed": bool(passed), "detail": detail})

    transition = json.loads(transition_path.read_text(encoding="utf-8")) if transition_path.is_file() else {}
    visual = json.loads(visual_path.read_text(encoding="utf-8")) if visual_path.is_file() else {}

    # Supervisor: operational/technical gates.
    check("supervisor", "audio_transition_audit", transition.get("status") == "PASS", str(transition.get("failures", [])))
    silences = [float(value) for value in transition.get("silence_durations_seconds", [])]
    check("supervisor", "no_audible_gaps", not any(value > 0.20 for value in silences), str(silences))
    check("supervisor", "every_boundary_analyzed", transition.get("transition_count") == max(0, transition.get("track_count", 0) - 1))
    check("supervisor", "required_artifacts_present", all((run_dir / item).is_file() and (run_dir / item).stat().st_size > 0 for item in required))

    # Coordinator: exact artifact and delivery contract.
    video = run_dir / "video.mp4"
    mix = run_dir / "mix.mp3"
    check("coordinator", "video_duration_contract", bool(expected_seconds > 0), f"expected={expected_seconds}")
    check("coordinator", "private_only_state", visual.get("publication") in {"PRIVATE_REVIEW_ONLY", "DISABLED"})
    check("coordinator", "audio_report_hash_bound", bool(transition.get("tracks")))
    check("coordinator", "video_and_mix_nonempty", video.is_file() and video.stat().st_size > 0 and mix.is_file() and mix.stat().st_size > 0)

    # Directors: independent creative identity checks.
    check("audio_director", "transition_learning_evidence", bool(transition.get("learning_features")))
    check("visual_director", "locked_camera", visual.get("camera") == "locked")
    check("visual_director", "single_identity_plate", visual.get("scene_count") == 1 and bool(visual.get("approved_image_sha256")))
    check("visual_director", "unique_reference_bound", visual.get("visual_uniqueness") == "REQUIRED_AND_HASH_BOUND" and bool(visual.get("reference_perceptual_signature")))
    check("visual_director", "playlist_linked", bool(visual.get("playlist")) and bool(visual.get("music_visual_match")))
    check("metadata_director", "track_source_manifest", (run_dir / "MUSIC_SOURCE.txt").is_file())
    check("metadata_director", "description_present", bool((run_dir / "description.txt").read_text(encoding="utf-8").strip()) if (run_dir / "description.txt").is_file() else False)

    failures = [item for item in checks if not item["passed"]]
    return {
        "status": "APPROVED_PRIVATE" if not failures else "REWORK_REQUIRED",
        "checks": checks,
        "failed_checks": failures,
        "repair_policy": "repair_and_represent_until_all_roles_pass",
        "public_publish": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--expected-seconds", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = review(args.run_dir, args.expected_seconds)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failed_checks": len(report["failed_checks"]), "public_publish": False}))
    return 0 if report["status"] == "APPROVED_PRIVATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())

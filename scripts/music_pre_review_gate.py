#!/usr/bin/env python3
"""Second automated gate before a human listens to an original candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_GENRES = {"jazz", "soul", "lofi"}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--technical-qa", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    errors = []
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        technical = json.loads(args.technical_qa.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f"cannot_read_gate_inputs:{exc}")
        report, technical = {}, {}

    if technical.get("status") != "PASS_TECHNICAL_AUDIO_ONLY":
        errors.append("technical_gate_not_passed")
    if report.get("status") != "generated_audio_needs_human_review":
        errors.append("producer_status_not_pending_review")
    if report.get("quality_gate") != "MUST_IMPROVE_APPROVED_BASELINE":
        errors.append("improvement_over_baseline_not_required")
    if report.get("baseline_reference") != "Moonlit Coffeehouse / run 45646476397":
        errors.append("baseline_reference_missing")
    if report.get("editorial_verdict") != "PENDING_HUMAN_LISTENING":
        errors.append("editorial_review_not_pending")
    if report.get("creative_approval") is not False:
        errors.append("creative_approval_must_remain_false")
    if report.get("rights_verified") is not False:
        errors.append("rights_must_remain_unverified")
    if report.get("eligible_for_video_assembly") is not False:
        errors.append("video_eligibility_must_remain_false")
    if report.get("publication_status") != "NOT_PUBLISHED":
        errors.append("publication_must_remain_disabled")
    if report.get("genre") not in REQUIRED_GENRES:
        errors.append("unsupported_or_missing_genre")

    outcome = {
        "status": "PASS_SECOND_AUTOMATED_GATE" if not errors else "BLOCKED_PRE_REVIEW_GATE",
        "checks": [
            "technical_audio_gate_passed",
            "improvement_over_baseline_declared_for_human_comparison",
            "rights_and_publication_safety_lock",
            "genre_and_review_state_validated",
        ],
        "errors": errors,
        "human_review_required": True,
        "creative_approval": False,
        "eligible_for_video_assembly": False,
        "verified_by": "music_pre_review_gate",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(outcome, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Evidence-bound autonomous candidate approval and quarantine gate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

try:
    from .autonomous_learning import append_feedback, load_model, probability, retrain
except ImportError:  # direct script execution from the GitHub Actions agent checkout
    from autonomous_learning import append_feedback, load_model, probability, retrain


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_is_primary(url: str, domains: list[str]) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return any(host == domain or host.endswith("." + domain) for domain in domains)


def license_is_allowed(name: str) -> bool:
    normalized = " ".join(name.upper().replace("_", " ").split())
    return normalized in {"CC0", "CC0 1.0", "CC0 1.0 UNIVERSAL", "CC BY 4.0", "CC BY 4.0 INTERNATIONAL"}


def evaluate(candidate: dict, policy: dict, model: dict) -> tuple[dict, dict]:
    title = str(candidate.get("title", ""))
    text = " ".join(str(candidate.get(key, "")) for key in ("title", "genres", "tags", "description")).lower()
    license_name = str(candidate.get("license_name", candidate.get("license", ""))).upper()
    source_url = str(candidate.get("source_url", ""))
    artifact = Path(str(candidate.get("artifact", candidate.get("file", ""))))
    expected_hash = str(candidate.get("artifact_sha256", candidate.get("sha256", "")))
    actual_hash = digest(artifact) if artifact.is_file() else ""
    features = {
        "primary_source": source_is_primary(source_url, policy["primary_domains"]),
        "license_allowed": license_is_allowed(license_name),
        "hash_verified": bool(expected_hash) and expected_hash == actual_hash,
        "technical_ok": candidate.get("technical_ok", candidate.get("technical_valid", False)) is True,
        "instrumental": candidate.get("instrumental", candidate.get("vocals", True) is False) is True,
        "editorial_match": any(term in text for term in policy["target_genres"]),
        "duration_ok": float(candidate.get("duration_seconds", 0) or 0) >= policy["min_duration_seconds"],
        "forbidden_term": any(term in text for term in policy["reject_terms"]),
    }
    score = probability(features, model)
    hard_failures = [name for name in policy["hard_requirements"] if not features[name]]
    if features["forbidden_term"]:
        hard_failures.append("forbidden_term")
    result = dict(candidate)
    result.update({"decision_score": round(score, 6), "decision_features": features,
                   "approval_mode": policy["mode"], "artifact_sha256": actual_hash or expected_hash})
    if not hard_failures and score >= policy["min_auto_approval_score"]:
        result.update({"decision": "ELIGIBLE_FOR_LIBRARY", "rights_verified": True,
                       "eligible_for_video_assembly": True,
                       "auto_approval_evidence": "primary_source_license_hash_technical_editorial_policy"})
        return result, {"decision": "approved", "title": title, "score": score, "features": features}
    result.update({"decision": "QUARANTINED", "rights_verified": False,
                   "eligible_for_video_assembly": False,
                   "quarantine_reasons": sorted(set(hard_failures or ["score_below_threshold"]))})
    return result, {"decision": "quarantined", "title": title, "score": score, "features": features}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quarantine", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--feedback", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    feature_order = policy["feature_order"]
    model = retrain(args.feedback, args.model, feature_order)
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    candidates = payload if isinstance(payload, list) else payload.get("candidates", payload.get("eligible", []))
    approved, quarantined = [], []
    for candidate in candidates:
        result, summary = evaluate(candidate, policy, model)
        append_feedback(args.feedback, summary["features"], 1 if summary["decision"] == "approved" else 0, summary["decision"])
        (approved if summary["decision"] == "approved" else quarantined).append(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.quarantine.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(approved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.quarantine.write_text(json.dumps(quarantined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"approved": len(approved), "quarantined": len(quarantined), "model_samples": model.get("samples", 0), "publication": "DISABLED"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

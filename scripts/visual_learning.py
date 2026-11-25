#!/usr/bin/env python3
"""Evidence-bound online learner for visual proof outcomes."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, value))))


def _default(features: list[str]) -> dict:
    return {"schema_version": 1, "algorithm": "online_logistic_regression",
            "samples": 0, "feature_order": features,
            "weights": [1.0] * len(features), "bias": -2.0}


def retrain(feedback: Path, model_path: Path, features: list[str]) -> dict:
    model = _default(features)
    if model_path.is_file():
        try:
            candidate = json.loads(model_path.read_text(encoding="utf-8"))
            if candidate.get("feature_order") == features and len(candidate.get("weights", [])) == len(features):
                model = candidate
        except (OSError, json.JSONDecodeError):
            pass
    rows = []
    if feedback.is_file():
        for line in feedback.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                if row.get("label") in (0, 1):
                    rows.append(row)
            except (TypeError, json.JSONDecodeError):
                continue
    for row in rows[int(model.get("samples", 0)):]:
        values = [float(bool(row.get("features", {}).get(name))) for name in features]
        prediction = _sigmoid(float(model["bias"]) + sum(w * v for w, v in zip(model["weights"], values)))
        error = float(row["label"]) - prediction
        model["weights"] = [w + 0.15 * error * v for w, v in zip(model["weights"], values)]
        model["bias"] = float(model["bias"]) + 0.15 * error
        model["samples"] = int(model.get("samples", 0)) + 1
    model["trained_rows"] = len(rows)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feedback", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    args = parser.parse_args()
    policy = json.loads(Path(__file__).resolve().parents[1].joinpath("config/visual_learning_policy.json").read_text(encoding="utf-8"))
    model = retrain(args.feedback, args.model, policy["feature_order"])
    print(json.dumps({"status": "RETRAINED", "samples": model["samples"], "model": str(args.model)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

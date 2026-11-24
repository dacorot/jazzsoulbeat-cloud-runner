#!/usr/bin/env python3
"""Small, reproducible online learner for the music gate.

The learner changes ranking, never the hard rights/technical requirements.
Feedback is append-only JSONL and model snapshots are versioned JSON, so each
decision can be reproduced or rolled back without a paid ML service.
"""
from __future__ import annotations

import json
import math
from pathlib import Path


def sigmoid(value: float) -> float:
    value = max(-40.0, min(40.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def default_model(feature_order: list[str]) -> dict:
    weights = [(-4.0 if name == "forbidden_term" else 1.0) for name in feature_order]
    return {"schema_version": 1, "algorithm": "online_logistic_regression",
            "samples": 0, "feature_order": feature_order,
            "weights": weights, "bias": -3.0}


def load_model(path: Path, feature_order: list[str]) -> dict:
    if not path.is_file():
        return default_model(feature_order)
    model = json.loads(path.read_text(encoding="utf-8"))
    if model.get("feature_order") != feature_order or len(model.get("weights", [])) != len(feature_order):
        return default_model(feature_order)
    return model


def vector(features: dict, feature_order: list[str]) -> list[float]:
    return [float(bool(features.get(name))) for name in feature_order]


def probability(features: dict, model: dict) -> float:
    values = vector(features, model["feature_order"])
    score = float(model.get("bias", 0.0)) + sum(w * x for w, x in zip(model["weights"], values))
    return sigmoid(score)


def retrain(feedback_path: Path, model_path: Path, feature_order: list[str]) -> dict:
    model = load_model(model_path, feature_order)
    rows = []
    if feedback_path.is_file():
        for line in feedback_path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                if isinstance(row, dict) and row.get("label") in (0, 1):
                    rows.append(row)
            except json.JSONDecodeError:
                continue
    learning_rate = 0.15
    for row in rows[model.get("samples", 0):]:
        x = vector(row.get("features", {}), feature_order)
        y = float(row["label"])
        p = sigmoid(float(model["bias"]) + sum(w * v for w, v in zip(model["weights"], x)))
        error = y - p
        model["weights"] = [w + learning_rate * error * v for w, v in zip(model["weights"], x)]
        model["bias"] = float(model["bias"]) + learning_rate * error
        model["samples"] = int(model.get("samples", 0)) + 1
    model["trained_rows"] = len(rows)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return model


def append_feedback(path: Path, features: dict, label: int, reason: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"features": features, "label": int(label), "reason": reason}, ensure_ascii=False) + "\n")

#!/usr/bin/env python3
"""Plan audiovisual assembly with metadata-driven audio transitions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MIN_CROSSFADE_SECONDS = 8.0
MAX_CROSSFADE_SECONDS = 4.0
DEFAULT_CROSSFADE_SECONDS = 12.0
MAX_ALLOWED_BOUNDARY_SILENCE_SECONDS = 0.20
BOUNDARY_SILENCE_TRIM_THRESHOLD_DB = -45


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _text(track: dict) -> str:
    return " ".join(
        str(track.get(key) or "")
        for key in ("title", "genre", "feel", "mood", "instruments")
    ).casefold()


def evaluate_crossfade(previous: dict, following: dict) -> dict:
    """Choose a bounded fade from adjacent track metadata.

    Equation:
      d = clamp(base + calm_bonus - energetic_penalty,
                MIN_CROSSFADE_SECONDS,
                min(MAX_CROSSFADE_SECONDS, 0.25 * shortest_track))
    """
    shortest = min(
        _number(previous.get("duration_seconds"), 180.0),
        _number(following.get("duration_seconds"), 180.0),
    )
    base = DEFAULT_CROSSFADE_SECONDS
    combined = f"{_text(previous)} {_text(following)}"
    calm_bonus = 0.8 if any(word in combined for word in ("calm", "slow", "soft", "sleep", "ambient", "mellow")) else 0.0
    energetic_penalty = 0.7 if any(word in combined for word in ("funk", "bouncy", "upbeat", "grooving", "fast")) else 0.0
    tempo_penalty = 0.0
    tempo_values = [_number(previous.get("tempo_bpm")), _number(following.get("tempo_bpm"))]
    valid_tempos = [tempo for tempo in tempo_values if tempo > 0]
    if valid_tempos and max(valid_tempos) >= 120:
        tempo_penalty = 0.3
    raw = base + calm_bonus - energetic_penalty - tempo_penalty
    maximum = min(MAX_CROSSFADE_SECONDS, max(MIN_CROSSFADE_SECONDS, shortest * 0.25))
    seconds = round(max(MIN_CROSSFADE_SECONDS, min(raw, maximum)), 2)
    return {
        "from": previous.get("title", ""),
        "to": following.get("title", ""),
        "crossfade_seconds": seconds,
        "curve": "tri",
        "formula": "clamp(2.0 + calm_bonus - energy_penalty - tempo_penalty, 0.8, min(4.0, 0.25*shortest_duration))",
        "gap_policy": "forbid_silence",
        "overlap_policy": "continuous_audio",
        "trim_boundary_silence": True,
        "boundary_silence_trim_threshold_db": BOUNDARY_SILENCE_TRIM_THRESHOLD_DB,
        "max_allowed_boundary_silence_seconds": MAX_ALLOWED_BOUNDARY_SILENCE_SECONDS,
    }


def transition_plan(tracks: list[dict]) -> list[dict]:
    if len(tracks) < 2:
        return []
    return [
        evaluate_crossfade(previous, following)
        for previous, following in zip(tracks, tracks[1:])
    ]


def plan(
    video_id: str,
    duration_seconds: int,
    audio_ids: list[str],
    visual_profile: str,
    tracks: list[dict] | None = None,
) -> dict:
    if not video_id or duration_seconds <= 0 or not audio_ids:
        raise ValueError("assembly_inputs_incomplete")
    metadata = tracks or [{"title": audio_id} for audio_id in audio_ids]
    if len(metadata) != len(audio_ids):
        raise ValueError("track_metadata_count_mismatch")
    transitions = transition_plan(metadata)
    return {
        "video_id": video_id,
        "duration_seconds": duration_seconds,
        "audio_ids": list(audio_ids),
        "visual_profile": visual_profile,
        "camera": "locked",
        "transition_count": len(transitions),
        "transitions": transitions,
        "audio_contract": {
            "crossfade_required": True,
            "crossfade_evaluated_per_boundary": True,
            "silence_allowed_between_tracks": False,
            "default_seconds": DEFAULT_CROSSFADE_SECONDS,
            "trim_leading_trailing_silence": True,
            "silence_threshold_db": BOUNDARY_SILENCE_TRIM_THRESHOLD_DB,
            "max_boundary_silence_seconds": MAX_ALLOWED_BOUNDARY_SILENCE_SECONDS,
        },
        "state": "PLANNED",
        "creative_approval": False,
        "rights_verified": False,
        "publication": "DISABLED",
    }


def contract() -> dict:
    return {
        "id": "video_assembly_agent",
        "requires_approved_audio": True,
        "requires_approved_visual": True,
        "requires_transition_evaluation": True,
        "no_silence_between_tracks": True,
        "trim_boundary_silence": True,
        "max_allowed_boundary_silence_seconds": MAX_ALLOWED_BOUNDARY_SILENCE_SECONDS,
        "publication": "DISABLED",
        "never_publish": True,
    }

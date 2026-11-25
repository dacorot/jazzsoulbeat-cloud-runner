#!/usr/bin/env python3
"""Free Stable Audio 3 audition producer.

Uses Stability AI's official Hugging Face ZeroGPU Space.  The Medium variant is
the only variant used for a publishable-length audition because the official
model documentation supports up to 380 seconds and describes it as the
higher-musicality model.  This adapter is deliberately an audition stage:
technical validation never grants creative or rights approval.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("music-production")
AUDIO = OUT / "generated"
SPACE = os.getenv("STABLE_AUDIO3_SPACE", "stabilityai/stable-audio-3")
MODEL = "medium"
TITLE = os.getenv("MUSIC_TITLE", "Moonlit Coffeehouse")
CATEGORY = os.getenv("MUSIC_CATEGORY", "coffee_time")
PROMPT = os.getenv(
    "MUSIC_PROMPT",
    "Original instrumental late-night jazz soul, elegant adult coffeehouse atmosphere, "
    "warm acoustic grand piano voicings, Rhodes accents, upright bass, brushed jazz drums, "
    "mellow tenor saxophone lead and restrained guitar comping, 78 BPM, gentle swing, "
    "memorable lyrical theme, conversational sax improvisation, contrasting bridge, "
    "dynamic development, natural room ambience, resolved ending, professionally recorded, "
    "no vocals, no lyrics, no cover, no quotation, no artist imitation, no sampling, no loop",
)
NEGATIVE_PROMPT = os.getenv(
    "MUSIC_NEGATIVE_PROMPT",
    "speech, vocals, lyrics, cover version, recognizable melody, artist imitation, "
    "harsh clipping, repetitive loop, cheap synth, chiptune, low fidelity, abrupt ending",
)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fail(status: str, message: str, details: dict | None = None) -> int:
    write_json(OUT / "production_report.json", {
        "status": status,
        "message": message,
        "details": details or {},
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "engine": "Stable Audio 3",
        "space": SPACE,
        "model": MODEL,
        "category": CATEGORY,
        "cost_policy": "free_only",
        "creative_approval": False,
        "rights_verified": False,
        "eligible_for_video_assembly": False,
        "publication_status": "NOT_PUBLISHED",
    })
    return 1


def _find_audio(value):
    if isinstance(value, (str, Path)):
        path = Path(value)
        if path.suffix.lower() in {".wav", ".mp3", ".flac", ".ogg", ".m4a"} and path.is_file() and not path.is_symlink():
            yield path
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _find_audio(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _find_audio(item)


def _duration() -> int:
    try:
        value = int(os.getenv("MUSIC_DURATION_SECONDS", "360"))
    except ValueError:
        value = -1
    return value


def main() -> int:
    duration = _duration()
    if CATEGORY not in {"work_study", "coffee_time", "sleep", "chill"} or not 180 <= duration <= 380:
        return fail(
            "blocked_invalid_brief",
            "Stable Audio 3 audition requires an instrumental category and 180–380 seconds.",
            {"category": CATEGORY, "duration_seconds": duration},
        )
    try:
        from gradio_client import Client
        client = Client(SPACE, verbose=False)
        api = client.view_api(return_format="dict")
        endpoints = api.get("named_endpoints", {}) if isinstance(api, dict) else {}
        if "/infer" not in endpoints:
            return fail(
                "blocked_api_changed",
                "The verified Stable Audio 3 /infer endpoint is unavailable. No endpoint was guessed.",
                {"available_endpoints": sorted(endpoints)},
            )
        result = client.predict(
            MODEL, PROMPT, duration, 8, 1.0, "pingpong", int(os.getenv("MUSIC_SEED", "20261114")),
            api_name="/infer",
        )
    except Exception as exc:
        message = str(exc)
        lowered = message.casefold()
        status = "blocked_generation"
        if "429" in lowered or "rate limit" in lowered:
            status = "blocked_rate_limit"
        elif "quota" in lowered or "zerogpu" in lowered:
            status = "blocked_free_quota"
        return fail(status, "Stable Audio 3 free generation failed; no paid fallback was used.", {"error": message[:1600]})

    source = next((path for path in _find_audio(result) if path.stat().st_size > 100_000), None)
    if source is None:
        return fail("blocked_no_audio_file", "Stable Audio 3 returned no verifiable local audio file.", {"result_preview": str(result)[:2000]})

    AUDIO.mkdir(parents=True, exist_ok=True)
    target = AUDIO / "candidate.wav"
    shutil.copy2(source, target)
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,sample_rate,channels", "-of", "json", str(target)],
            check=True, capture_output=True, text=True, timeout=60,
        )
        info = json.loads(probe.stdout)
        streams = info.get("streams", [])
        audio = [stream for stream in streams if stream.get("codec_type") == "audio"]
        actual = float(info.get("format", {}).get("duration", 0))
        if len(streams) != 1 or len(audio) != 1 or not math.isfinite(actual) or not 175 <= actual <= 390:
            raise ValueError(f"unexpected audio shape or duration: {actual}")
        with target.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        target.unlink(missing_ok=True)
        return fail("blocked_invalid_audio", "Stable Audio 3 returned invalid audio; it was discarded.", {"error": str(exc)[:800]})

    write_json(OUT / "production_report.json", {
        "status": "generated_audio_needs_human_review",
        "title": TITLE,
        "category": CATEGORY,
        "file": str(target),
        "bytes": target.stat().st_size,
        "sha256": digest,
        "duration_actual_seconds": round(actual, 3),
        "duration_requested_seconds": duration,
        "prompt": PROMPT,
        "negative_prompt": NEGATIVE_PROMPT,
        "engine": "Stable Audio 3",
        "space": SPACE,
        "model": MODEL,
        "model_license": "Stability AI Community License",
        "editorial_verdict": "PENDING_HUMAN_LISTENING",
        "creative_approval": False,
        "eligible_for_video_assembly": False,
        "endpoint": "/infer",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rights_note": "Stable Audio 3 is described by Stability AI as trained on fully licensed data and permits qualifying commercial use under its Community License. This does not prove originality or copyrightability of this individual output; human listening, similarity review and final rights review remain mandatory.",
        "model_card_url": "https://huggingface.co/stabilityai/stable-audio-3-medium",
        "license_url": "https://stability.ai/license",
        "commercial_use_statement": "qualifying_use_under_community_license_requires_license_compliance",
        "rights_verified": False,
        "human_review_required": True,
        "publication_status": "NOT_PUBLISHED",
    })
    print(json.dumps({"status": "generated_audio_needs_human_review", "file": str(target), "sha256": digest, "duration": round(actual, 3)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

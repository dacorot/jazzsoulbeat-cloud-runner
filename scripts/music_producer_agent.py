#!/usr/bin/env python3
"""Free-only ACE-Step producer. Calls the verified Gradio generation endpoint."""
import hashlib, json, math, os, shutil, subprocess, sys
from urllib.parse import urlparse

from scripts.music_briefs import GENRE_SIGNATURES, choose_brief, choose_genre_brief
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("music-production")
AUDIO = OUT / "generated"
OUT.mkdir(exist_ok=True)
AUDIO.mkdir(exist_ok=True)
SPACE = os.getenv("ACE_STEP_SPACE", "ACE-Step/Ace-Step-v1.5")
# An audition must be one song, 3–6 minutes; never stretch a loop to fill a video.
DEFAULT_DURATION_SECONDS = 240
NEGATIVE = (
    "copyrighted melody, cover, soundalike, artist imitation, childish, chiptune, "
    "synthetic test tones, robotically repeated arpeggios, low fidelity"
)

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def fail(status, message, details=None):
    report = {"status": status, "message": message, "details": details or {},
              "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "engine": SPACE, "cost_policy": "free_only"}
    write_json(OUT / "production_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1

def main():
    try:
        raw_duration = os.getenv("MUSIC_DURATION_SECONDS", str(DEFAULT_DURATION_SECONDS))
        duration = int(raw_duration)
        genre = os.getenv("MUSIC_GENRE", "").strip().lower()
        brief = choose_genre_brief(genre) if genre else choose_brief(os.getenv("MUSIC_CATEGORY", "coffee_time"))
        model = os.getenv("ACE_STEP_MODEL", "acestep-v15-turbo")
        if model not in {"acestep-v15-turbo", "acestep-v15-xl-turbo"}:
            raise ValueError("Only vetted free ACE-Step turbo models are permitted.")
        prompt = brief.prompt(duration)
    except (TypeError, ValueError) as exc:
        return fail(
            "blocked_invalid_brief",
            "Category or requested song length is outside the approved 3–6 minute range.",
            {"reason": str(exc)[:200]},
        )
    try:
        from gradio_client import Client
        client = Client(SPACE, token=os.getenv("HF_TOKEN") or None, verbose=False)
        api = client.view_api(return_format="dict")
    except Exception as e:
        return fail("blocked_free_service", "Could not connect to the public ACE-Step Space or inspect its API. No paid fallback was used.", {"error": str(e)[:1200]})

    write_json(OUT / "space_api_snapshot.json", api)
    endpoints = api.get("named_endpoints", {})
    info = endpoints.get("/generation_wrapper") if isinstance(endpoints, dict) else None
    if not info:
        return fail("blocked_api_changed", "The verified /generation_wrapper endpoint is unavailable. No other endpoint will be guessed.", {"available_endpoints": list(endpoints)[:100] if isinstance(endpoints, dict) else []})

    # Use the endpoint's advertised parameter order and defaults; override only known fields.
    overrides = {
        "selected_model": model,
        "generation_mode": "custom",
        "simple_query_input": prompt,
        "simple_vocal_language": "unknown",
        "param_4": prompt,
        "param_5": "[Instrumental]",
        "param_6": brief.bpm,
        "param_7": brief.key,
        "param_8": "4",
        "param_9": "unknown",
        "param_10": 8,
        "param_12": True,
        "param_13": "-1",
        "param_15": duration,
        "param_16": 1,
        "param_23": "text2music",
        "param_30": "mp3",
        "param_32": True,
        "param_36": NEGATIVE,
        "param_43": False,
        "param_44": False,
    }
    parameters = info.get("parameters", [])
    names = {p.get("parameter_name") for p in parameters if isinstance(p, dict)}
    # Gradio uses positional arguments. A renamed or removed control can alter
    # the meaning of every following value, so reject silently changed schemas.
    if not isinstance(parameters, list) or not {
        "selected_model", "param_4", "param_5", "param_6",
        "param_7", "param_15", "param_16", "param_23",
    }.issubset(names):
        return fail("blocked_api_changed",
                    "Public generation interface changed its critical parameters.",
                    {"endpoint": "/generation_wrapper"})
    values, mapped = [], {}
    for p in parameters:
        name = p.get("parameter_name", "")
        if name in overrides:
            value = overrides[name]
        elif p.get("parameter_has_default", False):
            value = p.get("parameter_default")
        else:
            value = None  # optional file inputs / optional metadata with no default
        values.append(value)
        mapped[name or f"parameter_{len(values)}"] = value if isinstance(value, (str, int, float, bool, type(None))) else str(value)

    try:
        result = client.predict(*values, api_name="/generation_wrapper")
    except Exception as e:
        failure = str(e)
        if "ZeroGPU quota" in failure or "quota exceeded" in failure.lower():
            return fail(
                "blocked_free_quota",
                "The free ZeroGPU allowance is exhausted; no paid fallback or immediate retry.",
                {"endpoint": "/generation_wrapper",
                "provider_retry_hint": failure[:500], "category": brief.slug, "genre": genre or None},
            )
        if "429" in failure or "rate limit" in failure.lower():
            return fail(
                "blocked_rate_limit",
                "Free model provider rate-limited this request; no immediate retry.",
                {"endpoint": "/generation_wrapper",
                "provider_retry_hint": failure[:500], "category": brief.slug, "genre": genre or None},
            )
        return fail(
            "blocked_generation",
            "The ACE-Step generation endpoint failed; no paid fallback was used.",
            {"endpoint": "/generation_wrapper", "error": failure[:1000],
             "category": brief.slug, "genre": genre or None, "requested_duration": duration},
        )

    found = []
    def walk(x):
        if isinstance(x, str):
            # Only Gradio-downloaded local files qualify as audio inputs.
            # Never fetch arbitrary URLs contained in untrusted model output.
            if len(x) < 2048 and Path(x).suffix.lower() in {".mp3", ".wav", ".flac", ".ogg", ".m4a"}:
                try:
                    p = Path(x)
                    if p.is_file() and not p.is_symlink():
                        found.append(p)
                except OSError:
                    pass
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x: walk(v)
    walk(result)

    target = None
    for item in found:
        try:
            if item.stat().st_size > 100_000:
                candidate = AUDIO / ("candidate" + item.suffix.lower())
                shutil.copy2(item, candidate)
                target = candidate
                break
        except OSError:
            continue

    if not target:
        preview = str(result)[:2500]
        if "Expected all tensors to be on the same device" in preview:
            return fail(
                "blocked_provider_device_mismatch",
                "Provider mixed CPU and GPU tensors during inference; no audio was produced.",
                {"endpoint": "/generation_wrapper", "model": model,
                 "result_preview": preview[:800]},
            )
        if "Model not fully initialized" in preview or "Missing components:" in preview:
            return fail(
                "blocked_model_uninitialized",
                "The free ACE-Step Space responded, but its model was not loaded on the provider. No paid fallback or unverified initialization call was attempted.",
                {"endpoint": "/generation_wrapper", "result_preview": preview},
            )
        return fail(
            "blocked_no_audio_file",
            "ACE-Step returned no verifiable audio; no upload or publication occurred.",
            {"endpoint": "/generation_wrapper", "result_preview": preview},
        )

    # A large file is not necessarily audio. Validate the returned media before
    # announcing even a preliminary result; musical approval still stays human-gated.
    try:
        probe_result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=codec_type", "-of", "json", str(target)],
            check=True, capture_output=True, text=True, timeout=60,
        )
        media_info = json.loads(probe_result.stdout)
        actual_duration = float(media_info.get("format", {}).get("duration", 0))
        has_audio = any(
            stream.get("codec_type") == "audio"
            for stream in media_info.get("streams", [])
        )
        if not has_audio or not math.isfinite(actual_duration) or not (
            0 < actual_duration and abs(actual_duration - duration) <= max(20, duration * 0.15)
        ):
            raise ValueError("No valid audio stream or duration outside expected range.")
        with target.open("rb") as handle:
            audio_sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        target.unlink(missing_ok=True)
        return fail(
            "blocked_invalid_audio",
            "ACE-Step returned an invalid or incomplete audio file; it was discarded.",
            {"error": str(exc)[:800]},
        )

    report = {
        "status": "generated_audio_needs_human_review",
        "title": brief.title,
        "category": brief.slug,
        "genre": genre or "jazz_soul",
        "genre_signature": GENRE_SIGNATURES.get(brief.slug, ""),
        "genre_authenticity_status": "PENDING_HUMAN_LISTENING",
        "file": str(target),
        "bytes": target.stat().st_size,
        "sha256": audio_sha256,
        "duration_actual_seconds": round(actual_duration, 3),
        "duration_requested_seconds": duration,
        "prompt": prompt,
        "negative_prompt": NEGATIVE,
        "engine": SPACE,
        "model": model,
        "editorial_verdict": "PENDING_HUMAN_LISTENING",
        "creative_approval": False,
        "eligible_for_video_assembly": False,
        "endpoint": "/generation_wrapper",
        "parameters": mapped,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rights_note": "ACE-Step repository code is Apache-2.0; ACE-Step/Ace-Step1.5 model weights are MIT. The official model card explicitly permits commercial use of generated music. It does not provide a separate, explicit Spotify/Apple Music distribution clause or guarantee copyrightability/uniqueness. Human listening and similarity review remain mandatory.",
        "model_card_url": "https://huggingface.co/ACE-Step/Ace-Step1.5",
        "code_license_url": "https://github.com/ace-step/ACE-Step/blob/main/LICENSE",
        "commercial_use_statement": "explicitly_allowed_by_model_card",
        "streaming_distribution_status": "not_explicitly_addressed",
        "rights_verified": False,
        "human_review_required": True,
        "publication_status": "NOT_PUBLISHED",
        "quality_gate": "MUST_IMPROVE_APPROVED_BASELINE",
        "baseline_reference": "Moonlit Coffeehouse / run 45646476397"
    }
    write_json(OUT / "production_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())

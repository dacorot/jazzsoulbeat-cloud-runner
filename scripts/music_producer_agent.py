#!/usr/bin/env python3
"""Free-only ACE-Step producer. Calls the verified Gradio generation endpoint."""
import json, os, shutil, sys
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("music-production")
AUDIO = OUT / "generated"
OUT.mkdir(exist_ok=True)
AUDIO.mkdir(exist_ok=True)
SPACE = os.getenv("ACE_STEP_SPACE", "ACE-Step/Ace-Step-v1.5")
# Start with a two-minute instrumental to maximize the chance of fitting free GPU quota.
DURATION = int(os.getenv("MUSIC_DURATION_SECONDS", "120"))
PROMPT = (
    "Original sophisticated contemporary jazz soul instrumental, 84 BPM, D minor. "
    "Expressive acoustic grand piano leads with a distinctive memorable melodic theme. "
    "Warm tenor saxophone answers the piano with emotional phrasing. Deep upright bass, "
    "brushed acoustic drums, subtle jazz guitar accents, rich extended jazz harmonies, "
    "elegant chord substitutions, organic live ensemble feel. Mature, cinematic, intimate "
    "midnight atmosphere. Beautiful melodic development, dynamic changes, carefully "
    "arranged introduction, memorable main theme, contrasting bridge, refined instrumental "
    "solo and natural musical ending. High fidelity professional studio recording. "
    "Entirely original melody and arrangement. No vocals, no samples, no recognizable "
    "existing melodies, no imitation of any named artist."
)
NEGATIVE = "copyrighted melody, cover, soundalike, artist imitation, childish, chiptune, low fidelity"

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
        from gradio_client import Client
        client = Client(SPACE, token=os.getenv("HF_TOKEN") or None, verbose=True)
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
        "selected_model": "acestep-v15-xl-turbo",
        "generation_mode": "custom",
        "simple_query_input": PROMPT,
        "simple_vocal_language": "unknown",
        "param_4": PROMPT,
        "param_5": "[Instrumental]",
        "param_6": 84,
        "param_7": "D minor",
        "param_8": "4",
        "param_9": "unknown",
        "param_10": 8,
        "param_12": True,
        "param_13": "-1",
        "param_15": DURATION,
        "param_16": 1,
        "param_23": "text2music",
        "param_30": "mp3",
        "param_32": True,
        "param_36": NEGATIVE,
        "param_43": False,
        "param_44": False,
    }
    values, mapped = [], {}
    for p in info.get("parameters", []):
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
        return fail("blocked_generation", "The correct ACE-Step generation endpoint was called but did not complete. No paid fallback was used.", {"endpoint": "/generation_wrapper", "error": str(e)[:1800], "parameters": mapped})

    found = []
    def walk(x):
        if isinstance(x, str):
            p = Path(x)
            if p.is_file():
                found.append(p)
            elif x.startswith(("http://", "https://")):
                found.append(x)
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x: walk(v)
    walk(result)

    target = None
    for item in found:
        try:
            if isinstance(item, Path):
                if item.stat().st_size > 100_000:
                    target = AUDIO / ("midnight_has_a_soul" + (item.suffix.lower() or ".mp3"))
                    shutil.copy2(item, target)
                    break
            else:
                from urllib.request import urlretrieve
                suffix = Path(item.split("?", 1)[0]).suffix or ".mp3"
                candidate = AUDIO / ("midnight_has_a_soul" + suffix)
                urlretrieve(item, candidate)
                if candidate.stat().st_size > 100_000:
                    target = candidate
                    break
        except Exception:
            continue

    if not target:
        return fail("blocked_no_audio_file", "ACE-Step returned from the generation endpoint, but no downloadable audio file could be verified.", {"endpoint": "/generation_wrapper", "result_preview": str(result)[:2500]})

    report = {
        "status": "generated_audio_needs_human_review",
        "title": "Midnight Has a Soul",
        "file": str(target),
        "bytes": target.stat().st_size,
        "duration_requested_seconds": DURATION,
        "prompt": PROMPT,
        "negative_prompt": NEGATIVE,
        "engine": SPACE,
        "model": "acestep-v15-xl-turbo",
        "endpoint": "/generation_wrapper",
        "parameters": mapped,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rights_note": "ACE-Step repository code is Apache-2.0; ACE-Step/Ace-Step1.5 model weights are MIT. The official model card explicitly permits commercial use of generated music. It does not provide a separate, explicit Spotify/Apple Music distribution clause or guarantee copyrightability/uniqueness. Human listening and similarity review remain mandatory.",
        "model_card_url": "https://huggingface.co/ACE-Step/Ace-Step1.5",
        "code_license_url": "https://github.com/ace-step/ACE-Step/blob/main/LICENSE",
        "commercial_use_statement": "explicitly_allowed_by_model_card",
        "streaming_distribution_status": "not_explicitly_addressed",
        "rights_verified": false,
        "human_review_required": true,
        "publication_status": "NOT_PUBLISHED"
    }
    write_json(OUT / "production_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())

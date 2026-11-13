#!/usr/bin/env python3
"""Cloud music producer for Jazz Soul Beat.
Uses only the public ACE-Step Hugging Face Space through Gradio's public API.
No paid API, no local GPU, no publishing. Fails closed if the Space/API is unavailable.
"""
import json, os, re, shutil, sys, time
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("music-production")
AUDIO = OUT / "generated"
OUT.mkdir(exist_ok=True)
AUDIO.mkdir(exist_ok=True)
SPACE = os.getenv("ACE_STEP_SPACE", "ACE-Step/Ace-Step-v1.5")
DURATION = int(os.getenv("MUSIC_DURATION_SECONDS", "180"))
MAX_WAIT = int(os.getenv("MUSIC_MAX_WAIT_SECONDS", "2400"))
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
    return 0 if status == "blocked_free_service" else 1

def param_name(p):
    return str(p.get("parameter_name") or p.get("label") or p.get("name") or "").lower()

def endpoint_list(api):
    eps = api.get("named_endpoints", {})
    if isinstance(eps, dict):
        return [(name, value) for name, value in eps.items()]
    return []

def main():
    try:
        from gradio_client import Client
    except Exception as e:
        return fail("blocked_dependency", "gradio_client could not be imported", {"error": str(e)})

    token = os.getenv("HF_TOKEN") or None
    try:
        client = Client(SPACE, token=token, verbose=True)
        api = client.view_api(return_format="dict")
    except Exception as e:
        return fail("blocked_free_service", "Could not connect to the public ACE-Step Space or inspect its API. No paid fallback was used.", {"error": str(e)[:1200]})

    write_json(OUT / "space_api_snapshot.json", api)
    candidates = []
    for name, info in endpoint_list(api):
        blob = (name + " " + str(info.get("description", ""))).lower()
        params = info.get("parameters", [])
        if any(k in blob for k in ("generate", "create", "music", "audio")) and params:
            candidates.append((name, info))
    if not candidates:
        return fail("blocked_api_changed", "The Space is reachable, but no supported music-generation endpoint was identified. API snapshot saved for diagnosis.", {"named_endpoints": list(api.get("named_endpoints", {}).keys()) if isinstance(api.get("named_endpoints"), dict) else []})

    # Prefer the endpoint whose name most clearly indicates music generation.
    candidates.sort(key=lambda x: (0 if "generate" in x[0].lower() else 1, 0 if "music" in x[0].lower() else 1))
    endpoint, info = candidates[0]
    params = info.get("parameters", [])
    values = []
    mapped = {}
    for p in params:
        name = param_name(p)
        default = p.get("parameter_default", p.get("default", None))
        value = default
        if any(k in name for k in ("prompt", "description", "caption", "style", "tag")):
            value = PROMPT
        elif "negative" in name:
            value = NEGATIVE
        elif any(k in name for k in ("lyrics", "lyric")):
            value = ""
        elif any(k in name for k in ("instrumental", "is_instrumental")):
            value = True
        elif any(k in name for k in ("duration", "length", "seconds")):
            value = DURATION
        elif "bpm" in name or "tempo" in name:
            value = 84
        elif any(k in name for k in ("keyscale", "key_scale", "tonality")):
            value = "D minor"
        elif "batch" in name or "num_samples" in name:
            value = 1
        elif "thinking" in name or "use_llm" in name:
            value = True
        elif "format" in name and isinstance(default, str):
            value = "wav" if "wav" in str(p) else default
        # Fail closed for required file/audio/reference inputs without defaults.
        ptype = str(p.get("parameter_type", {})).lower()
        if value is None and any(k in name for k in ("audio", "file", "reference", "upload")):
            return fail("blocked_required_input", "The generation endpoint requires a reference file or input the agent cannot safely invent.", {"endpoint": endpoint, "parameter": name})
        values.append(value)
        mapped[name or f"parameter_{len(values)}"] = value if isinstance(value, (str, int, float, bool, type(None))) else str(value)

    try:
        result = client.predict(*values, api_name=endpoint)
    except Exception as e:
        return fail("blocked_generation", "ACE-Step did not complete the generation request. No paid fallback was used.", {"endpoint": endpoint, "error": str(e)[:1600], "parameters": mapped})

    # Gradio returns local downloaded paths for audio/file outputs; search recursively.
    found = []
    def walk(x):
        if isinstance(x, str):
            if Path(x).is_file():
                found.append(Path(x))
            elif x.startswith("http://") or x.startswith("https://"):
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
                    target = AUDIO / ("midnight_has_a_soul" + item.suffix.lower())
                    shutil.copy2(item, target)
                    break
            else:
                from urllib.request import urlretrieve
                suffix = Path(item.split("?", 1)[0]).suffix or ".wav"
                candidate = AUDIO / ("midnight_has_a_soul" + suffix)
                urlretrieve(item, candidate)
                if candidate.stat().st_size > 100_000:
                    target = candidate
                    break
        except Exception:
            continue

    if not target:
        return fail("blocked_no_audio_file", "The Space returned a response, but no downloadable audio file could be verified.", {"endpoint": endpoint, "result_preview": str(result)[:2000]})

    report = {
        "status": "generated_audio_needs_human_review",
        "title": "Midnight Has a Soul",
        "file": str(target),
        "bytes": target.stat().st_size,
        "duration_requested_seconds": DURATION,
        "prompt": PROMPT,
        "negative_prompt": NEGATIVE,
        "engine": SPACE,
        "model_license_reference": "https://huggingface.co/spaces/ACE-Step/Ace-Step-v1.5",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "parameters": mapped,
        "rights_note": "Model code/weights are MIT per the model card. This does not guarantee output uniqueness or clear every third-party right. Check audio for similarity and retain generation records before commercial release.",
        "publication_status": "NOT_PUBLISHED"
    }
    write_json(OUT / "production_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())

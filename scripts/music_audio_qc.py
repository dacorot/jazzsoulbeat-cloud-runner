"""Conservative technical-only QC for model-generated Jazz Soul Beat audio.

This cannot judge jazz musicianship, phrasing, taste, or rights. A technical
PASS never authorizes video assembly, uploading, or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MIN_SONG_DURATION = 175.0
MAX_SONG_DURATION = 370.0

class AudioQualityError(ValueError):
    pass


def digest_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as source:
        for piece in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(piece)
    return sha.hexdigest()


def run_media_command(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout)


def verify_audio(report_path: Path) -> dict:
    report_path = Path(report_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise AudioQualityError("Production report must be a JSON object.")
    if report.get("status") != "generated_audio_needs_human_review":
        raise AudioQualityError("No successful model output with pending human review.")
    if report.get("rights_verified") is not False:
        raise AudioQualityError("Unexpected rights status: rights must remain unapproved.")
    if report.get("creative_approval") is not False or report.get("eligible_for_video_assembly") is not False:
        raise AudioQualityError("Model output cannot be creatively approved automatically.")
    if report.get("publication_status") != "NOT_PUBLISHED":
        raise AudioQualityError("Report has invalid publication state.")
    if not report.get("genre_signature"):
        raise AudioQualityError("Report is missing the explicit genre signature used for human comparison.")
    if report.get("genre_authenticity_status") != "PENDING_HUMAN_LISTENING":
        raise AudioQualityError("Genre authenticity must remain pending human listening.")

    # Input JSON is not trusted; ensure the audio is under the project staging directory.
    path = Path(report.get("file", ""))
    allowed_root = Path("music-production/generated").resolve()
    if not path.is_file() or path.is_symlink() or allowed_root not in path.resolve().parents:
        raise AudioQualityError("Audio must be a real regular file in the private staging directory.")
    if path.stat().st_size < 100_000:
        raise AudioQualityError("Audio is missing or suspiciously small.")
    checksum = digest_file(path)
    if report.get("sha256") != checksum:
        raise AudioQualityError("Audio SHA-256 differs from the producer manifest.")

    output = run_media_command([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,sample_rate,channels",
        "-of", "json", str(path),
    ], 45)
    media = json.loads(output.stdout)
    streams = media.get("streams", [])
    audio_streams = [x for x in streams if x.get("codec_type") == "audio"]
    if len(audio_streams) != 1 or len(streams) != 1:
        raise AudioQualityError("Expected one audio stream and no extra video or data streams.")
    sample_rate = int(audio_streams[0].get("sample_rate", 0))
    channels = int(audio_streams[0].get("channels", 0))
    duration = float(media.get("format", {}).get("duration", 0))
    if not math.isfinite(duration) or not MIN_SONG_DURATION <= duration <= MAX_SONG_DURATION:
        raise AudioQualityError(f"Invalid song duration: {duration!r}")
    if sample_rate < 22050 or channels not in (1, 2):
        raise AudioQualityError("Invalid sample rate or channel layout.")
    if abs(duration - float(report.get("duration_actual_seconds", 0))) > 1.0:
        raise AudioQualityError("Audio differs from probed duration in producer report.")

    analysis = run_media_command([
        "ffmpeg", "-nostdin", "-v", "info", "-i", str(path),
        "-map", "0:a:0", "-vn",
        "-af", "volumedetect,silencedetect=noise=-42dB:d=8",
        "-f", "null", "-",
    ], 180)
    text = analysis.stderr
    means = re.findall(r"mean_volume:\s*(-?[\d.]+) dB", text)
    maximum = re.findall(r"max_volume:\s*(-?[\d.]+) dB", text)
    if not means or not maximum:
        raise AudioQualityError("FFmpeg did not provide objective audio analysis.")
    mean_db = float(means[-1])
    peak_db = float(maximum[-1])
    if not -34.0 <= mean_db <= -8.0:
        raise AudioQualityError(f"Implausible average level {mean_db:.1f} dB.")
    if not -25.0 <= peak_db <= 1.0:
        raise AudioQualityError(f"Implausible peak level {peak_db:.1f} dB.")

    silence_starts = [float(x) for x in re.findall(r"silence_start:\s*([\d.]+)", text)]
    silence_ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", text)]
    max_silence = 0.0
    for i, start in enumerate(silence_starts):
        end = silence_ends[i] if i < len(silence_ends) else duration
        max_silence = max(max_silence, end - start)
    if max_silence > 15.0:
        raise AudioQualityError(f"Excessive extended silence: {max_silence:.1f}s.")

    return {
        "status": "PASS_TECHNICAL_AUDIO_ONLY",
        "sha256": checksum,
        "duration_seconds": round(duration, 3),
        "sample_rate": sample_rate,
        "channels": channels,
        "mean_level_db": mean_db,
        "peak_level_db": peak_db,
        "max_long_silence_seconds": round(max_silence, 3),
        "editorial_verdict": "PENDING_HUMAN_LISTENING",
        "genre": report.get("genre"),
        "genre_signature": report.get("genre_signature"),
        "genre_authenticity_status": "PENDING_HUMAN_LISTENING",
        "creative_approval": False,
        "rights_verified": False,
        "eligible_for_video_assembly": False,
        "youtube_upload": "NOT_ATTEMPTED",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=Path("music-production/production_report.json"))
    parser.add_argument("--output", type=Path, default=Path("music-production/TECHNICAL_AUDIO_QA.json"))
    args = parser.parse_args()
    try:
        outcome = verify_audio(args.report)
        success = True
    except (AudioQualityError, OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        outcome = {
            "status": "BLOCKED_TECHNICAL_QA",
            "error": str(exc)[:700],
            "creative_approval": False,
            "rights_verified": False,
            "eligible_for_video_assembly": False,
            "youtube_upload": "NOT_ATTEMPTED",
        }
        success = False
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in outcome.items() if k != "error"}, ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Independent post-download audit for review-only audio staging.

Fails closed on missing files, hash drift, non-audio payloads, unreadable
containers, duplicate hashes, or invalid download provenance. It never
changes rights, approval, library, or publication state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse

AUDIO_MAGIC = (b"ID3", b"OggS", b"fLaC", b"RIFF")
ALLOWED_SUFFIXES = {".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aiff"}
MAX_BYTES = 30_000_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ffprobe(path: Path) -> dict:
    command = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=format_name,duration",
        "-of", "json", str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return {"error": result.stderr.strip()[:240] or "ffprobe_failed"}
    try:
        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        duration = float(fmt.get("duration", 0) or 0)
        return {"format_name": str(fmt.get("format_name", "")), "duration_seconds": duration}
    except (ValueError, TypeError, json.JSONDecodeError):
        return {"error": "ffprobe_invalid_json"}


def audit(manifest_path: Path, output_dir: Path, require_nonzero: bool = False) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    downloaded = manifest.get("downloaded", [])
    errors = []
    warnings = []
    audited = []
    seen_hashes = {}

    if require_nonzero and not downloaded:
        errors.append("no_valid_audio_downloaded")

    for index, item in enumerate(downloaded, start=1):
        relative = Path(str(item.get("file", "")))
        path = output_dir / relative.name
        row = {"index": index, "file": str(path), "status": "PASS"}
        if not path.is_file():
            row["status"] = "FAIL"
            row["error"] = "file_missing"
            errors.append(f"{path.name}:file_missing")
            audited.append(row)
            continue
        size = path.stat().st_size
        row["bytes"] = size
        if size <= 1024 or size > MAX_BYTES:
            row["status"] = "FAIL"
            row["error"] = "invalid_size"
            errors.append(f"{path.name}:invalid_size")
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            row["status"] = "FAIL"
            row["error"] = "invalid_extension"
            errors.append(f"{path.name}:invalid_extension")
        with path.open("rb") as handle:
            prefix = handle.read(16)
        if not prefix.startswith(AUDIO_MAGIC):
            row["status"] = "FAIL"
            row["error"] = "audio_signature_missing"
            errors.append(f"{path.name}:audio_signature_missing")
        digest = sha256(path)
        row["sha256"] = digest
        if digest != str(item.get("sha256", "")):
            row["status"] = "FAIL"
            row["error"] = "sha256_mismatch"
            errors.append(f"{path.name}:sha256_mismatch")
        if digest in seen_hashes:
            row["status"] = "FAIL"
            row["error"] = "duplicate_sha256"
            errors.append(f"{path.name}:duplicate_sha256:{seen_hashes[digest]}")
        seen_hashes[digest] = path.name
        probe = ffprobe(path)
        row.update(probe)
        if probe.get("error") or not probe.get("format_name") or probe.get("duration_seconds", 0) <= 0:
            row["status"] = "FAIL"
            errors.append(f"{path.name}:unreadable_audio")
        url = str(item.get("download_url", ""))
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            row["status"] = "FAIL"
            errors.append(f"{path.name}:invalid_download_provenance")
        audited.append(row)

    report = {
        "status": "PASS" if not errors else "FAIL",
        "manifest": str(manifest_path),
        "downloaded_count": len(downloaded),
        "audited_count": len(audited),
        "passed_count": sum(row["status"] == "PASS" for row in audited),
        "failed_count": sum(row["status"] == "FAIL" for row in audited),
        "errors": errors,
        "warnings": warnings,
        "approval_mutated": False,
        "rights_verified": False,
        "publication": "DISABLED",
        "files": audited,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--require-nonzero", action="store_true")
    args = parser.parse_args()
    report = audit(args.manifest, args.output, args.require_nonzero)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "status", "downloaded_count", "audited_count", "passed_count",
        "failed_count", "approval_mutated", "rights_verified", "publication",
    )}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

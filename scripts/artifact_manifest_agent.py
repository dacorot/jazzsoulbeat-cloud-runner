#!/usr/bin/env python3
"""Create a hash-bound manifest for one validated production artifact folder."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = ("video.mp4", "mix.mp3", "thumb.jpg", "description.txt", "MUSIC_SOURCE.txt")


def manifest(run_dir: Path) -> dict:
    if not run_dir.is_dir():
        raise ValueError("production_run_directory_required")
    files = {}
    for name in REQUIRED:
        path = run_dir / name
        if not path.is_file() or path.stat().st_size <= 0:
            raise ValueError(f"required_artifact_missing:{name}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        files[name] = {"sha256": digest.hexdigest(), "bytes": path.stat().st_size}
    return {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_dir": str(run_dir),
        "artifact_set_sha256": hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest(),
        "files": files,
        "publication": "NOT_AUTHORIZED_BY_THIS_MANIFEST",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = manifest(args.run_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["artifact_set_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

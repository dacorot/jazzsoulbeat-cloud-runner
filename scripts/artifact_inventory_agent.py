"""Build a searchable, non-destructive inventory of project artifacts."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

IMAGE = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
AUDIO = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aiff", ".aif"}
VIDEO = {".mp4", ".mov", ".mkv", ".webm"}
MANIFEST = {".json", ".csv", ".yaml", ".yml"}
SECRET_NAMES = {"token.json", "drive_token.json", "client_secret.json", ".env"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(path: Path) -> tuple[str, str]:
    text = path.as_posix()
    suffix = path.suffix.lower()
    if path.name in SECRET_NAMES or path.name.endswith(".pem"):
        return "secret_excluded", "excluded"
    if "/__pycache__/" in f"/{text}" or "/.venv/" in f"/{text}" or "/.git/" in f"/{text}":
        return "runtime_excluded", "excluded"
    if "visual-rejected" in text:
        return "video", "rejected"
    if "approved-style-samples" in text:
        return "visual", "reference_approved"
    if "candidate_scenes" in text:
        return "visual", "candidate_pending_qa"
    if "/motion/" in f"/{text}" or "/motion/" in f"/{text}":
        return "visual", "motion_pending_qa"
    if "tracks/review/" in text:
        return "audio", "rights_pending"
    if "tracks/seasonal/" in text:
        return "audio", "seasonal_manifest_or_audio"
    if text.startswith("tracks/"):
        return "audio", "active_or_manifest"
    if text.startswith("output/") or text.startswith("music-production/"):
        return ("video", "render_or_review") if suffix in VIDEO else ("evidence", "report_or_manifest")
    if suffix in IMAGE:
        return "visual", "unclassified_image"
    if suffix in AUDIO:
        return "audio", "unclassified_audio"
    if suffix in VIDEO:
        return "video", "unclassified_video"
    if suffix in MANIFEST:
        return "evidence", "manifest"
    if suffix in {".py", ".md", ".txt"} or text.startswith(".github/"):
        return "code", "active"
    return "other", "unclassified"


def build(root: Path, output: Path) -> dict:
    items = []
    counts = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        domain, state = classify(path)
        rel = path.relative_to(root).as_posix()
        row = {"path": rel, "domain": domain, "state": state, "bytes": path.stat().st_size}
        if domain == "secret_excluded":
            row["hash"] = "EXCLUDED"
        elif path.stat().st_size <= 512 * 1024 * 1024:
            row["sha256"] = sha256(path)
        else:
            row["sha256"] = "SKIPPED_LARGE_FILE"
        items.append(row)
        key = f"{domain}:{state}"
        counts[key] = counts.get(key, 0) + 1
    report = {
        "schema_version": 1,
        "agent_id": "artifact_inventory_agent",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(root),
        "policy": "non_destructive_index_only",
        "counts": counts,
        "files": items,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    report = build(Path.cwd(), Path("output/asset-inventory/canonical-index.json"))
    print(json.dumps({"files": len(report["files"]), "counts": report["counts"]}, ensure_ascii=False))

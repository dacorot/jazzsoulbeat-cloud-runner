#!/usr/bin/env python3
"""Weekly, read-only copyright and license change watcher.

The watcher scans text manifests for source/license URLs, records a baseline
hash for each HTTPS evidence page, and flags changes or failures for review.
It never changes approval flags and never deletes files automatically.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".html", ".htm"}
URL_KEYS = {"source_url", "license_url", "license_evidence_url", "evidence_url", "rights_evidence_url"}
LICENSE_KEYS = {"license", "license_name", "license_url", "license_permission_status", "copyright_status"}
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
USER_AGENT = "JazzSoulBeatCopyrightWatch/1.0 (read-only weekly audit)"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _walk_values(value: Any, path: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield child_path, child
            yield from _walk_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, child
            yield from _walk_values(child, child_path)


def _read_records(path: Path) -> list[dict[str, Any]]:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return []
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return []
    records: list[dict[str, Any]] = []
    if path.suffix.lower() == ".csv":
        try:
            rows = list(csv.DictReader(text.splitlines()))
        except csv.Error:
            rows = []
        for index, row in enumerate(rows):
            records.append({"file": str(path), "record": f"row:{index + 2}", "values": row})
        return records
    if path.suffix.lower() == ".json":
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return []
        for record_path, child in _walk_values(value):
            if isinstance(child, dict):
                records.append({"file": str(path), "record": record_path or "root", "values": child})
        if isinstance(value, dict):
            records.append({"file": str(path), "record": "root", "values": value})
        return records
    lowered = text.casefold()
    if any(term in lowered for term in ("license", "copyright", "rights", "source_url")):
        records.append({"file": str(path), "record": "text", "values": {"text": text}})
    return records


def _extract_urls(values: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for key, value in values.items():
        if key.casefold() in URL_KEYS and isinstance(value, str):
            candidate = value.strip()
            if candidate and candidate not in urls:
                urls.append(candidate)
    return urls


def _license_text(values: dict[str, Any]) -> str:
    parts = []
    for key, value in values.items():
        if key.casefold() in LICENSE_KEYS and isinstance(value, str):
            parts.append(value)
    return " | ".join(parts)


def classify_license_text(text: str) -> str:
    value = text.casefold()
    if "all rights reserved" in value or "non-commercial" in value or "no commercial" in value:
        return "RESTRICTIVE_OR_NONCOMMERCIAL"
    if "cc0" in value or "creative commons zero" in value:
        return "CC0_EVIDENCE_PRESENT"
    if "cc by" in value or "creativecommons.org/licenses/by/" in value:
        return "CC_BY_EVIDENCE_PRESENT"
    return "LICENSE_NOT_IDENTIFIED"


def fetch_evidence(url: str) -> tuple[str, str, int]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.hostname.casefold() in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("evidence_url_must_be_public_https")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(MAX_RESPONSE_BYTES + 1)
        if len(data) > MAX_RESPONSE_BYTES:
            raise ValueError("evidence_response_too_large")
        content_type = response.headers.get_content_type()
        return _sha256(data), data.decode("utf-8", errors="replace"), response.status


def _decision(status: str, license_class: str) -> str:
    if status in {"SOURCE_CHANGED_REVIEW_REQUIRED", "SOURCE_UNREACHABLE_REVIEW_REQUIRED"}:
        return "REMOVE_FROM_ACTIVE_CATALOG_PENDING_CONFIRMATION"
    if license_class == "RESTRICTIVE_OR_NONCOMMERCIAL":
        return "REMOVE_FROM_ACTIVE_CATALOG_PENDING_CONFIRMATION"
    if status == "MISSING_EVIDENCE_REVIEW_REQUIRED":
        return "REVIEW_REQUIRED"
    return "KEEP_PENDING_NEXT_WEEKLY_CHECK"


def audit(roots: list[Path], state_path: Path, report_path: Path) -> dict[str, Any]:
    files = sorted({path for root in roots if root.exists() for path in root.rglob("*") if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and "copyright-watch" not in path.parts})
    previous: dict[str, Any] = {}
    if state_path.is_file():
        try:
            previous = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
    previous_sources = previous.get("sources", {}) if isinstance(previous, dict) else {}
    candidates: dict[str, dict[str, Any]] = {}
    for path in files:
        for record in _read_records(path):
            values = record["values"]
            if not isinstance(values, dict):
                continue
            urls = _extract_urls(values)
            if not urls and "text" not in values:
                continue
            license_hint = _license_text(values)
            for url in urls or [f"local:{record['file']}#{record['record']}"]:
                item = candidates.setdefault(url, {"source_url": url, "references": [], "license_hints": []})
                item["references"].append({"file": record["file"], "record": record["record"]})
                if license_hint and license_hint not in item["license_hints"]:
                    item["license_hints"].append(license_hint)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    next_state: dict[str, Any] = {"schema_version": 1, "checked_at": now, "sources": {}}
    rows: list[dict[str, Any]] = []
    for url in sorted(candidates):
        item = candidates[url]
        prior = previous_sources.get(url, {}) if isinstance(previous_sources, dict) else {}
        row = {**item, "checked_at": now, "http_status": None, "evidence_sha256": None, "license_class": classify_license_text(" ".join(item["license_hints"])), "status": "", "decision": ""}
        if url.startswith("local:"):
            row["status"] = "MISSING_EVIDENCE_REVIEW_REQUIRED"
        else:
            try:
                digest, body, http_status = fetch_evidence(url)
                row.update({"http_status": http_status, "evidence_sha256": digest, "license_class": classify_license_text(body + " " + " ".join(item["license_hints"]))})
                row["status"] = "SOURCE_CHANGED_REVIEW_REQUIRED" if prior.get("evidence_sha256") and prior.get("evidence_sha256") != digest else ("BASELINE_RECORDED" if not prior else "UNCHANGED")
            except (OSError, ValueError, urllib.error.URLError, urllib.error.HTTPError) as exc:
                row.update({"status": "SOURCE_UNREACHABLE_REVIEW_REQUIRED", "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
        row["decision"] = _decision(row["status"], row["license_class"])
        next_state["sources"][url] = {"evidence_sha256": row["evidence_sha256"], "license_class": row["license_class"], "checked_at": now}
        rows.append(row)
    summary = {}
    for row in rows:
        summary[row["status"]] = summary.get(row["status"], 0) + 1
    report = {"schema_version": 1, "agent": "copyright_watch_agent", "mode": "READ_ONLY", "checked_at": now, "roots": [str(root) for root in roots], "summary": summary, "policy": {"automatic_deletion": False, "automatic_rights_approval": False, "changed_or_unreachable": "remove from active catalog pending confirmation", "evidence_retention": "keep until reviewed"}, "records": rows}
    state_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(next_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.root, args.state, args.report)
    print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

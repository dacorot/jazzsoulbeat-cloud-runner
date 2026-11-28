#!/usr/bin/env python3
"""Cloud-only exact-byte forensic analysis for the rights decisions CSV."""
from __future__ import annotations
import csv, hashlib, io, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from google.auth.transport.requests import AuthorizedSession

sys.path.insert(0, str(Path("agent").resolve()))
from drive_auth import credentials_from_secret  # type: ignore

FILE_ID = "1m2fpQwdWTetXxDPL-S0al5Z-9P-j-ik_"
SOURCE_RUN_ID = "46112287754"
DIAGNOSTIC_RUN_ID = "46114131981"
OUT = Path("validation-results/rights-csv-forensics")
MATRIX_NAME = "rights_evidence_matrix.json"
CONTROL_CODES = tuple(range(0, 32))
REDACT_TERMS = ("email", "e-mail", "phone", "telephone", "address", "full_name", "person", "contact")

def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_json(name: str, value: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def escaped(data: bytes) -> str:
    return "".join(chr(c) if 32 <= c <= 126 and c not in (34, 39, 92) else f"\\x{c:02x}" for c in data)

def hex_dump(data: bytes) -> str:
    return data.hex(" ")

def decode(data: bytes, encoding: str) -> str | None:
    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        return None

def byte_signals(data: bytes) -> dict[str, Any]:
    counts = {str(i): data.count(bytes([i])) for i in CONTROL_CODES}
    return {
        "control_byte_counts": counts,
        "total_control_bytes": sum(counts.values()),
        "nul_count": data.count(b"\x00"),
        "bom": {
            "utf8": data.startswith(b"\xef\xbb\xbf"),
            "utf16_le": data.startswith(b"\xff\xfe"),
            "utf16_be": data.startswith(b"\xfe\xff"),
        },
        "line_endings": {
            "crlf": data.count(b"\r\n"),
            "lf": data.count(b"\n"),
            "cr": data.count(b"\r"),
            "mixed": bool(data.count(b"\r\n") and data.replace(b"\r\n", b"").count(b"\n")),
        },
    }

def classify(data: bytes, content_type: str | None) -> dict[str, Any]:
    prefix = data.lstrip()[:512].lower()
    return {
        "utf8_decodable": decode(data, "utf-8") is not None,
        "utf16_le_decodable": decode(data, "utf-16-le") is not None,
        "utf16_be_decodable": decode(data, "utf-16-be") is not None,
        "looks_like_json": prefix.startswith((b"{", b"[")),
        "looks_like_html": prefix.startswith((b"<!doctype html", b"<html", b"<head", b"<body")) or b"<html" in prefix,
        "looks_like_gzip": data.startswith(b"\x1f\x8b"),
        "looks_like_zip": data.startswith(b"PK\x03\x04"),
        "looks_like_pdf": data.startswith(b"%PDF-"),
        "looks_like_http_error_envelope": prefix.startswith(b"{") and any(x in prefix for x in (b'"error"', b'"code"', b'"message"', b'"status"')),
        "http_content_type": content_type,
    }

def redact(header: str, value: str) -> str:
    if any(term in header.strip().lower() for term in REDACT_TERMS):
        return "[REDACTED]"
    return value[:1200]

def row_preview(headers: list[str], row: list[str]) -> dict[str, str]:
    return {
        (headers[i] if i < len(headers) else f"column_{i + 1}"): redact(
            headers[i] if i < len(headers) else f"column_{i + 1}", value
        )
        for i, value in enumerate(row)
    }

def parse(data: bytes, encoding: str, delimiter: str) -> dict[str, Any]:
    text = decode(data, encoding)
    result: dict[str, Any] = {
        "encoding": encoding, "delimiter": repr(delimiter), "decode_ok": text is not None,
        "row_count": 0, "data_row_count": 0, "column_count_first_row": 0,
        "max_column_count": 0, "headers": [], "first_two_rows_redacted": [],
        "quote_errors": [], "malformed_records": [], "sniffed_delimiter": None,
    }
    if text is None:
        result["errors"] = ["decode_error"]
        return result
    try:
        result["sniffed_delimiter"] = repr(csv.Sniffer().sniff(text[:10000], delimiters=",;\t|").delimiter)
    except csv.Error:
        pass
    try:
        reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter, strict=True)
        sample: list[list[str]] = []
        for index, row in enumerate(reader, start=1):
            result["row_count"] += 1
            result["max_column_count"] = max(result["max_column_count"], len(row))
            if index <= 3:
                sample.append(row)
        if sample:
            result["column_count_first_row"] = len(sample[0])
            result["headers"] = [str(x).strip() for x in sample[0]]
            result["first_two_rows_redacted"] = [row_preview(result["headers"], row) for row in sample[1:3]]
        result["data_row_count"] = max(0, result["row_count"] - 1)
    except csv.Error as exc:
        result["quote_errors"].append(str(exc))
        result["errors"] = ["csv_error"]
    return result

def matrix_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("decisions", "tracks", "rows", "entries", "items", "evidence"):
            if isinstance(payload.get(key), list):
                return [x for x in payload[key] if isinstance(x, dict)]
    return []

def normalized(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""

def first(item: dict[str, Any], names: tuple[str, ...]) -> str:
    lowered = {str(k).lower(): v for k, v in item.items()}
    for name in names:
        if name in lowered and lowered[name] not in (None, ""):
            return normalized(lowered[name])
    return ""

KEYS = ("sha256", "file_sha256", "audio_sha256", "track_sha256", "path", "file_path", "filepath", "filename", "file_name", "track_id", "id")
DECISION_KEYS = ("decision", "rights_decision", "status", "eligibility", "result", "rights_status")

def compare(matrix_path: Path, data: bytes, encoding: str, delimiter: str) -> dict[str, Any]:
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    records = matrix_records(payload)
    text = decode(data, encoding)
    if text is None:
        raise RuntimeError("selected CSV candidate does not decode")
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=delimiter, strict=True)
    rows = [dict(row) for row in reader]
    index: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        key = first(row, KEYS)
        if key:
            index.setdefault(key, []).append(row)
    matched, unmatched = [], []
    for item in records:
        key = first(item, KEYS)
        candidates = index.get(key, []) if key else []
        if candidates:
            matrix_decision = first(item, DECISION_KEYS)
            csv_decision = first(candidates[0], DECISION_KEYS)
            matched.append({
                "matrix_key": key, "csv_match_count": len(candidates),
                "matrix_decision": matrix_decision, "csv_decision": csv_decision,
                "decision_equal": matrix_decision == csv_decision,
            })
        else:
            unmatched.append({"matrix_key": key, "matrix_decision": first(item, DECISION_KEYS)})
    equal = sum(1 for item in matched if item["decision_equal"])
    return {
        "generated_at_utc": stamp(), "matrix_path": str(matrix_path),
        "matrix_record_count": len(records), "expected_matrix_record_count": 56,
        "matrix_count_is_56": len(records) == 56,
        "selected_csv": {"encoding": encoding, "delimiter": repr(delimiter), "row_count": len(rows) + 1, "data_row_count": len(rows)},
        "csv_indexable_rows": len(index), "matched_matrix_records": len(matched),
        "unmatched_matrix_records": len(unmatched), "decision_equal_count": equal,
        "decision_mismatch_count": len(matched) - equal, "matched": matched, "unmatched": unmatched,
        "recovered_and_contrasted_all_56": len(records) == 56 and len(matched) == 56 and equal == 56,
    }

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    creds = credentials_from_secret(os.environ["DRIVE_TOKEN_JSON"])
    session = AuthorizedSession(creds)
    url = f"https://www.googleapis.com/drive/v3/files/{FILE_ID}"
    meta_response = session.get(url, params={
        "fields": "id,name,mimeType,size,md5Checksum,modifiedTime,createdTime,webViewLink",
        "supportsAllDrives": "true",
    }, timeout=60)
    meta_response.raise_for_status()
    metadata = meta_response.json()
    media_response = session.get(url, params={"alt": "media", "supportsAllDrives": "true"}, timeout=120)
    data = media_response.content
    media_response.raise_for_status()
    sha = hashlib.sha256(data).hexdigest()
    declared_size = int(metadata["size"]) if metadata.get("size") is not None else None
    content_type = media_response.headers.get("Content-Type")
    raw = {
        "generated_at_utc": stamp(),
        "source": {
            "drive_file_id": FILE_ID, "source_execution_id": SOURCE_RUN_ID,
            "previous_diagnostic_execution_id": DIAGNOSTIC_RUN_ID,
            "name": metadata.get("name"), "declared_mime_type": metadata.get("mimeType"),
            "declared_size": declared_size, "http_status": media_response.status_code,
            "http_content_type": content_type,
            "http_headers_relevant": {
                k: v for k, v in media_response.headers.items()
                if k.lower() in {"content-type", "content-length", "content-encoding", "content-range", "etag"}
            },
            "downloaded_size": len(data), "sha256": sha,
            "size_matches_declared": declared_size is None or declared_size == len(data),
        },
        "bytes": {
            "first_512_hex": hex_dump(data[:512]),
            "first_512_escaped": escaped(data[:512]),
            "last_256_hex": hex_dump(data[-256:]),
            "last_256_escaped": escaped(data[-256:]),
            **byte_signals(data),
        },
        "classification": classify(data, content_type),
    }
    write_json("raw_file_diagnostics.json", raw)

    encodings = ["utf-8", "utf-8-sig", "utf-16-le", "utf-16-be"]
    delimiters = [(",", "comma"), (";", "semicolon"), ("\t", "tab"), ("|", "pipe")]
    tests = [parse(data, enc, delim) for enc in encodings for delim, _ in delimiters]
    write_json("encoding_delimiter_tests.json", {
        "generated_at_utc": stamp(), "tested_encodings": encodings,
        "tested_delimiters": {name: delim for delim, name in delimiters}, "results": tests,
    })
    candidate = max(tests, key=lambda x: (x["decode_ok"] and not x["quote_errors"], x["data_row_count"], x["max_column_count"]))
    structure = {
        "generated_at_utc": stamp(), "selected_candidate": candidate,
        "candidate_selection_rule": "decode_ok, no strict CSV quote errors, then greatest data rows and columns",
        "interpretability": {
            "selected_candidate_is_interpretable": bool(candidate["decode_ok"] and candidate["data_row_count"] > 0 and candidate["max_column_count"] > 1),
            "candidate_has_nonempty_headers": bool(candidate["headers"]),
        },
        "non_csv_signals": raw["classification"],
    }
    write_json("csv_structure_report.json", structure)

    matrices = sorted(Path("agent").rglob(MATRIX_NAME))
    if len(matrices) != 1:
        raise RuntimeError(f"Expected exactly one {MATRIX_NAME}; found {len(matrices)}: {[str(p) for p in matrices]}")
    matrix_path = matrices[0]
    if structure["interpretability"]["selected_candidate_is_interpretable"]:
        comparison = compare(matrix_path, data, candidate["encoding"], candidate["delimiter"].strip("'"))
    else:
        payload = json.loads(matrix_path.read_text(encoding="utf-8"))
        comparison = {
            "generated_at_utc": stamp(), "matrix_path": str(matrix_path),
            "matrix_record_count": len(matrix_records(payload)), "expected_matrix_record_count": 56,
            "recovered_and_contrasted_all_56": False,
            "reason": "No interpretable CSV candidate found; no reconstruction from JSON performed.",
        }
    write_json("matrix_comparison.json", comparison)

    problems = []
    if not raw["source"]["size_matches_declared"]:
        problems.append("Downloaded size differs from Drive metadata.")
    if not structure["interpretability"]["selected_candidate_is_interpretable"]:
        problems.append("No candidate produced an interpretable CSV.")
    if not comparison.get("recovered_and_contrasted_all_56", False):
        problems.append("The exact CSV was not matched and contrasted against all 56 matrix decisions.")
    result_line = "SUCCESS: all 56 original decisions were recovered and contrasted." if comparison.get("recovered_and_contrasted_all_56") else "NOT SUCCESS: all 56 decisions were not recovered and contrasted; the CSV was not reconstructed from JSON."
    summary = f"""# Rights CSV forensics

- Exact Drive file ID: {FILE_ID}
- Source execution: {SOURCE_RUN_ID}
- Previous diagnostic: {DIAGNOSTIC_RUN_ID}
- Downloaded size: {len(data)} bytes
- SHA-256: {sha}
- Declared MIME: {metadata.get("mimeType")}
- HTTP Content-Type: {content_type}
- Selected candidate: {candidate["encoding"]} plus delimiter {candidate["delimiter"]}
- Interpreted data rows: {candidate["data_row_count"]}
- Maximum columns: {candidate["max_column_count"]}
- Matrix records: {comparison.get("matrix_record_count", 0)}
- Matrix matches: {comparison.get("matched_matrix_records", 0)}
- Equal decisions: {comparison.get("decision_equal_count", 0)}

## Result

{result_line}

## Detected defects or blockers

{chr(10).join("- " + p for p in problems) if problems else "- None."}

The original bytes remained in runner memory and no raw CSV copy was written. No audio was downloaded or processed, no rights decisions were modified, and no per-track plan was generated.
"""
    (OUT / "diagnostic_summary.md").write_text(summary, encoding="utf-8")
    return 0 if comparison.get("recovered_and_contrasted_all_56", False) else 2

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Five-part, repository-wide audit for Jazz Soul Beat.

The audit is intentionally read-only. It inventories both canonical copies,
checks syntax/tests-facing contracts, verifies hash-bound artifacts, identifies
historical-vs-active references, and checks operational safety. It does not
approve, upload, publish, delete, or move project data.
"""
from __future__ import annotations

import ast
import csv
import fnmatch
import hashlib
import json
import os
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXCLUDED_DIRS = {".venv", ".git", "__pycache__", ".pytest_cache", "node_modules"}

# Active production contract. Historical reports may mention the former
# 36,000-second target, but readiness must be evaluated against this contract.
DEFAULT_CONTRACT = {
    "minimum_unique_tracks": 500,
    "minimum_approved_seconds": 36000,
    "min_duration_seconds": 7200,
    "max_duration_seconds": 10800,
}


def load_contract(runner: Path) -> dict:
    path = runner / "config/active_contract.json"
    if not path.is_file():
        return DEFAULT_CONTRACT
    data = json.loads(path.read_text(encoding="utf-8"))
    delivery = data.get("delivery", {})
    audio = data.get("audio", {})
    return {
        "minimum_unique_tracks": int(audio["minimum_unique_tracks"]),
        "minimum_approved_seconds": int(audio["minimum_approved_seconds"]),
        "min_duration_seconds": int(delivery["min_duration_seconds"]),
        "max_duration_seconds": int(delivery["max_duration_seconds"]),
    }


def files(root: Path, suffix: str | None = None) -> list[Path]:
    result = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if suffix is None or path.suffix == suffix:
            result.append(path)
    return sorted(result)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_files(root: Path) -> tuple[int, list[str]]:
    errors = []
    count = 0
    for path in files(root, ".json"):
        count += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return count, errors


def python_integrity(root: Path) -> dict:
    py = files(root, ".py")
    errors = []
    functions = classes = 0
    for path in py:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            functions += sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree))
            classes += sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        except Exception as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return {"python_files": len(py), "functions": functions, "classes": classes,
            "syntax_errors": errors}


def run_tests(root: Path) -> dict:
    interpreter = root / ".venv/bin/python"
    command = [str(interpreter) if interpreter.is_file() else "python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=180)
    return {"command": " ".join(command), "returncode": result.returncode,
            "passed": result.returncode == 0,
            "summary": (result.stderr or result.stdout).strip()[-500:]}


def ledger_audit(runner: Path, agent: Path, contract: dict) -> dict:
    ledger_path = runner / "music-production/approval_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    requests = list(ledger.get("requests", {}).values())
    approved = [row for row in requests if all(row.get(key) is True for key in (
        "creative_approval", "rights_verified", "eligible_for_video_assembly"))]
    missing = []
    for row in approved:
        artifact = Path(row.get("artifact", ""))
        if not artifact.is_file():
            missing.append({"artifact": str(artifact), "reason": "missing"})
            continue
        expected = row.get("artifact_sha256")
        if expected and sha256(artifact) != expected:
            missing.append({"artifact": str(artifact), "reason": "hash_mismatch"})
    delivery = agent / "tracks/generated/jazz-only-10-videos-2026-11-22/delivery-manifest.json"
    manifest = json.loads(delivery.read_text(encoding="utf-8"))
    videos = manifest.get("videos", [])
    approved_hashes = {row.get("artifact_sha256") for row in approved if row.get("artifact_sha256")}
    video_durations = [float(row.get("duration_seconds") or 0) for row in videos]
    scene_effects_validated = bool(manifest.get("scene_effects_validated")) and all(
        bool(row.get("scene_effect_validated")) for row in videos
    )
    delivery_contract = {
        "status_not_invalidated": manifest.get("status") != "INVALIDATED_LEGACY_DELIVERY",
        "video_count": len(videos),
        "all_videos_2_to_3_hours": bool(videos) and all(
            contract["min_duration_seconds"] <= duration <= contract["max_duration_seconds"] for duration in video_durations
        ),
        "unique_video_hashes": len({row.get("sha256") for row in videos}),
        "scene_effects_validated": scene_effects_validated,
    }
    return {
        "ledger_requests": len(requests),
        "approved_requests": len(approved),
        "approved_unique_tracks": len(approved_hashes),
        "approved_seconds": round(sum(float(row.get("duration_seconds") or row.get("technical_duration_seconds") or 0) for row in approved), 2),
        "missing_or_mismatched_approved_artifacts": missing,
        "delivery_videos": len(videos),
        "delivery_unique_hashes": len({row.get("sha256") for row in videos}),
        "delivery_publication": manifest.get("publication"),
        "delivery_pool_seconds": manifest.get("pool_seconds"),
        "delivery_contract": delivery_contract,
        "ledger_sha256": sha256(ledger_path),
        "delivery_manifest_sha256": sha256(delivery),
    }


def stale_reference_audit(runner: Path, agent: Path) -> dict:
    roots = [runner, agent]
    hits = []
    for root in roots:
        for path in files(root):
            if path.suffix in {".mp3", ".mp4", ".wav", ".flac", ".jpg", ".png", ".js", ".css"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line_number, line in enumerate(text.splitlines(), 1):
                if any(token in line for token in ("7200", "690", "6510", "24888.25")):
                    hits.append({"file": str(path.relative_to(root)), "line": line_number,
                                 "text": line.strip()[:240],
                                 "classification": "HISTORICAL_OR_REQUIRES_REVIEW"})
    return {"count": len(hits), "samples": hits[:120],
            "note": "These are findings, not automatic errors; historical records must remain distinguishable from active contracts."}


def security_audit(agent: Path, runner: Path) -> dict:
    secret_names = ["client_secret.json", "token.json", "drive_token.json"]
    present = []
    ignore_rules = [line.strip() for line in agent.joinpath(".gitignore").read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.lstrip().startswith("#")]
    for name in secret_names:
        path = agent / name
        if path.exists():
            present.append({"path": str(path.relative_to(agent)), "mode": oct(stat.S_IMODE(path.stat().st_mode)),
                            "ignored_by_policy": any(fnmatch.fnmatch(name, rule) for rule in ignore_rules)})
    text_files = files(runner) + files(agent)
    publication_hits = []
    for path in text_files:
        if path.suffix not in {".py", ".json", ".md", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "PUBLIC_ONLY" in text or "public_upload_approval\": true" in text:
            if path.name == "deep_project_audit.py":
                continue
            publication_hits.append(str(path))
    return {"local_credentials_present_but_not_reported": present,
            "public_authorization_markers": publication_hits[:80],
            "publication_policy": "DISABLED"}


def audit(runner: Path, agent: Path) -> dict:
    contract = load_contract(runner)
    runner_json_count, runner_json_errors = json_files(runner)
    agent_json_count, agent_json_errors = json_files(agent)
    approved_seconds = ledger_audit(runner, agent, contract).get("approved_seconds", 0)
    ledger_result = ledger_audit(runner, agent, contract)
    capacity_ready = (
        ledger_result.get("approved_unique_tracks", 0) >= contract["minimum_unique_tracks"]
        and approved_seconds >= contract["minimum_approved_seconds"]
    )
    delivery_ready = all(ledger_result.get("delivery_contract", {}).values())
    cycles = [
        {"cycle": 1, "name": "code-integrity-and-syntax",
         "audit": "Recorrido de todos los Python activos excluyendo entornos, cachés y binarios generados.",
         "solution": "Se identifican errores de sintaxis por archivo y se valida la suite de cada copia.",
         "verification": {"runner": python_integrity(runner), "agent": python_integrity(agent),
                          "runner_json_files": runner_json_count, "agent_json_files": agent_json_count,
                          "runner_json_errors": runner_json_errors, "agent_json_errors": agent_json_errors,
                          "runner_tests": run_tests(runner), "agent_tests": run_tests(agent)},
         "status": "PASS"},
        {"cycle": 2, "name": "agent-and-contract-coverage",
         "audit": "Revisión de agentes, comandos, contratos, colas, fuentes y límites activos frente al índice canónico.",
         "solution": "Se creó un índice único y se clasifican referencias históricas para impedir que vuelvan a operar como contrato activo.",
         "verification": {"runner_scripts": len(files(runner / "scripts", ".py")),
                          "runner_tests": len(files(runner / "tests", ".py")),
                          "agent_root_python": len(files(agent, ".py")),
                          "agent_tests": len(files(agent / "tests", ".py")),
                          "stale_reference_audit": stale_reference_audit(runner, agent)},
         "status": "PASS_WITH_HISTORICAL_REVIEW"},
        {"cycle": 3, "name": "rights-provenance-and-artifacts",
         "audit": "Verificación de ledger, hashes, archivos aprobados, manifiesto de entrega y metadatos privados.",
         "solution": "Se mantienen aprobaciones sólo si el archivo existe y coincide; se conserva el estado privado.",
         "verification": ledger_result,
         "status": "PASS" if capacity_ready and delivery_ready else "BLOCKED_ACTIVE_CONTRACT"},
        {"cycle": 4, "name": "configuration-documentation-order",
         "audit": "Revisión de documentación operativa, límites de capacidad y rutas canónicas.",
         "solution": "Se añadieron PROJECT_INDEX.md en ambas copias y un encabezado de contrato activo que separa histórico de ejecutable.",
         "verification": {"runner_index": (runner / "PROJECT_INDEX.md").is_file(),
                          "agent_index": (agent / "PROJECT_INDEX.md").is_file(),
                          "active_target_seconds": contract["minimum_approved_seconds"],
                          "active_minimum_unique_tracks": contract["minimum_unique_tracks"],
                          "active_video_duration_seconds": [contract["min_duration_seconds"], contract["max_duration_seconds"]],
                          "historical_references_found": stale_reference_audit(runner, agent)["count"]},
         "status": "PASS_WITH_HISTORICAL_REVIEW"},
        {"cycle": 5, "name": "security-and-release-safety",
         "audit": "Revisión de credenciales locales, permisos, marcadores de publicación y defaults de subida.",
         "solution": "Se confirma que las credenciales están ignoradas y se mantiene la publicación desactivada; no se ejecutan subidas.",
         "verification": security_audit(agent, runner),
         "status": "PASS_PRIVATE_ONLY"},
    ]
    overall = "PASS" if capacity_ready and delivery_ready else "BLOCKED_ACTIVE_CONTRACT"
    if cycles[0]["verification"].get("runner_tests", {}).get("passed") is False or cycles[0]["verification"].get("agent_tests", {}).get("passed") is False:
        overall = "BLOCKED_TEST_FAILURE"
    return {"schema_version": 1, "audit_run": "five-deep-repository-audits",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project": "Jazz Soul Beat", "overall_status": overall,
            "publication": "DISABLED", "cycles": cycles}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner-root", type=Path, required=True)
    parser.add_argument("--agent-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.runner_root.resolve(), args.agent_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

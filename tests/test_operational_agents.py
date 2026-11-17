import csv
from pathlib import Path

from scripts.release_qa_agent import inspect as inspect_media
from scripts.rights_provenance_agent import audit_catalog
from scripts.scene_library_agent import inspect as inspect_scenes
from scripts.video_assembly_agent import plan


def test_rights_agent_is_read_only_and_prepares_attribution(tmp_path: Path):
    catalog = tmp_path / "candidates.csv"
    with catalog.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title", "artist", "source_url", "license"])
        w.writeheader()
        w.writerow({
            "title": "A",
            "artist": "Creator",
            "source_url": "https://example.test/a",
            "license": "CC BY 4.0",
        })
    result = audit_catalog(catalog)
    assert result["reviewable"] == 1
    assert result["compliance_ready"] == 1
    assert result["needs_human_confirmation"] == 1
    assert "A — Creator" in result["attribution_manifest"][0]["attribution"]
    assert not result["rights_verified"]
    assert not result["approval_mutated"]
    assert result["publication"] == "DISABLED"


def test_scene_agent_blocks_without_eight_images(tmp_path: Path):
    (tmp_path / "one.png").write_bytes(b"x")
    assert inspect_scenes(tmp_path)["status"] == "BLOCKED_INCOMPLETE_SCENE_LIBRARY"


def test_assembly_and_release_keep_gates_closed(tmp_path: Path):
    result = plan("v1", 3600, ["track-a"], "static_rain_steam_only")
    assert result["state"] == "PLANNED" and result["publication"] == "DISABLED"
    media = tmp_path / "review.mp4"
    media.write_bytes(b"mp4")
    qa = inspect_media(media)
    assert qa["status"] == "PASS_TECHNICAL_REVIEW_REQUIRED" and not qa["creative_approval"]

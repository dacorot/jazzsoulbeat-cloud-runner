from scripts.artifact_manifest_agent import manifest


def test_manifest_hashes_required_artifacts(tmp_path):
    for name in ("video.mp4", "mix.mp3", "thumb.jpg", "description.txt", "MUSIC_SOURCE.txt"):
        (tmp_path / name).write_bytes(name.encode())
    result = manifest(tmp_path)
    assert result["schema_version"] == 1
    assert len(result["artifact_set_sha256"]) == 64
    assert result["publication"] == "NOT_AUTHORIZED_BY_THIS_MANIFEST"

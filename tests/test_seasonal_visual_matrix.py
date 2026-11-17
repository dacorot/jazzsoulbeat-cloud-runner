import json
from pathlib import Path

def test_seasonal_visual_matrix_covers_four_seasons_and_five_playlists():
    root = Path(__file__).resolve().parents[1]
    matrix = json.loads((root / "config/seasonal_visual_matrix.json").read_text())
    assert set(matrix["seasons"]) == {"spring", "summer", "autumn", "winter"}
    assert len(matrix["playlist_mapping"]) == 5
    assert matrix["scene_diversity"]["same_hero_composition_allowed"] is False
    assert matrix["scene_diversity"]["photorealistic_allowed"] is False

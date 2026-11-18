"""Connect approved music to season, playlist and audience mood."""
from __future__ import annotations

SEASON_RULES = {
    "spring": {
        "genres": ["fresh jazz", "bossa nova", "smooth jazz", "light soul"],
        "instruments": ["nylon-string guitar", "Rhodes", "soft piano", "mellow saxophone"],
        "mood": "renewal, lightness and gentle focus",
        "playlists": {"coffee_time", "work_study", "chill", "sleep", "christian_jazz_worship"},
    },
    "summer": {
        "genres": ["soul jazz", "bossa nova", "light funk", "smooth jazz"],
        "instruments": ["Rhodes", "electric bass", "nylon-string guitar", "light percussion", "saxophone"],
        "mood": "open-air ease, golden-hour warmth and relaxed groove",
        "playlists": {"coffee_time", "chill", "work_study", "christian_jazz_worship"},
    },
    "autumn": {
        "genres": ["coffeehouse jazz", "soul jazz", "blues jazz"],
        "instruments": ["piano", "upright bass", "brushed drums", "tenor saxophone"],
        "mood": "warm reflection, rain and intimate evening calm",
        "playlists": {"coffee_time", "work_study", "sleep", "chill", "christian_jazz_worship"},
    },
    "winter": {
        "genres": ["quiet jazz", "ambient soul", "jazz ballad"],
        "instruments": ["soft piano", "Rhodes", "upright bass", "brushes"],
        "mood": "rest, warmth and quiet nighttime resolution",
        "playlists": {"sleep", "work_study", "christian_jazz_worship", "chill"},
    },
}


def contract() -> dict:
    return {"id": "seasonal_music_agent", "never_auto_approve": True,
            "never_publish": True, "requires_approved_tracks": True,
            "output_language": "English", "pdca": True}


def create_brief(season: str, playlist: str, approved_tracks: list[dict]) -> dict:
    rule = SEASON_RULES.get(season.strip().lower())
    if not rule:
        raise ValueError("unsupported_season")
    if playlist.strip().lower() not in rule["playlists"]:
        raise ValueError("playlist_not_compatible_with_season")
    if not approved_tracks or any(
        track.get("approved") is not True or track.get("rights_verified") is not True
        for track in approved_tracks
    ):
        raise ValueError("all_tracks_must_be_approved_and_rights_verified")
    return {"agent_id": "seasonal_music_agent", "season": season, "playlist": playlist,
            "language": "English", "genres": rule["genres"],
            "instrumentation": rule["instruments"], "mood": rule["mood"],
            "approved_track_count": len(approved_tracks), "publication": "DISABLED",
            "pdca_next_action": "Compare retention and playlist performance after publication."}

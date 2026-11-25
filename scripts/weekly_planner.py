"""Deterministic weekly production planning. Planning never approves assets or publishes."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

CATEGORIES = (
    ("Work & Study", "focused late-night library", "deep focus jazz"),
    ("Coffee Time", "rainy café window", "coffee shop jazz"),
    ("Sleep", "quiet moonlit bedroom", "sleep jazz"),
    ("Chill", "warm city rooftop at dusk", "chill soul jazz"),
    ("Christian Instrumental/Worship", "candlelit reading room", "christian instrumental jazz"),
)
SLOTS = (0, 2, 4)  # Monday, Wednesday, Friday; no unattended YouTube upload
ENVIRONMENTS = ("gentle rain", "soft snow", "window reflections", "moving clouds", "warm lamplight")
STATES = ("PLANNED", "ASSETS_PENDING", "RIGHTS_PENDING", "REVIEW_PENDING",
          "APPROVED_PRIVATE_UPLOAD", "UPLOADED_PRIVATE", "BLOCKED")
VALID_TRANSITIONS = {
    "PLANNED": ("ASSETS_PENDING", "BLOCKED"),
    "ASSETS_PENDING": ("RIGHTS_PENDING", "BLOCKED"),
    "RIGHTS_PENDING": ("REVIEW_PENDING", "BLOCKED"),
    "REVIEW_PENDING": ("APPROVED_PRIVATE_UPLOAD", "BLOCKED"),
    "APPROVED_PRIVATE_UPLOAD": ("UPLOADED_PRIVATE", "BLOCKED"),
    "UPLOADED_PRIVATE": (),
    "BLOCKED": (),
}

def transition(current: str, next_state: str) -> str:
    if current not in VALID_TRANSITIONS or next_state not in VALID_TRANSITIONS[current]:
        raise ValueError(f"Unsafe or invalid transition: {current} -> {next_state}")
    return next_state

def monday_of(day: dt.date) -> dt.date:
    return day - dt.timedelta(days=day.weekday())

def plan_week(day: dt.date) -> dict:
    monday = monday_of(day)
    week_index = (monday - dt.date(2026, 1, 5)).days // 7
    items = []
    for slot, offset in enumerate(SLOTS):
        release = monday + dt.timedelta(days=offset)
        cat_idx = (3 * week_index + slot) % len(CATEGORIES)
        category, setting, keyword = CATEGORIES[cat_idx]
        digest = hashlib.sha256(f"{release.isoformat()}:{category}".encode()).hexdigest()
        weather = ENVIRONMENTS[int(digest[:8], 16) % len(ENVIRONMENTS)]
        bpm = (68, 78, 66, 82, 72)[cat_idx]
        duration = 7200 + (int(digest[8:12], 16) % 13) * 300  # 2h–3h
        theme = f"{setting} with {weather}"
        items.append({
            "job_id": f"jsb-{release:%Y%m%d}-{cat_idx}",
            "target_date": release.isoformat(),
            "category": category,
            "concept": theme,
            "title": f"{category} Jazz | {theme.title()} | Relaxing Jazz & Soul",
            "thumbnail_text": f"{category} Jazz",
            "keywords": [keyword, "jazz soul instrumental", "relaxing jazz music", "jazz soul beats"],
            "bpm_target": bpm,
            "duration_seconds": duration,
            "width": 2560,
            "height": 1440,
            "visual_style": "original sophisticated adult cinematic illustration; non-anime; subtle seamless ambient motion; no real people",
            "human_approval_required": True,
            "youtube_upload_visibility": "private",
            "public_scheduling_enabled": False,
            "state": "PLANNED",
            "rights_verified": False,
            "video_sha256": None,
            "telegram_approval_id": None,
            "render_started": False,
            "notes": "Target only. Not a finished track, image, video, or approved license.",
        })
    return {
        "schema_version": 1,
        "week_monday": monday.isoformat(),
        "timezone": "America/Bogota",
        "budget": "zero-paid-services",
        "target_videos": 3,
        "jobs": items,
        "upload_policy": "PRIVATE_ONLY_AFTER_EXPLICIT_ARTIFACT_APPROVAL",
        "publication_policy": "PUBLIC_DISABLED",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--output", default="output/weekly-plan")
    args = parser.parse_args()
    day = dt.date.fromisoformat(args.date)
    plan = plan_week(day)
    directory = Path(args.output)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / f"{plan['week_monday']}.json"
    output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {output}: {len(plan['jobs'])} planned jobs; 0 videos rendered; 0 approved; 0 uploaded.")

if __name__ == "__main__":
    main()

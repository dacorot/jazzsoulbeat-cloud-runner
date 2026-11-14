#!/usr/bin/env python3
"""Read-only metadata discovery for Jazz Soul Beat.

This job never downloads, probes, transforms, or approves audio. Internet Archive
metadata is a secondary lead only; all rights layers and the authority of the
publisher remain unverified until checked against a primary rights-holder source.
"""
import csv
import json
import re
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

OUT = Path("music-library")
EVIDENCE = OUT / "evidence"
OUT.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)

MAX_METADATA_CHECKS = 80
MAX_AUDIO_FILE_BYTES = 30000000
GENRES = ("jazz", "soul", "blues", "bossa", "lofi", "gospel")
REJECT_TERMS = (
    "podcast", "episode", "sermon", "bible", "scripture", "lecture", "speech",
    "audiobook", "spoken word", "interview", "radio show", "radio program",
    "news", "cyberspace", "reading", "documentary", "soundtrack", "anime",
    "sample pack", "pastor", "psalm", "church", "gospel hall", "worship",
    "devotional", "preaching", "preacher", "homily", "testimony",
    "righteousness", "question", "answers", "live concert", "concert recording",
    "live performance",
)


def get_json(url):
    req = Request(url, headers={"User-Agent": "JazzSoulBeatReadOnlyMusicResearch/3.0"})
    with urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def clean(value):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "unknown"))[:90].strip("._") or "unknown"


def hunter():
    found = {}
    query_templates = []
    genre_terms = " OR ".join(GENRES)
    for license_query in (
        "licenseurl:http*publicdomain/zero*",
        "licenseurl:http*licenses/by/*",
    ):
        query_templates.append(
            f"mediatype:audio AND {license_query} AND ({genre_terms})"
        )

    successful_queries = []
    for query in query_templates:
        url = (
            "https://archive.org/advancedsearch.php?q=" + quote(query)
            + "&fl[]=identifier,title,creator,year,licenseurl,subject,description"
            + "&rows=150&page=1&output=json"
        )
        try:
            payload = get_json(url)
            docs = payload.get("response", {}).get("docs", [])
            successful_queries.append({
                "query": query,
                "count": len(docs),
                "total": payload.get("response", {}).get("numFound", 0),
            })
            for item in docs:
                if item.get("identifier"):
                    found[item["identifier"]] = item
        except Exception as error:
            print("HUNTER_SEARCH_ERROR", query, str(error)[:180])
        time.sleep(0.25)

    print("HUNTER_QUERIES", json.dumps(successful_queries))
    relevant = []
    for item in found.values():
        subjects = item.get("subject", [])
        if not isinstance(subjects, list):
            subjects = [subjects]
        subject_text = " ".join(str(value) for value in subjects).lower()
        title = str(item.get("title", "")).lower()
        description = str(item.get("description", "")).lower()
        combined = " ".join((title, description, subject_text))
        if any(term in combined for term in REJECT_TERMS):
            continue
        if not any(genre in subject_text for genre in GENRES):
            continue
        relevant.append(item)

    relevant.sort(key=lambda item: (
        str(item.get("title", "")).casefold(),
        str(item.get("identifier", "")).casefold(),
    ))
    print("HUNTER_FOUND", len(relevant), "METADATA_CHECK_LIMIT", MAX_METADATA_CHECKS)
    return relevant[:MAX_METADATA_CHECKS]


def claimed_license_text(license_url):
    value = str(license_url or "").strip().lower().rstrip("/")
    if "creativecommons.org/publicdomain/zero/1.0" in value:
        return "CC0 1.0 (metadata claim; not independently verified)"
    match = re.search(r"creativecommons\\.org/licenses/by/(1\\.0|2\\.0|2\\.5|3\\.0|4\\.0)", value)
    if match:
        return f"CC BY {match.group(1)} (metadata claim; not independently verified)"
    return "Unknown"


def license_is_candidate(value):
    value = str(value or "").strip().lower().rstrip("/")
    if "creativecommons.org/publicdomain/zero/1.0" in value:
        return True
    if "creativecommons.org/licenses/by/" in value:
        tail = value.split("creativecommons.org/licenses/by/", 1)[1]
        return bool(re.fullmatch(r"(1\\.0|2\\.0|2\\.5|3\\.0|4\\.0)(/[a-z-]+)?", tail))
    return False


def guardian(item):
    identifier = item["identifier"]
    try:
        metadata_url = "https://archive.org/metadata/" + quote(identifier)
        payload = get_json(metadata_url)
        metadata = payload.get("metadata", {})
        license_url = str(metadata.get("licenseurl", "")).strip()
        if not license_is_candidate(license_url):
            return None, "License metadata is not CC0 or CC BY"

        subjects = metadata.get("subject", [])
        if not isinstance(subjects, list):
            subjects = [subjects]
        subject_text = " ".join(str(value) for value in subjects).lower()
        title = str(metadata.get("title", item.get("title", "")))
        description = str(metadata.get("description", ""))
        combined = " ".join((title.lower(), description.lower(), subject_text))
        if any(term in combined for term in REJECT_TERMS):
            return None, "Spoken-word, podcast, or non-music metadata rejected"
        if not any(genre in subject_text for genre in GENRES):
            return None, "No explicit target-genre subject tag"

        creator = str(metadata.get("creator", item.get("creator", ""))).strip()
        uploader = str(metadata.get("uploader", "")).strip()
        normalize = lambda value: re.sub(r"[^a-z0-9]+", "", value.casefold())
        if not creator or not uploader or normalize(creator) not in normalize(uploader):
            return None, "Uploader authority not established by metadata"

        files = payload.get("files", [])
        audio_files = []
        for file_record in files:
            name = str(file_record.get("name", ""))
            if name.lower().endswith((".mp3", ".flac", ".ogg")) and not name.startswith("__MACOSX"):
                size = int(file_record.get("size", 0) or 0)
                if size and size <= MAX_AUDIO_FILE_BYTES:
                    audio_files.append(file_record)
        if not audio_files:
            return None, "No supported audio-file metadata under 30 MB"

        audio_files.sort(key=lambda file_record: (
            0 if str(file_record["name"]).lower().endswith(".mp3") else
            1 if str(file_record["name"]).lower().endswith(".ogg") else 2,
            int(file_record.get("size", 0) or 0),
        ))
        selected = audio_files[0]
        raw_duration = selected.get("length") or selected.get("duration")
        try:
            duration_seconds = round(float(raw_duration), 2) if raw_duration else None
        except (TypeError, ValueError):
            duration_seconds = None

        record = {
            "identifier": identifier,
            "title": title,
            "creator": creator,
            "uploader": uploader,
            "genre_evidence": subject_text,
            "source_type": "secondary_archive_lead_not_primary_rights_evidence",
            "source_authority_status": "unverified",
            "uploader_metadata_match": "yes_but_not_proof_of_authority",
            "license_claimed_text": claimed_license_text(license_url),
            "license_url": license_url,
            "license_evidence_url": metadata_url,
            "source_url": "https://archive.org/details/" + identifier,
            "file_name": selected["name"],
            "file_size": int(selected.get("size", 0) or 0),
            "duration_seconds": duration_seconds,
            "download_url": (
                "https://archive.org/download/" + quote(identifier, safe="")
                + "/" + quote(selected["name"], safe="/")
            ),
            "download_status": "not_downloaded",
            "audio_review_status": "not_listened",
            "attribution_exact": "",
            "composition_rights": "unknown",
            "arrangement_rights": "unknown",
            "performance_rights": "unknown",
            "master_rights": "unknown",
            "sync_permission": "unknown",
            "commercial_use_permission": "unknown",
            "youtube_monetization_permission": "unknown",
            "streaming_distribution_permission": "unknown",
            "rights_verified": "no",
            "candidate_status": "pending_primary_source_and_rights_review",
            "date": metadata.get("date", item.get("year", "")),
            "review_note": (
                "Metadata lead only. Do not download or use until a primary "
                "rights-holder source and every rights layer are independently verified."
            ),
        }
        return record, "PENDING_PRIMARY_SOURCE_AND_RIGHTS_REVIEW"
    except Exception as error:
        return None, "Metadata error: " + str(error)[:160]


def main():
    items = hunter()
    leads, rejected = [], []
    seen = set()
    for item in items:
        record, reason = guardian(item)
        if not record:
            rejected.append({
                "identifier": item.get("identifier"),
                "reason": reason,
            })
            continue
        if record["identifier"] in seen:
            continue
        seen.add(record["identifier"])
        leads.append(record)
        (EVIDENCE / (clean(record["identifier"]) + ".json")).write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        time.sleep(0.25)

    fields = [
        "identifier", "title", "creator", "uploader", "genre_evidence",
        "source_type", "source_authority_status", "uploader_metadata_match",
        "license_claimed_text", "license_url", "license_evidence_url",
        "source_url", "file_name", "file_size", "duration_seconds",
        "download_url", "download_status", "audio_review_status",
        "attribution_exact", "composition_rights", "arrangement_rights",
        "performance_rights", "master_rights", "sync_permission",
        "commercial_use_permission", "youtube_monetization_permission",
        "streaming_distribution_permission", "rights_verified",
        "candidate_status", "date", "review_note",
    ]
    with (OUT / "candidate_catalog.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(leads)

    review_lines = [
        "# Jazz Soul Beat — read-only music research",
        "",
        "**Status: METADATA LEADS ONLY — NOT APPROVED.**",
        "",
        "No audio was downloaded, probed, modified, or listened to in this run.",
        "Internet Archive metadata is a secondary lead, not proof that the uploader",
        "controls the composition, arrangement, performance, or master recording.",
        "Do not use these entries in a mix or production workflow.",
        "",
        "| Track | Creator claim | Duration metadata | License claim | Source |",
        "|---|---|---:|---|---|",
    ]
    for record in leads:
        review_lines.append(
            "| {title} | {creator} | {duration} | {license} | [Item page]({source}) |".format(
                title=str(record.get("title", "")).replace("|", "/"),
                creator=str(record.get("creator", "")).replace("|", "/"),
                duration=record.get("duration_seconds") or "unknown",
                license=record.get("license_claimed_text", "Unknown"),
                source=record.get("source_url", ""),
            )
        )
    (OUT / "CANDIDATE_REVIEW.md").write_text(
        "\\n".join(review_lines) + "\\n", encoding="utf-8"
    )
    (OUT / "rejected_report.json").write_text(
        json.dumps(rejected, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    summary = {
        "metadata_leads": len(leads),
        "rejected_metadata_records": len(rejected),
        "audio_downloads": 0,
        "audio_modifications": 0,
        "audio_listening_checks": 0,
        "rights_approved": 0,
        "license_policy": "CC0 and CC BY metadata only; NC, ND, SA and other licenses excluded",
        "source_policy": "Internet Archive is a secondary lead source, not primary rights evidence",
        "note": (
            "Every candidate remains pending. Verify the actual rights holder, "
            "composition, arrangement, performance, master, synchronization, "
            "commercial use, monetization, platform terms and exact attribution "
            "from primary sources before downloading or using any audio."
        ),
    }
    (OUT / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

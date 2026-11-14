#!/usr/bin/env python3
"""Free, license-first music acquisition pipeline for Jazz Soul Beat.
Hunter -> Guardian -> Downloader -> Curator. Only explicit CC0 or CC BY
items are candidates; NC, ND and SA licenses are excluded for monetized
video synchronization and editing. Metadata is evidence, not legal clearance.
"""
import csv, json, re, subprocess, time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

OUT = Path("music-library")
MAX_CANDIDATES = 12
MAX_AUDIO_FILE_BYTES = 30000000
MIN_CANDIDATE_DURATION_SECONDS = 180.0
AUDIO = OUT / "candidates"
EVIDENCE = OUT / "evidence"
for p in (AUDIO, EVIDENCE):
    p.mkdir(parents=True, exist_ok=True)

# Deliberately narrow: CC0 and CC BY only. BY-SA can impose share-alike
# obligations on adapted video; ND is unsuitable for synchronization/editing.
GENRES = ("jazz", "soul", "blues", "bossa", "lofi", "gospel", "ambient")
LICENSE_QUERIES = (
    "licenseurl:http*publicdomain/zero*",
    "licenseurl:http*licenses/by/*",
)

def get_json(url):
    req = Request(url, headers={"User-Agent": "JazzSoulBeatMusicAgents/2.0"})
    with urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))

def clean(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(s or "unknown"))[:90].strip("._") or "unknown"

def hunter():
    found = {}
    # Search the IA license index with several documented wildcard forms.
    # Genre-qualified searches run first; broader license-only searches are
    # fallback candidates and are filtered by metadata before download.
    query_templates = []
    genre_terms = " OR ".join(GENRES)
    for license_query in (
        "licenseurl:http*publicdomain*",
        "licenseurl:http*zero*",
        "licenseurl:http*licenses/by*",
        "licenseurl:http*by*",
    ):
        query_templates.append(f'mediatype:audio AND {license_query} AND ({genre_terms})')
    for license_query in (
        "licenseurl:http*publicdomain*",
        "licenseurl:http*zero*",
        "licenseurl:http*licenses/by*",
        "licenseurl:http*by*",
    ):
        query_templates.append(f'mediatype:audio AND {license_query}')
    successful_queries = []
    for q in query_templates:
        url = ("https://archive.org/advancedsearch.php?q=" + quote(q) +
               "&fl[]=identifier,title,creator,year,licenseurl,subject,description&rows=500&page=1&output=json")
        try:
            payload = get_json(url)
            docs = payload.get("response", {}).get("docs", [])
            successful_queries.append({"query": q, "count": len(docs),
                                       "total": payload.get("response", {}).get("numFound", 0)})
            for d in docs:
                if d.get("identifier"):
                    found[d["identifier"]] = d
        except Exception as e:
            print("HUNTER_SEARCH_ERROR", q, str(e)[:180])
        time.sleep(0.25)
    print("HUNTER_QUERIES", json.dumps(successful_queries))
    # Keep relevant musical items when metadata is available; the broad
    # fallback is still useful when archive genre tags are incomplete.
    genres = tuple(g.lower() for g in GENRES)
    docs = list(found.values())
    relevant = []
    for d in docs:
        text = " ".join(str(d.get(k, "")) for k in ("title", "creator", "subject", "description")).lower()
        if any(g in text for g in genres) or not text.strip():
            relevant.append(d)
    if relevant:
        docs = relevant
    print("HUNTER_FOUND", len(docs))
    return docs

def license_is_usable(value):
    u = str(value or "").strip().lower().rstrip("/")
    # Accept only canonical CC0 or Attribution URLs. Explicitly reject NC,
    # ND and SA variants, including older 2.0/3.0/4.0 versions.
    if "creativecommons.org/publicdomain/zero" in u:
        return True
    if "creativecommons.org/licenses/by/" in u:
        tail = u.split("creativecommons.org/licenses/by/", 1)[1]
        return bool(re.fullmatch(r"(1\.0|2\.0|2\.5|3\.0|4\.0)(/[a-z-]+)?", tail))
    return False

def guardian(item):
    ident = item["identifier"]
    try:
        meta = get_json("https://archive.org/metadata/" + quote(ident))
        m = meta.get("metadata", {})
        license_url = str(m.get("licenseurl", "")).strip()
        if not license_is_usable(license_url):
            return None, "License not CC0 or CC BY (commercial video use filter)"
        files = meta.get("files", [])
        candidates = []
        for f in files:
            name = f.get("name", "")
            if name.lower().endswith((".mp3", ".flac", ".ogg")) and not name.startswith("__MACOSX"):
                size = int(f.get("size", 0) or 0)
                if size and size <= MAX_AUDIO_FILE_BYTES:
                    candidates.append(f)
        if not candidates:
            return None, "No supported audio file under 120 MB"
        candidates.sort(key=lambda f: (
            0 if f["name"].lower().endswith(".mp3") else
            1 if f["name"].lower().endswith(".ogg") else 2,
            int(f.get("size", 0) or 0)))
        f = candidates[0]
        return {
            "identifier": ident,
            "title": m.get("title", item.get("title", "")),
            "creator": m.get("creator", item.get("creator", "Unknown")),
            "license_url": license_url,
            "license_evidence_url": "https://archive.org/metadata/" + ident,
            "source_url": "https://archive.org/details/" + ident,
            "file_name": f["name"],
            "file_size": int(f.get("size", 0) or 0),
            "download_url": "https://archive.org/download/" + quote(ident, safe="") + "/" + quote(f["name"], safe="/"),
            "date": m.get("date", item.get("year", ""))
        }, "LICENSE_METADATA_MATCH_REQUIRES_ITEM_REVIEW"
    except Exception as e:
        return None, "Metadata error: " + str(e)[:160]

def downloader(record):
    target = AUDIO / (clean(record["identifier"]) + "__" + clean(Path(record["file_name"]).name))
    if target.exists() and target.stat().st_size == record["file_size"]:
        return target
    req = Request(record["download_url"], headers={"User-Agent": "JazzSoulBeatMusicAgents/2.0"})
    with urlopen(req, timeout=150) as r, open(target, "wb") as w:
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            w.write(chunk)
    if record["file_size"] and target.stat().st_size != record["file_size"]:
        target.unlink(missing_ok=True)
        raise RuntimeError("Downloaded size mismatch")
    return target

def curator(path):
    try:
        raw = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration:format_tags=title",
             "-of", "json", str(path)], text=True)
        info = json.loads(raw)
        duration = float(info.get("format", {}).get("duration", 0))
        if duration < MIN_CANDIDATE_DURATION_SECONDS:
            return False, duration, "Under 2 minutes"
        return True, duration, "Duration passed; audio listening and rights-holder review required"
    except Exception as e:
        return False, 0, "Probe failed: " + str(e)[:120]

def main():
    candidates = hunter()
    approved, rejected, seen = [], [], set()
    # Process more than the first 20 broad archive results; cap successful
    # review candidates to keep each free runner execution bounded.
    for item in candidates:
        if len(approved) >= MAX_CANDIDATES:
            break
        record, reason = guardian(item)
        if not record:
            rejected.append({"identifier": item.get("identifier"), "reason": reason})
            continue
        if record["identifier"] in seen:
            continue
        seen.add(record["identifier"])
        try:
            path = downloader(record)
            passed, duration, note = curator(path)
            record.update({
                "local_file": str(path),
                "duration_seconds": round(duration, 2),
                "curator_status": "technical_pass_listening_required" if passed else "rejected",
                "curator_note": note
            })
            if passed:
                approved.append(record)
                (EVIDENCE / (clean(record["identifier"]) + ".json")).write_text(
                    json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                path.unlink(missing_ok=True)
                rejected.append({"identifier": record["identifier"], "reason": note})
        except Exception as e:
            rejected.append({"identifier": record["identifier"], "reason": "Download/probe error: " + str(e)[:180]})
        time.sleep(0.5)
    fields = ["identifier", "title", "creator", "license_url", "license_evidence_url",
              "source_url", "file_name", "file_size", "download_url", "date",
              "local_file", "duration_seconds", "curator_status", "curator_note"]
    with open(OUT / "candidate_catalog.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(approved)
    review_lines = [
        "# Jazz Soul Beat — music candidate review",
        "",
        "**Status: NOT APPROVED.** These files passed only metadata, download and minimum-duration checks.",
        "Every track requires human listening and item-page/rights-holder/license verification before use.",
        "",
        "| Track | Creator | Duration (s) | License | Source |",
        "|---|---|---:|---|---|",
    ]
    for record in approved:
        review_lines.append(
            "| {title} | {creator} | {duration_seconds} | [{license}]({license}) | [Item page]({source_url}) |".format(
                title=str(record.get("title", "")).replace("|", "/"),
                creator=str(record.get("creator", "")).replace("|", "/"),
                duration_seconds=record.get("duration_seconds", ""),
                license=record.get("license_url", ""),
                source_url=record.get("source_url", ""),
            )
        )
    (OUT / "CANDIDATE_REVIEW.md").write_text("\\n".join(review_lines) + "\\n", encoding="utf-8")
    (OUT / "rejected_report.json").write_text(
        json.dumps(rejected, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "found": len(candidates),
        "candidate_tracks_for_listening_review": len(approved),
        "minimum_duration_seconds": MIN_CANDIDATE_DURATION_SECONDS,
        "maximum_file_bytes": MAX_AUDIO_FILE_BYTES,
        "rights_approved": 0,
        "rejected": len(rejected),
        "license_policy": "CC0 and CC BY only; NC, ND and SA excluded",
        "note": "Unapproved candidates only. Metadata and duration checks do not establish rights-holder authority or final license clearance. Human listening and item-by-item rights review are mandatory."
    }
    (OUT / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

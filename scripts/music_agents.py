#!/usr/bin/env python3
"""Free, license-first music acquisition pipeline for Jazz Soul Beat.
Agents: Hunter -> Guardian -> Downloader -> Curator. No paid APIs.
Only Internet Archive items with explicit CC0/CC-BY/CC-BY-SA license URLs
are eligible. Every download keeps source, creator, license and evidence metadata.
"""
import csv, json, os, re, subprocess, sys, time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

OUT = Path("music-library")
AUDIO = OUT / "approved"
EVIDENCE = OUT / "evidence"
for p in (AUDIO, EVIDENCE): p.mkdir(parents=True, exist_ok=True)

# Explicitly permitted license families for commercial use, subject to each
# item's exact license terms and attribution obligations.
ALLOWED = ("creativecommons.org/publicdomain/zero/",
           "creativecommons.org/licenses/by/",
           "creativecommons.org/licenses/by-sa/")
SEARCHES = [
    'mediatype:audio AND (subject:jazz OR title:jazz)',
    'mediatype:audio AND (subject:soul OR title:soul)',
    'mediatype:audio AND (subject:bossa nova OR title:bossa)',
    'mediatype:audio AND (subject:blues OR title:blues)',
    'mediatype:audio AND (subject:lo-fi OR title:lo-fi)',
    'mediatype:audio AND (subject:christian OR title:gospel)',
]
def get_json(url):
    req = Request(url, headers={"User-Agent":"JazzSoulBeatMusicAgents/1.0 (license research)"})
    with urlopen(req, timeout=35) as r: return json.loads(r.read().decode("utf-8"))
def clean(s):
    return re.sub(r"[^A-Za-z0-9._-]+","_",str(s or "unknown"))[:90].strip("._") or "unknown"
def hunter():
    found = {}
    for q in SEARCHES:
        url = "https://archive.org/advancedsearch.php?q="+quote(q)+"&fl[]=identifier,title,creator,year&rows=40&page=1&output=json"
        try:
            docs = get_json(url).get("response",{}).get("docs",[])
            for d in docs: found[d["identifier"]] = d
        except Exception as e: print("HUNTER_SEARCH_ERROR",q,str(e)[:180])
    print("HUNTER_FOUND",len(found))
    return list(found.values())
def guardian(item):
    ident = item["identifier"]
    try:
        meta = get_json("https://archive.org/metadata/"+quote(ident))
        m = meta.get("metadata",{})
        license_url = str(m.get("licenseurl","")).lower()
        if not any(license_url.startswith(x) for x in ALLOWED):
            return None, "No explicit commercial-use CC license"
        files = meta.get("files",[])
        candidates=[]
        for f in files:
            name=f.get("name","")
            fmt=str(f.get("format","")).lower()
            if name.lower().endswith((".mp3",".flac",".ogg")) and not name.startswith("__MACOSX"):
                size=int(f.get("size",0) or 0)
                if size and size < 120_000_000: candidates.append(f)
        if not candidates: return None, "No supported audio file"
        # Prefer FLAC, then MP3, then OGG; avoid huge multi-album archives.
        candidates.sort(key=lambda f:(0 if f["name"].lower().endswith(".flac") else 1 if f["name"].lower().endswith(".mp3") else 2, int(f.get("size",0) or 0)))
        f=candidates[0]
        return {"identifier":ident,"title":m.get("title",item.get("title","")),
                "creator":m.get("creator",item.get("creator","Unknown")),
                "license_url":license_url,"license_evidence_url":"https://archive.org/metadata/"+ident,
                "source_url":"https://archive.org/details/"+ident,
                "file_name":f["name"],"file_size":int(f.get("size",0) or 0),
                "download_url":"https://archive.org/download/"+quote(ident,safe="")+"/"+quote(f["name"],safe="/"),
                "date":m.get("date",item.get("year",""))}, "LICENSE_APPROVED"
    except Exception as e: return None, "Metadata error: "+str(e)[:160]
def downloader(record):
    target=AUDIO/(clean(record["identifier"])+"__"+clean(Path(record["file_name"]).name))
    if target.exists() and target.stat().st_size == record["file_size"]: return target
    req=Request(record["download_url"],headers={"User-Agent":"JazzSoulBeatMusicAgents/1.0"})
    with urlopen(req,timeout=120) as r, open(target,"wb") as w:
        while True:
            chunk=r.read(1024*1024)
            if not chunk: break
            w.write(chunk)
    if record["file_size"] and target.stat().st_size != record["file_size"]:
        target.unlink(missing_ok=True); raise RuntimeError("Downloaded size mismatch")
    return target
def curator(path):
    try:
        raw=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration:format_tags=title","-of","json",str(path)],text=True)
        info=json.loads(raw); duration=float(info.get("format",{}).get("duration",0))
        # Reject tiny clips and audio shorter than two minutes.
        if duration < 120: return False, duration, "Under 2 minutes"
        return True,duration,"Duration passed; technical listening review still required"
    except Exception as e: return False,0,"Probe failed: "+str(e)[:120]
def main():
    candidates=hunter(); approved=[]; rejected=[]; seen=set()
    for item in candidates:
        if len(approved)>=20: break
        record,reason=guardian(item)
        if not record: rejected.append({"identifier":item.get("identifier"),"reason":reason}); continue
        if record["identifier"] in seen: continue
        seen.add(record["identifier"])
        try:
            path=downloader(record)
            passed,duration,quality=curator(path)
            record.update({"local_file":str(path),"duration_seconds":round(duration,2),
                           "curator_status":"technical_pass_listening_required" if passed else "rejected",
                           "curator_note":quality})
            if passed:
                approved.append(record)
                (EVIDENCE/(clean(record["identifier"])+".json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
            else:
                path.unlink(missing_ok=True); rejected.append({"identifier":record["identifier"],"reason":quality})
        except Exception as e: rejected.append({"identifier":record["identifier"],"reason":"Download/probe error: "+str(e)[:180]})
        time.sleep(1)
    fields=["identifier","title","creator","license_url","license_evidence_url","source_url","file_name","file_size","download_url","date","local_file","duration_seconds","curator_status","curator_note"]
    with open(OUT/"approved_catalog.csv","w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(approved)
    (OUT/"rejected_report.json").write_text(json.dumps(rejected,ensure_ascii=False,indent=2),encoding="utf-8")
    summary={"found":len(candidates),"approved_for_listening_review":len(approved),"rejected":len(rejected),
             "note":"A license metadata match is not a substitute for human review of the item page and exact license. No track is cleared for publishing until listening and attribution checks are completed."}
    (OUT/"run_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()

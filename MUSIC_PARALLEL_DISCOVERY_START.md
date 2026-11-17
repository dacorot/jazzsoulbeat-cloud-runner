# Parallel music discovery trigger

Updating this marker runs three independent, read-only discovery lanes: primary catalogs, community catalogs and an independent metadata search. All lanes compare against existing catalogs before any download; they produce candidate evidence only and never approve rights, import audio into the production library, or publish anything.


Regression trigger 2026-11-17T16:55:03.462Z: source partition + pre-download dedup validation.


Regression trigger 2026-11-17T16:59:30.810Z: independent CCmixter offset 40; all lanes must download.


Regression trigger 2026-11-17T17:02:47.634Z: primary fallback after Ketsa timeout.


Autonomy regression trigger 2026-11-17T18:16:27.424Z: runtime branch updated after PDCA repair.


Rights-audit regression trigger 2026-11-17T18:41:34.391Z: reject HTML and stage only direct audio responses.


- 2026-11-17T19:08:06.088Z: Deming retry after fixing direct official Incompetech audio URL resolution; review-only, rights and publication gates unchanged.


- 2026-11-17T19:11:56.414Z: Deming ACT correction: percent-encode direct catalog MP3 filenames before rerun.


- 2026-11-17T19:28:02.447Z: Deming ACT correction: auditor now falls back to mutagen when ffprobe is unavailable on runner images.


- 2026-11-17T19:37:23.880Z: Deming ACT correction: shared-contract test now includes rights_agent (8 active agents).


- 2026-11-17T20:02:27.640Z: Deming continuation: rights_agent now audits evidence for every discovery lane before handoff.


- 2026-11-17T20:04:33.308Z: Deming ACT correction: discovery lanes now use the portable review-only rights evidence auditor; no private-branch CLI dependency.


- 2026-11-17T20:36:39.131Z: Editorial ACT rerun: stage only the 32 remaining approved tracks; excluded titles stay out of future downloads.


- 2026-11-17T20:41:41.982Z: Deming ACT correction: primary staging now consumes only EDITORIAL_APPROVED_TITLES.txt (32 titles).

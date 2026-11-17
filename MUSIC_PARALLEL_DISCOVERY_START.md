# Parallel music discovery trigger

Updating this marker runs three independent, read-only discovery lanes: primary catalogs, community catalogs and an independent metadata search. All lanes compare against existing catalogs before any download; they produce candidate evidence only and never approve rights, import audio into the production library, or publish anything.


Regression trigger 2026-11-17T16:55:03.462Z: source partition + pre-download dedup validation.


Regression trigger 2026-11-17T16:59:30.810Z: independent CCmixter offset 40; all lanes must download.


Regression trigger 2026-11-17T17:02:47.634Z: primary fallback after Ketsa timeout.


Autonomy regression trigger 2026-11-17T18:16:27.424Z: runtime branch updated after PDCA repair.


Rights-audit regression trigger 2026-11-17T18:41:34.391Z: reject HTML and stage only direct audio responses.


- 2026-11-17T19:08:06.088Z: Deming retry after fixing direct official Incompetech audio URL resolution; review-only, rights and publication gates unchanged.


- 2026-11-17T19:11:56.414Z: Deming ACT correction: percent-encode direct catalog MP3 filenames before rerun.

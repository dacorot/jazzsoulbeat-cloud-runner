# Parallel music discovery trigger

Updating this marker runs three independent, read-only discovery lanes: primary catalogs, community catalogs and an independent metadata search. All lanes compare against existing catalogs before any download; they produce candidate evidence only and never approve rights, import audio into the production library, or publish anything.


Regression trigger 2026-11-17T16:55:03.462Z: source partition + pre-download dedup validation.


Regression trigger 2026-11-17T16:59:30.810Z: independent CCmixter offset 40; all lanes must download.

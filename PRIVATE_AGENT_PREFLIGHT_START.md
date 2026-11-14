Targeted preflight trigger marker. Updating this file runs the private-agent QA workflow.

Regression trigger 2026-11-14: verify exact-folder private production persistence and isolated original-music storage.

Regression trigger 2026-11-14: validate complete-render folder preconditions and exact-folder production Drive persistence.

Regression trigger 2026-11-14: ensure derived camera crops cannot satisfy the eight-independent-original-scenes production gate.

Regression trigger 2026-11-14: reject Windows-style traversal, alternate data streams, NUL bytes and noncanonical filenames in the visual scene manifest; run the full private-agent preflight against the current branch head.

Regression trigger 2026-11-14: re-run full QA after hardening production music-manifest path resolution against symlink substitution and Windows/noncanonical path forms.

Regression round 1 (2026-11-14): strict production license allowlist (CC BY 4.0/CC0 only); reject symlinked playlist roots, folders and sources; enforce exact SHA-256 human approval inside the YouTube upload function; retry resumable YouTube API chunks with bounded Google client retries. Run full private-agent QA, no YouTube upload.

Regression round 1 retry 2026-11-14: corrected license regex escaping after first QA exposed parser regressions; fixed upload test artifact lifetime; rerun all tests against current agent head.

Regression round 1 final rerun 2026-11-14: all source and regression-test fixes committed; validate exact current agent HEAD, including corrected strict-license regex and YouTube upload approval boundary.

# Public workflow artifact cleanup

This one-time trigger removes every GitHub Actions artifact previously stored in
this public controller repository. Those artifacts were build outputs, previews,
candidate audio bundles, or QA reports; none is an approved final product.
Project review files that are retained must live in the private Google Drive
library instead. This cleanup does not delete workflow logs, source code, the
private agent repository, or any Google Drive file.

Retry trigger: the first cleanup pass deleted a partial batch before a transient API disconnect; this second pass retries remaining artifacts with backoff and verifies the repository is empty.

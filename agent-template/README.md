# Reusable cloud agent template

This repository contains a reusable GitHub Actions runner for the next private agents.

## Required contract for each private agent

Each agent repository should provide:

- `requirements.txt` (may be empty or minimal).
- `main.py self-test`: deterministic synthetic QA, no external paid services, no public actions.
- `main.py drive-push` and `main.py drive-status`: persist only that agent's private state and outputs.
- `tests/`: unit and safety tests.
- A documented, explicit allowlist for files that may be persisted.
- Fail-closed behavior when credentials, quota, rights evidence or approvals are missing.

## Call the reusable workflow

Create a small caller workflow in each controller repository:

```yaml
name: Agent QA
on:
  workflow_dispatch:
  schedule:
    - cron: "0 13 * * 1"
permissions:
  contents: read
jobs:
  qa:
    uses: dacorot/jazzsoulbeat-cloud-runner/.github/workflows/reusable-private-agent.yml@main
    with:
      agent_repository: YOUR_ORG/YOUR_PRIVATE_AGENT
      agent_ref: main
      python_version: "3.11"
    secrets:
      PRIVATE_REPO_READ_TOKEN: ${{ secrets.PRIVATE_REPO_READ_TOKEN }}
      DRIVE_TOKEN_JSON: ${{ secrets.DRIVE_TOKEN_JSON }}
```

The caller must have `PRIVATE_REPO_READ_TOKEN` and `DRIVE_TOKEN_JSON` configured. Keep each agent's Drive namespace/folder isolated; do not reuse Jazz Soul Beat production data.

## Safety rules

- QA uses synthetic data only.
- Never include platform publishing credentials in the reusable QA workflow.
- Never auto-approve legal, financial, medical, or publication decisions.
- Publishing workflows must be separate, explicit, and default to private/draft.
- Schedules must be useful but not create duplicate overlapping runs.
- Every long-running job needs a timeout, concurrency group, checksums and recoverable persistence.
- Do not treat a green test run as proof that external rights, credentials, or publishing are configured.

## Included runner

`.github/workflows/reusable-private-agent.yml` checks out the private agent at the caller-selected ref, installs dependencies and FFmpeg, compiles and runs tests, executes its synthetic self-test, and stores QA outputs in private Drive.

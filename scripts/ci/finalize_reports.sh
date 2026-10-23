#!/usr/bin/env bash
# Ensure status.jsonl exists and print artifact slug for a CI job (e.g. ci/static).
set -euo pipefail
JOB_NAME="${1:?job name required, e.g. ci/static}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p tests/reports
if uv run --project backend python -c "import sys; from scripts.ci.changes import job_make_ci; sys.exit(0 if job_make_ci(sys.argv[1]) else 1)" "$JOB_NAME"; then
  if [[ ! -f tests/reports/status.jsonl ]]; then
    uv run --project backend python scripts/ci/ensure_job_status.py --job "$JOB_NAME"
  fi
fi
SLUG="${JOB_NAME/ci\//ci-}"
echo "artifact_slug=${SLUG}"

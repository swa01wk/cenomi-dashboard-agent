# Tests layout

| Path | Role |
|---|---|
| `backend/tests/unit/` | Backend unit tests (no database, no external network) |
| `backend/tests/integration/` | Backend integration tests against `cenomi_test` |
| `tests/tooling/` | Makefile, CI and harness acceptance tests |
| `tests/e2e/` | Playwright journeys (shell and product flows) |
| `tests/fixtures/golden/` | Golden expected values (ARCH-R084) |
| `tests/reports/` | Local and CI artefacts (JUnit, coverage, `status.jsonl`) |

## Traceability

- Pytest: `@pytest.mark.trace("AT-M0-T03-01", reqs=["ARCH-R026"])`
- Vitest / Playwright: test title prefix `[AT-M0-T04-01] …`

JUnit output carries AT IDs (pytest properties; Vitest/Playwright via title parsing).

## Running

```bash
make backend-test SUITE=unit
make backend-test SUITE=integration
uv run --project backend pytest tests/tooling -v
pnpm exec vitest run --config apps/web/vitest.config.ts
pnpm exec playwright test tests/e2e/support --project=desktop
```

## Quarantine

Flaky tests use `@pytest.mark.quarantine(defect="DEF-0001", expires="YYYY-MM-DD")` (max 7 days, owner approval). Run `uv run --project backend python scripts/lint/quarantine_expiry.py` before CI.

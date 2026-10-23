# AGENTS.md — working rules for coding agents (Cursor Composer) and contributors

| | |
|---|---|
| Document code | AGENTSMD (requirement IDs `AGENTSMD-Rnnn`) |
| Version | 1.1 · 2026-10-23 · M0 corrections PR (AGENTSMD-R005 ownership exceptions, HC-4 and HC-5) |
| Applies to | Every change in this repository |
| Companion | `.cursor/rules/*.mdc` (scoped rules), `plans/M<n>_*.md` (task cards), `plans/STATUS.md` (progress) |

This repository holds the **Cenomi Dashboard Intelligence Agent POC**. It recreates the Cenomi Admin and Tenant V2 dashboards on synthetic PostgreSQL data, adds a bounded analytics agent that answers with validated generative UI over AG-UI, and adds deterministic proactive insights. Everything is synthetic.

---

## 1. Before you write anything

**AGENTSMD-R001** Work only from an approved task card (`plans/M<n>_*.md`, IDs `M<n>-T<nn>`), and only after the owner has authorized that milestone's build (ADR-0015 §3). Check `plans/STATUS.md`. If the milestone is not authorized, stop and report.

**AGENTSMD-R002** Read in this order before implementing a card:
1. The card itself, all 20 fields.
2. Every spec section and contract named in its fields 2 and 11.
3. `docs/architecture/ARCHITECTURE.md` (module boundaries, conventions).
4. `docs/architecture/DEVELOPMENT_ENVIRONMENT.md` (Make targets, CI, PR rules).

**AGENTSMD-R003** Precedence when sources disagree, highest first:
1. The project owner's explicit instruction.
2. Approved decisions: `docs/design/DECISION_REGISTER.md`, `docs/adr/`.
3. PRD.
4. TA.
5. API Reference.
6. Approved specifications (`docs/`, `specs/`).
7. Existing code.

**If you find a conflict, stop and report it; do not resolve it.**

---

## 2. Repository map

| Path | What lives there | Editable by a card? |
|---|---|---|
| `docs/reference/`, `docs/design/baseline/`, `docs/handoff/` | Frozen references and design baseline | **Never** (hash-checked) |
| `plans/proposed/` | Provenance record of the proposed ESP | **Never** |
| `docs/adr/`, `docs/design/DECISION_REGISTER.md` | Decisions | Only in a specification PR |
| `docs/product/`, `docs/architecture/`, `docs/design/`, `docs/contracts/` | Specifications (prose) | Only in a specification PR |
| `specs/` | Machine-readable normative contracts | Only in a specification PR. After a contract is built, its Pydantic model is the source and the schema is GENERATED |
| `plans/ROADMAP.md`, `plans/M*_*.md` | Plan and task cards | Only in a specification PR |
| `plans/STATUS.md` | Progress | Updated at merges and decisions by the owner or the architect |
| `backend/src/cenomi/<module>/` | Backend modules (ARCHITECTURE §5.1) | Within the card's file ownership |
| `backend/migrations/` | Alembic revisions | Within the card; never edit a merged revision |
| `apps/web/`, `packages/` | Web app, generated contracts, viz primitives | Within the card; never edit GENERATED files |
| `tests/`, `backend/tests/` | Tests, fixtures, golden values | Within the card. Golden values change only with a CR |
| `scripts/`, `infra/`, `.github/`, `Makefile`, `docker-compose.yml` | Tooling | Within the card |

The Next.js tooling may manage an agent-docs block in `apps/web/AGENTS.md`. That file is tool-owned. **This root `AGENTS.md` is hand-owned and must not be rewritten by tools.**

---

## 3. Commands

Use the Makefile only (`specs/engineering/make_targets.yaml`; `make help` lists everything).

| When | Command |
|---|---|
| First time | `make setup`, then `make up` |
| Before every push | `make check` (fast, no database) |
| Card-specific | The targets named in the card's field 14, for example `make backend-test`, `make integration-test`, `make e2e GREP=AT-M0-T04` |
| Full local CI | `make ci` or `make ci JOB=<job>` |
| Never, unless the card or the owner says so | `make seed-reset`, `make db-downgrade`, `make down VOLUMES=1`, `make agent-test-live` |

---

## 4. Rules that are always on

Each rule names the check that enforces it.

| ID | Rule | Enforced by |
|---|---|---|
| **AGENTSMD-R004** | One card per branch and per PR. Branch name `feat\|fix\|test\|chore/m<n>-t<nn>-<slug>` | `ci/static` checks the head branch name against the `branch` ID pattern; review |
| **AGENTSMD-R005** | Touch only the paths in the card's field 13. Field 13 is read by the most-specific-path rule (DEVENV-R053): a broad glob never covers a file another card names. Two exceptions: lockfile and manifest updates for dependencies the card introduces (DEVENV-R052), and the listed changes to shared files and composition points (DEVENV-R054). Never make conflicting parallel changes to a shared file (DEVENV-R055). If the work needs any other path, **stop and report**; never widen the card | PR template field 5, review |
| **AGENTSMD-R006** | Never add a feature, screen, metric, agent capability or dependency the card does not name | Review; DEVENV-R002 (dependency changes must state why) |
| **AGENTSMD-R007** | Every acceptance criterion `AT-…` is an automated test carrying that ID (pytest `@pytest.mark.trace`; Vitest and Playwright title prefix `[AT-…]`). A card is done only when all its ATs are `PASSED`. A missing test is `NOT_IMPLEMENTED` and a skipped one is `SKIPPED`; neither counts (ARCHITECTURE §10.8). Never mark anything `NOT_APPLICABLE` yourself; only the three rules of ARCH-R101 can | `make trace-report CARD=<card>`, enforced by `ci/summary` |
| **AGENTSMD-R008** | Expected values come only from `tests/fixtures/golden/` or `tests/fixtures/metrics/`. Never compute an expected value with the code under test; never write an expected business number as a literal in test code | Review; ARCH-R084 |
| **AGENTSMD-R009** | Never edit a GENERATED file. Change its source and run `make codegen` | `make contracts-check` |
| **AGENTSMD-R010** | No SQL outside `cenomi.analytics` queries (from M2) and migrations. No string-built SQL anywhere | `make backend-lint` (SQL safety lint, ruff S608) |
| **AGENTSMD-R011** | Respect module boundaries (ARCHITECTURE §5.2, §6.1) | import-linter; ESLint boundaries |
| **AGENTSMD-R012** | No `dangerouslySetInnerHTML`. No string from an API or model rendered as HTML, URL or code | ESLint `react/no-danger`; review |
| **AGENTSMD-R013** | No secrets, real credentials or production data in the repository, logs, fixtures, screenshots or PR text | gitleaks (`make security-check`); log redaction test |
| **AGENTSMD-R014** | Business "now" is the dataset `as_of`. Never call `NOW()` in metric SQL or the wall clock in business logic | Review; lint added in M2 |
| **AGENTSMD-R015** | The word "overdue" is never used for approvals; no causal verbs without a mechanism | `specs-check` banned-term lint |
| **AGENTSMD-R016** | Authorization is enforced server-side through AccessScope. The web app only presents. Refusals are uniform | Security and isolation suites |
| **AGENTSMD-R017** | Missing, zero, empty, partial, unavailable and undefined are distinct states. Never substitute 0 or an estimate | Component state tests; golden tests |
| **AGENTSMD-R018** | Never skip or weaken a failing test to get green. Flaky tests follow the quarantine rule (ARCH-R088) with the owner's approval | `ci/quarantine`; quarantine expiry lint |
| **AGENTSMD-R019** | Never merge, never push to `main`, never force-push a shared branch, never change repository settings | Branch protection (DEVENV §8.4); ADR-0001 |
| **AGENTSMD-R020** | Fill every section of the PR template. Include `make check` output and, for UI changes, screenshots at desktop, tablet and phone widths | Review; template check |

---

## 5. When you are stuck

Stop and write a short report in the PR, or as a comment on the card. Name:
- the blocking question;
- the spec section or decision involved;
- the options you see.

Do not guess. Do not change a specification to make code pass. Open questions are recorded by the architect as `OQ-…` items in `plans/STATUS.md`.

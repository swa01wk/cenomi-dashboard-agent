# 6 · M0 specification-authoring plan

The M0 PR holds writing-order items 1–12 from tab 4. It is written in five authoring sessions, self-reviewed against a fixed checklist, then sent to you. It needs ED-01 to ED-06 decided first, because they change what the files say and how they reach the repository.

## Authoring sequence

| Session | Writes | Depends on | Your review focuses on |
| --- | --- | --- | --- |
| A | ADR-0001 (process), ADR-0002 (repository and sources of truth), ADR-0005 (backend topology); docs/reference copies; DESIGN\_BASELINE.md; DECISION\_REGISTER.md | ED-01, 02, 03 | Folder ownership; frozen versions are the right ones |
| B | PRODUCT\_SPEC.md: scope freeze, personas and roles, screens, card inventory, journey index, glossary, out of scope | Session A | Nothing added beyond the baseline; every card and journey traces to the PRD or a DX board |
| C | ARCHITECTURE.md; ADR-0003 (stack and version pinning), ADR-0004 (contract pipeline), ADR-0006 (database roles and schemas) | Session B; Stack and Sources of truth tabs | Module boundaries; AccessScope model; runtime boundaries |
| D | DEVELOPMENT\_ENVIRONMENT.md; bootstrap schemas (error\_envelope, principal, scope\_decision); AGENTS.md; .cursor/rules | Session C; ED-05, 07, 08, 09 | Can a clean clone be brought up from the text alone |
| E | plans/ROADMAP.md, plans/M0\_FOUNDATION.md (task cards below), plans/STATUS.md | Sessions A–D | Card sizing; acceptance tests; gate wording |

## Self-review checklist (run before the PR goes to you)

- [ ] Every statement of scope traces to the PRD, a DX board or a decision ID.
- [ ] No new feature, screen, agent capability or component; any gap found is an open question, not a decision.
- [ ] Every decision cited by ID; any new architectural choice is an ADR with status Proposed.
- [ ] Every module in ARCHITECTURE.md lists its responsibility, public interface and forbidden imports.
- [ ] Every command in DEVELOPMENT\_ENVIRONMENT.md maps to a make target in the M0 task cards.
- [ ] Every task card lists its files, contracts, steps, acceptance tests, out-of-scope items and done checklist.
- [ ] Open questions are listed in STATUS.md with an owner.

## M0 implementation task cards (written in plans/M0\_FOUNDATION.md)

| Card | Goal | Main files | Acceptance tests |
| --- | --- | --- | --- |
| M0-T01 | Repository scaffold and toolchain | root files, backend/pyproject.toml, pnpm-workspace.yaml, lint configs, Makefile | `make lint` and `make typecheck` pass on the skeleton |
| M0-T02 | Compose and Postgres initialization | docker-compose.yml, infra/postgres/init/\*.sql | Four roles and the schemas exist; reader cannot write; app role cannot write business schemas |
| M0-T03 | Backend skeleton | cenomi/core, cenomi/api/app.py | /health checks database and roles; errors use the envelope; logs are JSON with trace IDs |
| M0-T04 | Web skeleton | apps/web layout, rail, banner, /api rewrite | Playwright: shell renders with the synthetic-data banner; /api/health proxied |
| M0-T05 | Contract pipeline | cenomi/contracts, scripts/codegen, packages/contracts-ts | Exported schemas equal the bootstrap specs; TS and zod generated; CI fails on an edited generated file |
| M0-T06 | Dev sign-in and AccessScope interface | cenomi/auth, tests/fixtures/principals.yaml | /me returns the principal; a principal without grants gets an empty scope; the client cannot set scope |
| M0-T07 | CI workflows | .github/workflows/ci.yml | All jobs green on main; required checks configured |
| M0-T08 | ECharts verification harness (GDQ-06) | packages/viz verification page, tests/e2e/echarts-gate | DX3 gallery self-test runs on ECharts 5.6.0 in CI; result JSON stored as an artifact and summarized in STATUS.md |
| M0-T09 | AG-UI spike, throwaway (GDQ-11) | branch spike/agui only; report in docs/architecture/spikes/ | Report covers run lifecycle, text, tool call, state snapshot and delta, CUSTOM, cancelled outcome, frontend tool round trip and one model latency sample |
| M0-T10 | Cursor rules, PR template, STATUS wiring | .cursor/rules, .github/pull\_request\_template.md | PR template links a task card and its acceptance checklist |

M0 is about 6 hours of build plus about 3 hours for the spike and the ECharts harness. ED-06 proposes building M0 as soon as the M0 PR is merged, while PR-M1 to PR-M6 are still being written. The spike report then feeds PR-M4, the ECharts result feeds PR-M2, and slice day 1 gains those hours as buffer.

## What the M0 specifications leave out

Tables beyond roles and schemas, metrics, seed data, agent code, AG-UI contracts and UI beyond the shell. Each of these is fixed by its own milestone PR. M0 only fixes the seams they plug into.

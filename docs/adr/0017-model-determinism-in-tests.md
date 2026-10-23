# ADR-0017 — Model determinism in tests: mock, replay and controlled live evaluation

| | |
|---|---|
| Status | **Accepted** — PR-M0 merged 2026-10-22 at `4515031` (recorded 2026-10-23). **ED-08 Option A** was approved by the project owner on 2026-10-22. |
| Date | 2026-10-22 |
| Decision IDs | ED-08 (approved), DR-014, DR-015, GDQ-12; approved testing requirements (approval Part 7, areas E–G) |
| Decision text | `docs/design/DECISION_REGISTER.md` §5.1 "ED-08" (single source) |
| Related | ADR-0009 (reserved, PR-M3) specifies the LLM adapter, primary and fallback models, the replay provider's file format and its error code. It must conform to this ADR |

## Context

- Agent behaviour depends on a language model whose output varies between calls and costs money.
- Required CI checks must be deterministic, free of credentials and repeatable on any commit.
- The approved testing requirements already demand mock and replay tests that do not depend on live APIs, and opt-in live tests.

## Options considered

| Option | Summary | Outcome |
|---|---|---|
| A | Scripted mock for unit tests; recorded replay in CI; separate, controlled live evaluations | **Chosen** |
| B | CI calls the live model | Rejected: needs a model secret in PR workflows (conflicts with DEVENV-R027), non-deterministic, costs per run |

## Decision

ED-08 Option A, exactly as worded in DECISION_REGISTER §5.1 items 1–7, including the requirement the owner added on approval:

- **Missing recordings fail.** A replay miss fails the test explicitly and never triggers an unplanned live-model call. The `replay` provider has no code path to a live provider.

## Consequences

- `ci/agent` and `ci/e2e` run with `LLM_MODE=replay` and hold no model credential (`ci_checks.yaml`; AT-M0-T07-05).
- Live measurement happens only through `eval-live.yml` (protected `live-eval` environment, budget inputs) or `make agent-test-live`, never as a required check (ARCH-R089).
- Changing a prompt template version forces an explicit re-recording through `make agent-test-live RECORD=1`; recordings are committed only through a reviewed PR.
- In M0 the providers themselves do not exist yet. M0 delivers the configuration values (`LLM_MODE`), the test markers (`agent_mock`, `agent_replay`, `agent_live`; M0-T11) and the guarded `eval-live.yml` skeleton (M0-T07). The adapter and providers are built in M3.

## Verification

| Requirement | Acceptance test |
|---|---|
| CI references no secrets and runs agent jobs with `LLM_MODE=replay` | AT-M0-T07-05 |
| Live evaluation refuses without the protected environment and budget inputs | AT-M0-T07-08 |
| Unit tests cannot reach a non-local host | AT-M0-T11-07 |
| Replay miss fails and never calls a live provider | Defined in PR-M3 (ADR-0009, M3 plan) |

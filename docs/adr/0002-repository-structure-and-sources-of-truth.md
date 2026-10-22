# ADR-0002 — Repository structure, single sources of truth and slice planning

| | |
|---|---|
| Status | Proposed. **ED-03 Option A** (approved 2026-10-22, scope unchanged) and **ED-04 Option A** (approved 2026-10-22) are already decided; this ADR becomes Accepted when PR-M0 merges |
| Date | 2026-10-22 |
| Decision IDs | DR-034 (docs part superseded), ED-03, ED-04, DR-030 |

## Context

DR-034 (G0) set the repository naming from the project instructions and the TA §11 code layout. The Engineering Specification Plan (ESP) proposed a structure in which each fact has exactly one home. The owner approved the ESP on 2026-10-22, with refinements; `plans/ROADMAP.md` records the approved version.

## Decision

**1. Layout.** The repository layout is the approved ESP tab 5 tree, as recorded in `plans/ROADMAP.md` §4, with two approved additions:

| Folder | Holds |
|---|---|
| `specs/engineering/` | Make-target contract, CI check names and the specification-set version (machine-read) |
| `specs/traceability/` | Identifier conventions (machine-read) |

This supersedes the `docs/` part of DR-034. The TA §11 code layout (`services/api`, `services/agent`, `packages/metrics`) is superseded by the modular monolith in ADR-0005.

**2. One canonical home per concern.**

| Location | Rule |
|---|---|
| `specs/` | Normative and machine-read |
| `docs/` | Explains `specs/` and never restates a value from it. A table copied from a spec file is marked "rendered from <path>" and is drift-checked |
| Generated files | Committed, marked GENERATED, never hand-edited, and drift-checked in CI |
| `tests/fixtures/golden` | The only place expected values live |
| `plans/STATUS.md` | The only place progress lives |

The full source-of-truth table is `docs/architecture/ARCHITECTURE.md` §11.

**3. Frozen references (ED-03 A, scope unchanged).**
- `docs/reference/` and `docs/design/baseline/` keep the frozen copies committed in PR #1.
- They are never edited. A changed source becomes a new versioned file under a CR.
- This ADR does not widen ED-03. Its approval covers preserving the existing references and design baseline only.
- The one addition here is a *check*: `make specs-check` verifies `docs/handoff/SHA256SUMS` for the files under `docs/reference/` and `docs/design/baseline/`. A check does not interpret the documents, so it is within that scope.

**4. Slice planning (ED-04 A).**
- Five-day-slice task cards are tagged inside each milestone plan.
- `plans/SLICE_FIVE_DAY.md` (PR-M6) orders them into days. No task card exists twice.
- Every task card carries exactly one delivery class:

| Class | Meaning |
|---|---|
| `slice` | Required by the five-day integrated vertical slice |
| `full` | Part of the complete POC, built after the slice |
| `deferred` | Inside the approved scope, deliberately scheduled after the full-scope milestones (for example DR-026, DXD-84 if not reached) |

A deferred card is never deleted and is never described as out of scope.

**5. Proposed plans stay as provenance.** `plans/proposed/engineering-specification-plan/` is not edited. It is the record of what was proposed; `plans/ROADMAP.md` is the approved version, with numbered amendments.

## Consequences

- Composer reads every fact from one place, and CI rejects drift.
- Two extra `specs/` folders; both are small and validated by `make specs-check`.

## Verification

GATE-M0-05: `make specs-check` passes. Its checks include:
- reference hashes;
- ID conventions;
- the presence and structure of the files in `specs/engineering/`;
- the delivery class on every task card in every milestone plan.

# ADR-0001 — Record architecture decisions; specifications delivered by pull request

| | |
|---|---|
| Status | **Accepted** — PR-M0 merged 2026-10-22 at `4515031` (recorded 2026-10-23). The underlying decision **ED-01 Option A was approved by the project owner on 2026-10-22**. |
| Date | 2026-10-22 |
| Decision IDs | ED-01 (approved), DR-035 (superseded by this ADR), DR-041 |
| Supersedes | DR-035 "Planning documents committed manually" |

## Context

The design baseline (DX1–DX6, Final Design Gate, 22 Oct 2026) froze product and design decisions in the DR/DXD register. Engineering decisions made after the gate (the ED series, D-01, and choices made while writing specifications) need a durable, reviewable record that Cursor Composer can read from the repository.

DR-035 (G0) said planning documents are committed manually by the project owner. Since then, the owner authorized the documentation migration as a pull request (PR #1, merged 2026-10-22 at `d5db7f3`), and approved ED-01 Option A: specifications are authored on branches and merged through milestone-specific documentation PRs.

## Options considered

| Option | Summary | Outcome |
|---|---|---|
| A | Claude has push access; one documentation PR per milestone specification set; the owner reviews and merges; implementation then uses feature-level PRs | **Approved (ED-01 A)** |
| B | Claude publishes files to the Claude Project; the owner commits them (DR-035 unchanged) | Not chosen |

## Decision

1. Architecture decisions are recorded as ADRs in `docs/adr/`, numbered `ADR-nnnn`, using the template in `docs/adr/README.md`.
2. An ADR is required for:
   - a change to a contract, the stack or a version line, a module boundary, the database roles or schemas, the security model, or the agent lifecycle;
   - any engineering decision (ED, D-nn) once decided;
   - any deviation from the design baseline that the owner approves through a change request (CR).
3. An ADR is not required for naming, refactoring inside one module, or adding tests.
4. Lifecycle: Proposed → Accepted (the owner merges the PR) → Superseded or Rejected. Nothing is deleted.
5. **Specifications reach the repository by pull request.** Each milestone's specification set is one branch `docs/m<n>-<slug>` and one PR, opened by Claude and reviewed and merged only by the project owner. Implementation work uses feature branches and PRs (ADR-0015).
6. **No pull request is merged without the project owner's approval.** Claude never merges, never pushes to `main`, and never rewrites published history.
7. DR-035 is superseded. Its record stays in the register with status Superseded and a forward link to this ADR (`docs/design/DECISION_REGISTER.md`).

## Consequences

- Review comments live on the files, and CI can validate machine-readable specs in each specification PR.
- Claude needs push access to `swa01wk/cenomi-dashboard-agent`; this was confirmed on 2026-10-22.
- `plans/STATUS.md` is updated in the same PR as each decision and at each merge.

## Verification

- `make specs-check` (M0-T10) validates that every ADR file has the template headings and that the ADR index lists every ADR file.
- Gate check GATE-M0-09 confirms ADR-0001 to ADR-0006 and ADR-0015 are Accepted.

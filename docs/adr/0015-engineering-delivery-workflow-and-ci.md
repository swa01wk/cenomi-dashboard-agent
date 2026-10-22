# ADR-0015 — Engineering delivery workflow, CI scope and build authorization

| | |
|---|---|
| Status | Proposed. **ED-05 Option A** and **ED-06 Option A**, and the engineering delivery model (approval message of 2026-10-22, Parts 4 and 6–11), were approved by the project owner on 2026-10-22. This ADR becomes Accepted when PR-M0 merges |
| Date | 2026-10-22 |
| Decision IDs | ED-05, ED-06, ED-01, DR-037, DR-041, GDQ-06, GDQ-11 |

## Context

The owner asked for a disciplined process: feature branches, automated tests, GitHub Actions CI, explicit acceptance criteria and milestone exit gates. Implementation must not start until explicitly authorized.

## Decision

### 1. Delivery chain

Approved specification → feature branch → implementation → local checks (`make check`) → pull request → GitHub Actions CI → review → merge → integrated verification → milestone exit gate.

| Unit | Done when |
|---|---|
| Feature | Every acceptance test on its task card passes and CI is green. Generated code alone is not done |
| Milestone | Its exit gate passes on the **merged commit**: tests run on the integrated `main` SHA, a verification report is produced, and the owner approves it |

### 2. Scope of CI and CD (ED-05 A)

- GitHub Actions runs CI on every pull request and on every push to `main`.
- Container images are **built but never pushed**.
- There is no deployment, no registry publication and no release automation without separate authorization (DR-037).

**Workflows.** Three workflow files, plus one composite setup action (`.github/actions/setup`):

| File | Trigger | Purpose |
|---|---|---|
| `ci.yml` | `pull_request`, `push` to `main` | All validation jobs. One aggregating required check, `ci/summary` |
| `milestone-gate.yml` | `workflow_dispatch` | Runs the full suite on a chosen `main` SHA, plus gate-only checks (migration downgrade round-trip, full replay, performance runs from M5). Publishes the milestone verification report |
| `eval-live.yml` | `workflow_dispatch` | Live-model evaluation. Runs only from the protected `live-eval` environment, only on `main` or a branch in this repository, never on fork code, with budget limits |

Job names, triggers and required checks are fixed in `specs/engineering/ci_checks.yaml`. DEVELOPMENT_ENVIRONMENT.md §7 explains them.

### 3. Build authorization (ED-06 A)

- M0 may be implemented after PR-M0 is approved and merged, **subject to the owner's separate, explicit authorization to begin implementation**.
- Merging a specification PR does not authorize writing application code. This applies to every milestone.
- The conditions for authorizing M0 are listed in `plans/M0_FOUNDATION.md` §8. They include decisions on ED-07, ED-08 and ED-09, approved on 2026-10-22 (ADR-0016, ADR-0017, ADR-0018).

### 4. Branches and pull requests

- Every independently testable task card is built on its own short-lived branch from the latest `main`, named by the conventions in `specs/traceability/id_conventions.yaml`.
- Specification work uses `docs/m<n>-<slug>`.
- PR contents and merge policy are fixed in DEVELOPMENT_ENVIRONMENT.md §8:
  - squash merge;
  - review by the owner, given by the owner merging the PR (PRs are authored under the owner's account, and GitHub forbids self-approval; DEVENV-R039);
  - no merge with a failing required check;
  - rebased or validated against the latest `main`;
  - no force-push to `main`.
- Stacked PRs are allowed only when the dependency is named in both PR descriptions and the lower PR merges first.

### 5. Repository settings

Branch protection is **an M0 implementation requirement**. It is specified in DEVELOPMENT_ENVIRONMENT.md §8.4 in two stages:

| Stage | Contents | Must be in force |
|---|---|---|
| P1 | PR required; no force push; no deletion; squash only; conversation resolution | Before the first implementation PR merges |
| P2 | `ci/summary` required and strict | As soon as M0-T07 has merged |

Any merge outside these rules needs an owner-approved exception recorded as `EXC-nnn` in STATUS.md (DEVENV-R051). EXC-001, the pre-CI bootstrap cards, was approved conditionally on 2026-10-22 with seven conditions (DEVENV §8.4). The P1/P2 policy, with 0 required approving reviews, was approved on the same date.

The settings are **not applied** by Claude. As of 2026-10-22, `main` has no protection. Applying them needs the owner's action or explicit authorization.

## Consequences

- Composer works one task card at a time, with a predictable PR shape and CI signal.
- Milestone completion is evidence-based (commit SHA, dataset version, specification-set version) and is never inferred from merged PRs alone.

## Verification

GATE-M0-06 (CI baseline green on `main`; required check names match `ci_checks.yaml`) and GATE-M0-10 (stages P1 and P2 in force; every deviation covered by an approved `EXC-nnn`).

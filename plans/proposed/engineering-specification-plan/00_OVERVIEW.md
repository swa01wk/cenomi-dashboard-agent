# Cenomi POC — Engineering Specification Plan

Oct 22, 2026 · @Swaroop Shivakumar · Planning only: no code, migrations or repository changes

## Summary

This plan turns the approved DX1–DX6 baseline into a build order with gates. Specifications are written, reviewed and merged one milestone at a time. The slice is built only once its specifications (PR-M0 to PR-M4 and PR-M6) are merged. ED-06 proposes one exception: building M0 as soon as its own PR is merged. Every build step still waits for your explicit go-ahead.

- **Milestones:** M0 Foundation, M1 Data, M2 Metrics and dashboards, M3 Agent runtime, M4 AG-UI and generative UI, M5 Evaluation, M6 Proactive intelligence. They keep their G0 meaning and dependencies. Under DR-010, the complete M6 still follows M5.
- **Five-day slice (GDQ-01):** a delivery cut through M0–M4 and M6, not a separate milestone. Each milestone plan tags its slice task cards, and plans/SLICE\_FIVE\_DAY.md orders them into five days of about 49 hours. The full scope takes about 20 working days, including the slice.
- **Specifications:** 17 documents, 10 plan files, the ADRs and the machine-readable specs, delivered as seven milestone PRs in the order M0, M1, M2, M3, M4, M6, M5 (tab 4).
- **One source of truth per concern:** machine-readable specs live in specs/ and are read by code or tests. Prose in docs/ explains them and never restates them. Generated artefacts are committed and drift-checked in CI (Sources of truth tab).
- **Decisions recorded:** GDQ-01 to GDQ-12 are recorded as Option A in the Final Design Gate doc. That doc also holds the final definitions of the 17 batch defaults. 22 of the 23 open register decisions are now settled; DR-036 (evaluation scoring) is still open.
- **Needed from you:** 11 engineering decisions (tab 7). Six of them block writing the M0 specifications: delivery mechanism, backend topology, reference-document location, slice plan structure, CI/CD scope and when M0 is built.

Nothing has been written to the repository. The M0 specification PR is the first write after your approval.

## Baseline and scope freeze

The baseline is frozen as of 22 Oct 2026. Specifications may add precision but not features, screens, agent capabilities or architectural parts.

| # | Authoritative document | Where it lives now | Version frozen |
| --- | --- | --- | --- |
| 1 | Product Requirements Document | Project file Cenomi\_Dashboard\_Intelligence\_Agent\_PRD.md | As uploaded |
| 2 | Technical Architecture & Implementation Plan | Project file …Technical\_Architecture\_and\_Implementation\_Plan.md | As uploaded |
| 3 | Admin & Tenant Dashboard API Reference | Project file ADMIN\_TENANT\_DASHBOARD\_API\_REFERENCE.md | Generated 2026-10-13 |
| 4 | DX1–DX6 design artifacts | [Canvas design artifact](https://claude.ai/artifact/WyJr2wZFCGVdBY2a13uGyM) | Version 27 |
| 5 | Consolidated Design Decision Register | [Final Design Gate doc](https://claude.ai/artifact/FR1f4Feb9ae8uvSgwjdtGv), Decision register tab | 141 decisions + 22 Oct gate decisions |
| 6 | Final Design Gate Review | Final Design Gate doc, Design review report tab | 22 Oct outcome recorded |
| 7 | KPI and Synthetic Data Reconciliation Report | Final Design Gate doc, KPI tab; dataset sd-2026.10.20-01 | 51/51 checks |

The precedence order is: your explicit instructions, then approved decisions, then the PRD, the TA plan, the API Reference and the repository. ED-03 proposes frozen copies of documents 1–3 and exports of 5–7 in docs/reference/, so that Cursor reads them from the repository.

**Change control:** a change to scope or design is a change request (CR-nnn) in plans/STATUS.md. It must cite a PRD requirement or carry your approval. If it is architectural it also gets an ADR. A specification that finds a gap records it as an open question and does not decide it.

## How to read this plan

Tabs 1–7 are the seven items you asked for, in that order. The five tabs after them carry the supporting detail that items 4, 6, 7, 8 and 9 of your brief call for.

| Tab | Answers |
| --- | --- |
| 1 · Milestone dependency plan | Final dependency graph, contract freezes, what runs concurrently (brief items 1, 10) |
| 2 · Five-day vertical slice | Exact slice scope, day plan, demo journeys and gates (item 2) |
| 3 · Full-scope roadmap | Deliverables, interfaces, dependencies, acceptance, tests and gates per milestone (item 3) |
| 4 · Specification inventory | Every specification and its writing order (item 5) |
| 5 · Repository structure | Proposed tree and ownership rules |
| 6 · M0 authoring plan | What gets written first, how it is reviewed, M0 task cards and gate |
| 7 · Decisions for approval | Engineering decisions still needed |
| Stack and runtime | Stack, version lines, processes and boundaries (item 4) |
| Sources of truth | Canonical source per concern (item 6) |
| Golden data and evaluation | Fixtures, expected outputs, evaluation, detector and E2E cases (item 7) |
| Local development and CI | Compose, environment, database init, seeding, tests, CI (item 9) |
| ADR process and STATUS | ADR process and the STATUS.md template (item 8) |

# ADR process and STATUS.md

Architecture decisions are recorded as ADRs in docs/adr; progress, blockers and change requests live only in plans/STATUS.md. The register of DR and DXD decisions stays the frozen design baseline, and an ADR cites those IDs rather than restating them.

## When an ADR is required

- A change to a contract, the stack or a version line, a module boundary, the database roles or schemas, the security model, or the agent lifecycle.
- Any engineering choice not already fixed by a DR or DXD decision, such as ED-01 to ED-11 once you decide them.
- A deviation from the design baseline that you approve through a CR.

An ADR is not needed for naming, internal refactoring inside one module, or test additions.

## ADR lifecycle

1. **Proposed:** I write it in the milestone PR, with context, options, decision, consequences and the DR, DXD, GDQ or ED IDs it rests on.
2. **Accepted:** you approve the PR. The ADR index (docs/adr/README.md) is regenerated.
3. **Superseded:** a later ADR names it; the old one stays, with a link forward. Nothing is deleted.
4. **Rejected:** kept for the record, with the reason.

Template: Title · Status · Date · Decision IDs · Context · Options considered · Decision · Consequences · Verification (the test or gate that proves it holds).

## Initial ADRs

| ADR | Title | Rests on | PR |
| --- | --- | --- | --- |
| 0001 | Record architecture decisions | ED-01 | M0 |
| 0002 | Repository structure and single sources of truth | DR-034 (docs part superseded), ED-03, ED-04 | M0 |
| 0003 | Technology stack and version pinning | DR-027 | M0 |
| 0004 | Contract pipeline and bootstrap rule | DR-028 | M0 |
| 0005 | Backend as a modular monolith; agent in-process | ED-02 | M0 |
| 0006 | Database roles, schemas and read-only business data | DR-013, 021, 029 | M0 |
| 0007 | Metric registry, SQL templates and the as\_of parameter | DR-004, 030, 042 | M1 |
| 0008 | AccessScope authorization model | DR-019, 020; DXD-38, 56, 85 | M1 |
| 0009 | LLM adapter, primary and fallback, replay provider | DR-014, 015; GDQ-12; ED-08 | M3 |
| 0010 | AG-UI 1.0 pin and event mapping | DR-016, 017; GDQ-11; ED-10 | M4 |
| 0011 | ECharts 5.6.0, verification gate and fallbacks | DR-007; DXD-21, 23, 61; GDQ-06, 07 | M2 |
| 0012 | Materialized as-of snapshots | DXD-80; GDQ-03 | M1 |
| 0013 | Insight runner protocol and idempotency | DXD-86 and related | M6 |
| 0014 | Evaluation scoring | DR-036; ED-11 | M5 |

## Change requests under the scope freeze

A CR records: ID, date, requester, the requirement it cites (or “needs approval”), what changes, the affected specs, contracts and tests, the ADR if any, and your decision. Composer never opens a CR on its own; a task that cannot be done within its card stops and reports.

## plans/STATUS.md template

```markdown
# STATUS — Cenomi Dashboard Intelligence Agent POC
Updated: YYYY-MM-DD · Baseline: DX1–DX6 (canvas v27), GD 2026-10-22 · Dataset: sd-2026.10.20-01 (hash …)

## Current phase and milestone
Phase: Specification | Slice build | Full scope
Current milestone: M0 · State: Specs in review | Building | Gate passed
Next gate: <gate> · Criteria: <link to plan section>

## Milestones
| Milestone | Specs PR | Spec state | Build state | Slice cards | Gate | Blocked by |

## Contract freezes
| CF | Contracts | Frozen in | Date | Version |

## Specifications
| # | Path | State (Draft/In review/Approved) | PR | Open questions |

## Decisions
Approved this phase: GDQ-01–12 (2026-10-22); ED-xx …
Pending: <ID> — needed before <milestone> — owner

## Verification gates
| Gate | Status | Evidence |
| ECharts 5.6.0 (GDQ-06) | | |
| AG-UI spike (GDQ-11) | | |
| Model configuration (GDQ-12) | | |

## Change requests
| CR | Date | Summary | Cites | Decision |

## Blockers and risks
| ID | Blocker or risk | Owner | Since | Next action |

## Completion criteria for the current milestone
- [ ] … (copied from the milestone plan’s gate)
```

STATUS.md is updated at every merge and every gate, by whoever merges. Milestone plans hold scope and task cards, never status, so status never exists in two places.

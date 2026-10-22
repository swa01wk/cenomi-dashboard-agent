# Design decisions · DX4 corrections and DX5 (22 Oct 2026)

Source of truth: the "Cenomi Dashboard Agent — POC Design" canvas (pages DX4 and DX5). This note summarises the decisions so later sessions can find them.

## DX4 · conditionally approved, corrections completed
- DXD-31 (DXQ-05 C): no composite score by default. Instead the answer shows a multi-KPI table, the leader on each KPI (marked "Leader" in text), magnitude, severity and a stated ordering rule. A composite is produced only on explicit request, classified Derived, with a method card covering weighting, normalisation, missing data and limitations.
- DXD-32 (DXQ-06 C): analytical selections are local to each investigation (thread). The dashboard keeps its own selection state. A selection moves between them only by explicit, source-labelled import, which is visible in the composer before sending.
  - Supersedes DXD-29 and DX2 DXD-12 for analytical context.
  - DXD-25…28 remain in force.
- DXD-33 (DXQ-07 A): history is immutable. Answers show their dataset version. Re-running against current data is always an explicit action, and nothing refreshes silently.
- DXD-34: KPI reconciliation. J1's 41 counts approvals of all types older than a month at Rawdah Point; J3's 32 counts proposals of all ages there. Both reconcile:
  - Rawdah Point: 71 pending, 41 older than a month.
  - Central: 130 pending, 62 older.
  - All regions: 232 pending, 92 older.
  - No data or KPI definition changed. Approval statements now state which population they count.
- DXD-35: coverage semantics. A total built from incomplete reports is labelled "observed subset" (J4: 87 of 3,000 checked units, 18 of 25 malls). The full total is shown as Unavailable and is never estimated.
- DXD-36: every statement and visual carries an evidence envelope with these fields: class, metric and version, filters, access scope, freshness, dataset version and coverage.
- DXD-37: retrying a failed step creates answer v2, marked as revising v1. v1 is kept exactly as generated. "Run again" starts a new run with a new requestId.
- DXD-38: context isolation. Switching threads or roles, removing scope chips and resuming an investigation never widen access or import context implicitly. Imports and resumes are re-checked against the current access scope.
- DXD-39: accessibility. States are conveyed in text, not colour alone. Selections expose aria-pressed. The inspector is a dialog with focus management and Escape to close. A polite live region announces status. Text contrast is at least 4.5:1.
- DXD-40: AG-UI handoff contracts are recorded on their own board: the event → state reducer, run identity (threadId, runId, requestId, seq), cancellation, replay and reconnection, retry kinds, idempotency, and the SDK assumptions A1–A8 to verify in M0.

## DX5 · in review (awaiting approval before DX6)
- Proposed DXD-41…50:
  - Rendering takes values from the result (resultRef); payloads carry no numbers.
  - A closed registry of 15 component kinds.
  - Representation alternates per result shape, switchable with "View as".
  - One formatting module.
  - An 8-state vocabulary: default, partial, zero, empty, undefined ratio, loading, error, unavailable.
  - Size classes: 760, 420, 360 and 358 px.
  - A 7-step validator. On failure it falls back to a table, or withholds the visual when the user lacks access or the result is unknown.
  - An evidence envelope on every component.
  - Keyboard drilldown that emits a thread-local selection_ref.v1.
  - State fixtures are labelled as fixtures.
- Open questions DXQ-08…11:
  - Who picks the representation.
  - Which fallback to use.
  - How treemaps behave on narrow widths.
  - The maximum number of components per answer.

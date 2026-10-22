# Design decisions: DX5 refinements and DX6 (proposed)

Status as of 22 Oct 2026. This extends `claude/DESIGN_DECISIONS_DX4_DX5.md` (DXD-01…50). Design-only work: nothing in the GitHub repository was changed, and the user commits planning artefacts manually (DR-035 A). The canvas lives at https://claude.ai/artifact/WyJr2wZFCGVdBY2a13uGyM (v24, pages DX5 and DX6).

## DX5: approved with refinements (refinements completed in v23)

| ID | Decision | Rule |
|---|---|---|
| DXD-47 | Validation and fallback (amended) | Server-side validation, then defensive re-validation on the client. Per DXD-57, the deterministic table is used only for presentation failures on a result that is resolved, authorized and verified. |
| DXD-51 | Bounded representation policy (DXQ-08 A) | The agent chooses among the allowed representations based on intent, result shape, dimensions, accessibility preference and display space (rules P1–P6). The user can switch with View as. |
| DXD-52 | Deterministic table fallback (DXQ-09 A) | If a presentation payload is invalid, show a table built from the verified, authorized result. |
| DXD-53 | Treemap below 400 px (DXQ-10 A) | Render a ranked list that keeps the same keys and selection. |
| DXD-54 | Component budget (DXQ-11 A) | Up to 3 components in the panel and 6 in the workspace. Anything more is reached through Open in workspace or the inspector. |
| DXD-55 | Verified calculations | Every derived value comes from a calc record: method, formula, operands, periods, metric definition and evidence refs. The verifier recomputes it. Neither the LLM nor the renderer derives KPI values; the renderer only computes geometry. |
| DXD-56 | Authorization by grants | Compare the viewer's current grants against the result's scope, dimension values and records, never against labels. Revalidate results that are stored or resumed. If a result is only partly authorized, withhold it rather than filter it. Never name entities outside the grant. |
| DXD-57 | Failure taxonomy | Presentation, calculation, authorization, unknown result, stale, partial and unreadable are separate classes, each with its own outcome. |
| DXD-58 | Fallback preserves boundaries | The fallback keeps row limits and paging, evidence, partial coverage, formatting and authorization. |
| DXD-59 | Subset disclosure | Declare top-N, pages, samples and aggregates (`data-subset`) and disclose them in text. The renderer never aggregates. |
| DXD-60 | Continuity | Envelope and selection survive View as, moves between panel and workspace, expand and resume. Resume runs authorization again. |
| DXD-61 | ECharts at the Design Gate | Validate on the pinned Apache ECharts 5.6.0 runtime. HTML stand-ins do not count as evidence. |
| DXD-62 | Implementation priority | Keep the 15-kind registry. Build 10 core kinds first: kpi, text, table, bar, trend, notice, unavailable, evidence, records, insight. The 5 specialized kinds (compare, heatmap, funnel, treemap, method) use DX3 primitives. Kinds not yet built render through the table fallback. Total is about 20 h; the minimal path is about 14 h. |

## DX6: Proactive intelligence and Insight Inbox (all proposed, awaiting review)

### Detectors (deterministic, analytics layer)

| Detector | Rule | Trigger | Audiences | Type |
|---|---|---|---|---|
| D1 Concentration | Share ≥ 50% and value ≥ 20 | Weekly | Admin, region | Risk |
| D2 Sustained deterioration | ≥ 4 consecutive increases plus a minimum change (count ≥ 5, rate ≥ 2 pts) | Weekly / monthly | Admin, region | Risk |
| D3 Sustained improvement | Drop ≥ 50% from a start ≥ 5 | Weekly | Admin, region | Opportunity (P3) |
| D4 Anomaly | More than 2× the trailing 3-period average, and robust z ≥ 3 | Data-load event | Admin, region | Risk; a single period becomes Watch |
| D5 Coverage gap | Coverage < 90%; repeated misses raise urgency | Data-load event | Admin, region (split) | Data quality |
| D6 Cross-KPI co-movement | Two D2-type rules fire on the same entity in the same window | Weekly | Admin, region | Risk (cluster) |
| D7 Lease trend | ≥ 3 consecutive declines and ≥ 10% below the trailing average | Weekly | Admin, region, that lease | Risk; no baseline becomes Watch |
| D8 Tenant action required | ≥ 1 request in Action required | Status-change event | That lease only | Action needed |

### Decisions

| ID | Decision | Rule |
|---|---|---|
| DXD-63 | Detection is deterministic | The LLM does not decide what counts as an insight and computes nothing. Insight text is templated with fact tokens and verified like answers. |
| DXD-64 | Detector catalogue v1 | D1–D8. Thresholds are configuration facts and are shown in the "why" text. |
| DXD-65 | Audience-scoped instances, three checks | One instance per audience scope. Visibility is checked against grants at generation, at delivery and on every read. Deep links outside the grants are refused without revealing content. |
| DXD-66 | Transparent scoring | Priority = impact × urgency: P1 ≥ 6, P2 3–5, P3 ≤ 2. Low confidence turns the insight into Watch. Positive findings are P3. |
| DXD-67 | Shared lifecycle, personal triage | Shared states: Open, Investigating, Resolved, Merged, Superseded, Expired. Personal states (per user): New, Seen, Acknowledged, Snoozed, Dismissed. |
| DXD-68 | Dedupe, merge, re-notify, suppress | The dedupe key is detector\|entity\|metric\|audience; a matching key updates the insight silently. Re-notify only on ≥ 10% worsening or a band rise. Signals on one entity merge into a cluster. Dismissed and snoozed insights stay suppressed until their resurface rule applies. |
| DXD-69 | Quiet by default | These outcomes are logged decisions with reasons, visible to admins: not material, no change, within normal range, correlation only, not concluded, not evaluated, duplicate. |
| DXD-70 | Delivery | P1: in app immediately, and the related dashboard cards are marked. P2/P3: in-app daily digest. Watch: inbox and card indicators only; it never raises the badge. |
| DXD-71 | Investigation handoff | Opens a workspace thread with the insight imported explicitly and labelled. The shared status becomes Investigating, with a link to the thread. |
| DXD-72 | Feedback | Usefulness ratings and dismiss reasons are logged for detector review. No automatic threshold changes in the POC. A user can mute a detector for an entity. |
| DXD-73 | Scenario history | A declared history extension (weekly from 11 Aug, monthly from April), anchored to sd-2026.10.20-01. Every series ends on the dataset value. These are the golden scenarios for M5. |
| DXD-74 | Five-day priority | Core: runner (one schedule, one event), D1, D2, D5, D6 merge, inbox list/detail, acknowledge, dismiss, investigate, visibility checks, candidate log. Deferrable: D3, D4, D7, D8, snooze, digest, feedback review. |

### Open questions (recommendation listed first)

- **DXQ-12 Cadence:** (a) weekly/monthly schedules plus data-load events · (b) daily · (c) events only.
- **DXQ-13 Portfolio insights for regional managers:** (a) split per region at generation (INS-105 / INS-105C) · (b) not delivered.
- **DXQ-14 Digest channel:** (a) in-app only in the POC · (b) email as well.
- **DXQ-15 Positive findings:** (a) P3 Opportunity insights · (b) a weekly summary only · (c) not shown.
- **DXQ-16 Tenant proactive insights:** (a) own-lease Watch and Action-needed insights (D7, D8) · (b) none in the POC.

### Golden scenarios

- **S1** INS-107: P1 cluster at Rawdah Point. Approvals 22→41, which is 66.1% of Central.
- **S2** INS-104: P2, Mirage vacancy rising six months in a row (47→58). Updated silently.
- **S3** INS-105/105C: P2 coverage gap, seven malls missing September reports.
- **S4** INS-106: Watch, Gulf Gate mismatch 7.7% against a baseline of about 2.4%.
- **S5** INS-103: P3, Qasr old approvals 9→2.
- **S6** INS-108/T-201: Watch, lease T-31206 sales fell three months in a row, with no prior-year baseline.
- **S7** T-202: P2, tenant action needed (2 requests).
- **S8** INS-090: resolved automatically.

### Golden no-notification cases

- **N1** Duplicate 39→41 (+5.1%), merged.
- **N2** Not material: 23→25.
- **N3** No change: Sandstone flat at 13.0%.
- **N4** Within normal range: Cedar Park robust z 1.8.
- **N5** Correlation only: r = −0.41 (−0.35 without Rawdah).
- **N6** Tenant benchmark not evaluated, because of isolation.
- **N7** Mirage +3.6%, updated silently.
- **N8** Eastern trend not concluded: coverage 5 of 7.

### Verification and carried items

Verification run on the design prototype:
- Browser: 34/34
- Interaction logic: 62/62
- Data and grounding: 216/216, with 44 texts grounded

Carried to the final Design Gate:
- Real ECharts 5.6.0
- axe-core and screen reader
- Confirming the history extension as M1 seed scope

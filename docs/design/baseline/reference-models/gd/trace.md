| Requirement | What it asks | Design decisions | Design evidence | Architecture / spec home | GD status | Gap |
| --- | --- | --- | --- | --- | --- | --- |
| PAR-A01 | Properties card | DXD-16, 18; DR-020 | DX2 Admin · DX2-Verify | Metric layer + card adapter · KPI_CATALOG | Designed |  |
| PAR-A02 | KPI tiles (expiring, active, pending sales) | DR-002; DX2 notes | DX2 Admin | KPI_CATALOG (DUAL metrics) | Designed |  |
| PAR-A03 | Lease requests donut | DXD-24, 25 | DX2 · DX3 #3 | viz primitives (ECharts pie) | Verification pending | Real ECharts run |
| PAR-A04 | Sales funnel stage flow | DR-008, DR-018 | DX2 · DX3 #4 | HTML stage flow | Designed |  |
| PAR-A05 | Action required list | DR-001 | DX2 Admin | Notifications metric | Designed |  |
| PAR-A06 | Pending approvals half gauges | DXD-80; DX2 notes | DX2 · DX3 #5 · DX6 reconciliation | approvals.pending_by_delay v1 | Verification pending | Gauge arc fidelity on real ECharts |
| PAR-A07 | Pending amendments heatmap | DXD-05, 25 | DX2 · DX3 #6 · DX4 J1 | amendments.pending_by_age_band v1 | Verification pending | Real ECharts run |
| PAR-A08 | Service requests treemap + permit strip | DXD-22, 23 | DX2 · DX3 #7–8 | treemap primitive or HTML squarify | Verification pending | Treemap route GDQ-07 |
| PAR-A09 | Fit-out rings + handover callout | DR-002 | DX2 · DX3 #9 | gauge primitive | Verification pending | Real ECharts run |
| PAR-A10 | Fit-out drawings stacked bars | DR-002 | DX2 · DX3 #10 | bar primitive | Verification pending | Real ECharts run |
| PAR-A11 | Drawing grades A–D | DR-046, DR-047 | DX2 · DX3 #11 | fitout_drawing_documents | Verification pending | Real ECharts run |
| PAR-A12 | Unit discrepancy diverging bars | DXD-14, 35 | DX2 · DX3 #12 · DX4 J4 | unit_discrepancy.units v1 | Verification pending | Real ECharts run |
| PAR-T01 | Tenant tiles incl. payments unavailable | DXD-16; DR-019 | DX2 Tenant | Tenant adapters | Designed |  |
| PAR-T02 | Tenant action required (active profile) | DXD-93 | DX2 Tenant · DX6 T-202 | Lease scope | Designed |  |
| PAR-T03 | Reported sales chart | DXD-20 | DX2 Tenant · DX3 #13 | tenant_sales.reported_monthly | Verification pending | Real ECharts run |
| PAR-T04 | Tenant SR by status / category | DR-001 | DX2 Tenant · DX3 #14–15 | Server-side counts | Verification pending | Real ECharts run |
| PAR-T05 | Documents to upload | DXD-93 | DX2 Tenant · DX6 | Tenant documents metric | Designed |  |
| PAR-T06 | Announcements and events | DR-001 | DX2 Tenant | Server de-dup | Designed |  |
| PAR-T07 | Leasing opportunities | DXD-13 | DX2 Tenant (no map) | Public mall list | Designed |  |
| PAR-T08 | Prospective journey | DR-026 | — | PRODUCT_SPEC (stretch) | Deferred | Stretch |
| PAR-X01 | Empty, loading, error states | DXD-16, 45 | DX2 States · DX5 catalogue | One state vocabulary | Designed |  |
| PAR-X02 | Filters reach retrieval and agent context | DXD-05, 15 | DX2 panels · DX4 J1/J3 | Context store · AG-UI state | Designed |  |
| PAR-X03 | Drilldown = same population | DXD-11, 18, 27, 49 | DX2-Verify · DX4 J1 | Records = row form of the metric | Partial | DX2 record fixtures random (C21) |
| MET-01 | Charts and agent share one metric service | DXD-30, 41 | DX2 → DX4 → DX5 same model functions | cenomi_analytics | Designed |  |
| MET-02/03 | Registry fields; parity vs corrected ids | DR-042; DXD-80 | DX4 METRICS definitions | KPI_CATALOG + YAML | Designed | Catalog not yet written |
| MET-04 | Eight caveats as tests with exposing rows | DR-002; DX2 notes | DX2 notes | KPI_CATALOG · seed | Partial | Rows to be listed in the seed manifest |
| MET-05 | Numeric precision and formatting | DXD-44; DR-044 | DX5 formatter | One formatting module | Designed |  |
| MET-06 | Derived metrics; zero denominators | DXD-55, 59 | DX5 verified calculations | derive tool + verifier | Designed |  |
| MET-07 | No cohort conversion without lineage | DR-022, 023 | — | get_linked_cohort | Spec only | No journey (GDQ-09) |
| DATA-01–03 | Schema, scale, deterministic seed | DR-043, 047; DXD-81 | DX6 reconciliation | DATABASE_SCHEMA · SYNTHETIC_DATA_STRATEGY | Designed | Physical schema in M0 |
| DATA-04/05 | Lifecycles and named scenarios with truth | DXD-81, 82 | DX6 scenarios S1–S9, N1–N11; cohorts | Scenario manifest | Designed | TA §5.3 scenarios still to map |
| DATA-06/07 | Labels hidden from agent; synthetic marking | DXD-09 | Every board | seed_meta grants | Designed |  |
| AI-01 | Explain a KPI | DXD-04 | DX4 inspector Definition tab | describe_metric | Designed |  |
| AI-02 | Retrieve with inherited filters | DXD-05, 15 | DX4 J1 | get_metric | Designed |  |
| AI-03 | Deterministic math | DXD-55 | DX5 calc records | derive | Designed |  |
| AI-04 | Comparable comparisons | DXD-31 | DX4 J2, regions compare | compare | Designed |  |
| AI-05 | Cross-KPI investigation, no causal claim | DXD-31, 89 | DX4 J2 · DX6 INS-107, N5 | Planner + relationship graph | Designed |  |
| AI-06 | Pronouns and selected values | DXD-25, 26, 32 | DX4 J1 | selection_ref.v1 · analytical state | Designed |  |
| AI-07 | Facts vs hypotheses vs actions | DXD-08 | DX4–DX6 statement labels | AnswerDraft schema | Designed |  |
| AI-08 | Partial and absent data | DXD-14, 35 | DX4 J4, J5 | Coverage + unavailable catalog | Designed |  |
| AI-09 | Inspectable provenance | DXD-36, 48 | DX4 inspector · DX5 envelope | Evidence envelope | Designed |  |
| AI-10 | No cross-tenant leakage | DXD-38, 56, 65, 85 | DX4 J8, J10 · DX5 validator · DX6 K7, K11 | AccessScope | Designed |  |
| AI-11/12 | Coverage classes; no fabricated confidence | DXD-35, 57 | DX4, DX5 | Outcome attribute | Designed |  |
| L3 | 18 Level-3 items | DR-031, 032 | DX4 J1–J10 | AGENT_ARCHITECTURE | Designed |  |
| L4-CTX | Context assembly, continuity | DXD-06, 17, 32, 33, 60 | DX4 J7, J10 | Analytical state store | Designed |  |
| L4-XKPI | Cross-KPI reasoning | DXD-31 | DX4 J2 | get_panel / correlate | Designed |  |
| L4-INV | Multi-step investigation, hypotheses | DR-032; DXD-37 | DX4 J2, J6 | DAG executor | Designed |  |
| L4-DQ | Data quality and coverage | DXD-14, 35 | DX4 J4 · DX6 INS-105 | get_data_coverage | Designed |  |
| L4-BIZ | Business impact, role-aware | DXD-31 | DX4 J2 | Prompt policy | Partial | Impact measures limited (no revenue metric) |
| L4-UX | GenUI composition, chart↔conversation | DXD-41–62 | DX5 | GENERATIVE_UI | Verification pending | Real ECharts; PRD catalog mapping GDQ-02 |
| L4-REUSE | Result reuse (“show as table”) | DXD-43 | DX5 View as | reuse_dataset | Designed |  |
| L4-CLAR | Adaptive clarification | DR-032 | DX4 (clarification state only) | Clarification policy | Partial | No designed clarification journey |
| L5-P1 | Anomaly, discovery, prioritization | DXD-63–66, 89–91 | DX6 S1–S5, N1–N11 | cenomi_insights | Designed |  |
| L5-P2 | Monitoring, notifications, lifecycle, feedback | DXD-67–72, 75–88 | DX6 K1–K12 | Runner + inbox | Designed | Feedback re-ranking GDQ-05 |
| GUI-01 | 15 allowlisted components | DXD-42, 62 | DX5 registry | Registry | Partial | Differs from PRD §7 list (GDQ-02) |
| GUI-02 | Intent → composition | DXD-51 | DX5 policy P1–P6 | Composer | Partial | PRD “Distribution → donut or stacked” has no kind |
| GUI-03 | Interactions | DXD-25–28, 49 | DX3 · DX5 | selection_ref.v1 | Designed |  |
| GUI-04 | Bound to validated data | DXD-41, 47, 57 | DX5 validator | Server + client validation | Designed |  |
| GUI-05 | No fabricated charts for empty data | DXD-45 | DX5 states | Unavailable kind | Designed |  |
| GUI-06 / NFR-02 | Accessible alternatives; keyboard, screen reader | DXD-24, 39, 49 | DX3 · DX5 · DX6 smoke checks | viz primitives | Verification pending | axe-core + screen reader on real build |
| AGUI-01/02 | Pinned bidirectional stream; safe progress | DR-016, 017; DXD-40 | DX4-AGUI | cenomi_agui | Verification pending | SDK version check (GDQ-11) |
| AGUI-03 | Chart → agent and agent → dashboard sync | DR-025; DXD-05 | DX4 J1, J3 | Frontend tool | Designed |  |
| AGUI-04 | Ordering, reconnect, recovery | DXD-37, 40 | DX4 J9 | Run identity + seq | Designed |  |
| SEC-01–03 | Read-only, default deny, tenant cannot switch | DR-013, 019, 020; DXD-56, 85 | DX4 J8, J10 · DX6 K7, K11 | AccessScope + DB roles | Designed |  |
| SEC-04/05 | Injection as data; no model SQL/HTML/URLs | DXD-42, 47 | DX5 safety step | Validator | Designed |  |
| SEC-06/07 | No secrets in events; no REF defects | DR-001 | — | Observability rules | Spec only | Log-scan test in M3 |
| NFR-01 | Latency targets | DR-032 | — | Performance budget | Spec only | Measured in M5 |
| NFR-03/04 | Tracing; cache by scope + data version | DXD-40 | DX4 execution tab | Run ledger, dataset store | Designed |  |
| EVAL-01–06 | 150 questions, goldens, UI types, context, regeneration, demos | DXD-81, 82 | DX6 goldens; DX5 validator samples | EVALUATION_PLAN | Partial | Benchmark set to author |
| DEL-01/02 | Admin first; gates | DR-041 | This gate | plans/STATUS | Designed |  |
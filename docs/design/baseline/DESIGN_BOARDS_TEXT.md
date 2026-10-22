# DX1–DX6 design boards — extracted text

Generated 2026-10-22 from the local copy of the design canvas (published version 27, plus the DX5-GenUI wording fix). One section per board, in canvas order. Text only: layout, charts and interaction behaviour are preserved in renders/*.png and in the runnable boards/*.dc.html files.


# DX1 · Information architecture

## DX1 · App shell prototype (interactive, mid-fidelity)

File: boards/Main.dc.html · Render: renders/Main.png · interactive prototype

```text
Cenomi Dashboard Agent
POC
SYNTHETIC DATA · AS OF 20 OCT 2026
Ask about your portfolio…
/
4
Portfolio admin
Tenant · Lumen Retail Co.
Dashboard
Workspace
Insights
Portfolio overview
Portfolio admin · all 3 regions · 25 malls (synthetic)
Each card keeps its own filters (V2 parity)
Portfolio properties
No card filters
Stat tiles (properties, units, occupied, vacant, GLA) + unit occupancy meter
Action required
No card filters
Unread action-required notifications (list)
Sales funnel
2026 · All months · All regions · All malls
Four-stage flow — lease requests → leads → proposals → contracts, with signed / unsigned splits
Leasing and sales KPIs
No card filters
3 stat tiles — expiring leases · active leases · pending sales submissions
Lease requests
2026
Donut — by unit type / by registration source
Drawing document status
2026 · All regions · Architectural
Stacked columns A / B / C / D by mall · chart ↔ table
Fit-out and handover
2026 · All months · All regions · All malls
4 inspection progress rings + pending-handover callout
Fit-out drawings
2026 · All months · All regions · All malls
Horizontal stacked bars by discipline — submitted · pending · approved
Pending approvals
All regions · All malls
Half gauges — proposals · contracts · leases, share older than one month
Pending amendments
2026 · All months · Central · All malls
Expansion
HoldOver
Renewal
Termination
4 wk+
1
2
18
4
4 wk
0
1
3
1
3 wk
1
0
2
2
2 wk
2
1
1
1
1 wk
1
0
2
1
Click a cell to make it the agent's context. Full heatmap design in DX2/DX3.
Service requests
2026 · All months · All regions · All malls
Treemap by category + work-permit strip
Unit discrepancy
2026 · Sep · Mall-wise
Diverging bars — mismatch ◂ ▸ match
```

## DX1 · Navigation map — core analytical loop

File: boards/IA.dc.html · Render: renders/IA.png

```text
Navigation map — the core analytical loop
Seeing a KPI → asking a question → investigating → understanding an insight → acting. Five destinations; everything else is an overlay that keeps the user where they are. Solid border = screen or docked panel · dashed border = overlay.
Admin or Tenant dashboard
Entry screen. V2 cards with their own filters
Card focus
Chart · Table · Records · Definition
Agent panel (docked)
Quick questions with visible context chips
Analytical workspace
History · conversation · pinned canvas
Inspector
Evidence · Definition · Records · Execution
Notifications
Bell in the top bar, on every admin screen
Insight inbox
Replay checkpoints · lifecycle · feedback
Expand
Ask
Open
Inspect
Ask on a card · select a data point · top-bar search
Back to dashboard — filters and selection kept
Open inbox
Investigate
Inspector opens from anywhere. Every answer, generated chart, dashboard card and insight has an Evidence or Records action. The inspector slides over the current screen and closes back to it.
Filter changes need confirmation. When the agent suggests a dashboard filter, a confirm or dismiss control appears in the conversation. Applied changes are flagged on the card and can be undone.
Tenant persona. Dashboard, agent panel, workspace and inspector only — no insight inbox or notifications bell. Every view is limited to the tenant's own leases.
```

## DX1 · Canonical screen inventory

File: boards/Inventory.dc.html · Render: renders/Inventory.png

```text
Canonical screen inventory

Smallest set that demonstrates the whole POC: 4 screens, 1 docked panel and 4 overlays. The 11 surfaces in the brief map onto these (right-hand table) — none needs its own page.

SURFACE	KIND	PERSONAS	ENTRY POINTS	EXITS	PRIMARY ACTIONS	SECONDARY ACTIONS
Admin dashboard	Screen	Admin roles, by permission	Sign-in landing · rail · back from any screen	Card focus · agent panel · workspace · inbox	Read KPIs · change a card's filters · select a data point · ask on a card	Expand card · drilldown to records · definition tooltip
Tenant dashboard	Screen	Tenant users	Sign-in landing · rail	Card focus · agent panel · workspace	See next actions · documents · requests · sales	Ask on a card · change sales year or lease
Analytical workspace	Screen	All	“Open in workspace” · Investigate on an insight · rail	Back to dashboard · inspector	Multi-step investigation · pin results to the canvas · resume a past thread	Rename or delete a thread · switch chart ↔ table · export view
Insight inbox	Screen	Admin roles	Bell · rail	Workspace (Investigate) · inspector	Triage New → Acknowledged / Dismissed / Resolved · Investigate	Give feedback · browse replay checkpoints · filter by severity
Agent panel	Docked	All	Ask icon on a card · data-point selection · top-bar search · /	Workspace · inspector · close	Ask · follow up · confirm or dismiss suggested filter changes	Remove a context chip · suggested questions · view steps
Card focus	Overlay	All	Expand icon on any card or generated chart	Close · agent panel	Chart · Table · Records · Definition tabs	Ask about this card · select a row as context
Inspector	Overlay	All	Evidence or Records on an answer, chart, card or insight	Close (returns to the same place)	Evidence · Definition · Records · Execution tabs	Copy scope · ask about a record
Notifications	Overlay	Admin roles	Bell in the top bar	Inbox · close	Open an insight	Mark all seen
Filter-change confirmation	Inline	All	An agent answer that suggests a filter change	Apply · dismiss · undo	Apply the suggested filter to the named card	Undo from the card’s “changed” flag
BRIEF ASKS FOR	DELIVERED AS
Admin Dashboard	Admin dashboard screen
Tenant Dashboard	Tenant dashboard screen
Agent conversation panel	Agent panel (docked)
Expanded analytical workspace	Analytical workspace
Investigation workspace	Same screen — one place for multi-step work
KPI detail views	Card focus → Definition and Chart tabs
Data exploration tables	Card focus → Table / Records; generated tables
Evidence inspector	Inspector → Evidence tab
Insight inbox	Insight inbox screen
Proactive monitoring view	Inbox header: replay checkpoint timeline
Agent activity / history	Workspace history list · Inspector → Execution

Why the workspace and investigation merge. Splitting “conversation” from “investigation” would force users to choose a mode before they know how deep a question goes. One workspace, with pinned results, grows with the question.

Why monitoring has no screen of its own. Monitoring in this POC is synthetic historical replay. Its output is insights, so the replay timeline sits on top of the inbox rather than on a separate dashboard that would look like live monitoring.

Persona switch is demo-only. The top-bar switch between Portfolio admin and Tenant exists for the design review and the POC demo. Each persona sees only what its role permits.
```

## Direction A · Ink & Violet (selected)

File: boards/Direction-A.dc.html · Render: renders/Direction-A.png

```text
Cenomi Dashboard Agent
SYNTHETIC DATA · AS OF 20 OCT 2026
Portfolio admin
Ink and Violet
Calm, light, data-first. Deep ink chrome frames a quiet canvas; violet is reserved for the agent and for selection. Stays closest to the V2 palette roles.
Malls
25
8,140 units
Occupied units
7,114
87.4% of units
Vacant units
1,026
12.6% of units
Fit-out drawings
2026 · All regions
Submitted
Pending
Approved
Mechanical
Architectural
Electrical
Palette
Inter Tight for headings · Inter with tabular figures for data and body
Pending amendments
Renewal × 4 wk+ (18)
Why is this so high?
OBSERVED
18 renewal amendments in Central are 28+ days old.
DERIVED
40.9% of Central’s 44 pending amendments.
HYPOTHESIS
Two malls may share a slow review step — not confirmable from this data.
RECOMMENDATION
Start with the 9 Rawdah Point Mall renewals.
Evidence · 1 metric
Records
```

## Direction B · Night Operations (optional dark theme later)

File: boards/Direction-B.dc.html · Render: renders/Direction-B.png

```text
Cenomi Dashboard Agent
SYNTHETIC · AS OF 2026-10-20
Portfolio admin
Night Operations
Dark, dense, control-room. Monospaced figures and tight cards fit more on screen; bright accents carry status. Strong for monitoring, heavier for tenants.
MALLS
25
8,140 units
OCCUPIED UNITS
7,114
87.4% of units
VACANT UNITS
1,026
12.6% of units
Fit-out drawings
2026 · All regions
Submitted
Pending
Approved
Mechanical
Architectural
Electrical
Palette
IBM Plex Sans for UI · IBM Plex Mono for every figure
Pending amendments
Renewal × 4 wk+ (18)
Why is this so high?
OBS
18 renewal amendments in Central are 28+ days old.
DER
40.9% of Central’s 44 pending amendments.
HYP
Two malls may share a slow review step — not confirmable from this data.
REC
Start with the 9 Rawdah Point Mall renewals.
Evidence · 1 metric
Records
```

## Direction C · Warm Editorial (not selected)

File: boards/Direction-C.dc.html · Render: renders/Direction-C.png

```text
Cenomi Dashboard Agent
Synthetic data · as of 20 October 2026
Portfolio admin
Dashboard
Workspace
Insights
Warm Editorial
Narrative-led and approachable. Serif headlines and generous space make answers read like a briefing. Friendlier for tenants and executives; less dense.
Malls
25
8,140 units
Occupied units
7,114
87.4% of units
Vacant units
1,026
12.6% of units
Fit-out drawings
2026 · All regions
Submitted
Pending
Approved
Mechanical
Architectural
Electrical
Palette
Source Serif 4 for headlines and key figures · Source Sans 3 for UI
Pending amendments
Renewal × 4 wk+ (18)
Why is this so high?
Two Central malls hold most of the old renewals.
OBSERVED — 18 renewal amendments in Central are 28+ days old.
DERIVED — 40.9% of Central’s 44 pending amendments.
HYPOTHESIS — the two malls may share a slow review step; not confirmable from this data.
RECOMMENDATION — start with the 9 Rawdah Point Mall renewals.
Evidence
Records
```

## DX1 · Design decision register (approved)

File: boards/DX1-Decisions.dc.html · Render: renders/DX1-Decisions.png

```text
DX1 · Design decision register

Approved by the project owner on 22 Oct 2026. These decisions bind DX2–DX6 and the GENERATIVE_UI and PRODUCT_SPEC documents in M0.

ID	DECISION	WHAT IT MEANS FOR THE DESIGN	APPLIED IN	STATUS
DXD-01	Visual direction	Ink and Violet is the primary design system. Night Operations may follow later as an optional dark theme; Warm Editorial is not pursued.	All stages	Approved
DXD-02	Screen architecture	Four screens — Admin or Tenant dashboard, Analytical workspace, Insight inbox — plus the docked agent panel and four overlays: card focus, inspector, notifications, filter-change confirmation.	DX1 · all	Approved
DXD-03	Agent UX	Hybrid: docked agent panel for quick questions; expandable analytical workspace for multi-step investigations; contextual entry points on every card and data point.	DX2 entry points · DX4	Approved
DXD-04	Shared inspector	One inspector with Evidence, Definition, Records and Execution tabs, used for dashboard metrics, generated components and proactive insights alike.	DX2 card focus · DX4–DX6	Approved
DXD-05	Three kinds of context	Visibly separate (1) card-level dashboard filters, set on the card; (2) the agent's analytical query scope, which the user can narrow or widen in the panel without touching the dashboard; (3) proposed dashboard filter changes, which apply only after confirmation.	DX2 agent panel · DX4	Approved
DXD-06	State preservation	Moving between dashboard and workspace keeps the conversation, selected data points, card filters, pinned results and scroll position.	DX2 · DX4	Approved
DXD-07	Responsive behaviour	Desktop, tablet and mobile designs. Below desktop width the agent opens as an overlay (tablet) or full screen (mobile) instead of permanently narrowing charts.	DX2 responsive board	Approved
DXD-08	Statement labels	Every analytical statement carries a text label — Observed, Derived, Hypothesis, Recommendation, Unavailable. Colour supports the label and is never the only signal; hypotheses also use a dashed outline.	DX4–DX6	Approved
DXD-09	Synthetic data	The reference date and the synthetic-data designation stay visible on every screen, and every card footer repeats "As of 20 Oct 2026 · synthetic data".	All stages	Approved
```

# DX2 · Admin and Tenant dashboards (approved)

## DX2 · Admin dashboard (interactive)

File: boards/Admin.dc.html · Render: renders/Admin.png · interactive prototype

```text
Cenomi Dashboard Agent
POC
SYNTHETIC DATA · AS OF 20 OCT 2026
Ask about your portfolio…
4
Portfolio admin
Dashboard
Workspace
Insights
Design review controls
not part of the product
View as
Portfolio admin · all regions
Leasing manager · all regions
Fit-out manager · Central only
Data state
Live
Loading
Empty
Error
Portfolio overview
Portfolio admin · 3 regions · 25 malls · synthetic data as of 20 Oct 2026
All 12 cards visible for this role
Portfolio properties
Definition
No card filters
Properties
25
8,140 units
Occupied units
7,114
1,412,600 sqm occupied GLA
Vacant units
1,026
214,300 sqm vacant GLA
Unit occupancy
87.4% occupied · 12.6% vacant
As of 20 Oct 2026 · synthetic data
Action required
Definition
No card filters
27
unread notifications need your action
PROPOSAL

Proposal P-24117 for Arcadia Shoes at Rawdah Point Mall awaits your approval

19 Oct 2026
Open request
AMENDMENT

Renewal amendment AMD-24118 for lease T-30512 is ready for review

18 Oct 2026
Open request
SALES DATA

Sales data for Sep 2026 on lease T-32044 needs re-upload

17 Oct 2026
Open request
View all 27
As of 20 Oct 2026 · synthetic data
Sales funnel
Definition
Year
2026
2025
2024
2023
2022
Month
All months
Jan
Feb
Mar
Apr
May
Jun
Jul
Aug
Sep
Oct
Nov
Dec
Region
All regions
Central
Eastern
Western
Mall
All malls
Rawdah Point Mall
Sandstone Galleria
Qasr Plaza
Najd Gate Mall
Wadi Crescent Centre
Falcon Square
Oasis Row
Cedar Park Mall
Amber Heights
Mirage Commons
Gulf Gate Mall
Pearl Bay Centre
Dune Harbour Mall
Coral Point
Seabreeze Plaza
Lantern Quay
Mangrove Mall
Harbor Lights Mall
Tidewater Arcade
Coastline Galleria
Spice Route Mall
Minaret View
Breeze Walk
Marina Square West
Hijaz Crossing
Lease requests
1,284
›
Leads
702
›
Proposals
418
Signed 236
Unsigned 151
31 in other statuses
›
Contracts
296
Signed 201
Unsigned 74
21 in other statuses

Counts records created in the period at each stage — not a cohort, so stages are not conversion rates.

As of 20 Oct 2026 · synthetic data · live counts (snapshot table synced 20 Oct 02:00 is not shown)
Leasing and sales KPIs
Definition
No card filters
Expiring leases
412
Ending 20 Jul 2026 – 27 Jul 2027
Active leases
5,286
Dashboard definition · includes grace period
Pending sales data
846
Pending, re-upload or documents needed
As of 20 Oct 2026 · synthetic data
Lease requests
Definition
Year
2026
2025
2024
2023
2022
By unit type
By source
1,284
lease requests in 2026
Store
612
47.7%
Kiosk
188
14.6%
Food Court
164
12.8%
Office
121
9.4%
Other (3)
199
15.5%

Other = Media, Specialty, Entertainment. Other is not clickable (V2).

As of 20 Oct 2026 · synthetic data
Drawing document status
Definition
Year
2026
2025
2024
2023
2022
Region
All regions
Central
Eastern
Western
Architectural
MEP
Electrical
Chart
Table
A · Approved
B · Approved with comments
C · Change request
D · Rejected
Gulf Gate
Harbor Lights
Rawdah Point
Coral
Dune Harbour
Seabreeze
Tidewater
Coastline
Lantern
Mangrove
Minaret
Sandstone
Breeze
Marina Square West
Najd Gate
Hijaz
Wadi Crescent
Amber
Falcon
Mirage
Oasis

No drawings yet from 4 malls: Qasr Plaza, Cedar Park Mall, Pearl Bay Centre, Spice Route Mall.

As of 20 Oct 2026 · synthetic data
Fit-out and handover
Definition
Year
2026
2025
2024
2023
2022
Month
All months
Jan
Feb
Mar
Apr
May
Jun
Jul
Aug
Sep
Oct
Nov
Dec
Region
All regions
Central
Eastern
Western
Mall
All malls
Rawdah Point Mall
Sandstone Galleria
Qasr Plaza
Najd Gate Mall
Wadi Crescent Centre
Falcon Square
Oasis Row
Cedar Park Mall
Amber Heights
Mirage Commons
Gulf Gate Mall
Pearl Bay Centre
Dune Harbour Mall
Coral Point
Seabreeze Plaza
Lantern Quay
Mangrove Mall
Harbor Lights Mall
Tidewater Arcade
Coastline Galleria
Spice Route Mall
Minaret View
Breeze Walk
Marina Square West
Hijaz Crossing
72%
Pre-opening MEP
74 of 103 reviewed
67%
Pre-opening Arch.
69 of 103 reviewed
82%
Open ceiling
91 of 111 reviewed
78%
Close ceiling
80 of 103 reviewed
17handovers pending tenant acceptance
Review

Ring = reviewed ÷ (received + remaining + reviewed). Reviewed includes rejected, so it is not an approval rate.

As of 20 Oct 2026 · synthetic data
Fit-out drawings
Definition
Year
2026
2025
2024
2023
2022
Month
All months
Jan
Feb
Mar
Apr
May
Jun
Jul
Aug
Sep
Oct
Nov
Dec
Region
All regions
Central
Eastern
Western
Mall
All malls
Rawdah Point Mall
Sandstone Galleria
Qasr Plaza
Najd Gate Mall
Wadi Crescent Centre
Falcon Square
Oasis Row
Cedar Park Mall
Amber Heights
Mirage Commons
Gulf Gate Mall
Pearl Bay Centre
Dune Harbour Mall
Coral Point
Seabreeze Plaza
Lantern Quay
Mangrove Mall
Harbor Lights Mall
Tidewater Arcade
Coastline Galleria
Spice Route Mall
Minaret View
Breeze Walk
Marina Square West
Hijaz Crossing
Submitted
Pending
Approved
Mechanical
48
19
112
179
Architectural
61
27
134
222
Electrical
37
88
137

“Approved” is the dashboard’s reviewed bucket: approved, rejected or completed.

As of 20 Oct 2026 · synthetic data
Pending approvals
Definition
Region
All regions
Central
Eastern
Western
Mall
All malls
Rawdah Point Mall
Sandstone Galleria
Qasr Plaza
Najd Gate Mall
Wadi Crescent Centre
Falcon Square
Oasis Row
Cedar Park Mall
Amber Heights
Mirage Commons
Gulf Gate Mall
Pearl Bay Centre
Dune Harbour Mall
Coral Point
Seabreeze Plaza
Lantern Quay
Mangrove Mall
Harbor Lights Mall
Tidewater Arcade
Coastline Galleria
Spice Route Mall
Minaret View
Breeze Walk
Marina Square West
Hijaz Crossing
38%
Proposals · 117 pending
25 within a week
1w 25 · 2w 18 · 3w 14 · 1m 15 · 1m+ 45
42%
Contracts · 78 pending
16 within a week
1w 16 · 2w 11 · 3w 9 · 1m 9 · 1m+ 33
38%
Leases · 37 pending
9 within a week
1w 9 · 2w 6 · 3w 4 · 1m 4 · 1m+ 14

Gauge = share of pending items older than one month (31+ days). Bands: 1w 0–6 · 2w 7–13 · 3w 14–20 · 1m 21–30 · 1m+ 31+ days.

As of 20 Oct 2026 · synthetic data
Pending amendments
Definition
Year
2026
2025
2024
2023
2022
Month
All months
Jan
Feb
Mar
Apr
May
Jun
Jul
Aug
Sep
Oct
Nov
Dec
Region
All regions
Central
Eastern
Western
Mall
All malls
Rawdah Point Mall
Sandstone Galleria
Qasr Plaza
Najd Gate Mall
Wadi Crescent Centre
Falcon Square
Oasis Row
Cedar Park Mall
Amber Heights
Mirage Commons
Expansion
HoldOver
Renewal
Termination
4 wk+
1
2
18
4
4 wk
0
1
3
1
3 wk
1
0
2
2
2 wk
2
1
1
1
1 wk
1
0
2
1
0
Fewer
More
Shading by quintile of non-zero cells
As of 20 Oct 2026 · synthetic data
Service requests
Definition
Year
2026
2025
2024
2023
2022
Month
All months
Jan
Feb
Mar
Apr
May
Jun
Jul
Aug
Sep
Oct
Nov
Dec
Region
All regions
Central
Eastern
Western
Mall
All malls
Rawdah Point Mall
Sandstone Galleria
Qasr Plaza
Najd Gate Mall
Wadi Crescent Centre
Falcon Square
Oasis Row
Cedar Park Mall
Amber Heights
Mirage Commons
Gulf Gate Mall
Pearl Bay Centre
Dune Harbour Mall
Coral Point
Seabreeze Plaza
Lantern Quay
Mangrove Mall
Harbor Lights Mall
Tidewater Arcade
Coastline Galleria
Spice Route Mall
Minaret View
Breeze Walk
Marina Square West
Hijaz Crossing
Inquiry
1,927
Work permits
2,746
Complaints
990
General
1,067
Leasing
506
Billing
354
Construction
841
Hot work
557
421
379
278
270
Cleanliness
322
Air conditioning
288
Parking
221
159
Work permits by status
4,384 permits
Approved
2,058
In process
528
Rejected
160
Pending
98
Closed
1,540

Tile size = approved + in process + rejected. Pending and closed requests appear in tooltips but are not sized (V2 definition).

As of 20 Oct 2026 · synthetic data
Unit discrepancy
Definition
Year
2026
2025
2024
2023
2022
Month
Jan
Feb
Mar
Apr
May
Jun
Jul
Aug
Sep
Oct
Nov
Dec
Mall-wise
Month-wise
Mall
◂ Mismatch
Match ▸
Gulf Gate Mall
11
128
Rawdah Point Mall
6
301
Harbor Lights Mall
6
205
Najd Gate Mall
5
183
Pearl Bay Centre
5
181
Sandstone Galleria
5
169
Tidewater Arcade
5
165
Cedar Park Mall
5
145
Coastline Galleria
4
161
Wadi Crescent Centre
4
159
Qasr Plaza
4
153
Spice Route Mall
4
152
Dune Harbour Mall
4
144
Falcon Square
4
136
Minaret View
4
136
Seabreeze Plaza
4
121
Breeze Walk
4
114
Coral Point
3
129

Portfolio mismatch rate 2.9% (87 of 3,000 units). No report this month from 7 other malls. Bars share one scale.

As of 20 Oct 2026 · synthetic data
```

## DX2 · Tenant dashboard (interactive)

File: boards/Tenant.dc.html · Render: renders/Tenant.png · interactive prototype

```text
Cenomi Dashboard Agent
POC
SYNTHETIC DATA · AS OF 20 OCT 2026
Ask about your leases…
Maha · Lumen Retail Co.
Dashboard
Workspace
Design review controls
not part of the product
View as
Maha · company admin · 3 leases
Omar · lease contact · T-31206 only
Data state
Live
Loading
Empty
Error
Hi, Maha
Lumen Retail Co. (synthetic tenant)
3 leases · 5 units
Overview
Definition
Scoped to your 3 leases
Leases
3
5 units · 2 brands
Pending documents
3
Waiting for you to upload
Open service requests
9
of 46 requests
Pending sales data
1
2026 · 24 approved
Lease requests
1
2 approved · company-level
Company profile
2
Brands on file
Payments
—
Not available in this POC
As of 20 Oct 2026 · synthetic data
Action required
Definition
No card filters
4
need your action
SALES DATA

Sales data for Sep 2026 on lease T-32044 at Gulf Gate Mall needs re-upload

18 Oct 2026
Open
FIT-OUT DRAWING

Shopfront details drawing for lease T-31206 needs re-upload

17 Oct 2026
Open
DOCUMENT

Civil defence certificate requested for lease T-30512

15 Oct 2026
Open
View all notifications
As of 20 Oct 2026 · synthetic data
Reported sales
Definition
Year
2026
2025
2024
Lease
All my leases
T-30512 · Lumen · Rawdah Point Mall
T-31206 · Lumen Home · Sandstone Galleria
T-32044 · Lumen · Gulf Gate Mall
1.50M
750K
0
1.28M
1.19M
1.49M
1.32M
1.27M
1.40M
1.24M
1.20M
803K
Jan
Feb
Mar
Apr
May
Jun
Jul
Aug
Sep
Reported sales · all 3 leases · 2026
SAR 11,194,700

Counts submitted and approved reports. Not counted: Gulf Gate Mall · Sep 2026 (need re-upload).

Upload sales data
As of 20 Oct 2026 · synthetic data
Service requests
46 total · 9 open
Definition
Mall
All my malls
Rawdah Point Mall
Sandstone Galleria
Gulf Gate Mall
By status
By category
46
requests · 9 open
Submitted
3
In process
4
Action required
2
Approved
27
Rejected
3
Expired
2
Other (closed, completed)
5
Across Rawdah Point Mall, Sandstone Galleria and Gulf Gate Mall
All requests
As of 20 Oct 2026 · synthetic data
Documents to upload
Definition
No card filters
Operations
Lease T-30512 · Rawdah Point Mall — opens its Documents tab
1
Fit-out drawings
Lease T-31206 · Sandstone Galleria — opens its Fit-out tab
2
Documents waiting for you
3

Inquiry documents: none requested.

As of 20 Oct 2026 · synthetic data
Announcements and events
Definition
No card filters
TODAY
Night market weekend — Gulf Gate Mall
20–22 Oct
UPCOMING
Autumn family festival — Sandstone Galleria
30 Oct – 2 Nov
UPCOMING
Late-night shopping hours — Rawdah Point Mall
From 1 Nov
ANNOUNCEMENT
Updated fit-out guidelines published
15 Oct
ANNOUNCEMENT
Parking level B2 maintenance — Rawdah Point Mall
12 Oct
ANNOUNCEMENT
Reminder: September sales data due by 10 October
5 Oct
All announcements and events
As of 20 Oct 2026 · synthetic data
Leasing opportunities
Definition
No card filters
NG
Najd Gate Mall
Central · Riyadh
14
units available
Send enquiry
CG
Coastline Galleria
Western · Jeddah
11
units available
Send enquiry
PB
Pearl Bay Centre
Eastern · Al Khobar
9
units available
Send enquiry
FS
Falcon Square
Central · Riyadh
8
units available
Send enquiry
TA
Tidewater Arcade
Western · Jeddah
7
units available
Send enquiry
DH
Dune Harbour Mall
Eastern · Dammam
7
units available
Send enquiry
View more
As of 20 Oct 2026 · synthetic data
```

## DX2 · Card states

File: boards/States.dc.html · Render: renders/States.png

```text
Card states

Every card uses the same nine states. A state never shows a fabricated chart: empty, unavailable and error states replace the chart body, while the card title, filters and footer stay so the user keeps their bearings.

1 · LOADING
Pending approvals
All regions
All malls
As of 20 Oct 2026 · synthetic data

Skeleton in the shape of the content, with a shimmer. Filters stay usable. Shown per card, so one slow card never blocks the page.

2 · EMPTY — NO MATCHING RECORDS
Service requests
2026
Feb
Western
Minaret View
No service requests for these filters
Try a different month, region or mall.
As of 20 Oct 2026 · synthetic data

The filters are valid but nothing matches. The message names what is missing and how to widen the view.

3 · EMPTY — BEFORE THE DATASET STARTS
Lease requests
2023
No lease requests in 2023
The synthetic dataset starts in January 2024. Earlier years are kept in the year filter to match V2.
As of 20 Oct 2026 · synthetic data

V2 always offers the current year and the four before it. The POC keeps that and explains why 2022–2023 are empty.

4 · EMPTY — AFTER THE REFERENCE DATE
Sales funnel
2026
Nov
All regions
Nov 2026 is after the reference date
Synthetic data runs to 20 Oct 2026, so later months have no records.
As of 20 Oct 2026 · synthetic data

The frozen reference date is explicit. Nothing is ever computed or projected beyond it.

5 · ERROR
Fit-out and handover
2026
All months
All regions
Couldn’t load this card.
The rest of the dashboard is unaffected. Reference req_8f21c4.
Retry
As of 20 Oct 2026 · synthetic data

Plain-language message, a request reference for support, and Retry. Typed backend errors map to this one pattern; access denials do not (see 7).

6 · UNAVAILABLE — NOT IN THE DATASET
Overview
Pending sales data
1
2026 · 24 approved
Payments
—
Not available in this POC
UNAVAILABLE
Payments are not part of the synthetic dataset. The agent says so rather than estimating a figure.
As of 20 Oct 2026 · synthetic data

A dashed outline and a dash, never 0. The same Unavailable label the agent uses for questions like footfall.

7 · OUTSIDE YOUR ACCESS
Pending approvals
Central
All malls
Nothing in your access matches these filters
Your role covers the Central region only. Data outside your access is never shown, and an empty scope never falls back to all malls.
As of 20 Oct 2026 · synthetic data

Fixes V2 behaviour where an empty scope could mean “everything” or a 500 error. Cards the role cannot use at all are hidden, with a count in the page header.

8 · PARTIAL COVERAGE
Unit discrepancy
2026
Sep
Mall-wise
Gulf Gate Mall
11
128
Rawdah Point Mall
6
301
PARTIAL
No report this month from 7 of 25 malls. Totals cover the 18 that reported.
As of 20 Oct 2026 · synthetic data

The chart renders what exists and states what is missing, in words, beside it.

9 · NO VALUE FOR A MEASURE
Fit-out and handover
2026
Oct
Central
Oasis Row
—
Close ceiling
0 of 0 reviewed

A ratio with a zero denominator shows a dash and “0 of 0”, never 0% or 100%. The agent returns null with a reason for the same case.

As of 20 Oct 2026 · synthetic data

Applies to every ratio: gauges, rings, occupancy and shares.

RULES SHARED BY EVERY STATE

Footer on every card: “As of 20 Oct 2026 · synthetic data”. Cards with a related snapshot say which figures are live (Sales funnel).

Zero is shown as 0 (V2 sometimes dropped zero counts from responses). A missing or impossible value is a dash with a reason.

States are per card and announced to screen readers; Retry and filter controls stay keyboard reachable in every state.

The agent uses the same vocabulary: Empty, Partial, Unavailable and Outside your access map directly to its coverage classes.
```

## DX2 · Parity notes and intentional differences

File: boards/DX2-Notes.dc.html · Render: renders/DX2-Notes.png

```text
DX2 · Parity notes and intentional differences

What each card keeps from V2, and where the design deliberately differs. Every difference traces to an approved decision (DR = G0 register, DXD = DX1 register).

Admin cards
CARD	KEPT FROM V2	INTENTIONAL DIFFERENCES	BASIS
Portfolio properties	Three tiles (count/units, occupied units/GLA, vacant units/GLA), occupancy meter weighted by units, 1-decimal percentages	All-region admins see totals (V2 returned empty). Tiles select and drill into mall records in place.	DR-001, DR-020
Leasing and sales KPIs	Expiring, active (with grace period and superseded), pending sales status set	Overlap and pending-set caveats in the definition. Tiles drill into records rather than navigating away.	DR-002
Lease requests	Donut, unit type / source switch, top four + Other, Other not clickable, year filter	Percentages always use the displayed total (legacy bug fixed). Requests without a source are counted in a note. “Last synced” replaced by the reference date.	DR-001, DXD-09
Sales funnel	Four-stage flow appearance, live counts, signed/unsigned lists, year/month/region/mall filters	“Other statuses” shown so signed + unsigned visibly ≠ total. One calendar (Asia/Riyadh) for every stage. Mall filter always intersected with access (V2 widened or dropped it). Footer names the snapshot table it does not show.	DR-006, DR-008, DR-018
Action required	Latest three unread action-required items, badge count, type pills, bold IDs	Deterministic latest row per notification group.	DR-001
Pending approvals	Three half gauges, five bands (0–6 … 31+ days), captions, the 90% red-banner rule, region/mall filters	Band counts printed under each gauge so the value is readable without hover. Mall rows aggregated on the server. An empty scope gives an explained empty state, not a 500.	DR-020, DXD-07
Pending amendments	Type × delay-week heatmap, rows oldest first, alphabetical columns, quintile shading, future-dated rows in 4 wk+ (as a caveat)	Year and month in Asia/Riyadh (V2 mixed UTC). Selecting a cell makes it the agent’s context.	DR-006, DXD-05
Service requests	Treemap grouped Inquiry / Work permits / Complaints, tile = approved + in process + rejected, work-permit strip, work-permit-only mode for limited roles	Lease-less requests counted; region matching case-insensitive; the drilldown uses the same scope so counts reconcile. Layout in this mock is slice-and-dice; squarified layout is validated in DX3.	DR-001, DR-007
Fit-out and handover	Four rings, ring = reviewed ÷ (received + remaining + reviewed), pending-handover callout	Zero denominator shows a dash. Soft-deleted rows stay in the parity count (caveat); insights use the active-only metric.	DR-002
Fit-out drawings	Horizontal stacked bars per discipline, submitted / pending / approved, rows filtered by discipline permission	“Approved includes rejected” stated under the chart.	DR-002
Drawing document status	Stacked A–D columns by mall, discipline switch, chart ↔ table toggle, malls without drawings listed under the chart	One mall hierarchy shared with the fit-out cards (V2 attributed malls differently between cards).	DR-047
Unit discrepancy	Diverging bars, mall-wise / month-wise, latest report per mall per month, pending only in totals, own month select	Asia/Riyadh months (V2 used UTC). One shared scale, stated. Portfolio mismatch rate in the footnote.	DR-006
Tenant cards
CARD	KEPT FROM V2	INTENTIONAL DIFFERENCES	BASIS
Overview tiles	Leases · units · brands, pending documents, open service requests, sales pending/approved, lease requests, profile, payments placeholder	Every tile limited to the user’s permitted leases (V2 limited only some). Open requests counted on the server (V2 counted the first 200 rows in the browser). Payments shown as Unavailable, never 0.	DR-019, DR-020
Reported sales	Monthly columns, submitted + approved only, month of period end, only months with data, year and lease selects, SAR total band	Excluded submissions are named in the footnote.	DR-001
Service requests	Donut by status with V2 status order and colours, treemap by category, mall select	No truncation; same population as the open-requests tile.	DR-001
Documents, announcements, opportunities	Grouped document links with deep links for single items; merged event feed; mall list with available units	Today/upcoming duplicates removed on the server. Mall map omitted (out of POC scope). Mall images replaced by initials, since there are no brand assets.	DR-040
Across both dashboards
CHANGE	WHY	BASIS
Card filters stay per card — no global filter bar	V2 parity. The agent panel shows the active card’s filters separately from its own query scope.	DXD-05
“Last synced” replaced by “As of 20 Oct 2026 · synthetic data”	V2 sync labels were unreliable and the dataset is frozen.	DR-003, DXD-09
One permission controls a card’s visibility and its data	V2 could show a card whose data then returned 403. Hidden cards are counted in the page header.	DR-019
Every card gains Ask, Expand (Chart / Table / Records / Definition) and data-point selection	Entry points into the agent; accessible table alternative for every chart.	DXD-03, DXD-04
Ink and Violet visual language	Approved direction. V2 palette roles are kept as tokens so chart colours keep their meaning.	DXD-01
```

## DX2 · Tablet and mobile

File: boards/Responsive.dc.html · Render: renders/Responsive.png

```text
Tablet and mobile
Below 1280 px the agent opens over the dashboard instead of narrowing it; below 820 px every card stacks, filters move into a sheet and the agent takes the full screen.
Cenomi Dashboard Agent
SYNTHETIC DATA · AS OF 20 OCT 2026
Portfolio admin
Sales funnel
2026 · All regions
Lease requests
1,284
Leads
702
Proposals
418
Signed 236 · Unsigned 151
Contracts
296
Signed 201 · Unsigned 74
Pending approvals
All regions
38%
Proposals
42%
Contracts
38%
Leases
Pending amendments
2026 · Central
Expansion
HoldOver
Renewal
Termination
4 wk+
1
2
18
4
4 wk
0
1
3
1
Agent
Open in workspace
×

DASHBOARD FILTERS · PENDING AMENDMENTS

2026
All months
Central
All malls

AGENT QUERY SCOPE

Pending amendments by age band
2026 ×
Central ×
Selected: Renewal × 4 wk+ · 18 ×
Access: all regions

PROPOSED DASHBOARD CHANGES

None.

Suggested questions
Why is this so high?
Show these amendments as records
Ask a follow-up…
Send

Tablet · 1024 px. Cards pair up in two columns; wide visuals (funnel, document status, treemap) take the full row. The agent is an overlay sheet with a scrim, so charts keep their width. Closing it returns to the same scroll position and selection.

Cenomi Agent
SYNTHETIC · 20 OCT 2026
Portfolio overview
Portfolio properties
Malls
25
Occupied
7,114
Vacant
1,026
87.4% of units occupied
Pending amendments
2026 · Central · All malls ▾
Exp.
Hold.
Ren.
Term.
4 wk+
1
2
18
4
4 wk
0
1
3
1
3 wk
1
0
2
2
Swipe for 2 wk and 1 wk · Table view in Expand
Service requests
Dashboard
Workspace
Insights
Ask

Phone · dashboard. One column. Each card shows its filters as one summary chip; Ask moves to a bottom tab and to each card header.

Cenomi Agent
SYNTHETIC · 20 OCT 2026
Pending amendments
Pending amendments filters
Applies to this card only

YEAR

2026
2025
2024
More

MONTH

All months
▾

REGION

All
Central
Eastern
Western

MALL

All malls in Central
▾
Reset
Show 44 amendments

Phone · card filters. A bottom sheet with 44 px targets. The apply button previews the result count before the card changes.

‹
Agent
SYNTHETIC

CONTEXT FOR THIS QUESTION

Edit scope
Pending amendments
2026 · Central
Renewal × 4 wk+ · 18
Dashboard filters: 4
Proposed changes: none
Why is this so high?
Answer layout designed in DX4–DX5. On a phone, generated charts take the full width and open full screen when tapped.
Ask a follow-up…
Send

Phone · agent. Full screen. Context collapses to a summary with “Edit scope”; back returns to the same card and selection.
```

## DX2 · Design decision register (approved)

File: boards/DX2-Decisions.dc.html · Render: renders/DX2-Decisions.png

```text
DX2 · Design decision register

Decisions from the project owner’s DX2 review, 22 Oct 2026. They extend DXD-01…09 and bind DX3–DX6, GENERATIVE_UI.md and PRODUCT_SPEC.md in M0. “Prototype” says what the DX2 boards already show; “Designed in” says where the rest is drawn.

Gate DX2 · Approved

Approved in direction by the project owner, conditional on visual verification of the Admin dashboard. The verification ran on 22 Oct 2026: 64 of 64 browser checks passed, all 12 Admin cards render with data, and the stress tests finished with no errors (see the DX2 verification record board). The rendering defect in the exported PDF was a script syntax error and is fixed.

Next stage

DX3 · Chart Parity Gallery: every V2 chart type in its proposed implementation, with tooltips, legends, selection, drilldown, keyboard and screen-reader access, responsive behaviour and an ECharts treemap fidelity test.

ID	DECISION	WHAT IT MEANS FOR THE DESIGN	PROTOTYPE	DESIGNED IN	STATUS
DXD-10	Expanded cards	Keep the centred overlay for quick inspection. Every expanded card also offers Open in workspace, which moves the card into the analytical workspace with its filters, selection and active tab intact.	Overlay and the Open in workspace action on all 12 Admin cards.	DX4 workspace	Approved
DXD-11	Records vs Inspector	Dashboard drilldowns live in the card’s Records tab. The shared Inspector is reserved for evidence, definitions, calculation provenance and execution details. Both reuse the same table and dataset components.	Records tab drills to the selected point (e.g. 18 amendments, by mall).	DX4 inspector · GD components	Approved
DXD-12	Selection model	One active selection globally is the agent’s default context. Each card remembers its own last selection. The user can explicitly pin several selections for a cross-KPI comparison; unrelated selections are never combined automatically.	Single global selection. Per-card memory and pinning are not drawn yet.	DX4 context tray	Approved
DXD-13	Mall map	Out of the baseline. Keep the mall cards, available-unit counts, regions and actions.	Tenant opportunities card without the map.	—	Approved
DXD-14	Partial coverage everywhere	The same Partial label and a sentence naming what is missing (“covers 18 of 25 malls”) on dashboard charts and on agent-generated components. Coverage is a field of the result, not text the model writes.	Unit discrepancy card; States board, state 8.	DX3 charts · DX5 GenUI	Approved
DXD-15	Filters vs boundaries	Analytical filters are removable chips. Authorization boundaries (role access, lease restriction) and the frozen reference date sit in a separate Boundaries row with a lock icon. Neither the user nor the agent can remove or widen them in the panel.	Admin and Tenant agent panels.	DX4 · DX5	Approved
DXD-16	One state vocabulary	Cards and generative components share one set of states: loading, zero (shown as 0), empty (no match · before dataset · after reference date), unavailable (not in the dataset), error (reference and Retry), outside_access, partial, undefined_ratio (zero denominator: dash and “0 of 0”).	States board covers all eight on cards.	DX5 GenUI states	Approved
DXD-17	Context and scroll preservation	Opening or closing any overlay (expanded card, agent sheet, filter sheet, inspector) keeps page scroll, card filters, selection and active tab.	Verified for the expanded card: scroll and card position unchanged after close.	DX4 inspector	Approved
DXD-18	Chart and table share one dataset	Chart, Table and Records read the same authorized result for the card’s scope. A table may show finer rows (Other expanded) but its totals must reconcile with the chart.	Verified: heatmap 44 = 44; donut Other 199 = 97 + 74 + 28.	DX3 · GD	Approved
DXD-19	Phone navigation	Below 820 px the side rail becomes a bottom tab bar, matching the approved Responsive board.	Admin and Tenant boards.	—	Approved
DXD-20	Value labels on narrow charts	When direct value labels would collide, show the value on the selected mark and in the tooltip; the Table tab lists every value.	Reported sales below 520 px.	DX3 rule for all charts	Approved

DXD-19 and DXD-20 came out of the verification run, not the review; they apply the approved Responsive board and accessibility rules and are listed so the register stays complete.
```

## DX2 · Verification record — 64/64 checks, all 12 Admin cards

File: boards/DX2-Verify.dc.html · Render: renders/DX2-Verify.png

```text
DX2 · Verification record

Rendered in Chromium (Playwright) from the same files the canvas publishes, then driven through every interaction in your DX2 review. All 12 Admin cards and the Tenant views are shown exactly as captured. Run on 22 Oct 2026.

64 / 64
browser checks passed
12 / 12
Admin cards render with data
12,716
stress-test steps · 0 errors · 0 NaN or undefined values
0
unresolved template placeholders · 0 page errors
All 12 Admin cards · 1440 px · Portfolio admin · Live

Each card captured on its own, in dashboard order. Pending amendments opens with region = Central only for this review, so the filter-versus-scope demo has a filter to remove; the product default is All.

1
Portfolio properties
2
Action required
3
Sales funnel
4
Leasing and sales KPIs
5
Lease requests
6
Drawing document status
7
Fit-out and handover
8
Fit-out drawings
9
Pending approvals
10
Pending amendments
11
Service requests
12
Unit discrepancy
Interactions

Every assertion checks a concrete value or element, not only that a click succeeded.

Rendering
5/5
Admin renders with no unresolved template placeholders
Admin: 12 cards visible for Portfolio admin
KPI card shows 412 / 5,286 / 846
No page errors in any run
No page errors
Role-based card visibility
5/5
Leasing manager: 7 cards, 5 hidden
Fit-out manager: 6 cards
Fit-out manager: work-permit-only service requests
Fit-out manager region filter offers Central only
Fit-out properties limited to Central (10 malls, 3,420 units)
Leasing manager · 7 cards, 5 hidden (count in the header)
Fit-out manager · Central only, work-permit view
Card filters
5/5
Sales funnel region=Central → lease requests 560
Mall options narrow to Central (10 malls + All)
Month Nov 2026 → after-reference-date empty state
Filters reset → 1,284
Dashboard card filter still Central
Sales funnel · Nov 2026 gives the after-reference-date state
Chart selection and tooltips
8/8
Heatmap tooltip appears on hover
Cell selection shows selection bar
Donut legend selects Store · 612
Selecting another card replaces the global selection
Treemap tile selects
Diverging bar row selects Gulf Gate
Gauge selects proposals
Sales column selects Jan 2026 · SAR 1,284,000
Heatmap tooltip on hover
Ask about selection · agent scope chips
5/5
Ask about this opens the agent panel
Panel shows dashboard filters chips (2026 · All months · Central · All malls)
Scope includes the selection chip
Access boundary chip present and not removable
Removing Central widens agent scope only
Selection, then Ask: card filters, agent scope, locked boundaries
Central removed from the agent scope only; the card filter is unchanged
Expanded card · tabs · overlay
12/12
View records opens the expanded card on Records
Records match the cell (18, Rawdah 9 · Sandstone 6 · Qasr 3)
Table tab lists 5 bands with totals
Definition tab shows caveats
Chart tab returns to the heatmap
Backdrop closes the overlay; selection kept
Expanded overlay shows Open in workspace
Open in workspace hidden on cards that are not expanded
Open in workspace explains the hand-off
Chart and Table tabs use the same dataset (cell totals match)
Closing the overlay restores scroll position and card position
Lease requests table matches the donut (Store 612; Media+Specialty+Entertainment = Other 199)
View records opens the Records tab filtered to the cell (18)
Definition tab with caveats
Open in workspace on the expanded overlay
Data-state switching
4/4
Error state on all 12 cards
Retry restores one card only
Loading skeleton on all 12 cards
Empty state on all 12 cards
Error on every card; Retry restores one card
Tenant access restrictions
7/7
Tenant renders with no unresolved holes
Company admin: 3 leases, 9 open of 46, 1 pending sales
Payments shown as unavailable, not 0
Lease contact: 1 lease, 2 units, 1 open of 9
Lease contact can only pick T-31206
Lease contact action list limited to own lease
Tenant agent scope shows lease boundary
Company admin · 3 leases
Lease contact · T-31206 only
Responsive layouts
13/13
Tablet: approvals and amendments share a row
Tablet: sales funnel takes the full row
Tablet: agent opens as an overlay, charts keep width
Phone: cards stack in one column
Phone: no horizontal page scroll
Phone: agent is full screen
Phone tenant: no horizontal page scroll
Admin at 360px: nothing extends past its card, no horizontal scroll, bottom tab bar on the screen edge, no overlapping column labels
Admin at 390px: nothing extends past its card, no horizontal scroll, bottom tab bar on the screen edge, no overlapping column labels
Admin at 1024px: nothing extends past its card, no horizontal scroll
Tenant at 360px: nothing extends past its card, no horizontal scroll, bottom tab bar on the screen edge, no overlapping column labels
Tenant at 390px: nothing extends past its card, no horizontal scroll, bottom tab bar on the screen edge, no overlapping column labels
Tenant at 1024px: nothing extends past its card, no horizontal scroll
1024 · tablet grid
1024 · agent as an overlay sheet
390 · Admin with bottom tab bar
390 · agent full screen
390 · Tenant
390 · Reported sales (fixed)
390 · Service requests treemap
Defects found and fixed during verification
DEFECT	EFFECT	FIX
Missing closing parenthesis in the Pending approvals table function	The whole Admin script failed to parse, so placeholder names such as roleName printed raw and no chart drew. This is what your exported PDF showed.	Fixed; the file passes a parse check and renders with every value resolved.
KPI tiles not passed to the card	Leasing and sales KPIs rendered empty.	Wired; 412 / 5,286 / 846 confirmed.
Treemap labels on small tiles	Names overlapped in thin tiles.	Labels adapt to the tile’s share: name and value, value only, or tooltip only.
Unknown mall or region in allocation helpers	Could produce NaN in Sales funnel and Fit-out drawings after unusual filter sequences.	Helpers return an explicit empty scope.
Desktop rail kept on phones	Cards squeezed to 267 px; month labels clipped; the sales axis ran off the screen.	Bottom tab bar below 820 px, as on the approved Responsive board.
Column value labels at phone width	Adjacent values overlapped in Reported sales.	Below 520 px the value shows on the selected column and in the tooltip; the Table tab lists them all.
Boundary chips looked like filters	Access and as-of chips differed from filters only by a dashed border.	Separate “Boundaries” row with a lock icon; never removable (DX2 review refinement).
No route from the overlay to the workspace	Your DX2 decision 1 asked for both.	“Open in workspace” on every expanded card; the workspace itself is designed in DX4.

Method and limits. Local Chromium at 1440 × 900, 1024 × 768, 390 × 844 and 360 × 844. Google Fonts cannot be reached from the test sandbox, so the captures use a fallback sans-serif; in the canvas the boards load Inter. The stress test renders every role and data state, sweeps every filter option, then random-walks every handler (Admin 7,848 steps, Tenant 4,868). These are design prototypes: this record verifies design behaviour, not production code.
```

# DX3 · Chart parity gallery (conditionally approved)

## DX3 · Chart parity gallery (interactive, live ECharts)

File: boards/DX3-Gallery.dc.html · Render: renders/DX3-Gallery.png · interactive prototype

```text
DX3 · Chart parity gallery

Every V2 visual from the Admin and Tenant dashboards, rebuilt in its proposed implementation with the DX2 synthetic values. Each specimen states the V2 behaviour from the API reference, what this build does, how to drive it from the keyboard, and where it differs.

ECharts did not load · blocked or offline (cdnjs.cloudflare.com) · HTML visuals and the reference treemap still work
Desktop
Tablet · 768
Phone · 390
AGENT CONTEXT
Nothing selected. Select any mark, cell, tile or segment.

One active selection drives the agent context; every card keeps its own last selection, drawn dashed (DXD-12). Pinning several selections is designed in DX4.

Self-test

Runs in your browser against the loaded ECharts: rendering, data, aria, keyboard, tooltip, selection, treemap metrics and the 390 px frame. Copy the plain-text result back to Claude.

Run self-test
ADMIN DASHBOARD
1
Stat tiles

Portfolio properties · Leasing and sales KPIs · Tenant overview

HTML
Parity · Exact
Properties
25
8,140 units
Occupied units
7,114
1,412,600 sqm occupied GLA
Vacant units
1,026
214,300 sqm vacant GLA

SCREEN READER

V2 (API REFERENCE)
ui-kit StatTile; tinted backgrounds by role (violet, teal, orange; rose, violet, teal)
Tile links only when the user holds that tile’s permission
THIS BUILD
Native buttons; selecting a tile opens its Records
A value that is not in the dataset shows a dash and “Unavailable”, never 0 (DXD-16)
KEYBOARD

Tab between tiles; Enter selects.

DIFFERENCES

None.

2
Occupancy meter

Portfolio properties

HTML
Parity · Exact
Unit occupancy
87.4% occupied · 12.6% vacant

SCREEN READER

V2 (API REFERENCE)
Flex bar, occupied vs vacant, weighted by units
Percentages to one decimal
THIS BUILD
Each segment is a button with its count and share
Tooltip text equals the accessible name
KEYBOARD

Tab to a segment; Enter selects.

DIFFERENCES

None.

3
Donut · top four + Other, with a view switch

Lease requests (Admin)

ECharts pie
Parity · Exact
By unit type
By source
1,284
lease requests in 2026
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Store
612
47.7%
Kiosk
188
14.6%
Food Court
164
12.8%
Office
121
9.4%
Other (3)
199
15.5%

Other = Media, Specialty, Entertainment. Other is not clickable (V2).

SCREEN READER

V2 (API REFERENCE)
ui-kit Donut (in-house SVG) with a SegmentedControl: unit type / registration source
foldDonutSlices: sort, keep four in categorical4, fold the rest into “Other” (ink-3), not clickable
Centre total; legend with count and share
THIS BUILD
pie, radius 60–84 %, white 2 px separators; no ECharts legend
Centre total and legend are HTML: crisp text, real buttons, no hidden-series toggling
Shares use the displayed total (the legacy divide-by-source bug is not carried over)
KEYBOARD

Tab to the chart, then ← → (or ↑ ↓) move between values, Home / End jump, Enter selects, Escape clears. “Other” is announced as not selectable.

DIFFERENCES

None visible. Legend clicks select a slice instead of hiding it (ECharts’ default), so the ring always equals the total.

4
Stage flow · four stages with signed / unsigned splits

Sales funnel

HTML (DR-008)
Parity · Exact
Lease requests
1,284
›
Leads
702
›
Proposals
418
Signed 236
Unsigned 151
31 in other statuses
›
Contracts
296
Signed 201
Unsigned 74
21 in other statuses

SCREEN READER

V2 (API REFERENCE)
ui-kit StageFlow: Lease requests → Leads → Proposals → Contracts
Tints violet, rose, teal, amber; splits on Proposals and Contracts
THIS BUILD
Kept in HTML to preserve the V2 look; ECharts funnel is reserved for the GenUI funnel
“Other statuses” shown so signed + unsigned visibly differ from the total
KEYBOARD

Tab between stages; Enter selects.

DIFFERENCES

None.

5
Half gauges · one per approval type

Pending approvals

ECharts gauge
Parity · Close
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Proposals · 117 pending
25 within a week
1w 25 · 2w 18 · 3w 14 · 1m 15 · 1m+ 45
Contracts · 78 pending
16 within a week
1w 16 · 2w 11 · 3w 9 · 1m 9 · 1m+ 33
Leases · 37 pending
9 within a week
1w 9 · 2w 6 · 3w 4 · 1m 4 · 1m+ 14

SCREEN READER

V2 (API REFERENCE)
ui-kit HalfGauge per type; value = “1 month plus” ÷ total of five bands
Caption “N within a week”; red banner when every non-empty type is ≥ 90 % older than a month
THIS BUILD
gauge 180°→0°, progress arc with round caps, no pointer or ticks
Captions and band counts in HTML so they are readable without hover
KEYBOARD

Tab to the chart, then ← → (or ↑ ↓) move between values, Home / End jump, Enter selects, Escape clears.

DIFFERENCES

Arc thickness and cap shape to be compared side by side with V2 at GD.

6
Heatmap · amendment type × delay week

Pending amendments

ECharts heatmap
Parity · Exact
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
0
Fewer
More

SCREEN READER

V2 (API REFERENCE)
ui-kit Heatmap; rows oldest first (4 wk+ … 1 wk); columns in API order
Fill heatSequential5 by quantile of the non-zero values
THIS BUILD
heatmap on two category axes; quintile colours and label colours computed in the adapter (no visualMap), zero cells neutral
White 3 px gaps and rounded cells match the DX2 card
KEYBOARD

Tab to the chart, then ← → move across types and ↑ ↓ across age bands; Home / End; Enter selects; Escape clears.

DIFFERENCES

None.

7
Treemap · grouped by category, with category legend

Service requests (Admin)

ECharts treemap
Parity · Close · see lab
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Inquiry
1,927
Work permits
2,746
Complaints
990

SCREEN READER

V2 (API REFERENCE)
ui-kit Treemap, squarified, minShare 0.08; groups Inquiry / Work permits / Complaints
Tile = approved + in process + rejected; colours by category, permits by family (amber sequential)
Legend shows category totals
THIS BUILD
treemap squarified (golden-ratio target), nodeClick: false, breadcrumb hidden, no roam; fixed category order, leaves largest-first
Labels by share of the category: name + value ≥ 17 %, value only ≥ 7 %, otherwise tooltip only
Category legend is HTML; selecting a category selects the whole group
KEYBOARD

Tab to the chart, then ← → (or ↑ ↓) move between values, Home / End jump, Enter selects, Escape clears. Order: each category, then its tiles largest-first.

DIFFERENCES

Tile positions come from ECharts’ squarify, not the in-house one; measured in the treemap lab below. minShare semantics are an open question (lab, option A or B).

8
Work-permit status strip

Service requests (Admin)

HTML
Parity · Exact
Work permits by status
4,384 permits
Approved
2,058
In process
528
Rejected
160
Pending
98
Closed
1,540

SCREEN READER

V2 (API REFERENCE)
Strip under the treemap: permit statuses with counts
THIS BUILD
100 % strip of buttons; legend with counts below
KEYBOARD

Tab between segments; Enter selects.

DIFFERENCES

None.

9
Progress rings × 4

Fit-out and handover

ECharts gauge (360°)
Parity · Close
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Pre-opening MEP
74 of 103 reviewed
Pre-opening Arch.
69 of 103 reviewed
Open ceiling
91 of 111 reviewed
Close ceiling
80 of 103 reviewed

SCREEN READER

V2 (API REFERENCE)
ui-kit ProgressRing; colours categorical4
share = reviewed ÷ (received + remaining + reviewed); null when the total is 0
Sub-text “{reviewed} of {total} reviewed”
THIS BUILD
gauge 90°→−270° with a progress arc; a null share draws no arc and shows a dash (undefined ratio, DXD-16)
Labels in HTML under each ring
KEYBOARD

Tab to the chart, then ← → (or ↑ ↓) move between values, Home / End jump, Enter selects, Escape clears.

DIFFERENCES

None expected; ring thickness checked at GD.

10
Horizontal stacked bars

Fit-out drawings

ECharts bar
Parity · Exact
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Submitted
Pending
Approved

“Approved” is the dashboard’s reviewed bucket: approved, rejected or completed.

SCREEN READER

V2 (API REFERENCE)
ui-kit StackedBars; rows Mechanical (MEP), Architectural, Electrical
Segments pipeline3: Submitted, Pending, Approved
THIS BUILD
Stacked bar; totals as a right-hand category axis; inside labels only when a segment is ≥ 7 % of the largest row
KEYBOARD

Tab to the chart, then ← → move across statuses and ↑ ↓ across disciplines; Enter selects.

DIFFERENCES

None.

11
Stacked columns by mall, with a table view

Drawing document status

ECharts bar
Parity · Close
Chart
Table
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
A · approved
B · approved with comments
C · change request
D · rejected

No drawings yet from 4 malls: Qasr Plaza, Cedar Park Mall, Pearl Bay Centre, Spice Route Mall.

SCREEN READER

V2 (API REFERENCE)
ui-kit StackedColumns, one column per mall, sorted by total; outcome4 A–D
Malls without drawings listed in a footnote; DataTable alternative
THIS BUILD
Stacked bar, rotated mall labels; below 640 px it shows 7 malls at a time and keyboard focus scrolls the window
Chart and Table read the same dataset (DXD-18)
KEYBOARD

Tab to the chart, then ← → move across malls and ↑ ↓ across grades; Enter selects.

DIFFERENCES

Label rotation and paging on narrow widths are additions; V2 squeezed all columns.

12
Diverging bars · one shared scale

Unit discrepancy

ECharts bar
Parity · Exact
PARTIAL
No report this month from 7 of 25 malls. Totals cover the 18 that reported.
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Mismatch
Match

SCREEN READER

V2 (API REFERENCE)
ui-kit DivergingBars: mismatch grows left in #DC2626, match right in #8B5CF6
Sorted by mismatch, then match; footnote for malls with no report
THIS BUILD
Two stacked bar series, mismatch as negative values, absolute labels
Partial-coverage label beside the chart (DXD-14)
KEYBOARD

Tab to the chart, then ↑ ↓ move across malls and ← → between mismatch and match; Enter selects.

DIFFERENCES

None.

TENANT DASHBOARD
13
Monthly columns

Tenant · Reported sales

ECharts bar
Parity · Exact
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Reported sales · all 3 leases · 2026
SAR 11,194,700

SCREEN READER

V2 (API REFERENCE)
Columns by month, submitted + approved only, months with data only
Compact SAR labels; SAR total band
THIS BUILD
bar with labelLayout.hideOverlap; below 520 px the value shows only on the selected column (DXD-20)
KEYBOARD

Tab to the chart, then ← → (or ↑ ↓) move between values, Home / End jump, Enter selects, Escape clears.

DIFFERENCES

None.

14
Donut · status in a fixed order

Tenant · Service requests (by status)

ECharts pie
Parity · Close
46
requests · 9 open
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Submitted
3
In process
4
Action required
2
Approved
27
Rejected
3
Expired
2
Other (closed, completed)
5

SCREEN READER

V2 (API REFERENCE)
ui-kit Donut size 236; fixed order SUBMITTED … EXPIRED with STATUS_COLORS
Other statuses folded into “Other”, so the ring equals all rows
THIS BUILD
pie; legend in HTML with counts; centre total and open count
KEYBOARD

Tab to the chart, then ← → (or ↑ ↓) move between values, Home / End jump, Enter selects, Escape clears.

DIFFERENCES

“Other” uses #D4D0DE instead of #E5E7EB so the slice stays visible on white.

15
Treemap · category groups, one tile per status

Tenant · Service requests (by category)

ECharts treemap
Parity · Close · see lab
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Work permits
19
Inquiries
11
Work requests
7
Complaints
6
Lease amendments
3

SCREEN READER

V2 (API REFERENCE)
ui-kit Treemap (minShare 0.08); one group per category sorted by size; leaf per status coloured by status
Category/count strip underneath
THIS BUILD
Same treemap primitive as the Admin card; category strip as HTML buttons
KEYBOARD

Tab to the chart, then ← → (or ↑ ↓) move between values, Home / End jump, Enter selects, Escape clears.

DIFFERENCES

As for the Admin treemap.

L
Treemap fidelity lab

The DR-007 condition: does ECharts’ treemap reproduce the V2 layout?

Same data, same size, side by side. Left: a squarified layout (Bruls et al.) standing in for the V2 ui-kit, whose source is not in the API reference. Right: the ECharts treemap with the gallery’s settings. Metrics are measured from each layout.

760 px
480 px
326 px
A · label threshold
B · fold small leaves
Measure both layouts
13 tiles ·
V2 reference · squarified
General
1,067
Leasing
506
Billing
354
Construction
841
Hot work
557
421
379
278
270
Cleanliness
322
Air conditioning
288
Parking
221
159
ECharts 5.6.0 · treemap
ECharts did not load · blocked or offline (cdnjs.cloudflare.com)
Metric	V2 reference	ECharts	Pass rule
Area ÷ value, coefficient of variation	—	—	≤ 5%
Largest area error on one tile	—	—	reported
Mean tile aspect ratio	—	—	ECharts ≤ 1.25 × reference
Worst tile aspect ratio	—	—	reported
Largest-first reading order	—	—	≥ 90%
Leaves drawn	—	—	equal
Option A · label threshold

minShare only decides which tiles get labels. Every sub-category stays a tile and keeps its drilldown. Matches what DX2 shows.

Option B · fold small leaves

Leaves under 8 % of the whole treemap merge into one “Other” tile per category. Folding applies only when two or more leaves qualify. With this data, 8 of 13 sub-categories merge into two “Other” tiles, including all four complaint types, and lose their drilldown.

A
Accessibility model

The second DR-007 condition: keyboard and screen-reader access for every chart.

KEYBOARD
Tab	One stop per chart, then the chart’s HTML controls (legend, captions, view switch). HTML visuals are native buttons.
← → ↑ ↓	Move between values. Two-dimensional where the chart is: heatmap (type × age), stacked bars (discipline × status), document status (mall × grade), diverging bars (mall × side).
Home · End	First or last value.
Enter · Space	Select — the same code path as a mouse click, so the selection bar, agent context and Records target are identical.
Escape	Clear the selection on this card and hide the tooltip.
SCREEN READERS
The chart container is role="application" with aria-roledescription="chart", so arrow keys reach it in forms mode. Its label is the adapter’s data summary plus the key instructions.
ECharts’ aria option is on, with our summary as the description instead of the generic generated text.
Each move is announced through a polite live region: value, then position (“Renewal, 4 wk+: 18 amendments. 3 of 20.”). The gallery shows that text under each chart.
Focus shows the same tooltip as hover. Every chart keeps the Table tab from DX2 as the full non-visual alternative.
Trade-off: role="application" suppresses browse-mode reading inside the chart; the summary, live region and Table tab cover that.
COLOUR CONTRAST OF THE V2 PALETTE

Computed with the WCAG 2.2 formula. Text on a coloured mark needs 4.5:1; a mark needed to understand the chart needs 3:1 against the white card (1.4.11) unless the same information is also given as text.

Token	Used for	White text	Dark text	Label colour	Mark vs white card
 categorical4[0] violet #8B5CF6	Donut slice 1, ring 1, Match bars	4.23:1	4.14:1	Neither	Meets 3:1
 categorical4[1] teal #14B8A6	Donut slice 2, ring 2, occupancy, sales	2.49:1	7.05:1	Dark text	Below 3:1
 categorical4[2] amber #F59E0B	Donut slice 3, ring 3, Pending segments	2.15:1	8.17:1	Dark text	Below 3:1
 categorical4[3] rose #F43F5E	Donut slice 4, ring 4	3.67:1	4.78:1	Dark text	Meets 3:1
 pipeline3[0] sky #0284C7	Submitted segments	4.10:1	4.29:1	Neither	Meets 3:1
 pipeline3[2] green #059669	Approved segments, grade A	3.77:1	4.66:1	Dark text	Meets 3:1
 outcome4[3] red #DC2626	Grade D, Mismatch bars	4.83:1	3.63:1	White text	Meets 3:1
 amberSequential3 light #FDE68A	Operations permit tiles	1.25:1	14.09:1	Dark text	Below 3:1
 ink-3 (Other) #9A93AD	Other slice, Closed permits	2.94:1	5.98:1	Dark text	Below 3:1
 DX2 treemap Inquiry #6D28D9	Inquiry tiles (darkened)	7.10:1	2.47:1	White text	Meets 3:1
 DX2 treemap Complaints #BE123C	Complaint tiles (darkened)	6.29:1	2.79:1	White text	Meets 3:1

Marks below 3:1 (teal, amber, light amber, ink-3) remain acceptable only because every value is also given as text: direct labels or legend counts, the tooltip, and the Table tab. Labels on marks pick white or dark text by measured contrast.
```

## DX3 · Parity assessment, findings and decisions

File: boards/DX3-Parity.dc.html · Render: renders/DX3-Parity.png

```text
DX3 · Parity assessment and ECharts recommendation

How each V2 visual is reproduced in the interactive gallery, what has been verified so far, and what still needs one run with the real library before DR-007 can close at GD. Values are the DX2 synthetic values, so the gallery reconciles with the dashboards.

Recommendation · confirm ECharts at GD, on one condition

No V2 visual is blocked. Eleven visuals use ECharts and four stay HTML (DR-008). Everything the gallery adds on top of ECharts is built and verified: keyboard navigation, live announcements, selection, drilldown payloads, HTML legends and responsive frames. What is not yet verified is ECharts itself: treemap layout fidelity, keyboard-driven tooltips and the generated aria description. These need one browser run with ECharts 5.6.0, which this sandbox cannot load. The gallery's built-in self-test performs that run and reports pass or fail against the thresholds below.

If the treemap fails its thresholds

Keep ECharts for the other ten visuals and draw both treemaps with our own squarified HTML component. The algorithm already exists in the gallery: about 30 lines, exact areas, tested on 2,000 random layouts. It removes the only medium-risk row from the matrix without changing the rest of the stack.

Parity matrix
#	V2 VISUAL	CARDS	BUILT WITH	PARITY	WHAT THE BUILD ADDS OR CHANGES	VERIFIED SO FAR	ECHARTS RUN
1	Stat tiles	Properties, KPIs, Tenant overview	HTML	Exact	Native buttons; dash and “Unavailable” instead of 0 (DXD-16)	Selection, payload, keyboard (browser)	Not needed
2	Occupancy meter	Properties	HTML	Exact	Segments are buttons with count and share	Selection, phone frame	Not needed
3	Donut, top 4 + Other, view switch	Lease requests	ECharts pie	Exact	HTML centre total and legend; legend selects instead of hiding; Other not selectable; shares use the displayed total	Adapter, keyboard, click path, Other rule, payload, view switch	Pending
4	Stage flow with splits	Sales funnel	HTML (DR-008)	Exact	“Other statuses” line	Selection, phone stacking	Not needed
5	Half gauges ×3	Pending approvals	ECharts gauge	Close	Captions and band counts in HTML; arc thickness and caps to compare at GD	Adapter, keyboard, caption selection	Pending
6	Heatmap type × delay week	Pending amendments	ECharts heatmap	Exact	Quintile colours computed in the adapter, no visualMap; 2-D keyboard	2-D keyboard, tooltip text, selection style, kept style	Pending
7	Treemap + category legend	Service requests (Admin)	ECharts treemap	Close	Squarify with golden-ratio target; labels by share; fixed category order; tile positions differ from the in-house layout	Index mapping for keyboard and tooltip; reference layout metrics	Required
8	Work-permit strip	Service requests (Admin)	HTML	Exact	—	Selection	Not needed
9	Progress rings ×4	Fit-out and handover	ECharts gauge 360°	Close	Null share draws no arc and shows a dash	Adapter, keyboard	Pending
10	Horizontal stacked bars	Fit-out drawings	ECharts bar	Exact	Totals as a right-hand axis; inside labels only when wide enough	2-D keyboard	Pending
11	Stacked columns + table	Drawing document status	ECharts bar	Close	Rotated labels; 7 malls at a time below 640 px with keyboard paging; table from the same dataset	Table parity (21 malls), paging window, keyboard	Pending
12	Diverging bars	Unit discrepancy	ECharts bar	Exact	Partial-coverage label (DXD-14)	2-D keyboard	Pending
13	Monthly columns	Tenant reported sales	ECharts bar	Exact	labelLayout.hideOverlap; narrow: value on the selected column only (DXD-20)	Narrow label rule	Pending
14	Donut, fixed status order	Tenant service requests	ECharts pie	Close	“Other” darkened to #D4D0DE to stay visible on white	Adapter, keyboard	Pending
15	Treemap, leaf per status	Tenant service requests	ECharts treemap	Close	As row 7	Index mapping	Required
Verified in this session
39 of 39 browser checks on the gallery (Chromium, Playwright), with ECharts replaced by a labelled test double. Covered: keyboard paths, announcements, the click and Enter selection paths, active and kept styles, payloads, legends, view switches, table parity, phone frame, paging window, narrow label rule, blocked-CDN fallback, and no page errors.
Squarified reference layout: 2,000 random layouts with exact areas, in bounds, no overlaps. Admin data at 760 / 480 / 326 px gives an area CV of 0 % and 100 % largest-first order.
Palette contrast computed with the WCAG 2.2 formula (in the gallery’s accessibility section).
Every value comes from the DX2 models, so the gallery and the dashboards reconcile.
Needs the real ECharts run
Each chart renders with the SVG renderer, and its option data matches the adapter.
ECharts’ aria description carries our summary.
Keyboard focus shows the real ECharts tooltip, the same one as hover.
Treemap: area ÷ value CV ≤ 5 %, largest-first order ≥ 90 %, mean aspect ≤ 1.25 × reference. Read from the chart model at 760, 480 and 326 px.
Charts resize to a 390 px frame without overflow.
Side-by-side visual check of gauges, rings and both treemaps against V2 screenshots at GD.
Findings
ID	FINDING	DESIGN RESPONSE
F-01	ECharts gives no keyboard focus to individual data points	The gallery’s accessibility layer makes each chart one tab stop. Arrow keys move an active point (2-D where the chart is 2-D) and drive ECharts’ highlight and showTip. A polite live region announces the value and position, and Enter reuses the click path. It depends only on two documented actions.
F-02	ECharts’ default legend hides series when clicked	Hidden series would change totals and break parity. Legends are HTML: they show counts, are real buttons, and select rather than hide.
F-03	Selection state differs by series type in ECharts	Selection is drawn as data-level style (ink border, dashed when kept), the same for pie, bar, heatmap, treemap and gauge captions. It survives option rebuilds and is testable from getOption().
F-04	Treemap tile positions will not match the in-house layout	Fidelity is defined by measurable properties (area, order, shape, grouping, labels), not pixel identity. The HTML fallback is ready if ECharts misses a threshold.
F-05	minShare 0.08 is ambiguous in the API reference	Two readings are shown in the lab. Reading B would hide 8 of 13 sub-categories and their drilldowns, so A is recommended unless the ui-kit source says otherwise.
F-06	Several V2 palette colours are below 3:1 against the white card (teal, amber, light amber, ink-3)	Acceptable under WCAG 1.4.11 only because every value is also text: labels or legend counts, the tooltip, and the Table tab. Label text colour is chosen by measured contrast. Keep the hues for V2 recognition.
F-07	Narrow widths	Document status pages 7 malls at a time, and keyboard focus scrolls the window. Sales values show only on the selected column (DXD-20). Donut legends wrap below the chart.
F-08	Review-time CDN dependency	The gallery loads ECharts from cdnjs only for review, trying a local vendor file first. Production imports ECharts modules from npm, version pinned in M0 (DR-007).
Decisions needed before DX4
ID	QUESTION	OPTIONS	RECOMMENDATION
DXQ-1	How should DR-007 be verified?	(a) allow cdnjs.cloudflare.com and registry.npmjs.org for the session so Claude reruns the full suite; (b) attach echarts.min.js 5.6.0 and axe.min.js; (c) run the gallery’s self-test in Play and paste the result	(a): repeatable, and the vendor file can then ship inside the canvas
DXQ-2	What does minShare 0.08 mean?	A: label threshold · B: fold small leaves · or provide the ui-kit Treemap source	A, unless the source shows B
DXQ-3	Treemap fallback	If ECharts misses a threshold: our HTML squarify component, or accept the ECharts layout	HTML component
DXQ-4	Low-contrast V2 hues	Keep the hues with text equivalents, or darken marks to reach 3:1 (changes the V2 look)	Keep the hues

Design artefact for review. Not production code. Synthetic data as of 20 Oct 2026.
```

## DX3 · Design decision register (conditionally approved)

File: boards/DX3-Decisions.dc.html · Render: renders/DX3-Decisions.png

```text
DX3 · Design decision register

Decisions from the project owner’s DX3 review, 22 Oct 2026. They extend DXD-01…20 and bind DX4–DX6, GENERATIVE_UI.md, AGUI_INTEGRATION.md and API_CONTRACTS.md in M0.

Gate DX3 · Conditionally approved

The DX3 design architecture is approved. DR-007 (ECharts) stays open: real ECharts rendering and interaction validation is a requirement of Design Gate GD. Results from the ECharts test double show only that the gallery’s own layer works; they are never evidence of library compatibility.

Carried to GD
The gallery self-test passes with real ECharts 5.6.0: rendering, aria description, keyboard tooltip, selection, resize.
Treemap thresholds met (area CV ≤ 5 %, order ≥ 90 %, aspect ≤ 1.25 × reference), or both treemaps switch to the custom squarified component.
WCAG checks completed as listed under DXD-24.
minShare reading confirmed against the ui-kit source, if it is available.
ID	DECISION	WHAT IT MEANS FOR THE DESIGN	APPLIED IN	STATUS
DXD-21	How DR-007 is verified	First, run the gallery’s self-test in Play with real ECharts loaded and review the result. If the library cannot load in the canvas, validate with a local, version-pinned ECharts asset. Test-double runs never count as proof.	DX3 gallery · GD	Open until GD
DXD-22	minShare 0.08	Option A, provisionally. Every treemap category and sub-category stays a tile with its drilldown; the threshold only decides label visibility. Confirm against the original ui-kit source if available.	Both treemaps · DX5 GenUI treemap	Approved
DXD-23	Treemap fallback	If ECharts misses the agreed fidelity, accessibility or interaction thresholds, both treemaps use the custom squarified component. ECharts stays for the other suitable chart types.	GD · M2	Approved
DXD-24	V2 palette with verified accessibility	Keep the V2 hues. Every chart must still have accessible labels, visible focus indicators, text alternatives and selection states that do not rely on colour. WCAG compliance is verified, not assumed: a table alternative does not settle every contrast issue. Checks before GD: 1.4.1 use of colour, 1.4.3 text contrast, 1.4.11 non-text contrast, 2.1.1 keyboard, 2.4.7 focus visible, 2.4.11 focus not obscured (sticky bars), 4.1.2 name, role, value, 4.1.3 status messages. Automated with axe-core where it applies, plus a manual pass.	DX3 gallery · DX4 · DX5 · GD	Approved
DXD-25	One selection contract	Every selectable chart, table row, tile and generated component emits selection_ref.v1: dashboard cards, the agent panel, the workspace and generative UI alike.	DX3 gallery payloads · DX4 · DX5	Approved
DXD-26	What a selection carries	A semantic metric identifier with version and kind (parity or corrected), grain, dimensions, value and unit, filter context, authorization scope, and a validated dataset reference (dataset version, as-of date, result reference).	Selection contract	Approved
DXD-27	Chart ↔ table keeps the definition	Switching a chart to its table (dashboard card or generated component) reads the same result reference: same metric definition, grain, filters and access scope. A table may show finer rows only if they reconcile with the chart totals.	Cards · generated components	Approved
DXD-28	Same semantics everywhere	Selecting in the workspace or in a generated chart behaves exactly as on the dashboard: same states, the same Ask and View records actions, the same payload.	DX4 · DX5	Approved
DXD-29	Active, kept and pinned	One active selection globally is the agent’s default context. Each card or component keeps its own last selection, which is never sent automatically. Multi-selection analysis happens only after the user explicitly pins selections.	DX4 context tray	Approved
DXD-30	Grounded numbers	Every displayed number comes from the shared synthetic dataset. In the design prototypes, figures are computed by the DX2 model functions that draw the dashboard. In the product, they come from metric-service results. The model never types a number.	All stages	Approved
selection_ref.v1

Emitted by every selectable element. The agent receives only the active selection and any pinned ones; kept selections stay on their cards. The backend re-validates the dataset reference and scope before using a selection, so a stale or widened selection is rejected rather than trusted.

Generated components set surface to genui and componentId to the message and component IDs, and point resultRef at the tool result they render.

{
  "schema": "selection_ref.v1",
  "selectionId": "sel_3f9c21aa",
  "surface": "dashboard",               // dashboard | workspace | genui
  "componentId": "admin.pendingAmendments.heatmap",
  "metric": { "id": "amendments.pending_by_age_band", "version": "v1", "kind": "parity" },
  "grain": "amendment_type × age_band",
  "dimensions": [ { "name": "amendment_type", "value": "Renewal" },
                  { "name": "age_band", "value": "4 wk+" } ],
  "value": { "number": 18, "unit": "amendments" },
  "filters": { "year": 2026, "month": "All", "region": "Central", "mall": "All" },
  "scope": { "kind": "regions", "label": "Access: all regions" },
  "dataset": { "version": "sd-2026.10.20-01", "asOf": "2026-10-20",
               "resultRef": "res_7f3a0c12", "validated": true },
  "role": "active"                      // active | kept | pinned
}
```

# DX4 · Agent workspace (conditionally approved)

## DX4 · Agent workspace (interactive, 10 journeys)

File: boards/DX4-Workspace.dc.html · Render: renders/DX4-Workspace.png · interactive prototype

```text
DX4 · Dashboard Intelligence Agent workspace

Interactive design prototype. Ten journeys play the agent lifecycle step by step: context, plan, tool calls, evidence, generated components, confirmations and history. Every number comes from the shared synthetic dataset through fact tokens.

Desktop
Tablet · 1024
Phone · 390
J1 · Ask from a chart selection
J2 · Multi-step investigation
J3 · Confirmed dashboard filter change
J4 · Partial information
J5 · Unavailable data
J6 · Budget limit, failure and versioned retry
J7 · History and resume
J8 · Tenant access boundary
J9 · Interruption, reconnection and Stop
J10 · Context isolation checks
Play
Step
Skip to end
Restart
No journey loaded
Choose a journey, then Play or Step. You can also click around freely.
Cenomi Dashboard Agent POC
SYNTHETIC DATA · AS OF 20 OCT 2026
Dashboard
Workspace
Portfolio admin · 3 regions
Switch to tenant (demo)

Pending amendments

2026 · All months · Central · All malls

Expansion
HoldOver
Renewal
Termination
4 wk+
1
2
18
4
4 wk
0
1
3
1
3 wk
1
0
2
2
2 wk
2
1
1
1
1 wk
1
0
2
1

As of 20 Oct 2026 · synthetic data

Pending approvals

All regions · All malls

38%
Proposals · 117 pending
45 older than a month
42%
Contracts · 78 pending
33 older than a month
38%
Leases · 37 pending
14 older than a month

All types: 232 pending · 92 older than a month

Share older than one month · as of 20 Oct 2026 · synthetic data

Unit discrepancy

2026 · Sep · mall-wise

PARTIAL
Observed subset: no report this month from 7 of 25 malls.
Gulf Gate Mall
11
Rawdah Point Mall
6
Harbor Lights Mall
6
Najd Gate Mall
5
Pearl Bay Centre
5
Sandstone Galleria
5

Mismatched units in the latest report · as of 20 Oct 2026
```

## DX4 · Interaction specification (revised after review)

File: boards/DX4-Spec.dc.html · Render: renders/DX4-Spec.png

```text
DX4 · Interaction specification

The rules behind the workspace prototype, written to carry into AGENT_ARCHITECTURE.md, AGUI_INTEGRATION.md and GENERATIVE_UI.md in M0. Terms follow the G0 decisions (DR-016, DR-017, DR-031, DR-032) and DXD-01…40. Revised after the DX4 review: thread-local selections (DXD-32), composite only on request (DXD-31), immutable history (DXD-33), evidence envelope (DXD-36), versioned recovery (DXD-37). Event contracts are on DX4-AGUI.

Surfaces
Docked panel (420 px, dashboard): quick questions about a card or selection. Answers are compact; steps collapse to one summary line with Execution. Open in workspace keeps the thread, selection and filters.
Workspace: history · thread · context and canvas. Steps are expanded while a run is live and collapse when it completes.
Inspector (overlay, 480 px): Evidence, Definition, Records, Execution, opened from any answer, statement or component. Closing returns to the same place.
Tablet: history and context become drawers. Phone: one column; the panel and the inspector open full screen.
Order inside an answer
Header: run state while live, outcome when complete (supported, derived, partial, related only, unavailable, needs input), and the summary (tool nodes, iterations, time, model calls).
Activity: iterations, then nodes with tool, sanitised arguments, result summary, attempts.
Statements with text labels: Observed, Derived, Hypothesis (dashed), Recommendation, Unavailable. Each has Evidence.
Caveats from the metric definitions.
Components: notices first (partial, unavailable, error, outside access), then KPI cards, then charts and tables.
Proposed dashboard change, clarification options, suggested follow-ups.
What the agent receives
This investigation’s active selection (selection_ref.v1), shown in the composer as “Context sent” with its source.
This investigation’s pinned selections, only when pinned.
This investigation’s analytical scope chips (removable; removing one widens the question only up to the access scope).
The thread’s analytical state: focus entities, metrics, dataset refs, decisions.

Never sent: kept selections, the dashboard’s own selection unless imported, other investigations unless explicitly imported, raw rows. Boundaries (access scope, reference date) are applied on the server; the client cannot remove or widen them. Every selection is re-validated (dataset version, scope) on send and on resume.

Lifecycle, what the user sees, and the AG-UI events
STATE (DR-032)	LABEL IN THE UI	WHAT THE UI SHOWS	AG-UI EVENTS (DR-017)
RECEIVED → CONTEXT_RESOLVED	Received · Context resolved	The user message with its context chips. The access scope is noted in Execution.	RUN_STARTED, STEP_STARTED, STATE_SNAPSHOT
PLANNED → PLAN_VALIDATED	Planning · Plan checked	Queued plan nodes appear. The fast path (direct metric, frontend tool) skips the model.	ACTIVITY_SNAPSHOT (ANALYSIS_PLAN), STEP_FINISHED
EXECUTED	Running tools · n of m done	Nodes move through Queued → Running → Done, Retrying, Failed or Blocked. Parallel branches start together.	TOOL_CALL_START/ARGS/END/RESULT, ACTIVITY_DELTA
EXECUTED → PLANNED	Planning · Re-plan	A second iteration appears with its reason (“Three malls have no discrepancy report…”). At most one re-plan.	ACTIVITY_DELTA
FACTS_EXTRACTED · SYNTHESIZED · EVIDENCE_VERIFIED	Facts extracted · Writing · Evidence verified	Counts of facts and of numbers checked. Statements stream only after verification.	STATE_DELTA, TEXT_MESSAGE_START/CONTENT/END
COMPOSED → COMPLETE	Outcome	Components render from validated payloads; the outcome chip replaces the state; steps collapse.	CUSTOM cenomi.presentation.v1, RUN_FINISHED
CLARIFICATION_REQUIRED	Needs your input	An explanation and option buttons; choosing one starts a new run.	CUSTOM (choice), RUN_FINISHED
ERROR	Error	Typed error with a request reference; earlier output stays visible. A failed node offers Retry this step, which creates answer v2 (J6).	RUN_ERROR
CANCELLED	Stopped	Stop aborts the stream and calls the idempotent cancel endpoint. Completed tool results stay in Execution; no partial narrative. Run again starts a new run (J9).	RUN_ERROR (code CANCELLED)
Any state · stream interrupted	Reconnecting · Recovered	A strip shows the last event received, then the replayed range. Duplicates are ignored by (runId, seq). The run continues on the server (J9).	Replay from the run ledger (our endpoint, not part of AG-UI)

Reasoning events are not forwarded. Tool arguments are sanitised summaries; rows and SQL never reach the client. The prototype shows the event log in Inspector → Execution so the mapping can be reviewed.

Errors, gaps and boundaries
SITUATION	BEHAVIOUR	STATEMENT LABEL	OUTCOME	JOURNEY
Tool timeout	One automatic retry, shown as Retrying with the attempt and reason.	—	unchanged	J2
Tool fails after retry	Node Failed. Answer v1 uses what loaded and says what is missing. Retry this step re-runs only that node as a new run and adds answer v2 (“revises v1”); v1 stays exactly as generated and is marked superseded.	Unavailable	partial → v2 supported	J6
Connection lost mid-run	Reconnect with backoff; replay missed events after the last seq; drop duplicates. Nothing is re-executed.	—	unchanged	J9
User presses Stop	Run cancelled; tool results kept; no partial narrative; Run again uses a new request id.	—	stopped	J9
Plan over budget (more than 8 tool nodes)	The validator rejects the plan; the agent offers smaller scopes instead of truncating silently.	Recommendation	needs input	J6
Partial coverage	A Partial notice names what is missing. An observed total is labelled “observed subset” with its coverage (18 of 25 malls); the full total is an Unavailable card, never extrapolated. Every statement and visual inherits “Coverage: partial”.	Unavailable for the missing total	partial	J2, J4
Concept not in the dataset	check_concept_availability; no number and no estimate. Related facts only with a “not a proxy” caveat.	Unavailable, then Observed	related only	J5
Outside the access scope	The node is Blocked before any query. An Outside your access notice explains the boundary; in-scope data follows.	Unavailable	related only	J8
Verifier rejects a draft	One retry, then a deterministic template answer (DR-031). Shown in Execution; not demonstrated in a journey.	as drafted	unchanged	—
Free text the prototype cannot answer	A clearly marked prototype note. The product would run the normal lifecycle.	—	—	any
Selection semantics (DXD-25…28, DXD-32)
Same visual states and selection_ref.v1 on dashboard cards, the panel, the workspace and generated components.
The dashboard keeps its own selection state. Each investigation keeps its own active, kept and pinned selections.
A selection crosses into an investigation only by explicit import (Ask about this, or Import a selection…), labelled with its source and visible in the composer before sending.
Active: solid outline, “Selected” text and aria-pressed. Kept: dashed outline. Pinned: dark chip and “Pinned”. Never colour alone.
Imports and resumes are re-checked against the current access scope; mismatches are refused.
History and resume (DXD-33)
One thread per investigation: title, time, question count, dataset version, outcome.
Resume shows answers, pins and canvas exactly as generated, with the dataset version. Nothing is refreshed silently.
Re-run with current data is always an explicit action and creates a new run; stored answers never change.
Investigations of another role are never listed, opened or importable.
Grounding
Statements reference facts as tokens; the server fills values from tool results (DR-031).
In the prototype, 71 of 71 statements and component texts pass an automated check: no digit outside a fact token except dates, IDs and band names.
Every fact traces to a metric, filters and result reference shown in Evidence.
Derived values (shares, ranks) come from derive, with the formula shown.
Decisions recorded at the DX4 review
ID	QUESTION	DECISION	RECORDED AS
DXQ-05	Composite rankings across KPIs	Option C: composite only on explicit request, with weighting, normalisation, missing-data treatment and limitations disclosed. Default: multi-KPI table, KPI leaders, magnitude, severity and a transparent order.	DXD-31
DXQ-06	Active selection when switching threads	Option C: analytical selections are local to each investigation; dashboard selection kept separately; cross-thread use only by explicit, labelled import. Supersedes DXD-29 for analytical context.	DXD-32
DXQ-07	Resuming after the dataset changes	Option A: preserve answers exactly as generated, show the dataset version, offer an explicit re-run; never refresh silently.	DXD-33

Design artefact for review. Not production code. Synthetic data as of 20 Oct 2026.
```

## DX4 · Journeys step by step (verified captures)

File: boards/DX4-Journeys.dc.html · Render: renders/DX4-Journeys.png

```text
DX4 · Journeys, step by step

Each journey as played in the interactive workspace board, with the frame captured at its key moment. Captures come from Chromium runs of the same file the canvas publishes (fallback font in the test sandbox; Inter on the canvas).

10
journeys · ten DX4 priorities plus the review corrections
77 / 77
browser checks passed (incl. keyboard, focus, contrast)
211
logic checks: isolation, versioning, recovery, envelopes
71 / 71
statements and component texts use only fact tokens
0
page errors · no unresolved placeholders
J1
Ask from a chart selection

Dashboard · docked panel

Docked agent panel
Explicit import of the dashboard selection
Plan and tool activity
Evidence envelope per statement
Select Renewal × 4 wk+ on the heatmap
The cell is selected on the dashboard (selection_ref.v1, surface dashboard). That selection belongs to the dashboard, not to any investigation.
Ask about this
The panel opens and the selection is imported into this investigation, labelled “imported from Dashboard · Pending amendments” in the composer before sending.
Ask “Why are so many renewal amendments older than four weeks?”
Context resolved → plan (three parallel tool calls) → re-plan adds a related KPI → facts → verified answer.
Read the answer
18 of 44 (40.9 %); 9 at Rawdah Point. Both approval populations are stated: 41 older than a month out of 71 pending of all ages. Every statement carries class, filters, access, freshness, dataset version and coverage.
Open Evidence, Records or Execution
Fact tokens with source, result and coverage; 8 oldest of the 18 records; lifecycle, budgets, run and request ids and the AG-UI event log with sequence numbers.
J2
Multi-step investigation · composite only on request

Expanded workspace

DXQ-05 · no default composite
Leaders, magnitude and severity
Disclosed composite on request
Thread-local selections and pins
Ask which Central malls need leasing attention first
Four parallel calls (one reused, one retried) and a coverage re-plan. No combined score is calculated.
Read the default answer
KPI leaders, magnitude (Rawdah Point: 37 more old approvals than any other mall) and a transparent order. Sandstone Galleria is above the median on 4 of 4 KPIs and leads none. A multi-KPI table marks “Leader” in text.
Ask “Combine the KPIs into one score.”
Only now: an equal-weight mean rank, classified Derived, with a method card for weighting, normalisation, missing data and limitations.
Select and pin two rows
Selections and pins live in this investigation. The dashboard’s heatmap selection is kept and shown separately; it is not sent.
Compare pinned
Reuses the comparison result (no new query) and names the higher mall on each KPI.
J3
Confirmed dashboard filter change

Workspace → dashboard

Agent proposes; the user confirms
Populations stated
Changed flag and undo
Ask to show Rawdah Point on the dashboard
The proposal states what the card will show: 71 pending of all ages (32 · 23 · 16), 41 older than a month. Nothing changes yet.
Apply filter
Pending approvals switches to Central · Rawdah Point Mall, adds the all-types line (71 · 41) and is flagged “Changed after your confirmation”. Apply is idempotent per proposal id.
Undo
The card returns to All regions · All malls (232 · 92).
J4
Partial information · observed subset

Workspace · new investigation

Coverage semantics
Portfolio total unavailable
Coverage inherited by every visual
Ask how many units had mismatches in September
Metric and coverage are queried in parallel.
Read the answer
87 of 3,000 checked units is labelled the observed subset covering 18 of 25 malls. The portfolio-wide total is an Unavailable card (“—”), never an estimate; the seven missing malls are named. Every statement and component shows “Coverage: partial”.
J5
Unavailable data

Workspace · new investigation

Unavailable concept
Related information, clearly labelled
Ask for footfall at Gulf Gate Mall
check_concept_availability finds no visitor-count source and no approved proxy.
Read the answer
No number and no estimate. Related facts follow with a caveat that they are not a proxy for footfall. Outcome: Related only.
J6
Budget limit, failing tool, versioned recovery

Workspace · new investigation

Plan rejected by budget
Tool failure after retry
v1 preserved, v2 added
Leaders by region, no composite
Ask to compare every KPI for all malls over three years
The plan needs 12 tool nodes; the limit is 8. The run stops at “Needs your input” with three smaller scopes.
Choose “By region, 2026 only”
Vacancy fails twice (503). Answer v1 is Partial and says vacancy was left out rather than guessed.
Retry this step
Only the failed node re-runs, as a new run. Answer v2 (“revises v1”) adds vacancy (Eastern 14.3 %, Western 12.0 %, Central 11.9 %). v1 stays exactly as generated and is labelled “superseded · kept unchanged”; the inspector lists both versions.
J7
History, resume and no silent refresh

Workspace · history

DXQ-07 · immutable history
Dataset version shown
Explicit re-run
No cross-thread context
Open history
Each investigation shows outcome, question count and dataset version.
Resume a thread
Answers are shown exactly as generated with their dataset version; stored selections and scope are re-checked against current access. “Re-run with current data” is a separate, explicit action.
Switch threads
The other thread’s selection does not follow. It appears only under “Import a selection…”, with its source.
J8
Tenant access boundary

Tenant · docked panel

Authorization boundary in conversation
Blocked before any query
Ask how my sales compare with other tenants
The node for other tenants’ sales is blocked by the AccessScope before it runs; no query is made.
Read the answer
An Unavailable statement explains the boundary; the tenant’s own figures follow.
J9
Interruption, reconnection and Stop

Workspace · new investigation

Reconnect and replay by seq
Duplicates ignored
Stop → CANCELLED
Run again = new run
Ask which Central malls have the most vacant units
Three parallel tool calls start.
The connection drops
A strip says “Connection lost after event #N. Reconnecting”. The client resumes from the run ledger (GET /runs/{id}/events?after=N); replayed duplicates are dropped by (runId, seq).
Press Stop before the answer is written
Abort plus idempotent POST /runs/{id}/cancel. Outcome Stopped; completed tool results stay in Execution; no partial narrative is shown.
Run again
A new run with a new request id; the stopped run stays in the thread.
J10
Context isolation checks

Workspace · threads, roles, scope

Thread switch
Explicit import
Role switch
Scope removal never widens access
Open another investigation, import, then clear
Nothing crosses threads unless imported; the import is labelled with its source and can be cleared.
Remove the “Region: Central” scope chip
The next question widens only up to access (all regions). Boundaries cannot be removed.
Switch to tenant and back (demo control)
Tenant sees no admin investigations, selections or imports. Back as admin, stored selections and scope are re-checked before use. Cross-scope imports are refused.
R
Tablet and phone

Same journeys at 1024 and 390 px

Tablet
History and context become drawers opened from the thread header; the inspector overlays the thread.
Phone
One column. The docked panel and the inspector open full screen; statement labels sit above their text. Nothing overflows the 390 px frame.
```

## DX4 · Decision register DXD-31…40

File: boards/DX4-Decisions.dc.html · Render: renders/DX4-Decisions.png

```text
DX4 · Design decision register

Decisions and corrections from the project owner’s DX4 review, 22 Oct 2026. They extend DXD-01…30 and bind DX5–DX6, AGENT_ARCHITECTURE.md, AGUI_INTEGRATION.md, GENERATIVE_UI.md and KPI_CATALOG.md in M0.

Gate DX4 · Conditionally approved · corrections completed

DXQ-05, DXQ-06 and DXQ-07 are recorded as DXD-31…33. Corrections 1–7 from the DX4 review are addressed in the prototype and recorded as DXD-34…40. The approved DX4 design is otherwise unchanged. Nothing in the GitHub repository was modified.

Verification
Browser run of the workspace board: 77 of 77 checks pass (journeys, keyboard, focus, contrast, phone overflow).
Logic run: 211 checks pass, including 172 evidence envelopes, isolation, versioning and recovery.
Grounding: 71 of 71 statements and component texts use only fact tokens for numbers.
Carried to GD: axe-core and a manual screen-reader pass on the real build (axe-core could not be loaded in this sandbox).
ID	DECISION	RULE	APPLIES TO	STATUS
DXD-31	Composite rankings only on request	DXQ-05 · Option C. By default the agent answers prioritisation questions with a multi-KPI comparison table, the leader on each KPI (marked “Leader” in text), magnitude and severity, and a narrative that states its ordering rule. A combined score is produced only when the user explicitly asks; it is classified Derived and carries a method card: weighting, normalisation, missing-data treatment and limitations. The default answer says no combined score was calculated.	J2 · J6 · agent prompt and composer rules · GENERATIVE_UI (method kind)	Approved
DXD-32	Analytical selections are thread-local	DXQ-06 · Option C. Each investigation keeps its own active, kept and pinned selections and scope chips. The dashboard keeps its selection state separately. A selection crosses into an investigation only by explicit import (Ask about this, or Import a selection…), labelled with its source and visible in the composer (“Context sent”) before submission. Revises DXD-29; see reconciliation below.	DX4 workspace · DX5 · selection contract	Revises DXD-29
DXD-33	History is immutable	DXQ-07 · Option A. Resumed investigations show answers exactly as generated, with their dataset version. Re-run with current data is an explicit action that creates a new run; stored answers never change and are never refreshed silently.	J7 · history · run store	Approved
DXD-34	KPI reconciliation (finding)	J1’s 41 and J3’s 32 measure different populations of the same KPI at Rawdah Point: 41 is all approval types older than a month; 32 is proposals of all ages. Both reconcile (table below). No synthetic-data correction was needed and no KPI definition changed. Fix: every approval statement names its population, the proposal states all-types totals, and the dashboard card adds an all-types line.	J1 · J3 · Pending approvals card · KPI_CATALOG note	Resolved
DXD-35	Coverage semantics	An observed total from incomplete reports is labelled “observed subset” with its coverage (J4: 87 of 3,000 checked units, 18 of 25 malls). The full-portfolio total is an Unavailable card (“—”), never estimated. Partial coverage is inherited by every statement and visual built on the subset.	J2 · J4 · GENERATIVE_UI unavailable variant	Approved
DXD-36	Evidence envelope on every statement and visual	Every statement and generated component carries: evidence class, metric ids and versions, filters (inherited from the answer when a derived value has none of its own, and marked so), authorization scope, freshness (as-of date), dataset version, and coverage. Compact form in the panel, full form in the workspace and inspector; coverage “partial” is shown in text, not only colour.	All answers · DX5 component contract	Approved
DXD-37	Versioned recovery	A successful retry of a failed node is a new run that creates answer v2 (“revises v1”). v1 is preserved exactly as generated, labelled “superseded · kept unchanged”, and both appear in the inspector’s Versions list. Run again after Stop is also a new run with a new request id; the stopped run stays.	J6 · J9 · run store	Approved
DXD-38	Context isolation rules	Switching threads, changing roles, removing scope chips and resuming investigations can never widen authorization or import context implicitly. Imports and resumes are re-checked against the current access scope; mismatches are refused or dropped with a banner. Another role’s investigations are not listed, opened or importable. Removing a scope chip widens only to the access scope; boundaries cannot be removed.	J7 · J10 · server AccessScope	Approved
DXD-39	Accessibility of evidence, activity and selection	Evidence labels, coverage, version and connection states are text. Selectable rows, bars and cells expose aria-pressed and a text state. The inspector is a dialog that takes focus, supports Escape and restores focus; tabs use arrow keys. One polite live region announces run status. Text contrast ≥ 4.5:1 on all labels and controls (automated).	DX4 · DX5 · GD (axe-core on real build)	Approved
DXD-40	AG-UI handoff contracts	Event-to-state mapping, run identity (threadId, runId, requestId, seq), cancellation, interruption and reconnection, retry kinds and idempotency are fixed as design contracts on DX4-AGUI. Assumptions about the AG-UI SDK are listed for verification against the pinned version in M0.	AGUI_INTEGRATION.md · API_CONTRACTS.md · M4	Approved
DXD-32 · Reconciling with the earlier selection decisions
EARLIER DECISION	STATUS	WHAT CHANGES
DXD-25 · one selection contract	Kept	All surfaces still emit selection_ref.v1.
DXD-26 · what a selection carries	Kept	Unchanged. The scope field is now also used to refuse cross-scope imports.
DXD-27 · chart ↔ table keeps the definition	Kept	Extended: the table view also keeps the coverage label.
DXD-28 · same semantics everywhere	Kept	Same states and actions on dashboard, panel, workspace and generated components.
DXD-29 · one active selection globally	Superseded for analytical context	Replaced by DXD-32. “Active” now means active within its store: the dashboard has one, each investigation has one. Per-card kept selections and explicit pinning are unchanged.
DX2 DXD-12 · dashboard selection becomes the agent context	Superseded for analytical context	The dashboard selection reaches an investigation only through Ask about this (explicit import) or Import a selection…, labelled with its source.
DXD-34 · Pending approvals tie-out (computed from the synthetic dataset)

Pending approvals as of 20 Oct 2026, all delay bands. “Older” is the over-one-month band. Mall rows sum to Central and regions sum to the portfolio for every type and every delay band.

TYPE	RAWDAH · PENDING	RAWDAH · OLDER	CENTRAL · PENDING	CENTRAL · OLDER	ALL REGIONS · PENDING	ALL REGIONS · OLDER	CHECK
Proposals	32	19	67	31	117	45	ties out
Contracts	23	15	43	22	78	33	ties out
Leases	16	7	20	9	37	14	ties out
All types	71	41	130	62	232	92	ties out
What J1 and J3 actually said
J1: “Rawdah Point also holds 41 of Central’s 62 approvals waiting more than a month … out of 71 pending approvals of all ages there.”
J3: “It will show 71 pending approvals of all ages (32 proposals, 23 contracts, 16 leases), 41 of them older than a month.”
Dashboard card: per-type gauges plus “All types: 71 pending · 41 older than a month” when filtered to Rawdah Point; 232 · 92 for all regions.
Other figures re-checked
Amendments 4 wk+ in Central: 25 (mall rows sum to the region); renewals 18.
Vacancy in Central: 408 of 3,420 units, mall rows sum to the region.
No KPI definition or synthetic record was changed.
DXD-38 · Isolation checks (automated)
LOGIC CHECK (NODE)	RESULT
Switching thread does not carry t1 active selection	pass
Switching thread does not carry t1 pins	pass
Composer shows no selection after switching thread	pass
Importables are listed with a source	pass
Explicit import is labelled with its source	pass
Import does not move the selection out of the source thread	pass
Tenant has nothing importable from admin threads	pass
Tenant cannot open an admin investigation	pass
Tenant history lists no admin investigations	pass
Admin-scoped selection cannot be imported as tenant	pass
Tenant-scoped selection cannot be imported as admin	pass
Resume drops a stored selection whose scope no longer matches access	pass
Boundaries unchanged after removing scope	pass
Boundaries cannot be removed via unscope	pass
BROWSER CHECK (CHROMIUM)	RESULT
Switching thread does not carry the other thread’s selection	pass
Other thread’s selection is offered as an explicit import with source	pass
Import list shows sources	pass
Dashboard selection is shown separately and not sent	pass
Context tray is thread-local: active, kept, 2 pinned	pass
Role switch to tenant hides admin threads and imports	pass
J10 ends in admin with boundaries intact and scope removed	pass
DXD-37 · Versioning checks · DXD-39 · Accessibility checks
VERSIONING AND HISTORY	RESULT
Retry leaves version 1 exactly as generated	pass
Retry creates version 2 that revises version 1	pass
v1 stays partial; v2 is supported	pass
Version labels distinguish v1 and v2	pass
v2 has its own run id	pass
J6 v1 kept and labelled superseded	pass
J6 v2 labelled as revision	pass
Inspector lists versions v1 and v2	pass
J7 resume shows dataset version; answers preserved	pass
Re-run with current data is explicit	pass
ACCESSIBILITY (BROWSER)	RESULT
Keyboard: Enter on a table row selects it (aria-pressed)	pass
Selection has text, not only colour	pass
Inspector opens as dialog and focuses its heading	pass
Arrow keys move between inspector tabs	pass
Escape closes inspector and restores focus to the trigger	pass
Escape closes the inspector	pass
Live region announces agent status	pass
All buttons have an accessible name	pass
Text contrast ≥ 4.5:1 on labels, chips, envelopes and controls	pass
J2 multi-KPI table marks leaders in text	pass
Sorted column exposes aria-sort	pass

Design artefact for review. Not production code. Synthetic data as of 20 Oct 2026.
```

## DX4 · AG-UI handoff contracts

File: boards/DX4-AGUI.dc.html · Render: renders/DX4-AGUI.png

```text
DX4 · AG-UI handoff contracts

Design contracts for AGUI_INTEGRATION.md and API_CONTRACTS.md (DXD-40). They fix how the client reduces AG-UI events into state, how runs are identified, and how cancellation, interruption, reconnection, retry and idempotency behave. The DX4 workspace prototype follows these rules; its Execution tab shows the event log with sequence numbers.

Run identity
threadId: one investigation. Owns selections, pins, scope and runs (DXD-32).
runId: one execution, server-assigned.
requestId: client UUID per user submit; the idempotency key for POST /runs.
seq: server-assigned, strictly increasing within a run; persisted with every event in agent.run_events.
version and revises: answer lineage within a thread (DXD-37).
Rules the client keeps
Reduce only by (runId, seq); drop seq ≤ lastSeq.
Never rewrite a finished run; new information is a new run.
Statements render only after EVIDENCE_VERIFIED; numbers arrive filled from fact tokens.
Presentation payloads are validated before render; invalid → fallback.
Only sanitised arguments and summaries reach the client; never rows or SQL.
Retry kinds
Automatic tool retry: inside the run, one retry for timeouts; shown as Retrying with the attempt.
Retry this step: user action on a failed node; new run with retryOf; answer v2.
Run again: after Stop or error; new run, new requestId.
Re-run with current data: explicit, from history; new run; stored answers unchanged (DXD-33).
Resubmit (double-click, network): same requestId; same run.
Event → client state
AG-UI EVENT	PAYLOAD USED	CLIENT STATE CHANGE	UI
RUN_STARTED	threadId, runId, seq	Create runs[runId] {threadId, requestId, version, revises, phase RECEIVED, lastSeq}. Bind to the pending user message by requestId.	Agent header with “Received”.
STEP_STARTED / STEP_FINISHED	stepName = lifecycle state (DR-032)	Set phase. Ignore a transition not permitted from the current phase (log it).	Phase chip; Execution lifecycle row.
STATE_SNAPSHOT	run state (scope, context sent, budgets)	Replace runs[runId].state.	Execution · Run identity and context.
STATE_DELTA	JSON Patch (RFC 6902)	Apply to runs[runId].state; on patch failure request a snapshot.	Counters (facts, numbers checked).
ACTIVITY_SNAPSHOT / DELTA	activityType ANALYSIS_PLAN: iterations, nodes, statuses, re-plan reason	Replace or patch runs[runId].plan.	Activity: iterations and nodes (Queued, Running, Done, Retrying, Failed, Blocked).
TOOL_CALL_START / ARGS / END	toolCallId, toolCallName, sanitised args	Upsert nodes[toolCallId]; args only as the sanitised summary.	Node row with tool and arguments.
TOOL_CALL_RESULT	toolCallId, summary, rows, resultRef, error?	Set node result, attempts, status; never store rows.	Result line; attempt lines; Failed notice.
TEXT_MESSAGE_START / CONTENT / END	messageId, delta (only after EVIDENCE_VERIFIED)	Append to stmts; numbers arrive already filled from fact tokens.	Statements stream with labels and envelopes.
CUSTOM cenomi.presentation.v1	component payload + envelope	Validate against the schema. Valid → comps.push; invalid → fallback text or table, log validation error.	Generated component or fallback.
TOOL_CALL_* (frontend tool)	propose_dashboard_filters: proposalId, card, filters	Create proposals[proposalId] pending. On confirm, send the tool result once.	Proposal card with Apply, Dismiss, Undo.
RUN_FINISHED	outcome	Set outcome, done; collapse activity; mark thread outcome.	Outcome chip; follow-ups; live-region announcement.
RUN_ERROR	code (CANCELLED, BUDGET, TOOL, VERIFIER, INTERNAL), message, requestRef	Set phase ERROR or CANCELLED; keep completed results; no partial narrative.	Error notice or “Stopped” card with Run again.
Reasoning events	—	Not forwarded by the server; the client ignores any that arrive.	Nothing.
Interruption, reconnection and cancellation
Interruption and reconnection (J9)
SERVER RUN_STARTED · seq 1 … TOOL_CALL_START · seq 15
CLIENT Stream ends without RUN_FINISHED. lastSeq = 15. Strip: “Connection lost after event #15. Reconnecting (attempt 1 of 5)”.
SERVER The run continues; events 16–18 are written to the ledger.
CLIENT GET /runs/{runId}/events?after=15 (backoff 1 s).
SERVER Replays 16–18 from the ledger. Events 14 and 15 also arrive again from the transport buffer.
CLIENT Drops seq 14 and 15; applies 16–18. Strip: “Recovered · events #16–#18 replayed; 2 duplicates ignored by (runId, seq)”.
Cancellation (J9)
CLIENT User presses Stop. Abort the stream; POST /runs/{runId}/cancel.
SERVER Cancels pending tool calls and the model call; keeps completed tool results; writes RUN_ERROR code CANCELLED.
CLIENT Phase CANCELLED, outcome Stopped. No partial narrative. Completed nodes stay in Execution. Run again offered.
CLIENT Run again → POST /runs with a new requestId (same question and context snapshot).
SERVER New runId. The stopped run remains in the thread.
Idempotency
OPERATION	KEY	SERVER	CLIENT
Submit a question	requestId (client UUID per submit)	POST /runs with the same requestId returns the existing runId; no second run.	Double-click or network retry shows one run.
Receive an event	(runId, seq)	seq is assigned by the server, strictly increasing per run, persisted in agent.run_events.	Drop any event with seq ≤ lastSeq.
Stop	runId	POST /runs/{id}/cancel is idempotent; a finished run returns its final state.	Abort the stream first; repeated Stop is harmless.
Reconnect	runId, lastSeq	GET /runs/{id}/events?after=lastSeq replays from the ledger, then live; if the ledger expired, a STATE_SNAPSHOT plus final events.	Backoff 1, 2, 4, 8, 16 s (5 attempts), then “Couldn’t reconnect” with Reload run.
Retry a failed node	retryOf {runId, nodeId} + new requestId	New run; only that node executes; version = previous + 1; revises = previous runId.	Adds answer v2; v1 unchanged.
Run again after Stop	new requestId	New run from the same question and context.	Stopped run stays in the thread.
Apply a proposal	proposalId / toolCallId	Tool result accepted once; repeats ignored.	Apply is disabled after the first click; Undo is a separate client action.
Choose a clarification option	choiceId + new requestId	Starts a new run; repeats with the same requestId return it.	Selected option shows aria-pressed.
Client state shape (illustrative)
{
  "threads": { "t6": { "persona": "admin", "dsv": "sd-2026.10.20-01",
    "sel": { "active": "selection_ref.v1 | null", "kept": {}, "pins": [] },
    "scope": ["Region: Central"], "runs": ["r9_31", "r9b_40"] } },
  "runs": { "r9_31": {
    "threadId": "t6", "requestId": "req_7f3a…", "version": 1, "revises": null,
    "phase": "CANCELLED", "outcome": "cancelled", "lastSeq": 22,
    "conn": "replayed", "plan": { "iterations": [ … ] },
    "nodes": { "<toolCallId>": { "status": "done", "summary": "…", "resultRef": "…" } },
    "stmts": [], "comps": [], "proposals": {} } }
}
Assumptions to verify against the pinned AG-UI SDK in M0
ID	ASSUMPTION	IF IT DOES NOT HOLD
A1	Event types and names as listed (RUN_*, STEP_*, STATE_*, TOOL_CALL_*, TEXT_MESSAGE_*, CUSTOM) exist in the pinned AG-UI SDK.	Map to the nearest event; keep the reducer table as the contract.
A2	ACTIVITY_SNAPSHOT / ACTIVITY_DELTA are available for the plan.	Carry the plan in STATE_* under state.plan.
A3	TOOL_CALL_RESULT is emitted for backend tools.	Send results as STATE_DELTA on state.nodes.
A4	Resume and replay are not part of AG-UI; they are our endpoint backed by agent.run_events.	Already assumed. Confirm no SDK feature conflicts.
A5	The transport (SSE) can carry a per-event id; we put seq in the payload regardless.	Seq in payload only.
A6	CUSTOM payload size is adequate for presentation payloads (target ≤ 64 KB; tables ≤ 200 rows).	Send a reference and fetch the payload by resultRef.
A7	Events within a run arrive in order on one stream.	Reorder by seq in a small buffer before reducing.
A8	Frontend tool calls can wait for user confirmation without timing out the run.	End the run with the proposal; the confirmation starts a new run.
Tests M4 must include
Reducer: every event type in the table, including unknown or out-of-order lifecycle transitions.
Dedupe: replayed events with seq ≤ lastSeq do not change state.
Cancel: abort plus cancel call; CANCELLED keeps tool results; no statements shown.
Reconnect: drop the stream mid-run; replay restores the same final state as an uninterrupted run.
Retry: node retry produces v2 with revises; v1 is byte-identical before and after.
Idempotent submit: the same requestId twice yields one run.
Proposal: Apply twice sends one tool result.
Presentation: invalid CUSTOM payload renders the fallback and logs a validation error.

Design artefact for review. Endpoint paths are proposals for API_CONTRACTS.md. Not production code.
```

# DX5 · Generative UI (approved · refinements complete)

## DX5 · Generative UI lab, catalogue and validator (interactive, refined)

File: boards/DX5-GenUI.dc.html · Render: renders/DX5-GenUI.png · interactive prototype

```text
DX5 · Generative UI · validated declarative components

The agent never writes UI code. It sends a cenomi.presentation.v1 payload that names an approved component and a validated result. The renderer reads every number from that result, so text, card, table and chart cannot disagree. Charts here are HTML stand-ins for layout and states; production renders them with the DX3 ECharts primitives (DR-007).

One result, four representations
Component catalogue
Payload validator

Renewal backlog · complete
Mismatch rate · partial
Mismatches · 25 malls · subsets
Tenant sales · tenant scope
Workspace · 760
Panel · 420
Phone · 358
Highest first
Lowest first
A–Z
Run invariance check
USER INTENT
Which is highest or lowest
How much / how many
Exact values
ACCESSIBILITY
Default
Screen reader preference

THE RESULT (ANALYSIS_RESULT.V1) · AUTHORITATIVE

Renewal amendments waiting 4 weeks or more · Central

res_8d5121cf

{ "schema": "analysis_result.v1", "ref": "res_8d5121cf", "metric": { "id": "amendments.pending_by_age_band", "name": "Pending amendments by age band", "unit": "amendments", "kind": "parity"
 }, "grain": [ "mall" ], "filters": { "type": "Renewal", "band": "4 wk+", "region": "Central", "year": 2026
 }, "scope": { "kind": "regions", "label": "Access: all regions"
 }, "access": "region · Central", "dataset": { "version": "sd-2026.10.20-01", "asOf": "2026-10-20"
 }, "coverage": { "status": "complete", "note": ""
 }, "rows": [
  [ "Rawdah Point Mall", 9 ],
  [ "Sandstone Galleria", 6 ],
  [ "Qasr Plaza", 3 ],
  [ "Amber Heights", 0 ],
  [ "Cedar Park Mall", 0 ],
  [ "Falcon Square", 0 ],
  [ "Mirage Commons", 0 ],
  [ "Najd Gate Mall", 0 ],
  [ "Oasis Row", 0 ],
  [ "Wadi Crescent Centre", 0 ] ]
}

ENVELOPE CARRIED BY EVERY REPRESENTATION

Observed · amendments.pending_by_age_band v1 · type Renewal, band 4 wk+, region Central, year 2026 · Access: all regions · data as of 20 Oct 2026 · sd-2026.10.20-01 · Coverage: complete

REPRESENTATION POLICY (DXD-51) · PRIMARY: BAR CHART (RANKED)

P1 · Registry: categorical results allow Text, KPI card, Table, Bar chart (ranked).
P2 · Intent “Which is highest or lowest” prefers Bar chart (ranked) → Table → KPI card → Text.
P3 · Data: 10 values; no rule removes a representation.
P4 · Width 760 px: no change.
P5 · Accessibility: every representation has text values, names and states; no change.
P6 · Budget: 6 generated components at this size (DXD-54); further supporting information via Open in workspace and the inspector.

Answer composition at this width: KPI card → Bar chart (ranked) (primary) → Evidence block

INVARIANCE CHECK · AMD · WORKSPACE · VALUE_DESC

All four representations show the same facts, calculations, access scope and coverage; any subset is declared and disclosed.

INVARIANT
text
5 values, all equal to the result; envelope identical
INVARIANT
card
3 values, all equal to the result; envelope identical
INVARIANT
table
10 values, all equal to the result; envelope identical; every row present
INVARIANT
chart
10 values, all equal to the result; envelope identical; every row present

TEXT VIEW AS OPTION 4

Renewal amendments waiting 4 weeks or more · Central
amendments.pending_by_age_band · v1 · parity

OBSERVED
18 renewal amendments in Central have waited four weeks or more.

OBSERVED
9 are at Rawdah Point Mall, 6 at Sandstone Galleria and 3 at Qasr Plaza. The other 7 Central malls have none.

EVIDENCE
Observed · amendments.pending_by_age_band v1 · type Renewal, band 4 wk+, region Central, year 2026 · Access: all regions · data as of 20 Oct 2026 · sd-2026.10.20-01 · Coverage: complete

CARD VIEW AS OPTION 3

Renewal amendments waiting 4 weeks or more · Central
amendments.pending_by_age_band · v1 · parity
Central total
18

Rawdah Point Mall 9

Malls with none 7

EVIDENCE
Observed · amendments.pending_by_age_band v1 · type Renewal, band 4 wk+, region Central, year 2026 · Access: all regions · data as of 20 Oct 2026 · sd-2026.10.20-01 · Coverage: complete

TABLE VIEW AS OPTION 2

Renewal amendments waiting 4 weeks or more · Central
amendments.pending_by_age_band · v1 · parity
MALL	COUNT
Rawdah Point Mall
	9
Sandstone Galleria
	6
Qasr Plaza
	3
Amber Heights
	0
Cedar Park Mall
	0
Falcon Square
	0
Mirage Commons
	0
Najd Gate Mall
	0
Oasis Row
	0
Wadi Crescent Centre
	0

Central total: 18

EVIDENCE
Observed · amendments.pending_by_age_band v1 · type Renewal, band 4 wk+, region Central, year 2026 · Access: all regions · data as of 20 Oct 2026 · sd-2026.10.20-01 · Coverage: complete

CHART AGENT’S CHOICE · PRIMARY

Renewal amendments waiting 4 weeks or more · Central
amendments.pending_by_age_band · v1 · parity
Rawdah Point Mall
9
Sandstone Galleria
6
Qasr Plaza
3
Amber Heights
0
Cedar Park Mall
0
Falcon Square
0
Mirage Commons
0
Najd Gate Mall
0
Oasis Row
0
Wadi Crescent Centre
0

Count of amendments

Central total: 18

EVIDENCE
Observed · amendments.pending_by_age_band v1 · type Renewal, band 4 wk+, region Central, year 2026 · Access: all regions · data as of 20 Oct 2026 · sd-2026.10.20-01 · Coverage: complete

SELECTION · THREAD-LOCAL (DXD-32)

Click or press Enter on any bar, point, cell, stage, tile or row. Arrow keys move between marks; Escape clears.
```

## DX5 · Generative UI contract (revised)

File: boards/DX5-Contract.dc.html · Render: renders/DX5-Contract.png

```text
DX5 · Generative UI contract

Design contract for GENERATIVE_UI.md, AGUI_INTEGRATION.md and API_CONTRACTS.md, revised after the DX5 review. DX5 is approved; the refinements DXD-55…62 are folded in below. The interactive board demonstrates and tests every rule.

1 · The result is authoritative
Tools produce analysis_result.v1: rows, facts (raw and formatted), metric, filters, scope, dimensions, dataset, coverage.
Every derived fact carries a verified calculation record (DXD-55). Neither the LLM nor the renderer derives business values.
Components read values from the result, never from the payload.
2 · The payload only chooses how
cenomi.presentation.v1 names a registered component, a resultRef, a title and encodings.
The agent picks among allowed representations through a bounded policy (DXD-51); the user can switch with View as.
No code, markup, links or values in the payload.
3 · Checks before anything renders
Result checks: resolve, authorize against grants, verify calculations.
Presentation checks: schema, registry, grounding, envelope, limits, safety.
Only a presentation failure on a good result falls back to the table (DXD-57).
cenomi.presentation.v1 · example
{
 "schema": "cenomi.presentation.v1",
 "component": "bar",
 "resultRef": "res_8d5121cf",
 "title": "Renewal amendments 4 wk+ by mall · Central",
 "subtitle": "[[t]] in Central · [[r0]] at Rawdah Point Mall",
 "encoding": {
  "x": "mall",
  "y": "value",
  "sort": "value_desc"
 },
 "envelope": {
  "cls": "Observed",
  "scope": "Access: all regions",
  "dataset": "sd-2026.10.20-01",
  "coverage": "Coverage: complete"
 },
 "interactions": {
  "select": true,
  "drilldown": "records"
 }
}
Calculation record · derived fact (DXD-55)
{
 "method": "ratio",
 "formula": "mismatched units ÷ units checked (reporting malls)",
 "operands": [
  {
   "fact": "mm",
   "label": "mismatched units",
   "value": 33
  },
  {
   "fact": "den",
   "label": "units checked",
   "value": 1291
  }
 ],
 "periods": "2026-09",
 "metric": "unit_discrepancy.mismatch_rate v1",
 "evidence": [
  "q_d65e3f50"
 ],
 "status": "verified",
 "verifier": "derive v1 · deterministic · recomputed by the evidence verifier"
}
analysis_result.v1 · excerpt
{
 "schema": "analysis_result.v1",
 "ref": "res_8d5121cf",
 "metric": {
  "id": "amendments.pending_by_age_band",
  "name": "Pending amendments by age band",
  "unit": "amendments",
  "kind": "parity"
 },
 "cls": "Observed",
 "grain": ["mall"],
 "shape": "categorical",
 "filters": {
  "type": "Renewal",
  "band": "4 wk+",
  "region": "Central",
  "year": 2026
 },
 "scope": {
  "kind": "regions",
  "label": "Access: all regions"
 },
 "dataset": {
  "version": "sd-2026.10.20-01",
  "asOf": "2026-10-20"
 },
 "coverage": {
  "status": "complete",
  "note": ""
 },
 "rows": [
  ["Rawdah Point Mall", 9, "fact r0"],
  ["Sandstone Galleria", 6, "fact r1"],
  ["Qasr Plaza", 3, "fact r2"],
  ["… 7 more rows"]
 ],
 "total": {
  "value": 18,
  "fact": "t"
 },
 "facts": {
  "t": "18",
  "r0": "9",
  "zero_n": "7"
 }
}
Component registry and implementation priority (DXD-42, DXD-62)
KIND	NAME	PRIORITY	RESULT SHAPES	MAX ROWS	RESPONSIVE RULE	INDICATIVE EFFORT
kpi	KPI card	Core	categorical, time, matrix, stages, hierarchy, scalar	—	Same at all sizes; sub-values wrap.	0.5 h
text	Text	Core	categorical, time, scalar	—	Labels stack above statements at ≤ 360 px.	1 h (with insight)
table	Table	Core	categorical, time, matrix, stages, hierarchy, multi	200	Horizontal scroll inside the component; never the page.	2 h (paging, fallback)
bar	Bar chart (ranked)	Core	categorical	30	Long labels truncate; the full label stays in the accessible name.	1 h (DX3 ECharts bar)
trend	Trend (line)	Core	time	60	Every other month label at ≤ 360 px; values strip hidden in the panel (values remain in point names and the table view).	1 h (DX3 ECharts line)
heatmap	Heatmap	Specialized	matrix	120	Column labels abbreviate at ≤ 360 px.	0.5 h (wrap DX3 heatmap)
funnel	Funnel	Specialized	stages	8	Bars left-align at ≤ 360 px.	0.5 h (wrap DX3 funnel)
treemap	Treemap	Specialized	hierarchy	60	Below 400 px becomes a ranked list (same keys).	1 h (wrap DX3 treemap + ranked list)
compare	Comparison table	Specialized	multi	30	Rows become stacked cards at ≤ 360 px; “Leader” stays as text.	0.5 h (table preset)
insight	Insight panel	Core	categorical, time, scalar	—	Labels stack at ≤ 360 px.	with text
notice	Warning / partial notice	Core	any (attached to a result)	—	Wraps.	0.5 h (with unavailable)
unavailable	Unavailable card	Core	any (attached to a result)	—	Wraps.	with notice
evidence	Evidence block	Core	any (attached to a result)	—	Fewer facts listed in compact sizes; all in the inspector.	1 h
method	Method card	Specialized	any (attached to a result)	—	Wraps.	0.5 h (static layout)
records	Drilldown records	Core	records	50	Horizontal scroll; ≤ 50 rows, then “Show all in records”.	1 h (reuse dashboard drilldown)

All fifteen stay in the registry. Core kinds are built first; specialized kinds wrap the DX3 dashboard ECharts primitives or are simple layouts. Until a specialized kind exists, a payload naming it renders through the deterministic table, so no data, evidence or selection is lost. Efforts are indicative for Cursor-assisted work and are finalised in the M4 plan.

Validation pipeline (DXD-47, amended by DXD-57)
STEP	CHECKS
R1 · Result resolves	resultRef names a validated result of this run (or a stored one being resumed).
R2 · Authorization (grants vs scope, dimensions, records)	The viewer’s current grants cover every region, mall and lease in the result scope and dimensions, and every drilldown record. Re-run on resume. Never a label comparison.
R3 · Calculations verified	Every derived fact has a verified calculation record; the verifier recomputes it from its operands.
P1 · Schema	cenomi.presentation.v1; required fields; no unknown fields (a payload cannot carry its own values, data or rows).
P2 · Registry	Component is in the closed registry and can show this result’s shape; encodings name real dimensions.
P3 · Grounding	Text uses fact tokens only; every token is a fact of the result.
P4 · Envelope	Any envelope field present equals the result’s envelope (class, dataset, coverage, scope).
P5 · Limits	Rows per component, title length, payload ≤ 64 KB.
P6 · Safety	No markup, script, links or forbidden keys in any string.
Failure classes and what the user sees
CLASS	WHEN	SHOWS	SAMPLE
None	All checks pass.	Render.	—
Partial data	Coverage is partial (not a failure).	Render with “Coverage: partial — …”, “No report” cells and a Partial notice.	V2
Stale data	Result was generated with an older dataset version (stored answers).	Render exactly as generated with a Stale label and Re-run with current data (DXD-33).	S1
Presentation failure	The payload fails P1–P6 but the result resolves, is authorized and verified.	Deterministic table from the result: its title, envelope, coverage, formatting, row limit and paging. Rejected payload logged.	I1–I5, I7–I9, F1
Calculation failure	A derived value has no verified calculation, or does not recompute.	Error card naming the failure. No values, no table fallback. The analytics step can be re-run.	C1
Authorization failure	The viewer’s current grants do not cover the result or its records.	Withheld. No values, labels, counts or out-of-grant entity names.	I6, A2, A3
Unknown result / unreadable payload	resultRef does not resolve, or the payload is not valid JSON.	Withheld. Nothing is guessed.	I10
Authorization by grants (DXD-56)
Viewers carry grants: regions (admin all, regional manager Central), or leases (tenant T-31206, lease-level results only).
Each result carries its access scope: level, regions, malls, leases. Records are checked one by one on drilldown.
A result partly outside grants is withheld, never filtered by the renderer: a narrower question is a new query.
Stored results are revalidated on resume; error messages never name out-of-grant entities.
RESULT	SCOPE	PORTFOLIO ADMIN	CENTRAL MANAGER	TENANT
Renewal amendments waiting 4 weeks or more · Central	region · Central	allowed	allowed	withheld
Unit mismatch rate · Central malls · September 2026	region · Central	allowed	allowed	withheld
Reported sales · lease T-31206 · January to September 2026	lease · Central	allowed	allowed	allowed
Pending amendments by type and age band · Central	region · Central	allowed	allowed	withheld
Leasing funnel · portfolio · 2026	portfolio · Central, Eastern, Western	allowed	withheld	withheld
Service requests by category and type · portfolio · 2026	portfolio · Central, Eastern, Western	allowed	withheld	withheld
Central malls · four KPIs side by side · no combined score	region · Central	allowed	allowed	withheld
Mismatched units by mall · portfolio · September 2026	portfolio · Central, Eastern, Western	allowed	withheld	withheld
Representation policy (DXD-51)
RULE	INPUT	EFFECT
P1	Registry	Keep only kinds that can show the result’s shape; drop Text without verified statements.
P2	Intent	Order by the user’s intent: ranking → bar, headline → card, trend → line, exact values → table, composition → treemap, concentration → heatmap, conversion → funnel.
P3	Data and dimensions	Fewer than three time points removes the line; more rows than the width limit keeps the bar as a disclosed top-N with the table holding every row.
P4	Display space	Treemap below 400 px → ranked list; a heatmap with more than four columns at ≤ 360 px → table first.
P5	Accessibility	A screen-reader preference puts the table first; charts stay under View as. Every kind has text values, names and states regardless.
P6	Budget	Panel 3, workspace 6 generated components; extra supporting information through Open in workspace and the inspector (DXD-54).
Policy outcomes in the prototype
INTENT	RESULT	SIZE	PRIMARY	VIEW AS	COMPOSITION
ranking	Renewal amendments waiting 4 weeks or more · Central	workspace	Bar chart (ranked)	Table → KPI card → Text	KPI card → Bar chart (ranked) (primary) → Evidence block
headline	Renewal amendments waiting 4 weeks or more · Central	panel	KPI card	Text → Table → Bar chart (ranked)	KPI card (primary) → Evidence block
ranking	Renewal amendments waiting 4 weeks or more · Central	workspace · screen reader	Table	Bar chart (ranked) → KPI card → Text	KPI card → Table (primary) → Evidence block
ranking	Mismatched units by mall · portfolio · September 2026	panel	Bar chart (ranked)	Table → KPI card → Text	Partial notice → KPI card → Bar chart (ranked) (primary)
trend	Reported sales · lease T-31206 · January to September 2026	phone	Trend (line)	Table → KPI card → Text	KPI card → Trend (line) (primary) → Evidence block
composition	Service requests by category and type · portfolio · 2026	phone	Treemap	Table → KPI card	KPI card → Treemap (primary) → Evidence block
concentration	Pending amendments by type and age band · Central	workspace	Heatmap	Table → KPI card	KPI card → Heatmap (primary) → Evidence block
conversion	Leasing funnel · portfolio · 2026	panel	Funnel	Table → KPI card	KPI card → Funnel (primary) → Evidence block
Subsets, pages and samples are always disclosed (DXD-59)
KIND	WHEN	DISCLOSURE
Complete	Every row of the result is shown.	No line; declaration kind “complete”.
Top-N	A chart at its width limit (bar: workspace 15, panel 10, canvas/phone 8).	“Subset · top 10 of 25 malls by highest value. The other 15 are in the table view; totals cover all rows.”
Page	A table over its page size (workspace 25, panel 10, canvas/phone 8).	“Page 1 of 3 · rows 1–10 of 25. Totals cover all rows.” with Previous / Next.
Sample	Records drilldowns that return a sample.	“Showing 8 of 18 records, oldest first.”
Aggregate	Only when the result itself carries an aggregate row with a verified calculation.	Row labelled “Other N malls” with its calculation in Evidence. The renderer never aggregates.

Each chart and table declares data-subset: kind, keys shown, total rows and order. The invariance check verifies the declaration against the result.

Continuity (DXD-60)
ACTION	GUARANTEE
Switch representation (View as)	Same componentId, resultRef and selection key; envelope identical; selection shown on marks or as a selection note on kinds without marks.
Move panel ↔ workspace	Component instance moves with its id, selection and envelope; layout changes per size class only.
Expand	Dialog over the page with the same instance; Escape returns focus; nothing re-queried.
Resume a thread	Rehydrate {componentId, resultRef, selection} and re-run R1–R3 with current grants. If authorization fails the component is withheld and the stored selection is not restored.
Fallback	Keeps componentId and selection keys; marks become table rows.
State vocabulary (DXD-45)
STATE	MEANS	SHOWS	SOURCE IN THE PROTOTYPE
Default	The validated result.	All values printed; envelope.	Result rows
Partial	Some rows or periods are missing from the result.	“No report” / “Not loaded” in place of the value (hatched, never a zero bar); Partial chip; envelope says “Coverage: partial — …”.	Real (mismatch rate) or labelled fixture
Zero	The value exists and is 0.	Prints 0; empty bar track; no hatch.	Real (Mirage Commons)
Empty	No records match the filters.	No numbers; explains that empty is not zero; suggests widening within access.	Any result
Undefined ratio	Denominator is 0.	“Not defined”, never 0% or 100%; reason in the card.	Labelled fixture
Loading	Tool running; nothing validated yet.	Skeleton lines; role=status; no values.	—
Error	Tool failed after retry.	Error card with request ref and Retry this step (adds answer v2, DXD-37).	—
Unavailable	The concept or total cannot be computed.	“—”, the reason, and what is available instead; envelope class Unavailable.	Real (Central-wide rate) or concept
Formatting (DXD-44)
VALUE	RULE
Counts	1,291 · thousands separator; no decimals.
Rates	2.6% · one decimal; computed from counts in the result (num and den kept as facts).
Money	SAR 2,424,000 · currency code first; no abbreviation in values (axis labels may say “K” only as text, never as a value).
Dates	20 Oct 2026 in text; 2026-09 in filters.
Missing	“No report” (source did not report), “Not loaded” (tool did not return it), “—” (unavailable total).
Zero vs empty	0 is a value; empty means no records; both are distinct from missing.
Undefined	“Not defined” when a denominator is 0.
Validator lab · the nineteen sample payloads
ID	CASE	VIEWER	FAILING CHECKS	CLASS	OUTCOME
V1	Valid · ranked bar	Portfolio admin	—	No failure	Rendered
V2	Valid · KPI card, partial	Portfolio admin	—	Partial data	Rendered
V3	Valid · tenant trend	Tenant	—	No failure	Rendered
I1	Unknown component	Portfolio admin	registry:unknown_component	Presentation failure	Fallback table
I2	Line chart on a categorical grain	Portfolio admin	registry:shape_mismatch	Presentation failure	Fallback table
I3	Literal number in the title	Portfolio admin	grounding:literal_number	Presentation failure	Fallback table
I4	Payload carries its own numbers	Portfolio admin	schema:unknown_field	Presentation failure	Fallback table
I5	Hides partial coverage	Portfolio admin	envelope:envelope_mismatch	Presentation failure	Fallback table
I6	Outside the viewer’s access	Tenant	authorization:not_authorized	Authorization failure	Withheld
I7	Markup in a label	Portfolio admin	safety:unsafe_string, grounding:literal_number	Presentation failure	Fallback table
I8	Token that is not a fact	Portfolio admin	grounding:unknown_fact	Presentation failure	Fallback table
I9	Over the row limit	Portfolio admin	limits:max_rows	Presentation failure	Fallback table
I10	Unknown or expired result	Portfolio admin	resolve:result_not_found	Unknown or expired result	Withheld
A1	Regional manager · Central result	Central manager	—	No failure	Rendered
A2	Regional manager · portfolio result	Central manager	authorization:not_authorized	Authorization failure	Withheld
A3	Resumed after access narrowed	Central manager · resumed	authorization:not_authorized	Authorization failure	Withheld
C1	Calculation not verified	Portfolio admin	calculation:calculation_unverified	Calculation failure	Calculation error
S1	Stale stored answer	Portfolio admin · resumed	—	Stale data	Rendered
F1	Invalid payload on a 25-row partial result	Portfolio admin	registry:shape_mismatch	Presentation failure	Fallback table

Design artefact for review. Charts in the DX5 board are HTML stand-ins; production uses the DX3 ECharts primitives, validated against the pinned ECharts runtime at the Design Gate (DXD-61). Not production code. Synthetic data as of 20 Oct 2026.
```

## DX5 · Verification record

File: boards/DX5-Verify.dc.html · Render: renders/DX5-Verify.png

```text
DX5 · Verification record

Chromium runs of the interactive DX5 board as published, plus a Node run of the same component code, after the DX5 refinements. Captures use a fallback font in the test sandbox (Inter on the canvas).

45 / 45
browser checks
3,778 / 3,778
logic checks (355 component views)
33 / 33
lab combinations invariant, subsets declared
19 / 19
validator payloads: expected class and outcome
Lab · complete result at workspace width; all four representations invariant.
Lab · partial result at panel width; “No report” rows; Central-wide rate unavailable.
Lab · 25-mall result at panel width: disclosed top-10 chart and paged table, both invariant.
Lab · tenant result at phone width; tenant scope in every envelope.
Continuity · expanded dialog keeps the instance, selection and envelope.
Continuity · checks after View as, panel move, expand, close and resume.
Resume · portfolio component resumed by a Central manager is withheld; selection not restored.
Validator · stored result revalidated on resume against narrowed grants.
Validator · unverified calculation: error card, no values, no fallback.
Validator · fallback table keeps row limit, paging, partial coverage and evidence.
Validator · stale stored answer shown as generated with a Stale label.
Catalogue · bar chart in all eight states.
Drilldown · keyboard selection emits selection_ref.v1; same-population records.
Catalogue · treemap below 400 px becomes a ranked list.
Browser checks
CHECK	RESULT
Lab: in-page invariance check passes for every result × width × order (33 combinations)	pass
Lab: independent DOM check — shared facts identical, one envelope, same row total, any subset disclosed (33/33)	pass
Lab: tenant result carries the tenant access scope	pass
Lab: partial result shows “No report” (never zero) for the three missing malls in table and chart	pass
Lab: text representation states the Central-wide rate is unavailable	pass
Lab: the invariance check catches a tampered chart value (mutation test)	pass
Lab: the invariance check catches a changed envelope (mutation test)	pass
Keyboard: arrow keys move focus between marks	pass
Keyboard: Enter selects the focused mark (aria-pressed)	pass
Drilldown emits selection_ref.v1 (genui, thread-local) with the selected value	pass
Drilldown records are filtered to the selected mall	pass
Selected mark carries text, not only colour	pass
Escape clears the selection	pass
Selecting on another component keeps the earlier selection as kept (DXD-25…28)	pass
Heatmap cell emits both dimensions and value 18	pass
Trend point emits month and SAR value	pass
Funnel stage emits stage and count	pass
Policy: ranking intent marks the chart as the agent’s choice	pass
Policy: headline intent makes the card the agent’s choice	pass
Policy: screen-reader preference puts the table first; the chart stays a View as option	pass
Inspector shows how a derived value was produced (ratio, operands, period)	pass
Selection survives View as across table, card, text and back	pass
Expanded view is a dialog with the same component, selection and envelope	pass
Escape closes the expanded view back to the workspace	pass
Continuity checks pass for panel, expand, close and resume (component id, envelope, selection)	pass
Resuming a portfolio component as a Central manager withholds it and drops the stored selection	pass
Catalogue: 284 renders (component × state × size) — no bad values, envelope present, nothing overflows its frame	pass
View as: switching bar → table → card → text keeps every shared fact identical	pass
Catalogue matrix shows every applicable state	pass
Treemap below 400 px becomes a ranked list with the same keys	pass
Unavailable card shows “—”, the reason, the alternative, and an Unavailable envelope	pass
Undefined ratio shows “Not defined”, never 0%, and is labelled a fixture	pass
Zero state uses real data (Mirage Commons) and prints 0	pass
Empty state explains empty is not zero and shows no numbers from the result	pass
Loading state shows no values	pass
Validator: all 19 sample payloads give the expected outcome, failure class and failing step	pass
Fallback keeps the row limit, discloses paging, partial coverage and evidence	pass
Fallback paging moves to rows 11–20 without re-querying	pass
Validator: an edited payload with a literal number fails grounding and falls back	pass
Validator: invalid JSON is withheld	pass
All buttons have an accessible name	pass
Tabs expose role=tab and aria-selected	pass
Live region announces validation and selection	pass
Text contrast ≥ 4.5:1 for every visible text node on all three tabs (416 checked)	pass
No page errors or dialogs	pass
Logic checks (selection)
CHECK	RESULT
Renewal template order matches the data (Rawdah, Sandstone, Qasr)	pass
Renewal total 18; 7 malls with none	pass
Highest reported mismatch rate is Cedar Park Mall	pass
Observed subset 33 of 1,291 across 7 malls	pass
Tenant highest March, lowest September	pass
Tenant total SAR 2,424,000	pass
Built 355 component views	pass
A1 Regional manager · Central result → valid	pass
A2 Regional manager · portfolio result → rejected	pass
A3 Resumed after access narrowed → rejected	pass
C1 Calculation not verified → rejected	pass
S1 Stale stored answer → valid	pass
F1 Invalid payload on a 25-row partial result → rejected	pass
A2 reports not_authorized and withhold	pass
A3 reports not_authorized and withhold	pass
C1 reports calculation_unverified and calc_error	pass
F1 reports shape_mismatch and fallback	pass
Plain object parse ignores prototype tricks	pass
Forbidden __proto__ key is rejected	pass
Drilldown emits selection_ref.v1 with value, resultRef and scope	pass
Drilldown records are the same population (Rawdah Point rows)	pass
Selecting elsewhere keeps the previous selection on its component	pass
Heatmap cell selection carries both dimensions and value 18	pass
amd: every derived fact has a verified calculation that recomputes	pass
mm: every derived fact has a verified calculation that recomputes	pass
ts: every derived fact has a verified calculation that recomputes	pass
hm: every derived fact has a verified calculation that recomputes	pass
fn: every derived fact has a verified calculation that recomputes	pass
tm: every derived fact has a verified calculation that recomputes	pass
cmp: every derived fact has a verified calculation that recomputes	pass
ud25: every derived fact has a verified calculation that recomputes	pass
amd_stale: every derived fact has a verified calculation that recomputes	pass
amd_zero: every derived fact has a verified calculation that recomputes	pass
hm_zero: every derived fact has a verified calculation that recomputes	pass
mm_undef: every derived fact has a verified calculation that recomputes	pass
ts_partial: every derived fact has a verified calculation that recomputes	pass
hm_partial: every derived fact has a verified calculation that recomputes	pass
fn_partial: every derived fact has a verified calculation that recomputes	pass
fn_undef: every derived fact has a verified calculation that recomputes	pass
tm_partial: every derived fact has a verified calculation that recomputes	pass
Unverified calculation is detected (C1)	pass
Every rate is a derived fact	pass
Grants check allows a Central manager on a Central result whose label says “all regions”	pass
Record-level check denies a record outside grants	pass
Tenant record check denies another lease at the same mall	pass
Stale stored answer renders as generated, classified stale	pass

Not covered here and carried to the final Design Gate: GenUI charts on the pinned ECharts runtime (DXD-61), axe-core and a screen-reader pass on the real build.
```

## DX5 · Decision register DXD-41…62

File: boards/DX5-Decisions.dc.html · Render: renders/DX5-Decisions.png

```text
DX5 · Design decision register

Decisions from the project owner’s DX5 review, 22 Oct 2026. They extend DXD-01…40 and bind GENERATIVE_UI.md, AGUI_INTEGRATION.md, API_CONTRACTS.md, AGENT_TOOLS.md and the M4 plan.

Gate DX5 · Approved with refinements · refinements completed

DXQ-08…11 are recorded as DXD-51…54 (all Option A). The review clarifications are recorded as DXD-55…62 and built into the prototype and contracts. DXD-41…50 stand, with DXD-47 amended by DXD-57. Nothing in the GitHub repository was modified.

Carried to the final Design Gate
DXD-61: run the GenUI charts on the pinned Apache ECharts 5.6.0 runtime (rendering, accessible names, keyboard, selection, resize, subset lines) — HTML stand-ins are not evidence.
DX3 conditions remain: real ECharts self-test, treemap thresholds, axe-core and screen-reader pass.
Confirm the indicative GenUI effort inside the five-day plan in M4.
ID	DECISION	RULE	STATUS
DXD-41	The result is authoritative	Generated components render values only from the validated result named by resultRef; payload text uses fact tokens only.	Approved
DXD-42	Closed component registry	Fifteen approved kinds; no model-generated code; new kinds through design review.	Approved
DXD-43	Representation alternates	View as switches representation without modifying or re-querying the result.	Approved
DXD-44	One formatting module	Counts, rates, SAR, missing, zero and undefined formatted once, for every representation.	Approved
DXD-45	State vocabulary	Default, partial, zero, empty, undefined ratio, loading, error, unavailable; never conflated.	Approved
DXD-46	Size classes	Workspace 760, panel 420, canvas 360, phone 358, expanded 1000; per-kind responsive rules.	Approved
DXD-47	Validation and fallback	Server-side validation with client-side defensive re-validation. Amended by DXD-57: the deterministic table only for presentation failures on a resolved, authorized, verified result.	Approved · amended
DXD-48	Envelope per component	Every component prints the evidence envelope; a payload envelope that disagrees is rejected.	Approved
DXD-49	Drilldown and selection	Marks are buttons with names, aria-pressed and “Selected” text; arrows, Enter, Escape; selection_ref.v1 into the investigation; records from the same population.	Approved
DXD-50	Fixtures are labelled	Design-only state fixtures are labelled; production never renders fixtures.	Approved
DXD-51	Bounded representation policy (DXQ-08 A)	The agent selects among allowed representations using intent, result shape, dimensions, accessibility preference and display space (rules P1–P6); the user switches with View as.	Approved
DXD-52	Deterministic table fallback (DXQ-09 A)	An invalid presentation payload falls back to a table from the verified, authorized result.	Approved
DXD-53	Treemap below 400 px (DXQ-10 A)	Becomes a ranked list with the same keys and selection.	Approved
DXD-54	Component budget (DXQ-11 A)	At most three generated components in the docked panel and six in the workspace; further supporting information through Open in workspace and the inspector.	Approved
DXD-55	Verified calculations	Every derived value originates from a verified calculation recording method, operands, comparison periods, metric definition and evidence references. The verifier recomputes it. Neither the LLM nor the renderer derives business KPI values; the renderer computes only geometry.	Approved
DXD-56	Authorization by grants	Validate the viewer’s current grants against the result scope, dimension values and records; never compare labels. Revalidate stored and resumed results. Withhold rather than filter a partly-authorized result; never name out-of-grant entities.	Approved
DXD-57	Failure taxonomy	Presentation, calculation, authorization, unknown result, stale and partial are distinct classes with distinct outcomes. Only presentation failures with valid, authorized results use the table fallback.	Approved
DXD-58	Fallback preserves boundaries	The fallback keeps row limits and paging, evidence, partial coverage, formatting and authorization.	Approved
DXD-59	Subset disclosure	Any subset, top-N, page, sample or aggregate is declared and disclosed in text; the renderer never aggregates.	Approved
DXD-60	Continuity	Envelope and selection semantics are preserved across View as, panel ↔ workspace moves, expansion and resume (resume re-runs authorization).	Approved
DXD-61	ECharts at the Design Gate	Final Design Gate validates the GenUI charts on the pinned Apache ECharts runtime (5.6.0) — rendering, names, keyboard, selection, resize, subset disclosure — not on HTML stand-ins.	Approved
DXD-62	Implementation priority	Registry keeps 15 kinds; ten core kinds first, five specialized kinds wrap DX3 primitives or simple layouts; unbuilt kinds render through the table fallback.	Approved
Generative UI share of the five-day POC (indicative)
WORK	PRIORITY	EFFORT
Shared renderer shell: registry lookup, envelope, formatter, validator (client re-validation), fallback table with paging	Core	4 h
Core kinds: KPI, text + insight, table, bar, trend, notice + unavailable, evidence, records	Core	8 h
Specialized kinds: comparison (table preset), heatmap, funnel, treemap + ranked list, method card	Specialized	3 h
Selection, View as, panel ↔ workspace moves, expand, resume revalidation	Core	2 h
Tests: invariance, validator samples, continuity, authorization matrix, a11y smoke	Core	3 h

About 20 hours in total, more than one development day. The minimal shippable path is the shell, the core kinds and selection (about 14 hours), which fits day 4 with the AG-UI wiring if the dashboard ECharts primitives from M2 are reused. Specialized kinds (about 3 hours) are the first scope to defer, because the table fallback keeps their data, evidence and selection usable. The M4 plan fixes the final allocation.

Design artefact for review. Not production code. Synthetic data as of 20 Oct 2026.
```

# DX6 · Proactive intelligence and Insight Inbox (conditionally approved · refinements complete)

## DX6 · Insight Inbox v2 (interactive, 12 journeys, 3 roles, replayed detectors)

File: boards/DX6-Inbox.dc.html · Render: renders/DX6-Inbox.png · interactive prototype

```text
DX6 · Proactive intelligence and Insight Inbox

Scheduled and event-triggered evaluations find risks, opportunities, anomalies, deteriorating trends and cross-KPI relationships in the dashboard metrics. Each insight explains why it was generated, shows its evidence and calculations, states confidence and limits, and moves into the analytical workspace for investigation. Insights, versions and the candidate log come from a deterministic replay of detectors-1.1 at each checkpoint against sd-2026.10.20-01 (DR-005). Investigations are private; only lifecycle status and explicitly shared summaries reach other recipients.

K1 · Scheduled evaluation
K2 · Event-triggered evaluation
K3 · Triage the inbox
K4 · Investigate privately
K5 · Dismiss, feedback and suppression
K6 · Dashboard notifications
K7 · Role visibility and tenant isolation
K8 · When the agent stays quiet
K9 · Insight lifecycle and versions
K10 · Private investigation and shared summary
K11 · Stale evidence and a grant change
K12 · Duplicates, re-runs and recovery
Back
Next step
Skip to end
Restart
Pick a journey
Cenomi Dashboard Agent POC
SYNTHETIC DATA · AS OF 20 OCT 2026 · SD-2026.10.20-01
Insight Inbox
Dashboard
Evaluation runs
Workspace
3
Portfolio admin
Regional manager · Central
Tenant · T-31206

Open
Closed and snoozed
All
All types
Risk
Opportunity
Data quality
P1
RISK
10/20
Rawdah Point Mall · approval and renewal backlogs are both rising
Rawdah Point Mall · New
P2
DATA QUALITY
10/19
Seven malls have not filed September unit-discrepancy reports
Portfolio · unit discrepancy reports · New
P2
RISK
09/20
Mirage Commons · vacancy has risen every month since May
Mirage Commons · Seen
P3
OPPORTUNITY
10/06
Qasr Plaza · approvals waiting 31+ days are down to 2 from 9
Qasr Plaza · New
WATCH
RISK
10/19
Gulf Gate Mall · September unit mismatches jumped
Gulf Gate Mall · New

Select an insight to see why it was generated and its evidence.
```

## DX6 · Contract v2: detectors-1.1, privacy, API, tables, decisions DXD-63…93

File: boards/DX6-Contract.dc.html · Render: renders/DX6-Contract.png

```text
DX6 · Proactive intelligence contract (v2, after review)

Design contract for AGENT_ARCHITECTURE.md, AGENT_TOOLS.md, API_CONTRACTS.md, DATABASE_SCHEMA.md and EVALUATION_PLAN.md, updated with the DX6 review: detectors-1.1 quality rules, private investigations, run identity and recovery, and the amended five-day priority. Everything shown in the inbox is produced by replaying the detectors at checkpoints (DXD-82).

Gate DX6 · Conditionally approved · refinements complete

DXQ-12…16 are recorded as DXD-75…79 (all Option A). DXD-63…74 are approved in principle with the refinements recorded as DXD-80…93. Six refinements were addressed: KPI reconciliation, investigation privacy, idempotency and recovery, five-day priority, detector quality, verification. Nothing in the GitHub repository was modified.

For your attention at GD
S6 expected outcome corrected: the T-31206 sales dip is seasonal, so no insight (see Refinements board). Needs confirmation.
Three new as-of metrics (DXD-80) enter the KPI catalog as new, not parity.
One seed cohort is required for S1 (6 renewal amendments resolved in the window).
Checkpoint or event
Weekly, monthly or a data-load / status-change event (DXD-75); one run key (DXD-86).
→
Claim and read
One worker claims the run; detectors read as-of metrics; rows ingested later are invisible.
→
Stage candidates
Every screened candidate with its decision and reason, including those not generated.
→
Score and cluster
Impact × urgency, confidence caps; same key → new version; two metrics on one entity → cluster.
→
Publish atomically
Candidates, versions, lifecycle events and the notification outbox in one transaction (DXD-87).
→
Deliver
P1 in app now; P2/P3 digest; Watch inbox only. Outbox keys make delivery idempotent.
→
Triage and investigate
Acknowledge, snooze, dismiss, feedback; private investigation; optional shared summary (DXD-83, DXD-84).
Detector quality rules · detectors-1.1 (DXD-89)
DETECTOR	INPUTS	CADENCE · MINIMUM HISTORY	RULE (CONFIGURATION KEYS IN DETECTORS-1.1)	MISSING DATA AND COVERAGE	DENOMINATORS	CONFIDENCE, CLEARING
D1 · Concentration	approvals.pending_by_delay.asof (1m+), mall within region	Weekly · one checkpoint (a level)	share ≥ 50%, items ≥ 20, regional total ≥ 30, ≥ 3 malls	Any mall missing at the checkpoint → not evaluated for that region	Shares need a denominator ≥ 10 (Mirage Commons 1 of 1 is never a 100% share)	Resolves when no member rule holds at 2 consecutive evaluations
D2 · Sustained deterioration	Any as-of count or rate metric	Weekly window 7 checkpoints (6 changes); monthly 6 (5 changes)	≥ 4 increases, 0 decreases, net ≥ 5 (counts) or ≥ 2.0 pts (rates), and ≥ 10%	A missing checkpoint in the window → not evaluated (insufficient data); regional aggregates need coverage ≥ 80%	Rates use counts at both ends of the window; denominator ≥ 10	Resolves when below the last firing value at 2 consecutive evaluations (INS-090)
D3 · Sustained improvement	As D2 (counts)	Weekly window 7	latest ≤ 50% of the window maximum, maximum ≥ 5, ≥ 3 decreases in the last 4 changes	As D2	—	P3; updates silently; expires after 4 evaluations without change
D4a · Anomaly against own baseline	unit_discrepancy.units (rate), calendar month, on report load	3 prior months	rate ≥ 2.0× the trailing mean, ≥ 5 extra mismatched units, ≥ 50 units checked	Fewer than 2 prior months → not evaluated	Units checked ≥ 50	One period → Low → Watch; two consecutive → Medium Risk (DXD-91); clears if the next month is below the threshold
D4b · Anomaly against peers	Same month, all reporting malls	One period	robust z ≥ 3 with ≥ 15 reporting malls	Fewer peers or MAD = 0 → not evaluated	—	Supporting evidence; on its own it is a Watch
D5 · Coverage gap	Data coverage per reporting source and audience scope	On load and at month close	coverage < 90%; urgency rises when a mall misses ≥ 2 months	—	Expected malls from the location registry	Resolves when the missing reports arrive or coverage ≥ 90%
D6 · Cross-KPI co-movement	Two D2 firings on one entity at one checkpoint	Weekly	≥ 2 metrics meet D2 with overlapping windows	Inherits D2	—	Resolves when fewer than 2 members hold at 2 consecutive evaluations. Cross-entity associations (|r| ≥ 0.3, n ≥ 8) are logged as “correlation only” and never published
D7 · Lease trend	tenant_sales.reported_monthly, own lease	Monthly · ≥ 13 months for the prior-year comparison	3 consecutive declines, ≤ −10% against the trailing 8 months, and ≤ −10% against the same month last year	Missing month → not evaluated; no prior year → Watch (Low)	—	If the prior year shows the same movement → not generated (seasonal)
D8 · Tenant action required	tenant_action_items.open, own lease	Event and weekly	≥ 1 open item; urgency 2 from 7 days, 3 from 14 days	—	—	Resolves when no item is open
Scoring, confidence and promotion (DXD-90, DXD-91)
ELEMENT	RULE
Impact	Share of the parent total ≥ 50% → 3, ≥ 25% → 2, else 1 · rate ≥ 20% → 3, ≥ 15% or a rise ≥ 3 pts → 2 · coverage < 75% → 2 · tenant action → 2
Urgency	Persistence: first evaluation and still rising → 2; held at ≥ 3 consecutive evaluations → 3 · coverage: repeated miss → 2 · tenant action: oldest item ≥ 7 days → 2, ≥ 14 → 3, else 1
Confidence	High: complete inputs, the rule’s window met, a baseline where one is required · Medium: a Watch that persisted for two periods · Low: one period only or no required baseline → Watch
Re-notify	Band rises, or the primary value worsens ≥ 10% against the last notified version (INS-101: 22 → 27 band rise, 27 → 32, 32 → 39; 39 → 41 is +5.1% → no)
Watch → Risk	Promotion when the signal persists for two periods; band recomputed; the band rise notifies. Clears automatically if the next period does not repeat.

Every threshold is a configuration fact with its key and version (for example detectors-1.1 · D1.share_min) and appears in the insight’s “why” text. Changing a threshold is a new configuration version and therefore a new run key.

Correlation is not causation (safeguards)
D6 needs both metrics rising on the same entity over the same checkpoints; the text says “rising together” and the insight carries a mandatory “Not concluded: no cause” line.
Cross-entity associations (for example vacancy vs approvals across Central, r = −0.41) are logged as “correlation only” and never published.
Hypotheses carry no numbers, are labelled “not established by the data”, and suggest a check the agent can run.
Missing data is never a reason to guess: a claim that data is missing must be true of the dataset (golden invariant GI-10).
What is shared and what is private (DXD-83, DXD-84)
ITEM	VISIBLE TO	RULE
Insight content, evidence, versions	All recipients of the instance	Re-checked against current grants on every read
Shared status (Investigating, Resolved) and the investigator’s role	All recipients	No thread id, link, question or answer
Resolve outcome note	All recipients	Author labelled; the UI warns before saving
Investigation thread (questions, answers, results)	Owner only	Re-authorized on every read; refused after a grant change
Shared summary	All recipients whose grants contain its scope	Owner-selected verified statements; facts must lie inside the instance scope
Personal triage, feedback, mute	The user only	Feedback reasons visible to admins in aggregate for detector review
API (for API_CONTRACTS.md)
ENDPOINT	BEHAVIOUR
GET /insights?status=&type=	Caller’s inbox: instances addressed to the caller and inside current grants.
GET /insights/{id} · /insights/{id}/versions	Re-checks grants on every read; uniform refusal (DXD-85).
POST /insights/{id}/acknowledge · /snooze · /dismiss · /feedback	Personal state; idempotent by (insightId, userId, action, requestId).
POST /insights/{id}/investigate	Creates a private thread owned by the caller; adds the caller to the shared investigators; status Investigating.
POST /insights/{id}/summaries	Owner shares selected statements from their thread; rejected if any fact lies outside the instance scope.
POST /insights/{id}/resolve	Shared Resolved with an outcome note (shared).
GET /evaluation-runs · /evaluation-runs/{key}/candidates	Admin only.
POST /internal/triggers	Scheduler and loaders; returns queued, coalesced or duplicate; never exposed to users.
SSE /notifications	App-level stream of outbox deliveries for the caller (badge, P1).
Tables (for DATABASE_SCHEMA.md)
TABLE	KEY COLUMNS
insights.evaluation_run	run_key (unique), trigger_kind, trigger_ref, checkpoint, dataset_version, config_version, partition, status, attempt, lease_owner, lease_expires_at, outcome_hash
insights.trigger_event	event_id (unique), kind, partition, checkpoint, received_at, run_key
insights.candidate_staging / insights.candidate	run_key, eval_key, detector, entity, metric, audience, decision, reason, insight_id, values
insights.insight	id, dedup_key (unique while open), audience class, scope, type, current_version, shared_status, investigators[]
insights.insight_version	(insight_id, version) unique, run_key, checkpoint, dataset_version, config_version, facts (with calc), statements, priority, confidence, notified, reason
insights.insight_event	append-only history (generated, version, merged, resolved, seen, acknowledged …)
insights.notification_outbox	key = insight · version · recipient · channel (unique), delivered_at
insights.user_state	insight_id, user_id, state, snooze_until, dismiss_reason, mute, feedback
agent.conversation (thread)	owner_user_id, scope, imported_insight_id, imported_version, dataset_version · private
insights.shared_summary	insight_id, owner, statements (fact ids), scope, dataset_version, created_at
Decision register DXD-63…93
ID	DECISION	RULE	STATUS
DXD-63	Detection is deterministic	Detectors are deterministic rules in the analytics layer over semantic-layer metrics. The LLM decides nothing about what is an insight and computes nothing; insight text is templated with fact tokens and verified like answers (DR-031, DXD-55).	Approved
DXD-64	Detector catalogue	D1–D8, refined as detectors-1.1 (DXD-89).	Approved · refined
DXD-65	Audience-scoped instances and three checks	Visibility is checked at generation, at delivery and on every read against current grants. Refined by DXD-76 and DXD-85.	Approved · refined
DXD-66	Transparent scoring	Priority = impact × urgency (P1 ≥ 6, P2 3–5, P3 ≤ 2); Low confidence → Watch; positive findings → P3. Impact and urgency rules made explicit by DXD-90.	Approved · refined
DXD-67	Shared lifecycle, personal triage	Open, Investigating, Resolved, Merged, Superseded, Expired are shared; New, Seen, Acknowledged, Snoozed, Dismissed are per user. Investigation content is private (DXD-83).	Approved · refined
DXD-68	Deduplicate, merge, re-notify, suppress	Same key → new version; re-notify only on a band rise or a worsening of 10% or more measured against the last notified version; two metrics on one entity → cluster; dismissed and snoozed suppressed until their resurface rule.	Approved · refined
DXD-69	Quiet by default	Not material, no sustained change, within normal range, correlation only, not concluded, not evaluated, seasonal pattern and duplicate are logged decisions with reasons, visible to admins.	Approved · refined
DXD-70	Delivery	P1 in app immediately and on its dashboard cards; P2 and P3 in the in-app daily digest; Watch in the inbox and on card indicators, never the badge.	Approved
DXD-71	Investigation handoff	Investigate opens a workspace thread with the insight imported and labelled (DXD-32). The thread is private to its owner (DXD-83); recipients see only the shared status.	Approved · refined
DXD-72	Feedback	Useful / not useful and dismiss reasons are logged for detector review; no automatic threshold changes; per-user mute.	Approved
DXD-73	Scenario history	Amended by DXD-81: the history extension is a constraint on the seed that must be reproducible from record lifecycles.	Approved · refined
DXD-74	Five-day priority	Amended by DXD-92 (D8 is core).	Approved · refined
DXD-75	Evaluation cadence (DXQ-12 A)	Weekly checkpoints (Tuesday), monthly checkpoints on the as-of day of month for stock metrics, calendar months for monthly reports, plus data-load and status-change events. All are synthetic historical replay at checkpoints ≤ as_of (DR-005).	Approved
DXD-76	Instances per authorized scope (DXQ-13 A)	One instance per distinct computation scope. Regional instances are computed independently within each authorized region; audiences are the roles whose current grants contain the scope. Operator and tenant audiences never share an instance.	Approved
DXD-77	In-app digest only (DXQ-14 A)	No email in the POC (DR-011).	Approved
DXD-78	Positive findings (DXQ-15 A)	P3 Opportunity insights; they update silently.	Approved
DXD-79	Tenant proactive insights (DXQ-16 A)	Own-lease Watch and Action-needed insights only, computed from the tenant’s lease alone.	Approved
DXD-80	Canonical approval-age metric	Parity metric approvals.pending_by_delay v1 is the live V2 card (proposals from creation; contracts and leases from last change; bands 0–6, 7–13, 14–20, 21–30, ≥ 31 Asia/Riyadh days). History uses new metrics approvals.pending_by_delay.asof v1, amendments.pending_by_age_band.asof v1 and units.vacant.asof v1, computed from seeded status history and equal to the parity metric at as_of. Label: “waiting 31+ days (1m+)”. “Overdue” is not used.	Recorded · refinement
DXD-81	Reconstructible scenario history	Every declared series must be reproduced from record lifecycles in the seed and end on the 20 Oct snapshot. Golden-data invariants GI-01…GI-16 run in M1 and M5.	Recorded · refinement
DXD-82	Replay oracle	Insights, versions, notifications and the candidate log are produced only by replaying detectors over the checkpoint calendar; nothing is hand-authored except sentence templates. The replay hash is a golden value.	Recorded · refinement
DXD-83	Private investigation threads	A thread belongs to the user who opened it and is re-authorized on every read against that user’s current grants. Other recipients see the shared status “being investigated” with the investigator’s role, never the thread, its questions or answers. Resolve notes are shared and labelled as such.	Recorded · refinement
DXD-84	Explicit shared summaries	The owner may share a summary: selected verified statements whose facts lie inside the insight instance’s scope, re-checked per viewer. No shared or collaborative threads in the POC.	Recorded · refinement
DXD-85	Uniform refusals for deep links	Insight and thread links are re-authorized; the response is the same whether the item is unauthorized or does not exist.	Recorded · refinement
DXD-86	Run identity and triggers	run_key = hash(trigger kind, checkpoint, dataset version, configuration version, partition), unique. Events are deduplicated by event id. One worker processes runs in checkpoint order with claim leases.	Recorded · refinement
DXD-87	Atomic publication and idempotent delivery	Candidates are staged; one transaction publishes candidates, insight versions (optimistic version check; a version for an older checkpoint never overwrites a newer one), lifecycle events and notification outbox rows keyed insight · version · recipient · channel.	Recorded · refinement
DXD-88	Restart, late and corrected data	A restart discards staging and re-runs. Detector inputs carry ingested_at and checkpoints read only rows ingested by then. A correction is a new dataset version and a new run at the latest checkpoint; earlier versions keep their dataset; insights are labelled stale until re-evaluated.	Recorded · refinement
DXD-89	Detector quality rules (detectors-1.1)	Configurable, versioned thresholds recorded as configuration facts in every insight; minimum history; missing-data and coverage behaviour; minimum denominators; formal consecutive-period definition; cross-entity associations are never published.	Recorded · refinement
DXD-90	Scoring rules	Impact from share of the parent total, rate level or rise, coverage; urgency from persistence across evaluations, oldest-item age or repeated misses. Bands unchanged.	Recorded · refinement
DXD-91	Watch promotion and clearing	A Watch becomes a Risk when its signal persists for two periods (Medium confidence; High if the peer test also holds); the band rise notifies. If the next period does not repeat, it clears.	Recorded · refinement
DXD-92	Five-day priority (amends DXD-74)	Core: evaluation runner, D1, D2, D5, D6 clustering, D8, inbox list, detail and evidence, acknowledge, dismiss, investigate, authorization, deduplication and candidate log, end-to-end tests. Secondary (in full scope): D3, D4, full D7, snooze, digest scheduling, feedback analytics.	Recorded · refinement
DXD-93	Lease-scoped tenant actions	D8 counts the lease’s own action items (documents to upload, requests in Action required, sales re-uploads). Company-wide counts are never used for a lease audience.	Recorded · refinement

Design artefact for review. Not production code. Synthetic data as of 20 Oct 2026; detector replay detectors-1.1, hash 82fde5250960761d.
```

## DX6 · Golden scenarios v2 (S1–S9, N1–N11; S6 and S7 corrected)

File: boards/DX6-Scenarios.dc.html · Render: renders/DX6-Scenarios.png

```text
DX6 · Golden scenarios and expected outcomes (v2)

Generated by the detector replay (detectors-1.1) at every checkpoint against sd-2026.10.20-01; each scenario is reproducible from record cohorts (Refinements board). EVALUATION_PLAN.md treats them as golden: each S-case must produce its insight with the stated versions, band and audiences; each N-case must produce no notification and log the stated decision. Replay hash 82fde5250960761d.

S6 corrected — needs your confirmation

S6 (lease T-31206 sales, Watch) relied on “no prior-year data”. The dataset holds 2024–2025 (DX2 tenant board, DR-004): September is +7.5% against September 2025, and June→September fell 17.9% in both years. Correct behaviour is no insight (now N9, seasonal). The tenant journey keeps S7 (lease-scoped action needed). Own-lease Watch (DXD-79) stays a capability, verified with a labelled micro-fixture unless you prefer a seeded scenario (GD decision).

S7 corrected

T-202 previously counted 2 service requests in Action required. Those are company-wide (Rawdah Point 1, Gulf Gate 1); lease T-31206 has none. T-202 now counts the lease’s 2 fit-out drawings to upload.

Generated insights (S-cases) · * = notified version
CASE	INSIGHT	KIND	TITLE (LATEST VERSION)	WHAT IT TESTS	BAND · CONFIDENCE	VERSIONS	AUDIENCES	SERIES
S1	INS-107	Risk · cross-KPI cluster	Rawdah Point Mall · approval and renewal backlogs are both rising	Two metrics meet D2 on one mall at one checkpoint; D1 concentration 66.1%; INS-101 merged.	P1 · High	P1*	admin, central	

Approvals waiting 31+ days: 22 · 24 · 27 · 29 · 32 · 35 · 39 · 41

S2	INS-104	Risk · deterioration (monthly)	Mirage Commons · vacancy has risen every month since May	Vacancy up every month; version 2 updated silently (+3.6% < 10%).	P2 · High	P2* → P2	admin, central	

Vacant units (20th of the month): 47 · 48 · 50 · 51 · 53 · 56 · 58

S3	INS-105	Data quality · late data	Seven malls have not filed September unit-discrepancy reports	18 of 25 malls reported; Central instance INS-105C computed within Central.	P2 · High	P2*	admin	—
S4	INS-106	Ambiguous · Watch	Gulf Gate Mall · September unit mismatches jumped	One-month jump (D4a 3.3×, D4b z 15.9); could be an audit-method change. Promotion rule shown.	Watch · Low	Watch	admin	

Mismatch rate: 2.1% · 2.8% · 2.1% · 7.7%

S5	INS-103	Positive	Qasr Plaza · approvals waiting 31+ days are down to 2 from 9	D3 fires on 6 Oct (4 vs a maximum of 9); updates silently to 2.	P3 · High	P3* → P3 → P3	admin, central	

Approvals waiting 31+ days: 9 · 9 · 8 · 7 · 5 · 4 · 3 · 2

S7	T-202	Action needed · tenant	2 fit-out drawings are waiting for your upload	Two lease-scoped drawings; P3 → P2 when the oldest passes 7 days (band rise notifies).	P2 · High	P3* → P3* → P2*	tenant	—
S8	INS-090	Lifecycle · auto-resolve	Qasr Plaza · approvals waiting 31+ days rising	D2 fires 1 Sep (3 → 9); clears 22 Sep (8, then 7).	P3 · High	P3* → P3	admin, central	—
S9	INS-101	Versions and band rise (new)	Rawdah Point Mall · approvals waiting 31+ days keep rising	Seven versions: P2 → P1 on 15 Sep; re-notified at +18.5% and +21.9%; merged 20 Oct.	P1 · High	P2* → P2 → P1* → P1 → P1* → P1 → P1*	admin, central	

Approvals waiting 31+ days: 22 · 24 · 27 · 29 · 32 · 35 · 39

Decisions not to notify (N-cases)
CASE	RUN	DETECTOR	ENTITY	AUDIENCE	DECISION	REASON
N1	w_2026-10-20	D1 · Concentration + D2	Rawdah Point Mall · approvals	admin, central	Merged	Open insight INS-101 covered this signal (39 → 41, +5.1% since its last notified version, below 10%). Merged into INS-107; no separate notification.
N2	w_2026-10-20	D2 · Sustained deterioration	Central · amendments 4 wk+ (all types)	admin, central	Not generated · not material	Rose from 23 to 25 over the window; 2 increases (needs 4); net change +2 (needs +5).
N3	m_2026-10-20	D2 · Sustained deterioration	Sandstone Galleria · vacancy	admin, central	Not generated · no sustained change	Vacancy 13.0% is high but shows no sustained change (2 increases, 1 decrease, +0.2 pts in five months). A stable high level is already visible on the dashboard.
N4	e_2026-10-19_ud	D4 · Anomaly (D4b)	Cedar Park Mall · mismatch rate	admin, central	Not generated · within normal range	Highest in Central (3.3%) but within the range of the 18 reporting malls: robust z 1.8 < 3. No temporal jump against its own baseline.
N5	w_2026-10-20	D6 · Cross-KPI association (screen)	Central malls · vacancy vs approvals 31+ days	admin, central	Not generated · correlation only	Across 10 Central malls r = −0.41 (−0.35 without Rawdah Point). Cross-entity associations are never published as insights in detectors-1.1: no shared movement over time and no mechanism in the data.
N6	w_2026-10-20	D7 · Lease trend	Lease T-31206 vs other tenants	tenant	Not evaluated · isolation	Tenant-audience detectors use only the tenant’s own lease. Benchmarks against other tenants are never computed for a tenant audience.
N7	m_2026-10-20	D2 · Sustained deterioration	Mirage Commons · vacancy	admin, central	Updated silently	D2 holds (5 of 5 increases, +3.3 pts). Silent update: +3.6% since the last notified version (56 → 58), below 10%.
N8	e_2026-10-19_ud	D2 · Sustained deterioration	Eastern · mismatch rate	admin	Not concluded · coverage	Only 5 of 7 Eastern malls reported (71%), below the 80% needed to evaluate a regional trend. Re-evaluated when reports arrive.
N9	m_2026-10-20	D7 · Lease trend	Lease T-31206 · reported sales	admin, central, tenant	Not generated · seasonal pattern	Three monthly declines to SAR 241,800 (−11.4% against the January–August average), but +7.5% against the same month last year; June→September moved −17.9% in 2025 and −17.9% in 2026. The prior year shows the same movement, so this is not reported.
N10	e_2026-10-19_ud	D4 · Anomaly (D4b)	Breeze Walk · mismatch rate	admin	Not generated · within normal range	Highest in Western (3.4%) but within the range of the 18 reporting malls: robust z 2.0 < 3. No temporal jump against its own baseline.
N11	w_2026-10-13	D2 · Sustained deterioration	Rawdah Point Mall · renewals 4 wk+	admin, central	Not generated · not yet sustained	Renewals 4 → 8: net change +4 (needs +5).

N1–N8 keep their meaning from v1 (N3 is now “no sustained change”, N4 is the peer test). N9–N11 are new: the seasonal tenant decline, a second within-range mall, and a renewal signal that is not yet sustained a week before D6 fires.
```

## DX6 · Verification record v2

File: boards/DX6-Verify.dc.html · Render: renders/DX6-Verify.png

```text
DX6 · Verification record (v2)

Chromium runs of the interactive Insight Inbox as published, a Node run of the same interaction code, a Python run over the replayed scenario data, the reconciliation invariants and the runner protocol model.

44 / 44
browser checks · 12 journeys
81 / 81
interaction logic checks
387 / 387
data checks · 43 texts grounded
51 / 51
golden-data invariant checks
13 / 13
runner protocol tests
Tests requested in the review and where they are
REQUESTED	COVERED BY
Duplicated triggers	R1, R2 (runner) · K12
Concurrent evaluations	R3, R4, R8 (runner)
Recovery	R5, R6, R7 (runner) · K12
Role changes	K11 · logic: grant revoked → inbox, links, own thread refused
Insight-version changes	S9, T-202 band rise · logic and browser K9
Notification suppression	R10 · K5 · re-notify rule in S9 and N1
Private investigation threads	K10 · logic: shared status only, link refused, scoped summary
Stale evidence	R13 · K11 · logic: stale label and stale import
K1 · Checkpoint replay with run key, staged candidates and atomic publish.
K2 · Late-arriving reports; the Gulf Gate jump is a Watch with its promotion rule.
K3 · Why the P1 was generated: four rules with versioned thresholds.
K3 · Evidence, series and facts with calculations.
K4 · Private investigation with the insight imported and labelled.
K9 · INS-101 versions: band rise, re-notifications, merge.
K10 · The Central manager sees only the shared status.
K10 · Share a summary: the out-of-scope statement is blocked.
K10 · The shared summary as the Central manager sees it.
K11 · Stale evidence after a newer dataset version.
K11 · After a grant change: empty inbox, links and own thread refused.
K7 · Tenant: one lease-scoped action insight.
K8 · Monthly checkpoint: seasonal decline not reported; stable vacancy not news.
K12 · Duplicate event, re-run, crash recovery and full replay.
Browser
CHECK	RESULT
Bell badge counts new P1–P3 insights (Watch excluded): 3	pass
K1: candidates hidden until staged; run key, checkpoint and configuration shown	pass
K1: the cluster created by this run is not counted before publish	pass
K1: timeline reaches delivery; the log shows generated, merged and not generated	pass
K1: badge rises when the run publishes	pass
K2: event run opens the Gulf Gate Watch with Low confidence and its promotion rule	pass
K3: P1 explains four rules with configured thresholds	pass
K3: facts table shows calculations and versioned thresholds	pass
K3: every displayed series value is a fact (data-fact)	pass
K3: confidence, hypothesis, limitations, not concluded and versions shown; acknowledged	pass
K4: private investigation opens with the insight imported and labelled	pass
K4: answer is grounded and labels the hypothesis	pass
K4: insight shows Investigating and the owner’s private link	pass
K5: dismiss dialog with reasons and mute option	pass
K5: next evaluation suppresses the dismissed insight and notifies nothing	pass
K6: dashboard cards carry indicators with the top band	pass
K6: indicator opens the insight	pass
K7: Central manager sees the Central coverage instance and no Eastern or portfolio insight	pass
K7: deep link to the Eastern insight is refused without revealing it	pass
K7: tenant inbox shows only its own lease insight, lease-scoped	pass
K7: tenant link to the operator P1 is refused	pass
K7: tenant dashboard has only its own cards	pass
K8: weekly checkpoint lists its decisions not to generate, each with a reason	pass
K8: monthly checkpoint shows the seasonal decision and the stable high vacancy	pass
K8: event run shows “Not concluded · coverage” and “within normal range”	pass
K9: INS-101 shows seven versions, the band rise and its merge	pass
K9: INS-090 resolved automatically with the series values	pass
K9: resolved with a shared outcome note and full history	pass
K10: the Central manager sees Investigating without the thread or conversation	pass
K10: link to the admin’s thread is refused	pass
K10: share dialog blocks the out-of-scope statement	pass
K10: the Central manager sees the shared summary	pass
K11: stale evidence label after a newer dataset version	pass
K11: investigation imports the insight labelled stale	pass
K11: after the grant change the inbox is empty and both links are refused	pass
K12: duplicate event is ignored	pass
K12: crash before publish restarts to the same result	pass
K12: full replay is identical	pass
Keyboard: Enter on a list item opens it (aria-current)	pass
Escape closes the dismiss dialog	pass
All buttons have an accessible name	pass
Live region present	pass
Text contrast ≥ 4.5:1 for every visible text node (374 checked)	pass
No page errors	pass
Interaction logic
CHECK	RESULT
K1 runs to the end with no bad values	pass
K1 Back replays to the previous step	pass
K2 runs to the end with no bad values	pass
K2 Back replays to the previous step	pass
K3 runs to the end with no bad values	pass
K3 Back replays to the previous step	pass
K4 runs to the end with no bad values	pass
K4 Back replays to the previous step	pass
K5 runs to the end with no bad values	pass
K5 Back replays to the previous step	pass
K6 runs to the end with no bad values	pass
K6 Back replays to the previous step	pass
K7 runs to the end with no bad values	pass
K7 Back replays to the previous step	pass
K8 runs to the end with no bad values	pass
K8 Back replays to the previous step	pass
K9 runs to the end with no bad values	pass
K9 Back replays to the previous step	pass
K10 runs to the end with no bad values	pass
K10 Back replays to the previous step	pass
K11 runs to the end with no bad values	pass
K11 Back replays to the previous step	pass
K12 runs to the end with no bad values	pass
K12 Back replays to the previous step	pass
Grants check refuses an Eastern insight even if its audience list names the Central manager	pass
Tenant is refused a mall-level insight even if addressed to the tenant	pass
Tenant instances are tenant-only and lease-level (operator and tenant audiences never share an instance)	pass
Admin badge counts new P1–P3 insights only (Watch excluded): 3	pass
Opening marks seen and lowers the badge	pass
Personal state is per user: the Central manager still has INS-107 as new	pass
Investigate sets the shared status and opens a thread owned by the admin	pass
Other recipients see the shared status only — no thread id, no link, no conversation	pass
A deep link to another user’s thread is refused	pass
Thread readable by its owner while the scope is inside current grants	pass
Share dialog blocks the one statement whose facts are outside the insight’s scope	pass
Published summary contains only in-scope verified statements	pass
The Central manager sees the summary (4 statements), re-checked against their grants	pass
Tenant inbox lists only its lease-level action insight	pass
Tenant deep link to an operator insight is refused	pass
Tenant sees its own cards (2 documents to upload) and no evaluation-run log	pass
Tenant evidence uses lease T-31206 only (no company-wide counts)	pass
After the Central grant is removed the manager’s inbox is empty	pass
Deep links are re-checked after a grant change	pass
The manager’s own thread is refused once its scope is outside their grants	pass
Dashboard indicators disappear with the grant	pass
After a newer dataset version, the insight is labelled stale with its evidence version	pass
Investigating a stale insight imports it labelled stale (DX5 stale class)	pass
Dismissed insight leaves the open list	pass
Next evaluation on the same data notifies nothing: dismissed and snoozed are suppressed	pass
INS-101: 7 versions, 4 notified (new, band rise, two ≥10% worsenings)	pass
T-202: P3 → P3 → P2 as the oldest item ages past 7 days	pass
Merged insight shows Merged and its version table	pass
Runs view shows the duplicate-event outcome from the runner model	pass
Pending approvals card shows its open insights with the top band	pass
Scenario data
CHECK	RESULT
INS-107 explains why, confidence and limitations	pass
INS-107 priority follows the rule (P1)	pass
INS-107 every version records dataset and configuration; the latest matches the shown band	pass
INS-107 versions are ordered by checkpoint	pass
INS-107 Central-audience instance is inside Central	pass
INS-107 hypothesis carries no number	pass
T-202 explains why, confidence and limitations	pass
T-202 priority follows the rule (P2)	pass
T-202 every version records dataset and configuration; the latest matches the shown band	pass
T-202 versions are ordered by checkpoint	pass
T-202 tenant instance is lease-level and tenant-only	pass
T-202 tenant facts come only from lease T-31206	pass
INS-105 explains why, confidence and limitations	pass
INS-105 priority follows the rule (P2)	pass
INS-105 every version records dataset and configuration; the latest matches the shown band	pass
INS-105 versions are ordered by checkpoint	pass
INS-105C explains why, confidence and limitations	pass
INS-105C priority follows the rule (P2)	pass
INS-105C every version records dataset and configuration; the latest matches the shown band	pass
INS-105C versions are ordered by checkpoint	pass
INS-105C Central-audience instance is inside Central	pass
INS-104 explains why, confidence and limitations	pass
INS-104 priority follows the rule (P2)	pass
INS-104 every version records dataset and configuration; the latest matches the shown band	pass
INS-104 versions are ordered by checkpoint	pass
INS-104 Central-audience instance is inside Central	pass
INS-104 hypothesis carries no number	pass
INS-106 explains why, confidence and limitations	pass
INS-106 priority follows the rule (Watch)	pass
INS-106 every version records dataset and configuration; the latest matches the shown band	pass
INS-106 versions are ordered by checkpoint	pass
INS-106 hypothesis carries no number	pass
INS-103 explains why, confidence and limitations	pass
INS-103 priority follows the rule (P3)	pass
INS-103 every version records dataset and configuration; the latest matches the shown band	pass
INS-103 versions are ordered by checkpoint	pass
INS-103 Central-audience instance is inside Central	pass
INS-103 hypothesis carries no number	pass
INS-101 explains why, confidence and limitations	pass
INS-101 priority follows the rule (P1)	pass
INS-101 every version records dataset and configuration; the latest matches the shown band	pass
INS-101 versions are ordered by checkpoint	pass
INS-101 Central-audience instance is inside Central	pass
INS-090 explains why, confidence and limitations	pass
INS-090 priority follows the rule (P3)	pass
INS-090 every version records dataset and configuration; the latest matches the shown band	pass
INS-090 versions are ordered by checkpoint	pass
INS-090 Central-audience instance is inside Central	pass

Carried to the final Design Gate and M5: axe-core and a screen-reader pass on the real build; the detectors and invariants re-run against the M1 seeded database; the runner model becomes integration tests against PostgreSQL.
```

## DX6 · Review refinements: KPI reconciliation, privacy, idempotency, priorities

File: boards/DX6-Refinements.dc.html · Render: renders/DX6-Refinements.png

```text
DX6 · Review refinements

The six refinements from the DX6 review: (1) canonical KPI reconciliation with golden-data invariants, (2) investigation privacy, (3) idempotency, replay and recovery, (4) five-day priorities, (5) detector quality (on the Contract board) and (6) verification (on the Verify board).

1 · Canonical KPI reconciliation — Rawdah Point approvals
Canonical definition (DXD-80)
ASPECT	RULE
Population	Proposals with admin status Pending Proposal; contracts with Contract Sent; leases with Contract Signed; within the lease visibility rule and the viewer’s grants (REF §3b.2)
Age basis	Proposals: days since pms_created_at. Contracts and leases: days since pms_last_modified_at — any change resets the age
Bands	0–6 · 7–13 · 14–20 · 21–30 · ≥ 31 whole days in Asia/Riyadh (DR-006); the 1m+ band is ≥ 31 days, labelled “waiting 31+ days”
Excluded	Future or NULL timestamps (dropped, REF); not an SLA — “overdue” is never used
Filters	Region and mall only; no year or month (V2). Card total = Σ malls (REF returns rows per mall)
Reference time	as_of = 2026-10-20 for parity (DR-003); checkpoints t ≤ as_of for the as-of metric, which must equal the parity value at t = as_of
Shares	Numerator and denominator at the same checkpoint; denominator ≥ 10; Rawdah 41 / Central 62 = 66.1%; 41 / 71 = 57.7% of Rawdah’s own pending
Canonical snapshot · Rawdah Point Mall · 20 Oct 2026 (DX2 card = records)
TYPE	0–6	7–13	14–20	21–30	≥ 31 (1M+)	ALL
Proposals	4	3	2	4	19	32
Contracts	3	2	1	2	15	23
Leases	3	2	2	2	7	16
All types	10	7	5	8	41	71

Central: 130 pending, 62 waiting 31+ days (Rawdah 66.1%). All regions: 232 pending, 92 waiting 31+ days. Weekly 1m+ history for Central: 36 · 38 · 40 · 42 · 45 · 48 · 49 · 52 · 53 · 54 · 57 · 58 · 61 · 62 (21 Jul → 20 Oct).

What was apparently inconsistent

The DX1 shell insight said “41 of 71 pending items are older than 31 days (58%)” at a 30 Sep checkpoint, rising “from 22% to 58%”, with “Central median 19%”. DX4/DX6 say 41 approvals waiting 31+ days on 20 Oct, rising from 22 on 1 Sep. The 41 and 71 are the same population and agree; the date, the measure (share vs count), the boundary wording and the median were wrong in DX1. The DX1 board now shows the canonical insights.

Discrepancies found across DX1–DX6 and their resolution
ID	WHERE	CLAIM	FINDING	RESOLUTION	STATUS
C1	DX1 shell insight i1	“41 of 71 pending items are older than 31 days” dated to the 30 Sep checkpoint	41 of 71 is the 20 Oct snapshot. On 29 Sep the series is 32.	DX1 shell insights are superseded by the DX6 canonical insights; the DX1 board now shows INS-107 values with their dates.	Fixed
C2	DX1 shell insight i1	“rose from 22% to 58% between the 31 Jul and 30 Sep checkpoints” (a share)	DX6 uses a count (22 on 1 Sep). 22% and 22 are different measures on different dates; the earlier share has no source.	Insights report the count; the share is reported only at the checkpoint where both parts exist (57.7% on 20 Oct).	Fixed
C3	DX1 shell insight i1	“Central median 19%”	Recomputed median share of pending approvals waiting 31+ days across Central malls: 45.0%. 6 malls have fewer than 10 pending items (Mirage Commons: 1 of 1 = 100%).	Statement withdrawn. Shares need a minimum denominator of 10 (detector configuration).	Fixed
C4	DX1 shell, DX6 text	“older than 31 days” and “approvals over a month”	V2 band is ≥ 31 days (“1 month plus delay”); “older than 31 days” would mean ≥ 32.	Canonical label: “waiting 31+ days (1m+)”. Contracts and leases count from their last change, proposals from creation.	Fixed
C5	DX5 sample I3, review language	“overdue approvals”, “12 overdue renewals”	No SLA exists in the dataset; DX2 caveat: age bands are not SLA breaches. Canonical Rawdah renewals in 4 wk+: 9.	“Overdue” is banned in generated text (verifier word list). I3 stays a rejection test; its number is deliberately ungrounded and labelled so.	Fixed
C6	DX6 history	Weekly “approvals over a month” history	V2 computes approvals live against NOW(); there is no history in REF. A history is a new as-of metric.	New metrics approvals.pending_by_delay.asof v1 and amendments.pending_by_age_band.asof v1 (kind: new), computed from seeded status history. At the as-of date they must equal the parity metrics (GI-01).	Needs KPI-catalog approval (M0)
C7	DX6 text	“waiting”	Contracts and leases age from pms_last_modified_at: any change resets the age.	Insight definitions and limitations say so; cohorts in the seed do not modify 1m+ contracts unless a scenario requires it.	Fixed
C8	INS-090	Generated by D2 with a level threshold of 8 after three increases; resolved “5 on 22 Sep”	D2 needs ≥ 4 increases in 6 changes and a net change ≥ 5. The series is 7 on 22 Sep (5 is 29 Sep).	Regenerated by the replay: fires on 1 Sep (3 → 9 since 21 Jul), clears on 22 Sep (8, then 7).	Fixed
C9	INS-101	D1 concentration first generated 13 Oct	Replaying the declared history, D1 already holds on 15 Sep (27 of 53, 50.9%).	Regenerated: INS-101 opens on 1 Sep (D2), D1 joins on 15 Sep, merged into INS-107 on 20 Oct.	Fixed
C10	INS-103	D3 improvement first generated 20 Oct	Replay: D3 holds on 6 Oct (4 against a window maximum of 9).	Regenerated: generated 6 Oct, updated silently on 13 and 20 Oct.	Fixed
C11	Renewals history	Rawdah renewals 4 wk+ 4 → 9	The visible DX4 records fix the ages of the pending renewals; the series needs 6 renewals that were 4 wk+ and were resolved in the window (2026-07-31 to 2026-10-16).	Recorded as a required seed cohort (golden scenario manifest). Without it D6 cannot fire.	Fixed (seed requirement)
C12	INS-108 / T-201, thread answer	“No prior-year data”; “Sales for 2025 are not in the dataset”	DX2 tenant board and DR-004 include 2024–2025. September is +7.5% against September 2025; June→September fell 17.9% in 2025 and 17.9% in 2026.	D7 uses the prior year when ≥ 13 months exist. Result: not generated, seasonal pattern (N9). S6 expected outcome corrected — needs your confirmation.	Fixed · decision GDQ
C13	T-202 and tenant dashboard card	“2 service requests are waiting for your action” for lease T-31206	The 2 are company-wide (Rawdah 1, Gulf Gate 1). Lease T-31206 (Sandstone Galleria) has 0.	D8 counts lease-scoped action items: 2 fit-out drawings to upload (Lighting layout since 12 Oct; Shopfront details re-upload since 17 Oct).	Fixed
C14	INS-104 hypothesis	“the dataset holds no lease-expiry schedule”	Lease end dates exist (expiring-leases KPI, DX2).	Hypothesis kept as a hypothesis with a checkable question: which Mirage Commons leases ended since April without renewal.	Fixed
C15	INS-104	Created 20 Sep by run_m_2026-10-20	Creation and run disagree.	Version 1 from run_m_2026-09-20; version 2 from run_m_2026-10-20.	Fixed
C16	INS-107 limitation	“no earlier history in the POC”	DR-004: transactional history from 2024-01-01.	Limitation states the detector window (7 weekly checkpoints) instead.	Fixed
C17	DR-005 vs DX6	Month-end checkpoints (DR-005 example) vs weekly + monthly-on-the-20th + events	Different calendars.	DXQ-12 A: weekly Tuesday checkpoints, monthly on the as-of day for stock metrics, calendar months for monthly reports, plus data-load and status-change events. DR-005 note updated.	Fixed
C18	DX6 detectors	Coverage thresholds 90% (D5) and 80% (regional evaluation) unnamed	Two different purposes.	Config keys coverage.alert_below = 0.90 and coverage.min_for_regional_eval = 0.80.	Fixed
C19	DX6 contract D4	“double the trailing average; robust z ≥ 3” (and/or unclear)	Two tests with different meanings.	D4a temporal and D4b cross-sectional, each stated in the evidence.	Fixed
C20	DX6 contract D6	“both fire D2-type rules”	Renewals had a flat week (7 → 7); strict D2 would not fire.	Formal D2: ≥ 4 increases in the last 6 changes, no decrease, net change ≥ minimum.	Fixed
C21	DX2 approvals drill-down	Records with random ages (31–140) and random mall labels	A fixture, not the seeded population. The reconstructed cohort needs, for example, 15 Rawdah items aged ≥ 122 days.	Drill-down records come from the seed in M2 (DXD-49); the prototype fixture stays labelled (DXD-50).	Carried to M1/M2
Golden-data invariants (DXD-81)
ID	INVARIANT	EVIDENCE	RESULT
GI-01	Snapshot parity: records reproduce every DX2 card value by type and band	11 / 11	pass
GI-02	Every declared series ends on the 20 Oct snapshot	19 / 19	pass
GI-03	Every series value is reproduced from record lifecycles (status history and timestamps)	13 / 13	pass
GI-05	Region = Σ malls at every checkpoint	2 / 2	pass
GI-06	Shares use one checkpoint for both parts; minimum denominator	1 / 1	pass
GI-09	Tenant-audience facts come from the tenant’s lease only	1 / 1	pass
GI-10	A “no baseline” claim must be true of the dataset	1 / 1	pass
GI-11	Bitemporal: rows are visible only to checkpoints after ingestion	1 / 1	pass
GI-15	Vacancy = Σ malls; units consistent	1 / 1	pass
GI-16	Coverage: reported + missing = expected malls	1 / 1	pass
GI-04	Ageing monotonicity (implied by GI-03: an unmodified pending item ages 7 days per weekly checkpoint)	by construction	pass
GI-07	Band boundaries and age basis exactly as the V2 SQL	used by GI-01/03	pass
GI-12	Quiet background: replay produces exactly the declared candidates	42 candidates	pass
GI-13	Replay determinism (byte-identical twice)	82fde5250960761d	pass
GI-14	Every number in an insight equals the series value at its labelled checkpoint	43 texts	pass
Record cohorts that reproduce the history (seed requirements)
MALL	PENDING ON 20 OCT	RESOLVED IN WINDOW	OLDEST (DAYS)	PENDING AGED ≥ 122 DAYS
Rawdah Point Mall	71	0	150	15
Sandstone Galleria	14	2	128	4
Qasr Plaza	7	7	124	2
Najd Gate Mall	12	2	126	3
Wadi Crescent Centre	11	1	124	2
Falcon Square	5	0	124	2
Oasis Row	3	0	124	2
Cedar Park Mall	4	1	122	1
Amber Heights	2	0	122	1
Mirage Commons	1	0	122	1

Renewal amendments: the ages of the visible DX4 records are fixed, so the Rawdah series needs 6 renewals that reached 4 wk+ and were resolved in the window; Sandstone needs 7, Qasr 4. These cohorts go into the golden scenario manifest for M1.

2 · Investigation access and privacy (DXD-83…85)
Private by default
Investigate creates a thread owned by the user, carrying the insight’s scope and imported version.
Every read re-checks owner and current grants; after a grant change the owner loses it too (K11).
Other recipients see “being investigated by Portfolio admin (private)” — no thread id, link or content (K10).
Explicit collaboration
The owner can share a summary: chosen verified statements only.
Every fact in a shared statement must lie inside the insight instance’s scope; otherwise it cannot be selected (the portfolio-wide statement in K10).
Each viewer’s grants are re-checked when the summary is shown. No shared threads in the POC.
Deep links
/insights/{id} and /investigations/{id} are re-authorized on every request.
The refusal is identical for “not yours” and “does not exist”.
Tenant and operator audiences never share an instance, so an admin’s investigation status never reaches a tenant.
3 · Idempotency, replay and recovery (DXD-86…88)
Runner protocol (one local worker, PostgreSQL tables, no queue infrastructure)
TRIGGER Scheduler (checkpoint) or loader (event id) calls POST /internal/triggers → queued · coalesced · duplicate
CLAIM Worker takes the oldest queued run (checkpoint order) with a 300 s lease; an expired lease can be taken over (attempt + 1)
STAGE Delete staging for this run key; evaluate read-only detectors; write candidates to staging
PUBLISH BEGIN · insert candidates · per insight: check current version, skip older checkpoints, insert version and events · insert outbox rows · mark run completed with outcome hash · COMMIT
DELIVER Delivery loop marks outbox rows delivered by key; a repeat is a no-op
CORRECT New dataset version → new run key at the latest checkpoint; versions marked “data corrected”; stale label until then

Scheduled and event runs coexist because both resolve to a run key over (trigger, checkpoint, dataset, configuration, partition). The same checkpoint triggered twice is one run; a new dataset or configuration version is a new run. Replay of the whole calendar on a fixed dataset gives identical candidates, versions and notifications (hash c1e36ced42cebecc).

Runner model tests
ID	CASE	RESULT
R1	Duplicate event delivery is ignored	pass
R2	The same checkpoint triggered twice runs once (run key = trigger · checkpoint · dataset · config)	pass
R3	Concurrent claims: one worker holds the lease; another can take over only after it expires	pass
R4	An older checkpoint replayed late never overwrites a later version	pass
R5	Crash after staging: nothing is visible; the restart discards staging and publishes once	pass
R6	Crash inside publish: the transaction rolls back; no partial insight or notification	pass
R7	Crash after commit or during delivery: re-trigger is a no-op and each notification is delivered exactly once	pass
R8	Triggers arriving in any order give the same versions, candidates and notifications	pass
R9	Deterministic replay: the detector replay and the runner replay are byte-identical across runs	pass
R10	Only notified versions create outbox rows (silent updates, Watch and merges do not)	pass
R11	Late-arriving rows are invisible to earlier checkpoints and visible from their ingestion run on	pass
R12	A corrected dataset version gets a new run key; the insight gains a version marked “data corrected”, earlier versions keep their dataset, no notification without a band rise	pass
R13	Insights whose evidence predates the latest dataset version are flagged stale until re-evaluated	pass
4 · Five-day priorities (DXD-92, amends DXD-74)
WORK	PRIORITY	INDICATIVE EFFORT
Evaluation runner: run key, trigger dedupe, claim, staging, atomic publish, outbox	Core	5 h
Detectors D1, D2, D5 and D6 clustering on as-of metrics	Core	4 h
D8 tenant action required (lease-scoped)	Core	1.5 h
Insight Inbox list, detail, evidence, versions; acknowledge, dismiss, investigate (private thread)	Core	5 h
Authorization on every read; uniform refusals; audience instances	Core	2 h
Deduplication, re-notify rule, candidate log view	Core	2 h
End-to-end tests: golden S/N cases, replay hash, runner cases R1–R13, privacy and grant changes	Core	3 h
D3, D4a/b, full D7 with prior year	Secondary	3 h
Snooze, digest scheduling, shared summaries, feedback analytics	Secondary	3 h

Core ≈ 22.5 hours, more than one development day; it fits only if M6 is given about three days and builds on the M3 tool layer. GD assesses the overall five-day plan. Secondary items stay in the full approved scope.
```

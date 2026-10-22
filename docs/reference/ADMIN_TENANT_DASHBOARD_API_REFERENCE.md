# Admin & Tenant Dashboards — API, Chart and SQL Reference

**Frontend:** `cenomi-frontend-2` (branch `tenant-central-new-ui`), page `apps/cenomi-tenant-web/app/(state)/(main)/dashboard/page.tsx`
**Backend:** `cenomi-api-2` (branch `rv/release-prod-api-v2.43.00`)
**UI v2 design references:** `cenomi-frontend-2/docs/ui-v2/ui-v2-dashboard-redesign.md`, `ui-v2-tenant-dashboard-redesign.md`, and the mockups `docs/ui-v2/reference/super-admin-dashboard.html` (+ `super-admin-dashboard-default.png`, `-dock.png`) and `docs/ui-v2/reference/tenant-dashboard.html` (+ `tenant-dashboard-overview.png`, `-categories.png`, `-dock.png`)
**Generated:** 2026-10-13. Everything here comes from reading the code. No queries were run against a database, and every JSON example uses made-up values.

> **How to read this document**
> - Each card section covers: the **V2 component** and its **legacy component**, the permission that makes the card visible, the card's filters, the **chart type**, which response fields feed which series, the **API calls**, and the **backend trace** (route → handler → usecase → repository) with the **SQL** and an **example response**.
> - File references carry the repo name as a prefix: `cenomi-frontend-2/…` or `cenomi-api-2/…`.
> - Every success response is wrapped as `{"success": true, "data": <payload>}` by `api.Success`. Some examples below show only the `data` payload.
> - `app/main.go` and `internal/constants/constants.go` have uncommitted local edits, so line numbers in those two files may be slightly off.

---

## Contents

1. Overview: which dashboard renders, and how requests reach Go
2. Endpoint index (all dashboards)
3. Admin Dashboard: core cards (frontend)
   - 3a. Backend trace: summary-data, unique-properties/details, notifications, sales-data, contracts, sales-funnel, proposals, lead-enquiries
   - 3b. Backend trace: lease-requests-summary, pending-approval, pending-amendments-summary, service-request-summary, service-requests, units-with-fitout
4. Admin Dashboard: fit-out, document status and unit discrepancy cards (frontend + backend)
5. Tenant Dashboard (frontend + backend, including the prospective tenant view)
6. Consolidated findings and risks

---

## 1. Overview

### 1.1 Which dashboard renders (`dashboard/page.tsx`)

| User | Condition | UI v2 flag ON (`isUiV2Enabled()`) | UI v2 flag OFF (legacy) |
|---|---|---|---|
| Must hold `VIEW_DASHBOARD` | Without it, the page redirects to `/dashboard/servicerequest?sort_by=updated_at&order=DESC` and shows `<Forbidden/>` | — | — |
| `userType = ADMIN`, not `CUSTOMER_RELATIONS_TEAM` | Admin dashboard | `<SurveyIndicator variant="v2"/>` + `AdminDashboardV2` | `AdminDashboard` |
| `userType = ADMIN` + `CUSTOMER_RELATIONS_TEAM` role | Contact-centre dashboard | legacy `ContactCenterDashBoard` (not covered here) | `ContactCenterDashBoard` |
| `userType = TENANT`, `IsProspective = false` | Tenant dashboard | `TenantDashboardV2 summary={summary}` | `TenantDashboard summary={summary}` |
| `userType = TENANT`, `IsProspective = true` | Prospective tenant | legacy `ProspectiveTenant` (it has its own redesign) | `ProspectiveTenant` |
| Anyone else | | `<Forbidden/>` | `<Forbidden/>` |

The page always calls `getSummary(TenantProfileID)` → `GET /v1/summary-data/{tenantProfileId}` when a profile ID is present, and passes the result to the tenant dashboards. Admins have `TenantProfileID = 0`, so the call is skipped for them. If it did run for an admin, the handler would return 400 or 401: the endpoint is tenant-only in practice.

### 1.2 How requests reach the backend

- The frontend calls `httpRequest(...)` (`cenomi-frontend-2/libs/api/src/lib/API_Handler/API_Handler.ts`) with path constants from the `endPoints` module. In dev, `/backend_api/*` is rewritten by `next.config.js` to `localhost:8000/v1/*`.
- The Next.js BFF routes under `apps/cenomi-tenant-web/app/api/*` (`dashboard`, `summary-data`, `announcements-events/dashboard-summary` …) are **hard-coded mocks**. The dashboards never call them.
- The header `x-active-tenant-profile-id` overrides the session's tenant profile (`cenomi-api-2/internal/middleware/middleware.go:292-300`).
- **Permission middleware:** `PermissionCheck` (`cenomi-api-2/internal/middleware/middleware.go:587`) uses `internal/config/pathpermission.json`.
  - A path with **no entry is allowed** for any logged-in user.
  - The match is "any one of" the listed permissions.
  - The middleware fills `userData.RoleIDs` and `userData.ActivePermissions`.
  - `SkipPermissionCheck` (`app/main.go:~4590`) skips the path check for most of the admin-dashboard summary group: `pending-approval`, `pending-amendments-summary`, `lease-requests-summary`, `units-with-fitout`.
- **Row scoping:** almost every endpoint scopes rows through `tenantContactUsecase.GetPermittedItems` / `GetPermittedAccessItems` (`cenomi-api-2/tenant_contact/usecase/tenant_contact_usecase.go:852/860/868`, repo `tenant_contact/repository/postgres/tenant_contacts_repository.go:2029`):

```sql
SELECT
  ARRAY(SELECT DISTINCT lease_id FROM tenant_contacts WHERE tenant_contact_user_id = $1 AND lease_id IS NOT NULL %s) AS lease_ids,
  ARRAY(SELECT DISTINCT tenant_profile_id FROM tenant_contacts WHERE tenant_contact_user_id = $1 %s) AS tenant_profile_ids,
  ARRAY(SELECT DISTINCT property_id FROM tenant_contacts WHERE tenant_contact_user_id = $1 AND property_id IS NOT NULL) AS property_ids,
  ARRAY(SELECT DISTINCT region_id FROM tenant_contacts WHERE tenant_contact_user_id = $1 AND region_id IS NOT NULL) AS region_ids,
  COALESCE(MAX(CASE WHEN lease_override IS NOT NULL THEN lease_override END), NULL) AS lease_override,
  COALESCE(MAX(CASE WHEN property_override IS NOT NULL THEN property_override END), NULL) AS property_override,
  COALESCE(MAX(CASE WHEN company_override IS NOT NULL THEN company_override END), NULL) AS company_override
FROM tenant_contacts
WHERE tenant_contact_user_id = $1 %s
GROUP BY tenant_contact_user_id;
-- tenant users: AND tenant_profile_id NOT IN (SELECT tenant_profile_id FROM tenant_contacts WHERE tenant_contact_user_id=$1 AND lease_override=0)
-- TenantProfileID != 0: AND tenant_profile_id = $2      | admins: AND tenant_profile_id IS NOT NULL
```

  - **Admins:** `FetchPropertyAccessRows` (`SELECT region_id, property_id, property_override FROM tenant_contacts WHERE tenant_contact_user_id=$1 …`) feeds `resolveAdminAccessiblePropertyIDs` (`:806`).
    - Explicit `property_id` rows are used as they are.
    - `property_override = -1` with a region expands to that region's properties.
    - `property_override = -1` with **no** region sets `AllProperties = true` and leaves `Properties` empty. Each endpoint treats this differently: some apply no filter, some return nothing (see §6).
  - The expand variant (`GetPermittedItems`) can also expand all lease IDs with `SELECT lease_id FROM cenomi.leases WHERE property_id = ANY($1)`. For admins this can be very large.
  - **Tenants:** `SELECT lease_id, property_id FROM cenomi.leases WHERE tenant_profile_id = ANY($1)`.

### 1.3 Admin card visibility (V2 `admin/v2/dashboardLayout.ts`, mirrors legacy)

| Card id | V2 component | Chart form (V2) | Visible when the user has | Grid span |
|---|---|---|---|---|
| `properties` | `PropertiesCard` | stat tiles + occupancy meter | `ADMIN_DASHBOARD_SUMMARY` | 12 |
| `actionRequired` | `ActionRequiredCard` | notification list | `canViewActionRequiredWidget(perms)` | 4 |
| `salesFunnel` | `SalesFunnelCard` | stage flow (funnel) | `SALESFUNNEL_WIDGET` and not a limited contractor role | 8 |
| `kpis` (stacked under the funnel) | `KpiTiles` | 3 stat tiles | any of `EXPIRING_LEASE_VIEW`, `VIEW_CONTRACTS`, `SALES_DATA_LIST`, and not a limited contractor | (8) |
| `leaseRequests` | `LeaseRequestsCard` | donut | `LEASE_REQUEST_WIDGET` | 4 |
| `documentStatus` | `DocumentStatusCard` | stacked columns + table toggle | any of `VIEW_ARCH_DRAWING`, `VIEW_MEP_DRAWING`, `VIEW_ELECTRICAL_DRAWING` | 8 |
| `fitoutHandover` | `FitoutHandoverCard` | progress rings + handover callout | `VIEW_FIT_OUT_SUMMARY` | 7 |
| `fitoutDrawings` | `FitoutDrawingsCard` | stacked horizontal bars | any drawing permission (same as above) | 5 |
| `pendingApprovals` | `PendingApprovalsCard` | half gauges | `PENDING_APPROVALS_WIDGET` | 6 |
| `pendingAmendments` | `PendingAmendmentsCard` | heatmap | `PENDING_AMENDMENTS_WIDGET` | 6 |
| `serviceRequests` | `ServiceRequestsCard` | treemap + work-permit strip | `canViewDashboardWorkPermitChart(perms)` | 7 |
| `unitDiscrepancy` | `UnitDiscrepancyCard` | diverging bars | `VIEW_DISCREPANCY_REPORT` | 5 |

> ⚠️ The frontend shows each card based on a *widget* permission, but the backend endpoint checks a *different* permission (for example `SALESFUNNEL_WIDGET` vs `SALES_FUNNEL_LIST`/`VIEW_CONTRACTS`, `PENDING_APPROVALS_WIDGET` vs `PENDING_APPROVALS`). A user can therefore see a card and still get a 403, which shows as the card's error state.

Each V2 card keeps **its own filters** in component state (`useCardFilters`). The spec's single global filter bar was not built. `CardFilters` renders year / month / region / mall per card, and `paramsFor(card)` turns them into a query string.

### 1.4 Chart forms at a glance (UI v2 vs legacy)

| Card | UI v2 (in-house `ui-kit` SVG charts) | Legacy |
|---|---|---|
| Properties | Stat tiles + occupancy meter | 3 `cards.tsx` tiles |
| KPIs | 3 stat tiles | side cards |
| Lease requests | Donut (by registration source / unit type) | recharts donut (`LeaseRquest.tsx`) |
| Sales funnel | Stage flow: Lease requests → Leads → Proposals → Contracts | `SalesFunnel.tsx` / `funnelCard` |
| Fit-out & handover | 4 progress rings (POI Mech, POI Arch, OCI, CCI) + handover callout | `FitoutHandoverWrapper` (recharts) |
| Fit-out drawings | Stacked horizontal bars (Mechanical / Architectural / Electrical) | `FitoutDrawing.tsx` |
| Drawing document status | Stacked columns by mall + table view | `FitoutDrawingDocumentStatus*` |
| Action required | Notification list | `ActionRequired` |
| Pending approvals | Half gauges per type × delay band | spiral (d3) / `Approvals.tsx` |
| Pending amendments | Heatmap (amendment type × delay week) | `AmendmentChart` (recharts) |
| Service requests | Treemap by category + work-permit status strip | `ServiceStackedCard` / horizontal stacked bars |
| Unit discrepancy | Diverging bars by month | `UnitDiscrepancyReport` |
| Tenant: Service requests | Donut + treemap | chart.js doughnuts (`PieChart`, `SRPieChart`) |
| Tenant: Sales | Columns by month | recharts |

---

## 2. Endpoint index

All paths are under `/v1`. "Perm" is the backend `pathpermission.json` gate; "—" means no entry, so any logged-in user can call it.

| # | Endpoint | Used by | Backend entry (cenomi-api-2) | Data source | Perm |
|---|---|---|---|---|---|
| 1 | `GET summary-data/{tenantProfileId}` | page → tenant KPI tiles | `tenantsummary/delivery/http/tenant_summary_handler.go:23` | live, single CTE query | — (tenant-only in practice) |
| 2 | `GET unique-properties/details?page=1&limit=1&allow_pagination=true` | Admin › Properties | `unique_property/delivery/http/unique_property_handler.go:45` | live units + lease-occupancy CTE; GLA from synced columns | `UNIQUE_PROPERTY_DETAILS` |
| 3 | `GET contracts?page=1&limit=1&is_expiring=true` | Admin › KPI "Expiring leases" | `contract/delivery/http/contract_handler.go:62` | live `leases` | `VIEW_CONTRACTS` \| `SR_CONTRACTS_VIEW` |
| 4 | `GET contracts?page=1&limit=1&status=ACTIVATED` | Admin › KPI "Active leases" | same | live | same |
| 5 | `GET sales-data?page=1&limit=1&status=PENDING,NEED_REUPLOAD,…` | Admin › KPI "Pending sales data"; tenant sales | `sales_data/delivery/http/sales_data_handler.go:34` | live `sales_data` | `SALES_DATA_LIST` \| `VIEW_SALESDATA_REPORT` |
| 6 | `GET lease-requests-summary?filter=by_registration_source\|by_unit_type&year=` | Admin › Lease requests | `lease_request_summary/delivery/http/lease_request_summary_handler.go:24` | live `lead_enquiries` | skipped |
| 7 | `GET lead-enquiries?total_required=true&origin=sales_funnel&all_leases=true&…` | Admin › Sales funnel (lease requests, leads); drilldowns; prospective tenant | `lead_enquiry/delivery/http/lead_enquiry_handler.go:72` | live | see §3a |
| 8 | `GET proposals?total_required=true&origin=sales_funnel&all_leases=true&…` | Admin › Sales funnel (proposals) | `proposal/delivery/http/proposal_handler.go:36` | live | see §3a |
| 9 | `GET contracts?total_required=true&origin=sales_funnel&all_leases=true&…` | Admin › Sales funnel (contracts) | `contract/delivery/http/contract_handler.go:62` | live | `VIEW_CONTRACTS` |
| 10 | `GET sales-funnel?year=&month=&region=&mall=` | Admin › Sales funnel (`last_synced_at`, legacy filters/values) | `sales_funnel/delivery/http/sales_funnel_handler.go:22` | **batch table** `cenomi.sales_funnel` | `SALES_FUNNEL_LIST` |
| 11 | `GET notifications?page=1&limit=15&is_action_required=true` | Admin & tenant › Action required | `notification/delivery/http/notification_handler.go:28` | live | — |
| 12 | `GET pending-approval?region=&mall=&unique_property_id=` | Admin › Pending approvals | `pending_approval/delivery/http/pending_approval_handler.go:23` | live leases + proposals (filter lists from `r_pending_approvals_summary`) | skipped |
| 13 | `GET pending-amendments-summary?year=&month=&region=&mall=` | Admin › Pending amendments | `pending_amendments/delivery/http/pending_amendments_handler.go:37` | `leased_units_amendments` (Yardi-synced) | skipped |
| 14 | `GET service-request-summary?year=&month=&region=&mall=&service_category=` | Admin › Service requests | `service_requests_summary/delivery/http/service_request_summary_handler.go:29` | live `service_request` | checked |
| 15 | `GET service-requests?…` | Admin service-request and fit-out drilldowns; tenant SR card (`page=1&limit=200[&mall=]`) | `servicerequest/delivery/http/service_request_handler.go:158` | live | checked |
| 16 | `GET fitout-summary?year=&month=&region=&unique_property_id=` | Admin › Fit-out & handover, Fit-out drawings (fetched twice in V2) | `fitout_summary/delivery/http/fitout_summary_handler.go:114` (handler `:136`) | live `service_request` | see §4 |
| 17 | `GET units-with-fitout?property_id=` · `GET unit-fitout-status?unit_id=` | Admin legacy unit fit-out view | `fitout_summary_handler.go:882` / `:615` | live | skipped |
| 18 | `GET fitout-drawing-document-status-summary/by-mall` · `/by-document-type` | Admin › Drawing document status (+ drilldown) | `fitout_summary_handler.go:122` / `:757` | live + archive tables | see §4 |
| 19 | `GET discrepancy/monthly-graph` · `/monthly-graph/mismatch-units` | Admin › Unit discrepancy (+ drilldown) | `discrepancy/delivery/http/discrepancy_handler.go:36` / `:215` | live | see §4 |
| 20 | `GET contracts?limit=200` (V2) · `?status=ACTIVATED,SUPERSEDED&limit=1000` (legacy) | Tenant › greeting, mall picker, lease picker | `contract_handler.go:62` | live | `VIEW_CONTRACTS` |
| 21 | `GET unique-properties?page=1&limit=100` (V2) · `?page=N&limit=6` (legacy) | Tenant › Leasing opportunities; prospective | `unique_property/…` (public route group) | live + synced `available_units` | — |
| 22 | `GET announcements-events/dashboard-summary?announcement_limit=5` | Tenant › Announcements & events | see §5 | live | see §5 |
| 23 | `GET configuration/NEW_SURVEY` | Survey banner (tenants) | `configuration/…` | config table | — |
| 24 | `GET lead-enquiries?tenant_profile_id=` · `GET lead-enquiries/details?lead_enquiry_code=&lead_enquiry_id=` | Prospective tenant view | `lead_enquiry_handler.go:72` | live | details is **public** |

---

## 3. Admin Dashboard — Core Cards (frontend)

> Status: the frontend tracing is complete. On the backend, routes, required permissions and handler entry points are confirmed. **Usecase/repository file:line references and the SQL are NOT yet captured** (see "Gaps" at the end).

### 0. Page, rendering switch and shared plumbing

- Page: `cenomi-frontend-2/apps/cenomi-tenant-web/app/(state)/(main)/dashboard/page.tsx`
  - The page calls `getSummary(tenantProfileId)` → `GET summary-data/{TenantProfileID}` (`libs/api/src/lib/summary/summaryApi.ts:4`, endpoint `SUMMARY_ENDPOINT = 'summary-data/{0}'`, `endPoints.ts:144`). The call is skipped when `TenantProfileID` is falsy. The result (`data.list`, type `SummaryType`: leases, units, approved/pending documents, payments, service requests, sales data, inquiries, brands, `pending_*_documents`) is passed **only to tenant dashboards** (`TenantDashboardV2`, `TenantDashboard`, `ProspectiveTenant`). For admins it is fetched (if they have a profile id) and never used.
  - Without `VIEW_DASHBOARD`, the page redirects to `/dashboard/servicerequest?sort_by=updated_at&order=DESC`.
  - `userType === ADMIN` and not `CUSTOMER_RELATIONS_TEAM` → `AdminDashboardV2` when `isUiV2Enabled()`, otherwise the legacy `AdminDashboard`.
- Backend route: `cenomi-api-2/tenantsummary/delivery/http/tenant_summary_handler.go:23` (`GET /summary-data/{tenant-profile-id}` → `handler.List`). There is no entry in `pathpermission.json`, so only authentication is required.
- HTTP: `httpRequest` (`libs/api/src/lib/API_Handler/API_Handler.ts`) sends `fetch(${NEXT_PUBLIC_API_BASE_PATH}/${url})` with `credentials:'include'` (cookie auth). It adds `x-active-tenant-profile-id` only for TENANT users. A missing cookie redirects to `/signin`. No Next BFF routes are involved.
- Backend auth: all routes are registered in `cenomi-api-2/app/main.go:933-941` (private group: `ValidateAccessToken` → `PermissionCheck(permissionsConfig)` → `InjectAuditLogger`). `PermissionCheck` (`internal/middleware/middleware.go:587`) matches `internal/config/pathpermission.json`. The match is **any-of** (`internal/utils/utils..go:182,220`). The middleware then sets `userData.RoleIDs` / `ActivePermissions` to the roles that grant the route's permission, and downstream repositories use these for property scoping. A route with no config entry is allowed for any authenticated user.

| Endpoint (GET, under /v1) | Backend permission (any-of) | Handler |
|---|---|---|
| `summary-data/{id}` | none | `tenantsummary/delivery/http/tenant_summary_handler.go:23` |
| `unique-properties/details` | none | `unique_property/delivery/http/unique_property_handler.go:45` (FetchDetails) |
| `contracts` | VIEW_CONTRACTS, SR_CONTRACTS_VIEW | `contract/delivery/http/contract_handler.go:62` (List) |
| `sales-data` | SALES_DATA_LIST, VIEW_SALESDATA_REPORT | `sales_data/delivery/http/sales_data_handler.go:34` (List) |
| `lease-requests-summary` | LEASE_REQUEST | `lease_request_summary/delivery/http/lease_request_summary_handler.go:24` |
| `sales-funnel` | SALES_FUNNEL_LIST | `sales_funnel/delivery/http/sales_funnel_handler.go:22` |
| `lead-enquiries` | LEAD_INQUIRY_LIST | `lead_enquiry/delivery/http/lead_enquiry_handler.go:72` (Fetch) |
| `proposals` | VIEW_PROPOSALS | `proposal/delivery/http/proposal_handler.go:36` (List) |
| `notifications` | none | `notification/delivery/http/notification_handler.go:28` (List) |
| `pending-approval` | PENDING_APPROVALS | `pending_approval/delivery/http/pending_approval_handler.go:23` |
| `pending-amendments-summary` | PENDING_AMENDMENTS_WIDGET | `pending_amendments/delivery/http/pending_amendments_handler.go:37` |
| `service-request-summary` | SERVICE_REQUEST_SUMMARY, SERVICE_REQUEST_WIDGET | `service_requests_summary/delivery/http/service_request_summary_handler.go:29` |
| `service-requests` | SERVICE_REQUEST_LIST, VIEW_MARKETING_CONTENT, VIEW_ISSUE_LOD_SR | `servicerequest/delivery/http/service_request_handler.go:158` (List) |
| `units-with-fitout` | none | `fitout_summary/delivery/http/fitout_summary_handler.go:119` |

Note: the frontend visibility permissions (e.g. `SALESFUNNEL_WIDGET`, `LEASE_REQUEST_WIDGET`, `PENDING_APPROVALS_WIDGET`) differ from the backend route permissions (`SALES_FUNNEL_LIST`, `LEASE_REQUEST`, `PENDING_APPROVALS`). A card can therefore be visible and still get a 403, which renders as the card's error state.

### 0.1 Card visibility (V2 `dashboardLayout.ts` `visibleDashboardCards`, which mirrors legacy `adminDashboard.tsx`)

| Card id | Shown when |
|---|---|
| properties | `ADMIN_DASHBOARD_SUMMARY` |
| kpis | not a limited contractor role (FACILITIES_CONTRACTOR / RDD_CONTRACTOR) AND any of `EXPIRING_LEASE_LIST`(EXPIRING_LEASE_VIEW), `VIEW_CONTRACTS`, `SALES_DATA_LIST` |
| leaseRequests | `LEASE_REQUEST_WIDGET` |
| salesFunnel | not limited AND `SALESFUNNEL_WIDGET` |
| actionRequired | `canViewActionRequiredWidget`: true if the contractor permission catalog is not provisioned (none of VIEW_NOTIFICATIONS / VIEW_DASHBOARD_WORK_PERMIT_CHART / VIEW_LEASE_CONTACTS_TAB / VIEW_LEASE_UNITS_TAB present); otherwise requires `ACTION_REQUIRED_WIDGET` |
| pendingApprovals | `PENDING_APPROVALS_WIDGET` |
| pendingAmendments | `PENDING_AMENDMENTS_WIDGET` |
| serviceRequests | `SERVICE_REQUEST_WIDGET` or `VIEW_DASHBOARD_WORK_PERMIT_CHART` (work-permit-only mode = the latter without the former) |

Layout rows (spec §4.2): [properties 12] / [actionRequired 4, salesFunnel 8 + kpis stacked below] / [leaseRequests 4, documentStatus 8] / fit-out row / [pendingApprovals 6, pendingAmendments 6] / [serviceRequests 7, unitDiscrepancy 5]. When a partner card is hidden, the visible card spans 12.

### 0.2 Filters (V2)

- `useCardFilters.ts`: per-card local `useState` (not the URL, even though the spec proposed `nuqs`). Defaults are `{year: currentYear, month: null, region: null, mall: null}`. Changing the region clears the mall.
- `dashboardFilters.ts` `CARD_FILTER_SUPPORT`: properties/kpis/actionRequired have none; leaseRequests has year; salesFunnel, pendingAmendments and serviceRequests have year, month, region and mall; pendingApprovals has region and mall.
- `cardParams` → `{year, month ('Jan'..'Dec'), region, unique_property_id}`, emitted only when supported and set. `filterQueryString` orders them year, month, region, unique_property_id.
- `CardFilters.tsx` options: years = the current year and the 4 before it. Regions come from Redux `state.properties.uniquePropertyList` (`useDashboardRegionOptions`, fallback Central/Eastern/Western). Malls come from `state.properties.data` (`useDashboardMallOptions`), narrowed by region.
- Legacy: each card owns its own filter state. Option lists come from the card's API response `filters` (`years`, `regions`, `unique_property_ids` mapped against `uniquePropertyList`). Legacy queries are built with `useQueryGenerator.createQueryString`, which **merges the current page URL search params** into each query. In legacy, changing year or month resets region and mall.

---

### 1. Cenomi Properties (`properties`)
- V2: `v2/PropertiesCard.tsx` + `v2/usePropertySummary.ts`. Legacy: `adminDashboard.tsx` `populateCard` + `cards/cards.tsx`. Permission `ADMIN_DASHBOARD_SUMMARY`. No filters.
- API: `getDashboardPropertySummary()` (`adminDashboardAPI.ts:20`) → `GET unique-properties/details?page=1&limit=1&allow_pagination=true`, called on mount.
- Visual (V2): three ui-kit `StatTile`s (custom, no chart library), plus a CSS flex occupancy meter.
  - Tiles: violet = `total_properties_count` / `total_units`; teal = `total_occupied_units` / `total_occupied_gross_leasable_area`; orange = `total_vacant_units` / `total_vacant_gross_leasable_area`.
  - Meter segments are weighted by occupied units (series-teal) and vacant units (series-amber).
  - Percentages: `percentOf(part,total)` = round(part/total*1000)/10.
- Legacy visual: three colored link cards (#FFEDED / #ECDBFF / #F5DAEE).
- Drilldown: `/dashboard/properties?status=properties|occupied|vacant&sort_by=mall&order=DESC&page=1&limit=10` (page navigation).
- Response (fields used): `{success, data:{total_properties_count, total_units, total_occupied_units, total_occupied_gross_leasable_area, total_vacant_units, total_vacant_gross_leasable_area, ...}}`.
- Backend: `unique_property_handler.go:45` FetchDetails. SQL: pending.

### 2. KPI tiles (`kpis`)
- V2: `v2/KpiTiles.tsx` + `v2/useKpiCounts.ts`. Legacy: `adminDashboard.tsx` sideCards + `cards/cards.tsx`. No filters.
- APIs (all called in parallel on mount):
  1. Expiring: `getContractsListingData(tenantProfileId,'page=1&limit=1&is_expiring=true')` (`proposalsApi.ts:257`) → `GET contracts?page=1&limit=1&is_expiring=true[&tenant_profile_id=<id if a positive integer>]` → `data.total_count`.
  2. Active: `GET contracts?page=1&limit=1&status=ACTIVATED[&tenant_profile_id=..]` → `data.total_count`.
  3. Pending sales: called only with `SALES_DATA_LIST`, otherwise 0. `getSalesDataDashboard()` (`salesdataApi.ts:89`) → `GET sales-data?page=1&limit=1&status=PENDING,NEED_REUPLOAD,NEED_UPLOAD_SUPPORTING_DOCUMENT,NEED_UPLOAD_AUDITED_SALES` → `data.total_count`. The tenantProfileId argument is ignored.
- Visual: `StatTile` with hues rose (expiring), violet (active) and teal (pending sales). Each tile links to `/dashboard/expiringleases`, `/dashboard/leases` or `/dashboard/salesdata`, only when the user holds that tile's own permission.
- Legacy bug: values were written by mutating `sideCards` after `setState` inside `Promise.all`, so only the expiring value was set reliably. V2 fixes this.
- Backend: `contract_handler.go:62`, `sales_data_handler.go:34`. SQL: pending.

### 3. Lease Requests (`leaseRequests`)
- V2: `v2/LeaseRequestsCard.tsx` + `v2/useLeaseRequestBreakdown.ts`. Legacy: `components/LeaseRquest.tsx` + `cards/UnitCard.tsx` + `graphs/doughNutChart.tsx` + `graphs/LeaseRequestPopup.tsx`. Permission `LEASE_REQUEST_WIDGET`. Filter: year only.
- API: `getLeaseRequestData(filter, year)` (`adminDashboardAPI.ts:30`) → `GET lease-requests-summary?filter=by_unit_type&year=Y` and `...filter=by_registration_source&year=Y`. V2 fetches both with `Promise.all`; legacy fetches them sequentially. Both refetch on year change.
- Response: `{data:{list:[{unit_type|source, count}], last_synced_at, filters:{years}}}`.
- V2 visual: ui-kit `Donut` (custom SVG) with a SegmentedControl that switches unit types / sources.
  - `displayName` converts `FOOD_COURT` to "Food Court".
  - `foldDonutSlices` sorts by value, keeps 4 slices coloured with `categorical4` [#8B5CF6,#14B8A6,#F59E0B,#F43F5E], and folds the rest into "Other" (ink-3, not clickable).
  - Meta shows "Last Synced" from `last_synced_at` (by-unit first).
- Legacy visual: recharts `PieChart` donut with a 9-colour palette. Legacy bug: unit-type legend percentages divide by the registration-source total.
- Drilldowns:
  - Unit-type slice → `/dashboard/leaserequest?unit_type=<Display Name>&year=Y`.
  - Source slice → popup. V2 uses `LeadEnquiriesListModal` (`components/v2/listModals`); legacy uses `LeaseRequestPopup` via Redux `fetchInquiryList`. Both call `getLeadEnquiryList` → `GET lead-enquiries?source=<UPPER_SNAKE>&year=Y&page&limit[&sort_by&order]` (`pms_created_at` is mapped to `created_at`).
  - View Details → `/dashboard/leaserequest?year=Y`.
- Backend: `lease_request_summary_handler.go:24`; `lead_enquiry_handler.go:72`. SQL: pending.

### 4. Sales Funnel (`salesFunnel`)
- V2: `v2/SalesFunnelCard.tsx` + `v2/useSalesFunnelCounts.ts`. Legacy: `components/Sales.tsx` + `cards/funnelCard.tsx` + `graphs/SalesFunnel.tsx`. Permission `SALESFUNNEL_WIDGET`. Filters: year, month (Jan..Dec), region, mall.
- APIs, via Redux thunks in `libs/app-state/src/lib/features/SalesFunnel/salesFunnelSlice.ts` (API module `libs/api/src/lib/salesfunnel/SalesfunnelApi.ts`). With `Q = year=..[&month][&region][&unique_property_id]`:
  - `fetchSalesFunnel('?Q')` → `GET sales-funnel?Q`. Used only for `sales_funnel_data.last_synced_at` (and, in legacy, `filters` for the option lists).
  - `fetchLeaseRequests` → `GET lead-enquiries?Q&total_required=true&origin=sales_funnel&all_leases=true` → `lease_request_counts`, `leads_count`.
  - `fetchProposals` → `GET proposals?<same>` → `all_counts`, `signed_count`, `un_signed_count`.
  - `fetchSalesFunnelContracts` → `GET contracts?<same>` → `all_counts`, `signed_count`, `un_signed_count`.
  - All four refetch on any filter change. The card errors if any of them fails, and is ready only when all four succeed.
- Note: the counts do **not** come from `sales-funnel`'s own `lease_request`/`lead`/`proposal`/`contract` numbers.
- V2 visual: ui-kit `StageFlow`, four stages.

  | Stage | Value | Tint / dot | Splits |
  |---|---|---|---|
  | Lease Requests | `lease_request_counts` | violet / brand | none |
  | Leads | `leads_count` | pink / rose | none |
  | Proposal | `all_counts` | teal | signed / unsigned |
  | Contract | `contracts.all_counts` | orange / amber | signed / unsigned |

- Legacy visual: recharts `AreaChart` with a gradient (#5200b0→#C030D6→#F775A5→#FF8680) and overlaid link boxes. Legacy also adds a fifth point, "Contract signed".
- Drilldowns: `/dashboard/salesfunnel?Q&...`. Each link exists only when the user has the matching permission (`LEAD_INQUIRY_LIST` for the first two, `VIEW_PROPOSALS`, `VIEW_CONTRACTS`).

  | Stage | Query suffix |
  |---|---|
  | Lease Requests | `active_tab=leaseRequest` |
  | Leads | `active_tab=leaseRequest&inquiry_status=LEAD_APPROVED` |
  | Proposal | `active_tab=proposal` |
  | Proposal signed | `active_tab=proposal&proposal_status=Proposal Signed` |
  | Proposal unsigned | `active_tab=proposal&proposal_status=Pending Proposal,Proposal Sent,Proposal Review,Proposal Rejected` |
  | Contract | `active_tab=contract` |
  | Contract signed | `active_tab=contract&contract_status=Contract Signed,Contract Active,Contract Terminated` |
  | Contract unsigned | `active_tab=contract&contract_status=Pending Contract,Contract Sent,Contract Rejected` |

- Backend: `sales_funnel_handler.go:22`, `lead_enquiry_handler.go:72`, `proposal_handler.go:36`, `contract_handler.go:62`. SQL: pending.

### 5. Action Required From You (`actionRequired`)
- V2: `v2/ActionRequiredCard.tsx` + `v2/useActionRequired.ts` + `v2/actionRequired.ts`. Legacy: `dashboards/tenant/ActionRequired.tsx` (Redux `fetchNotification`, infinite scroll, 15 per page). No filters.
- API: `getNotifications(1,15,true)` (`notificationApi.ts:10`) → `GET notifications?page=1&limit=15&is_action_required=true`.
  - V2 keeps rows where `read_at === null`, shows the first 3, and uses the badge count `data.un_read_notifications_count`.
- Visual: a list.
  - Pill per `notification_type` (CONTRACT, PROPOSAL, SALES_DATA, SERVICE_REQUEST(_COMMENTS), AMENDMENT(_DETAILS), PAYMENT, ENQUIRY), all in the info tone.
  - Text is `text_content.ar|en`, with IDs (`[A-Za-z]{0,3}\d{4,}`) set in bold, plus the `created_at` date.
- Drilldowns:
  - "Open request" calls `handleNotificationNavigation` (`utils/Util.ts:2853`), which only routes by type; the sales-data section is chosen by `salesDataSection(category)`.
  - "View all" → `/dashboard/notifications?action_required=true`.
- Backend: `notification_handler.go:28`. SQL: pending.

### 6. Pending Approvals (`pendingApprovals`)
- V2: `v2/PendingApprovalsCard.tsx` + `v2/approvals.ts` + `useSummary`. Legacy: `components/Approvals.tsx` + `cards/approvalsCard.tsx` + `graphs/SpiralChart.tsx` (d3 `arc`). Permission `PENDING_APPROVALS_WIDGET`. Filters: region, mall.
- API: `GET pending-approval[?region=X&unique_property_id=N]` (`GET_PENDING_APPROVALS_DATA`).
- Response: `{list:[{type:'proposal'|'contract'|'lease', delay_by:'1 week delay'|'2 week delay'|'3 week delay'|'1 month delay'|'1 month plus delay', count}], last_synced_at, filters:{regions, malls, unique_property_ids}}`.
- V2 visual: one ui-kit `HalfGauge` (SVG) per type.
  - Value = (1 month plus) / total of the 5 bands.
  - Caption: "N within a week", "none within a month" or "nothing pending".
  - A red banner appears when every non-empty type has at least 90% older than a month.
- Legacy visual: d3 spiral arcs, colours 1w #FF8680, 2w #F775A5, 3w #DB2E6D, 1m #C030D6, 1m+ #8316FF.
- Drilldowns: gauge → `/dashboard/pendingapprovals?region&unique_property_id&section=<type>` plus:
  - proposal: `status=Pending Proposal`
  - contract: `display_status=Contract Sent`
  - lease: `display_status=Contract Signed` in V2; legacy sent `Contract Sent`.
  - View Details → `section=proposal&status=Pending Proposal`.
- Backend: `pending_approval_handler.go:23`. SQL: pending.

### 7. Pending Amendments (`pendingAmendments`)
- V2: `v2/PendingAmendmentsCard.tsx` + `v2/amendments.ts`. Legacy: `components/Amendments.tsx` + `cards/amendmentCard.tsx` + `graphs/AmendmentChart.tsx` (recharts `ScatterChart` bubbles). Permission `PENDING_AMENDMENTS_WIDGET`. Filters: year, month, region, mall.
- API: `GET pending-amendments-summary?year[&month][&region][&unique_property_id]`.
- Response: `{list:[{amendment_type, one_week_delay, two_week_delay, three_week_delay, four_week_delay, four_week_plus_delay}], last_synced_at, filters}`.
- V2 visual: ui-kit `Heatmap`.
  - Rows (oldest first): 4w+, 4w, 3w, 2w, 1w. Columns: `amendment_type` in API order.
  - Fill uses `heatSequential5` by quantile of the non-zero values.
- Legacy visual: bubbles where z = count. Colours: green (1w) #CCF0CD/#00B303, yellow (2–3w) #FDF1CC/#F7BA00, red (4w, 4w+) #F7DED9/#C72000.
- Drilldown: View Details (needs `VIEW_PENDING_AMENDMENTS`) → `/dashboard/pendingamendments?sort_by=amendment_start,amendment_end&order=DESC,DESC&<filters>`.
- Backend: `pending_amendments_handler.go:37`. SQL: pending.

### 8. Service Requests (`serviceRequests`)
- V2: `v2/ServiceRequestsCard.tsx` + `v2/serviceRequests.ts`. Legacy: `components/ServiceRequests.tsx` + `cards/ServiceStackedCard.tsx` + `graphs/groupedStackedBarChart.tsx` (recharts stacked bars: Approved #00B303, In-Process #F7BA00, Rejected #C72000) + `graphs/serviceRequestPopUp.tsx`.
- Permission: `SERVICE_REQUEST_WIDGET` or `VIEW_DASHBOARD_WORK_PERMIT_CHART` (permit-only).
- Filters: year, month, region, mall. Legacy adds a unit filter, whose options come from `GET units-with-fitout?property_id=&region=` and which sends `unit_id`.
- API: `GET service-request-summary?<filters>&service_category=INQUIRY,WORK_PERMIT,COMPLAINTS` (`WORK_PERMIT` only in permit-only mode).
- Response: `{list:[{service_category, sub_category, approved, in_process, rejected, pending, closed}], last_synced_at, filters}`.
- V2 visual: ui-kit `Treemap` (squarified, minShare 0.08), grouped Inquiry / Work Permits / Complaints.
  - Leaf value = approved + in_process + rejected. Pending and closed are excluded, as in legacy.
  - Rows are merged per sub_category.
  - Colours: `categorical4` per category; work-permit tiles use `amberSequential3` by family (CONSTRUCTION_ darkest, MAINTENANCE_ mid, OPERATIONS light).
  - The legend shows category totals.
- Drilldowns:
  - V2 tile → `ServiceRequestsListModal` → `GET service-requests?year&month&region&unique_property_id&service_category&sub_category&status=APPROVED,IN_PROCESS,REJECTED&page&limit&sort_by=updated_at&order=DESC[&search]`. A status select can narrow it, and permit popups can switch sub_category.
  - Legacy bar click → popup with status = clicked bar (IN_PROCESS is sent as `ACTION_REQUIRED,IN_PROCESS`).
  - View Details → `/dashboard/servicerequest?<query>&sort_by=updated_at&order=DESC`.
- Backend: `service_request_summary_handler.go:29`, `service_request_handler.go:158`, `fitout_summary_handler.go:119`. SQL: pending.

---

### Gaps
- Backend usecase/repository file:line references, SQL (verbatim or reconstructed), dynamic WHERE / role-scoping branches, Go post-processing and Go response structs are **not yet documented** for any endpoint above. Four background tracing agents were still running when this report was required. Response shapes above come from TypeScript usage only.

---

### 3a. Backend trace — summary, properties, notifications, sales, funnel sources

Scope: the eight admin-dashboard GETs in `admin_core.md`. Every file:line below was read on branch `rv/release-prod-api-v2.43.00`. All responses use the envelope `{"success": true, "data": <payload>}` from `cenomi-api-2/internal/api` (`SuccessResponse`, line 45). Only the `data` part is shown in the examples.

**No caching and no external calls (Yardi, SAP, Appian, etc.) happen on any of these eight read paths.** The only non-DB work is cloud-storage signed-URL generation in `sales-data`, and only for rows that carry a `document_id`.

---

#### 0. Shared plumbing

**Route groups (`cenomi-api-2/app/main.go`)**

| Group (main.go lines) | Middleware chain | Endpoints from this report |
|---|---|---|
| Private group, 932-941 | `ValidateAccessToken(TenantCookie, SetContextUserData, SetContextEnquirySource)` → `PermissionCheck(permissionsConfig, SkipPrivateOperation)` → `InjectAuditLogger` → `registerPrivateRoutes` (main.go:1953) | summary-data (2577), unique-properties/details (2288), notifications (2291), lead-enquiries view (2442), sales-data (2475), proposals (2570), contracts (2608) |
| `adminDashboadRoutes` group, 973-979 (function at main.go:4021) | `ValidateAccessToken(cookieAccessToken, cookieContactVerified, SetContextAdminUser)` → `PermissionCheck(permissionsConfig, SkipPermissionCheck)` | **sales-funnel (main.go:4253)** |

**`sales-funnel` has no route-permission check.**
- `SkipPermissionCheck` (main.go:4590) returns `true` (skip) for every path except `/v1/service-request-summary` and `/v1/home-dashboard/*`.
- So the `SALES_FUNNEL_LIST` entry in `pathpermission.json` is never enforced.
- The only gate is `SetContextAdminUser` (`internal/middleware/middleware.go:309`), which rejects non-ADMIN users.
- Because PermissionCheck is skipped, `userData.RoleIDs` and `userData.ActivePermissions` are not narrowed on this route.

**`PermissionCheck`** (`internal/middleware/middleware.go:587`)
- For each company role, `utils.HasPermission` (`internal/utils/utils..go:182`) is checked. A route with no config entry returns true for every role.
- Matching roles are collected into `userData.RoleIDs` and their permissions into `userData.ActivePermissions` (middleware.go:652-653).
- If no role matches, the response is 403.
- Consequence: on contracts and proposals, `ActivePermissions` holds only the permissions of roles that grant `VIEW_CONTRACTS` / `VIEW_PROPOSALS`. The unit-type gates further down read those narrowed lists.

**Access resolver used by almost every endpoint: `TenantContactUsecase.GetPermittedItems` / `GetPermittedAccessItems`**
- Files: `cenomi-api-2/tenant_contact/usecase/tenant_contact_usecase.go:852` (GetPermittedItems), `:861` (GetPermittedAccessItems), `:868` (getPermittedItems); repository `tenant_contact/repository/postgres/tenant_contacts_repository.go:2029`.
- Query 1, `queryAggregateTenantContacts` (repo line 60). This is the admin form, with `TenantProfileID == 0` and `ScopeAllCompanies == false`:

```sql
SELECT
  ARRAY(SELECT DISTINCT lease_id FROM tenant_contacts
        WHERE tenant_contact_user_id = $1 AND lease_id IS NOT NULL /* %s: "" for admin; TENANT adds
        AND tenant_profile_id NOT IN (SELECT tenant_profile_id FROM tenant_contacts WHERE tenant_contact_user_id=$1 AND lease_override=0) */) AS lease_ids,
  ARRAY(SELECT DISTINCT tenant_profile_id FROM tenant_contacts
        WHERE tenant_contact_user_id = $1 AND tenant_profile_id IS NOT NULL) AS tenant_profile_ids,
  ARRAY(SELECT DISTINCT property_id FROM tenant_contacts WHERE tenant_contact_user_id = $1 AND property_id IS NOT NULL) AS property_ids,
  ARRAY(SELECT DISTINCT region_id   FROM tenant_contacts WHERE tenant_contact_user_id = $1 AND region_id IS NOT NULL)   AS region_ids,
  COALESCE(MAX(CASE WHEN lease_override    IS NOT NULL THEN lease_override END), NULL)    AS lease_override,
  COALESCE(MAX(CASE WHEN property_override IS NOT NULL THEN property_override END), NULL) AS property_override,
  COALESCE(MAX(CASE WHEN company_override  IS NOT NULL THEN company_override END), NULL)  AS company_override
FROM tenant_contacts
WHERE tenant_contact_user_id = $1   -- (+ "AND tenant_profile_id = $2" when the session has an active TenantProfileID)
GROUP BY tenant_contact_user_id;
```

- Other branches of the same query:
  - `TenantProfileID != 0` → `AND tenant_profile_id = $2`.
  - `ScopeAllCompanies` (set by sales-data for admins) → `= ANY($2::bigint[])` when the session carries company IDs; otherwise `IS NOT NULL`.
- **Admin-only follow-ups**
  1. `FetchPropertyAccessRows` (repo line 2083, SQL `queryFetchPropertyAccessRows` line 132): `SELECT region_id, property_id, property_override FROM tenant_contacts WHERE tenant_contact_user_id=$1 …`.
  2. `resolveAdminAccessiblePropertyIDs` (usecase :806) resolves each row:
     - `property_override = -1` with a region → expand that region via `propertyRepo.FetchPropertyByFilters{RegionIDs}`.
     - `property_override = -1` with no region → `AllProperties = true`. **`Properties` stays empty in this case** (super-admin).
     - Otherwise → the explicit `property_id`.
  3. If properties exist and lease override = ALL (-1 or NULL with no leases):
     - With company override ALL or none, and only when `expandOverrideAllLeases` is true (GetPermittedItems only): `SELECT lease_id FROM cenomi.leases WHERE property_id = ANY($1)` (`lease/repository/postgres/lease_repository.go:488` / `:1292`). **This can return tens of thousands of IDs.**
     - With company-scoped access: the `…AND tenant_profile_id = ANY($2)` variant.
- **Non-admin follow-up:** `leaseRepo.FetchLeaseDataByCompany` (lease_repository.go:1798).
- **Proposal expansion** (GetPermittedItems only): `getProposalIdByLeaseIds` (`proposal/repository/postgres/proposal_repository.go:422`), which joins proposals to leases on `pms_tenant_code` for `lease_id = ANY($1)`.
- Finally, if `userData.TenantProfileID != 0`: `Companies = [TenantProfileID]` and `CompanyOverride = nil`.
- Override constants: `OverrideAll = -1`, `OverrideNone = 0` (`internal/constants/constants.go:4447-4449`).

---

#### 1. `GET /v1/summary-data/{tenantProfileId}`

- Route: `cenomi-api-2/tenantsummary/delivery/http/tenant_summary_handler.go:23`, registered at main.go:2577. There is no `pathpermission.json` entry, so any authenticated user passes.
- Handler: `tenant_summary_handler.go:27` (`List`).
  - Returns 400 when the ID is not numeric or is 0.
  - **Returns 401 when `userData.TenantProfileID != {id}`.** An admin session normally has `TenantProfileID = 0`, so this endpoint is effectively tenant-only. The frontend also skips the call when the ID is falsy.
- Usecase: `tenantsummary/usecase/tenant_summary_usecase.go:26`. Calls `GetPermittedItems` (full expansion) and uses only `permittedItems.Leases`, passed as `$9`.
- Repository: `tenantsummary/repository/postgres/tenant_summary_repository.go:291`. One `QueryRow`, SQL `fetchTenantSummaryQuery` (line 27). The query is static; no branch changes it.

Parameters:

| Param | Value |
|---|---|
| `$1` | tenantProfileID |
| `$2` | `'LEAD_APPROVED'` |
| `$3` | `{'PENDING','NEED_REUPLOAD','UPLOADED_SUPPORTING_DOCUMENT','NEED_UPLOAD_AUDITED_SALES'}` |
| `$4` | `'APPROVED'` |
| `$5` | `'IN_PROCESS'` |
| `$6` | `'APPROVED'` |
| `$7` | `'TENANT_PROFILE'` |
| `$8` | `'COMPANY_DOC_REQUEST_UPDATE'` |
| `$9` | permitted lease_ids |
| `$10` | `{'Requested','Requested Re-upload','Pending'}` |
| `$11` | `{'REQUESTED','RE_REQUESTED','NEED_REUPLOAD'}` |
| `$12` | `{'Requested','Requested Re-upload','Submitted'}` |

```sql
WITH amendment_summary AS (
  SELECT lua.lease_id,
         MIN(CASE WHEN lua.amendment_type='Termination' AND lua.amendment_status='Activated' THEN lua.amendment_start END) AS termination_start_date,
         MAX(CASE WHEN lua.amendment_type='Renewal'     AND lua.amendment_status='Activated' THEN lua.amendment_end   END) AS renewal_end_date
  FROM cenomi.leased_units_amendments lua
  WHERE lua.amendment_status='Activated' AND lua.amendment_type IN ('Termination','Renewal')
  GROUP BY lua.lease_id),
effective_end_date_calc AS (
  SELECT l.lease_id, l.end_date AS original_end_date, l.contract_status,
         (ams.termination_start_date IS NOT NULL) AS has_active_termination, ams.termination_start_date,
         (ams.renewal_end_date IS NOT NULL) AS has_active_renewal, ams.renewal_end_date
  FROM cenomi.leases l LEFT JOIN amendment_summary ams ON l.lease_id = ams.lease_id),
lease_summary AS (
  SELECT COUNT(l.lease_id) AS number_of_leases
  FROM cenomi.leases l
  JOIN effective_end_date_calc eed ON l.lease_id = eed.lease_id AND (
       CASE WHEN eed.has_active_termination THEN NOW()::date <= eed.termination_start_date + INTERVAL '30 days'
            WHEN eed.has_active_renewal     THEN NOW()::date <= eed.renewal_end_date + INTERVAL '30 days'
            ELSE (l.contract_status='Activated' AND l.end_date >= NOW()::date) OR NOW()::date <= l.end_date + INTERVAL '30 days' END)
  WHERE l.tenant_profile_id = $1 AND l.lease_id = ANY($9) AND l.contract_status = 'Activated'),
lease_units_count AS (
  WITH extracted_leases AS ( /* same join/predicate as lease_summary, SELECT l.lease_id */ )
  SELECT COUNT(leased_units.leased_unit_id) AS number_of_units
  FROM cenomi.leased_units WHERE leased_units.lease_id = ANY(SELECT lease_id FROM extracted_leases)),
approved_document_summary AS (
  WITH extracted_data AS (SELECT jsonb_array_elements(value::jsonb)->>'id' AS id_value FROM essential_data WHERE key='REQUIRED_DOCUMENTS')
  SELECT count(distinct document_type_id) AS approved_document_count FROM documents
  WHERE document_type_id IN (SELECT id_value FROM extracted_data) AND tenant_profile_id = $1),
lead_enquiry_summary AS (
  SELECT COUNT(CASE WHEN approval_status =  $2 THEN lead_enquiry_id END) AS lead_enquiry_approved_count,
         COUNT(CASE WHEN approval_status != $2 THEN lead_enquiry_id END) AS lead_enquiry_pending_count
  FROM lead_enquiries WHERE tenant_profile_id = $1),
brand_summary AS (
  SELECT COUNT(DISTINCT b.pms_brand_code) AS brands FROM brands b LEFT JOIN leases l ON l.brand_id=b.brand_id
  WHERE l.tenant_profile_id=$1 AND LOWER(l.contract_status)=ANY(ARRAY['activated']) AND l.end_date > now() AND l.lease_id = ANY($9)),
sales_data_summary AS (
  SELECT COUNT(CASE WHEN status = ANY($3) THEN sales_data_id END) AS pending_sales_data_count,
         COUNT(CASE WHEN status = $4 THEN sales_data_id END)     AS approved_sales_data_count
  FROM sales_data WHERE tenant_profile_id = $1),
service_request_summary AS (
  SELECT COUNT(CASE WHEN status=$5 THEN service_request_id END) AS pending_service_request_count,
         COUNT(CASE WHEN status=$5 AND category=$7 AND sub_category=$8 THEN service_request_id END) AS pending_profile_update_service_request_count,
         COUNT(CASE WHEN status=$6 THEN service_request_id END) AS approved_service_request_count
  FROM service_request WHERE tenant_profile_id = $1),
pending_lease_documents_summary AS (
  SELECT COUNT(dd.request_id) AS pending_count,
         COALESCE((SELECT dd.lease_id FROM draft_documents dd JOIN leases l ON dd.lease_id=l.lease_id
                   JOIN document_types dt ON dd.document_type_id=dt.document_type_id
                   WHERE l.tenant_profile_id=$1 AND dd.status=ANY($10) AND dt.category='Operations_Draft'
                   ORDER BY COALESCE(dd.updated_at, dd.created_at) DESC LIMIT 1), 0) AS latest_lease_id
  FROM draft_documents dd JOIN leases l ON dd.lease_id=l.lease_id JOIN document_types dt ON dd.document_type_id=dt.document_type_id
  WHERE l.tenant_profile_id=$1 AND dt.category='Operations_Draft' AND dd.status=ANY($10) AND dd.lease_id=ANY($9)),
pending_inquiry_documents_summary AS (
  SELECT COUNT(document_id) AS pending_count,
         COALESCE((SELECT cd.enquiry_id::text FROM company_documents cd WHERE cd.tenant_profile_id=$1 AND cd.approval_status=ANY($11)
                   ORDER BY cd.updated_at DESC LIMIT 1), '') AS latest_enquiry_id
  FROM company_documents WHERE is_additional_document = true AND approval_status = ANY($11) AND tenant_profile_id = $1),
pending_fitout_drawings_summary AS (
  SELECT COUNT(dd.request_id) AS pending_count,
         COALESCE((SELECT dd.lease_id FROM draft_documents dd JOIN leases l ON dd.lease_id=l.lease_id
                   WHERE l.tenant_profile_id=$1 AND dd.status=ANY($12) AND dd.document_type_id ILIKE('DR%DRW%')
                   ORDER BY COALESCE(dd.updated_at, dd.created_at) DESC LIMIT 1), 0) AS latest_lease_id
  FROM draft_documents dd JOIN leases l ON dd.lease_id=l.lease_id
  WHERE l.tenant_profile_id=$1 AND dd.status=ANY($12) AND dd.document_type_id ILIKE('DR%DRW%'))
SELECT number_of_leases, number_of_units, approved_document_count, lead_enquiry_approved_count, lead_enquiry_pending_count,
       brands, approved_sales_data_count, pending_sales_data_count, pending_service_request_count, approved_service_request_count,
       pending_profile_update_service_request_count,
       pending_lease_documents_summary.pending_count, pending_lease_documents_summary.latest_lease_id,
       pending_inquiry_documents_summary.pending_count, pending_inquiry_documents_summary.latest_enquiry_id,
       pending_fitout_drawings_summary.pending_count, pending_fitout_drawings_summary.latest_lease_id
FROM lease_summary, lease_units_count, approved_document_summary, lead_enquiry_summary, brand_summary,
     sales_data_summary, service_request_summary, pending_lease_documents_summary,
     pending_inquiry_documents_summary, pending_fitout_drawings_summary;
```

**Scoping, and things to watch**
- Only the lease, unit, brand and operations-draft counts are filtered by the permitted lease list `$9`.
- Lead enquiries, sales data, service requests, the inquiry-docs count and the fit-out drawings count are filtered by `tenant_profile_id` only.
- The `effective_end_date_calc` CTE scans **every** lease, not just this tenant's.
- The "pending sales" status set here contains `UPLOADED_SUPPORTING_DOCUMENT`. The dashboard KPI call (section 4) uses `NEED_UPLOAD_SUPPORTING_DOCUMENT` instead, so the two definitions of "pending sales" disagree.
- `completed_payments` and `pending_payments` are never populated, so they are always 0.

**Go post-processing** (`domain/tenantsummarydto.go:30`): `pending_documents` = operations count + inquiry count + drawing count.

**Response struct** (`domain/tenantsummarydto.go:4,25`):

```json
{"list":{"leases":3,"units":5,"approved_documents":4,"pending_documents":2,
 "pending_operations_documents":{"pending_count":1,"lease_id":1203},
 "pending_inquiry_documents":{"pending_count":0,"enquiry_id":""},
 "pending_drawing_documents":{"pending_count":1,"lease_id":1203},
 "completed_payments":0,"pending_payments":0,"approved_service_requests":7,"pending_service_requests":2,
 "pending_profile_update_service_requests":0,"approved_sales_data":12,"pending_sales_data":1,
 "approved_inquiries":2,"pending_inquiries":1,"brands":2}}
```

---

#### 2. `GET /v1/unique-properties/details?page=1&limit=1&allow_pagination=true`

- Route: `cenomi-api-2/unique_property/delivery/http/unique_property_handler.go:45`, registered at main.go:2288. There is no permission entry. chi matches the static `/details` path before `/{unique-property-id}` (line 44).
- Handler: `unique_property_handler.go:94` (`FetchDetails`); parser `:185`.
  - Defaults: page 1, limit 10, `allow_pagination=true`.
  - Accepts `search`, `region`, `status`, `sort_by` (mall, location or region) and `order`.
  - **ADMIN users always get `IsFilteredByAccess = true`.**
- Usecase: `unique_property/usecase/unique_property_usecase.go:104`.
  1. If `IsFilteredByAccess`: call `GetPermittedItems` (full expansion; only `.Properties` is used).
     - If `PropertyOverride == 0`: return empty.
     - Otherwise `propertyRepo.FetchPrimaryTenantVisibleUniquePropertyIDs(accessible.Properties)` (`property/repository/postgres/property_repository.go:1324`, SQL line 156). **That function returns `[]` when the input is empty**, and then the usecase returns empty.
     - Consequence: a super-admin with `AllProperties=true` and an empty `Properties` slice gets **an empty response from this endpoint**. That is a probable bug, given how property access is resolved above.
  2. `GetUniquePropertiesOccupancyCount`. If `TotalPropertiesCount == 0`, return empty.
  3. `FetchDetails`, which builds the paginated list. The dashboard requests 1 row and uses only the totals.

Access step SQL (`$1` = accessible property_ids):

```sql
SELECT DISTINCT q.unique_property_id FROM (
  SELECT primary_up.unique_property_id
  FROM properties p
  JOIN unique_properties child ON child.unique_property_id = p.unique_property_id
  JOIN unique_properties primary_up ON child.property_group_id IS NOT NULL
       AND primary_up.property_group_id = child.property_group_id
       AND primary_up.is_primary = true AND (primary_up.property_status)::text = 'TENANT_VISIBLE'
  WHERE p.property_id = ANY($1::bigint[])
  UNION
  SELECT child.unique_property_id
  FROM properties p JOIN unique_properties child ON child.unique_property_id = p.unique_property_id
  WHERE p.property_id = ANY($1::bigint[]) AND child.is_primary = true
    AND (child.property_status)::text = 'TENANT_VISIBLE' AND child.property_group_id IS NULL
) q;
```

Totals SQL: `GetUniquePropertiesOccupancyCount` (`unique_property/repository/postgres/unique_property_repository.go:353`, SQL line 78). The dashboard sends no region or search, so `%s` = ` AND unique_property_id = ANY($1)`. `CTEUnitLeaseOccupancy` is defined in `internal/repositorysql/unit_occupancy.go:19` and `SQLPropertyGroupJoinEligible` in `internal/repositorysql/property_group_join.go`.

```sql
WITH eligible AS (
  SELECT up.unique_property_id, up.property_group_id FROM unique_properties up
  WHERE up.property_status = 'TENANT_VISIBLE' AND up.is_primary = true
    AND EXISTS (SELECT 1 FROM properties p WHERE p.unique_property_id = up.unique_property_id AND p.property_status::text='TENANT_VISIBLE')
    AND unique_property_id = ANY($1)                -- [+ AND LOWER(region) LIKE LOWER($n)  (region || '%')]
                                                    -- [+ search: region::text LIKE / marketing_name / city / state / address1 / marketing_name_ar]
),
lease_best_activated_amendment AS (
  SELECT DISTINCT ON (lease_id) lease_id, amendment_type, amendment_end::date AS amendment_end
  FROM cenomi.leased_units_amendments WHERE LOWER(TRIM(COALESCE(amendment_status,'')))='activated'
  ORDER BY lease_id, isequence DESC NULLS LAST),
current_leases_for_unit AS (
  SELECT lu.unit_id, lu.lease_id, lu.unit_code AS lu_unit_code, l.start_date, l.end_date, l.contract_status
  FROM cenomi.leased_units lu JOIN cenomi.leases l ON l.lease_id = lu.lease_id
  LEFT JOIN lease_best_activated_amendment lbaa ON lbaa.lease_id = l.lease_id
  WHERE LOWER(TRIM(COALESCE(l.contract_status,''))) != 'cancelled' AND l.start_date IS NOT NULL AND l.start_date <= CURRENT_DATE
    AND (l.end_date IS NULL OR l.end_date >= CURRENT_DATE
         OR (lbaa.amendment_end IS NOT NULL AND lbaa.amendment_end >= CURRENT_DATE)
         OR UPPER(TRIM(COALESCE(lbaa.amendment_type,''))) IN ('HOLDOVER','MODIFICATION','EXPANSION'))),
best_activated_amendment AS ( /* DISTINCT ON (unit_id, lease_id): latest activated amendment + unit_in_amendment flag
                                 (unit_code NULL/'{}' => TRUE else u.pms_unit_code = ANY(lua.unit_code)) */ ),
best_lease_per_unit AS ( /* DISTINCT ON (unit_id) ordered by: active TERMINATION covering unit, HOLDOVER, ASSIGNMENT,
                            other amendment covering unit, end_date >= today; then end_date DESC */ ),
unit_sr_occupancy AS (
  SELECT u.unit_id, /* … */
         CASE WHEN blu.lease_id IS NULL THEN 'Vacant'
              WHEN LOWER(TRIM(COALESCE(blu.contract_status,'')))='cancelled' THEN 'Vacant'
              WHEN (/* same priority CASE incl. CURRENT_DATE BETWEEN start_date AND end_date */) THEN 'Occupied'
              ELSE 'Vacant' END AS occupancy_status
  FROM cenomi.units u LEFT JOIN best_lease_per_unit blu ON blu.unit_id = u.unit_id),
unit_agg AS (
  SELECT e.unique_property_id, COUNT(u.unit_id) AS total_units,
         COUNT(u.unit_id) FILTER (WHERE uso.occupancy_status='Occupied') AS occupied_units,
         COUNT(u.unit_id) FILTER (WHERE uso.occupancy_status='Vacant')   AS vacant_units
  FROM units u JOIN properties p ON p.property_id = u.property_id
  JOIN eligible e ON ( p.unique_property_id = e.unique_property_id
                       OR (e.unique_property_id = 3327 AND p.unique_property_id = 24166)
                       OR (e.unique_property_id = 1457 AND p.unique_property_id = 20535)
                       OR (e.property_group_id IS NOT NULL AND EXISTS (SELECT 1 FROM cenomi.unique_properties sib
                            WHERE sib.unique_property_id = p.unique_property_id AND sib.property_group_id = e.property_group_id)) )
  LEFT JOIN unit_sr_occupancy uso ON uso.unit_id = u.unit_id
  GROUP BY e.unique_property_id)
SELECT (SELECT COUNT(*) FROM eligible)::bigint AS total_properties_count,
       (SELECT COUNT(*) FROM eligible)::bigint AS total_count,
       COALESCE(SUM(ua.occupied_units),0)::bigint, COALESCE(SUM(ua.vacant_units),0)::bigint, COALESCE(SUM(ua.total_units),0)::bigint,
       COALESCE(SUM(up.vacant_gross_leasable_area),0)::bigint AS total_vacant_gla,
       COALESCE(SUM(up.occupied_gross_leasable_area),0)::bigint AS total_occupied_gla
FROM eligible e JOIN unique_properties up ON up.unique_property_id = e.unique_property_id
LEFT JOIN unit_agg ua ON ua.unique_property_id = e.unique_property_id;
```

Notes on the totals:
- Unit counts are computed **live** from the leases, units and amendments tables.
- GLA comes from the **synced** `unique_properties` columns.
- `status=occupied|vacant` is ignored in the totals query (`buildPropertiesQueryCondition(isTotalCount=true)`, repo :586).

List SQL: `FetchDetails` (repo :507, SQL line 200). It uses the same CTEs, but `eligible` has no filters. Filters are applied on the outer `sub` row:

```sql
… SELECT * FROM ( SELECT up.unique_property_id, up.marketing_name, … COALESCE(ua.vacant_units,0)::bigint AS vacant_units,
      COALESCE(ua.occupied_units,0)::bigint AS occupied_units, COALESCE(ua.total_units,0)::bigint AS total_units,
      COALESCE(up.vacant_gross_leasable_area,0)::bigint, COALESCE(up.occupied_gross_leasable_area,0)::bigint,
      COALESCE(up.total_gross_leasable_area,0)::bigint, up.gps_coordinates, up.mall_manager, up.product_unit_types, …
    FROM unique_properties up JOIN eligible e ON e.unique_property_id = up.unique_property_id
    LEFT JOIN unit_agg ua ON ua.unique_property_id = up.unique_property_id ) AS sub
WHERE 1 = 1  AND unique_property_id = ANY($1)
      /* [AND occupied_units >= 0 | vacant_units >= 0 when status=occupied|vacant] */
      /* [ORDER BY marketing_name|city|region <order>] */
      LIMIT 1 OFFSET 0;   -- pagination is interpolated with Sprintf, not bound
```

Go post-processing:
- The handler copies the totals into the response (`:140-146`).
- `limit` is emitted only when `allow_pagination=true`.
- Every top-level total has `omitempty`, so a value of 0 disappears from the JSON.

Response struct (`domain/uniquepropertydto.go:66`, item DTO `:9`):

```json
{"current_page":1,"total_count":38,"cities":null,"limit":1,
 "total_properties_count":38,"total_units":9120,"total_occupied_units":7340,"total_vacant_units":1780,
 "total_occupied_gross_leasable_area":1450000,"total_vacant_gross_leasable_area":310000,
 "list":[{"unique_property_id":1457,"marketing_name":"Mall of Arabia","region":"Western","address1":"","address2":"","address3":"",
   "city":"Jeddah","state":"","country":"SA","pincode":"","total_floors":3,"status":"ACTIVE","pms_property_status":"",
   "property_status":"TENANT_VISIBLE","vacant_units":42,"occupied_units":310,"total_units":352,
   "occupied_gross_leasable_area":120000,"vacant_gross_leasable_area":15000,"total_gross_leasable_area":135000,"mallmapid":""}]}
```

---

#### 3. `GET /v1/notifications?page=1&limit=15&is_action_required=true` (Action Required card)

- Route: `cenomi-api-2/notification/delivery/http/notification_handler.go:28`, registered at main.go:2291. There is no permission entry, so `RoleIDs` = all of the user's roles.
- Handler: `notification_handler.go:34`; parser `:91`.
  - Defaults: page 1, limit 10.
  - Also accepts `include_archived`, `search`, `notification_type`, `status=unread|read` and RFC3339 `from`/`to`.
  - `TenantProfileIDList` = every `Companies[].TenantProfileID != 0`.
  - `PermissionList` = every permission from every company role.
  - Also copies `UserID`, `RoleIDs` and `UserType`.
- Usecase: `notification/usecase/notification_usecase.go:42`.
  - **ADMIN only:** `fetchUniquePropertyIDAndLeaseID` (`:181`).
    1. `GetPermittedItems` (full expansion, so OverrideAll admins can produce very large lease arrays).
    2. `propertyRepo.Fetch{PropertyIDs}` turns properties into unique_property_ids. **With an empty property list, `buildPropertiesQuery` adds no filter and returns every property.**
  - `PermissionList` is intersected with `constants.NotifictaionPermissions` (`internal/constants/constants.go:5945`).
  - Three repository calls follow.
- Repository: `notification/repository/postgres/notification_repository.go`
  - `List` at `:353` (SQL `:187`)
  - `FetchNotificationsCount` at `:812` (SQL `:262`)
  - `FetchUnreadNotificationsCount` at `:830`
  - WHERE builder `buildQuery` at `:595`; lifecycle filter at `:583`

Final list SQL for an admin. The `n.tenant_profile_id = ANY(..)` condition is added only if the admin session carries non-zero company IDs; it is shown as omitted here.

```sql
WITH distinct_notifications AS (
  SELECT DISTINCT ON (COALESCE(n.group_id, n.notification_id))
    n.notification_id, n.tenant_profile_id, n.notification_type, n.text_content, n.created_at, n.read_at,
    n.target_type, n.target_user_id, n.target_role_id, n.action_required, n.lease_id, n.unique_property_id,
    NULL::timestamp AS archived_at, NULL::text AS archive_reason
  FROM notifications n
  WHERE n.action_required = $1                                   -- true (only when is_action_required=true)
    AND ((n.target_user_id = $2
          OR (n.target_role_id = ANY($3) AND (n.target_user_id IS NULL OR n.target_user_id = 0))
          OR target_permissions && $4::text[])
         AND (n.target_type = 'ADMIN' OR n.target_type IS NULL))
    AND (n.lease_id = ANY($5) OR n.unique_property_id = ANY($6) OR (n.lease_id IS NULL AND n.unique_property_id IS NULL))
    AND n.action_state IS DISTINCT FROM 'ACTION_DONE'
  ORDER BY COALESCE(n.group_id, n.notification_id))
SELECT * FROM distinct_notifications ORDER BY created_at DESC
LIMIT $7 OFFSET $8;                                              -- 15, 0
```

Variants of the WHERE clause:
- **Tenant users:** `((n.tenant_profile_id = ANY($x) OR (n.tenant_profile_id IS NULL AND n.target_user_id = $y)) …` and `(n.target_user_id=$ OR n.target_role_id=ANY($) OR target_permissions && $) AND (target_type='TENANT' OR NULL)`.
- **The lease/property clause** is added only for ADMIN, and only when either array is non-empty.
- **`include_archived=true`** switches to `queryListUserNotificationsWithArchive`: the same CTE is run against `notifications_archive` and combined with `UNION ALL`, and the `action_state` filter is dropped.

The count queries reuse the same WHERE clause:

```sql
WITH distinct_notifications AS (
  SELECT DISTINCT ON (COALESCE(n.group_id, n.notification_id)) n.notification_id, n.group_id
  FROM notifications n WHERE <same WHERE> )
SELECT COUNT(notification_id) FROM distinct_notifications;
-- unread badge: same + AND n.read_at IS NULL (still AND action_required=true and the ACTION_DONE filter)
```

- `un_read_notifications_count` therefore counts only **unread action-required** notifications, de-duplicated by group. That matches the V2 badge.
- Go post-processing: the DTO is mapped as-is. Note that `FetchUnreadNotificationsCount` mutates `request.IsUnRead`.

Response struct (`domain/notificationdto.go:84`, item `:9`):

```json
{"current_page":1,"total_count":4,"limit":15,"un_read_notifications_count":3,
 "list":[{"id":"9f1c…","tenant_profile_id":812,"text_content":{"en":"Proposal P0012345 awaits approval","ar":"…","type":"PROPOSAL","id":"12345"},
   "created_at":"2026-10-10T08:12:00Z","read_at":null,"notification_type":"PROPOSAL","target_type":"ADMIN",
   "target_user_id":0,"target_role_id":14,"action_required":true,"lease_id":1203,"unique_property_id":1457}]}
```

---

#### 4. `GET /v1/sales-data?page=1&limit=1&status=PENDING,NEED_REUPLOAD,NEED_UPLOAD_SUPPORTING_DOCUMENT,NEED_UPLOAD_AUDITED_SALES` (KPI tile)

- Route: `cenomi-api-2/sales_data/delivery/http/sales_data_handler.go:34`, registered at main.go:2475. Permission: `SALES_DATA_LIST` or `VIEW_SALESDATA_REPORT`.
- Handler: `sales_data_handler.go:122` (`List`); parsers `:1102` and `:1123`.
  - Defaults: page 1, limit 10, order DESC.
  - `status` is passed through as a raw string.
  - `enforceTenantProfileAccessForSalesDataList` (`:1039`): ADMIN and `SALES_DATA_TEAM` get a copy of `userData` with `ScopeAllCompanies=true` (`:1068`), which ignores the company switcher.
- Usecase: `sales_data/usecase/sales_data_usecase.go:711` (`Fetch`).
  - Calls `GetPermittedAccessItems` (`:716`), which does no lease or proposal expansion.
  - Returns empty when `LeaseOverride == 0` and no tenant filter is set.
  - `applySalesDataListAccessScope` (`:816`):
    - With no tenant filter, an ADMIN with lease override ALL/NULL → `PropertyIDs = accessible.Properties` when non-empty; `LeaseIDs = nil`.
    - Otherwise → `LeaseIDs = accessible.Leases`.
    - A super-admin with no properties gets **no scope at all**.
- Repository: `sales_data/repository/postgres/sales_data_repository.go`. `brand_id` is not set here, so the `buildLeadEnquiryFilterQueryCondition` path at `:950` is used.

```sql
-- GetSalesDataCount  (:430, SQL :96)
SELECT COUNT(sales_data_id) FROM sales_data
WHERE status IN ('PENDING','NEED_REUPLOAD','NEED_UPLOAD_SUPPORTING_DOCUMENT','NEED_UPLOAD_AUDITED_SALES')   -- string-concatenated, not bound
  AND lease_id IN (SELECT lease_id FROM leases WHERE property_id = ANY($1));   -- OverrideAll admin w/ properties
  -- non-OverrideAll: AND lease_id = ANY($1)
  -- optional: tenant_profile_id = $ | = ANY($), LOWER(lease_code) IN (LOWER($..)), sales_period overlap, source filter

-- Fetch  (:637, SQL :175)
SELECT sales_data_id, tenant_profile_id, lease_id, lease_code, sales_period_start, sales_period_end, sales_amt, status,
       document_id, created_by, updated_by, approved_by, submitted_by, submitted_by_email, created_at, updated_at, approved_at
FROM sales_data <same WHERE>
ORDER BY sales_period_start DESC LIMIT 1 OFFSET 0;

-- GetDistinctLeaseCodes  (:485, builder :1119, SQL :111) — only TenantProfileID/Status/BrandID are carried over, NO access scope
SELECT DISTINCT sd.lease_code, COALESCE(b.brand_name,''), COALESCE(p.marketing_name,''), COALESCE(b.brand_name_arabic,''), COALESCE(p.marketing_name_ar,'')
FROM sales_data sd LEFT JOIN leases l ON sd.lease_code = l.pms_tenant_code
LEFT JOIN brands b ON l.brand_id = b.brand_id LEFT JOIN properties p ON l.property_id = p.property_id
WHERE sd.lease_code IS NOT NULL AND sd.lease_code != ''
  AND sd.status IN ('PENDING','NEED_REUPLOAD','NEED_UPLOAD_SUPPORTING_DOCUMENT','NEED_UPLOAD_AUDITED_SALES');
```

Per-row enrichment (here at most 1 row, because `limit=1`):
- Usecase `:745-803`:
  - `commentRepo.Fetch` (unread comments)
  - `documentRepo.FetchByDocumentID`, followed by `storage.GetSignedURL` (Yardi documents use the SharePoint path)
  - `userRepo.FetchUserInfoByUserIDs`
- Handler `:190-241`:
  - `FetchLeaseByLeaseID`
  - `GetPropertyByID`
  - `GetTenantProfileByID`
  - source normalization

**Risks**
- `status` values are string-concatenated into the SQL, which is an injection risk.
- `lease_codes` is computed over **all tenants and properties**. This leaks data across scope and is a full-table query, even though the dashboard only reads `total_count`.

Response struct (`domain/salesdatadto.go:124`; the `is_monthly` pivot variant is not used here):

```json
{"current_page":1,"total_count":37,"limit":1,
 "list":[{"sales_data_id":"…","tenant_profile_id":812,"lease_id":1203,"lease_code":"t0106369",
   "sales_period_start":"2026-09-01T00:00:00Z","sales_period_end":"2026-09-30T00:00:00Z","sales_amt":125000,
   "status":"PENDING","property_name":"Mall of Arabia","property_id":55,"company_name":"ACME","brand_name":"ACME Shoes",
   "sales_report_frequency":"Monthly","source":"TENANT_PORTAL","created_by_name":"…"}],
 "lease_codes":[{"lease_code":"t0106369","brand_name":"ACME Shoes","mall_name":"Mall of Arabia","brand_name_arabic":"…","mall_name_arabic":"…"}]}
```

`total_count` has `omitempty`, so the key is missing when the count is 0. The frontend has to default it.

---

#### 5. `GET /v1/contracts?year=Y[&month=Mon][&region=R][&unique_property_id=N]&total_required=true&origin=sales_funnel&all_leases=true`

The KPI calls `?page=1&limit=1&is_expiring=true` and `&status=ACTIVATED` go through the same path; their differences are noted inline.

- Route: `cenomi-api-2/contract/delivery/http/contract_handler.go:62`, registered at main.go:2608. Permission: `VIEW_CONTRACTS` or `SR_CONTRACTS_VIEW`.
- Handler: `contract_handler.go:72` (`List`); parsers `:447` and `:220`.
  - Defaults: page 1, limit 10, `sort_by=pms_last_modified_at`, `order=DESC`. The funnel call sends no page or limit, so it fetches **10 rows** it never uses.
  - `month` is mapped through `monthCountMap` (`jan`→1).
  - `total_required=true` → `TotalRequired`; `origin` → `Origin`; `all_leases`/`allLeases=true` → `AllLeases`.
  - `params.TenantProfileID = userData.TenantProfileID` when no `tenant_profile_id` is sent; this is 0 for admins.
  - Post-processing (`:124-155`):
    - de-duplicates rows by `contract_id`
    - `filters.status = constants.ContractStatus`
    - strips contracted rent when `!canViewContractFinancials`
- Usecase: `contract/usecase/contract_usecase.go:105` (`List`). Steps:
  1. `FetchFilterDatas`: global and unscoped (repo `:1758`, SQL `:573`).
  2. Unit-type gate (`:116-134`):
     - `UnitTypesWithAccess` = the `{store, media, specialty}` types whose `VIEW_LEASE_STORE|MEDIA|SPECIALITY` permission is in `ActivePermissions`. `ActivePermissions` holds only the roles that grant `VIEW_CONTRACTS`.
     - If none match, `constants.ErrInvalidUserRole` → **HTTP 500**.
  3. `ContractsListingFlag = true`.
  4. `GetPermittedAccessItems` (`:155`). If `LeaseOverride == 0`, return all zeros.
  5. `usePropertyScopedAccess` (`:166`) is true when all of these hold: ADMIN, `TenantProfileID == 0`, lease override ALL/NULL, `Properties > 0`, `Leases == 0`.
  6. `fetchLocationFiltersWithAccess` (`:762`) → `FetchLocationFilters` (repo `:943`). **If it returns no cities, the endpoint returns all zeros.** Year, month, region and unique-property filters all apply to that city query.
  7. If `region` or `unique_property_id` (or unit_type/location) is set → `propertyRepo.FetchPropertyByFilters` (`:392`): `SELECT … FROM properties WHERE [LOWER(region)=LOWER($)] [AND unique_property_id=$]`.
  8. Scope assignment (`:195-235`):
     - **Property-scoped admin:** `PropertyIDs = filterProps ∩ accessible.Properties` (or all accessible properties); `LeaseIDs = nil`. If the result is empty, return zeros.
     - **Admin without property access** (for example a super-admin) **plus a region or mall filter:** `LeaseIDs = SELECT lease_id FROM cenomi.leases WHERE property_id = ANY(filterProps)`; `PropertyIDs = filterProps ∩ accessible.Properties`, which is usually empty.
     - **Otherwise:** `LeaseIDs = accessible.Leases`, de-duplicated; `PropertyIDs = filterProps`. A super-admin with no filter gets **no scope**.
  9. `GetContractCount`, then `List`, then `mapToContractsDTO` (`:463`, which runs FetchPropertyByFilters, FetchBrandName and FetchCompanyName on the 10 rows).
  10. If `Origin == "sales_funnel"`: `FetchAllCounts`, `FetchSignedCounts`, `FetchUnSignedCounts`. If `TotalRequired`: `FetchStatusCountSummary`.
- Repository: `contract/repository/postgres/contract_repository.go`
  - Builder `buildListContractsQuery`: `:1278`
  - `GetContractCount`: `:681`
  - `List`: `:761`
  - `FetchAllCounts`: `:1510`
  - `FetchSignedCounts`: `:1538`
  - `FetchUnSignedCounts`: `:1576`
  - `FetchStatusCountSummary`: `:1614`

**What `all_leases` and `origin=sales_funnel` do:** `shouldApplyLeaseListingVisibility` (`:649`) returns false when `AllLeases || Origin=="sales_funnel"` (also when `IsSyncFlag`). So **neither the `effective_end_date_calc` CTE nor the 30-day grace-period predicate is added**: expired and terminated leases are counted. Without these flags, which is the case for the KPI calls, the count and list get the amendment CTEs plus `NOW()::date <= COALESCE(eed.effective_end_date, l.end_date) + INTERVAL '30 days'`. Non-admins also get `COALESCE(eed.has_active_holdover,false)=false`.

WHERE builder order (`:1278`); each entry is appended only when its value is set:
1. `LOWER(p.derived_unit_type)=ANY($)` (UnitTypesWithAccess)
2. `l.lease_id=$` (contract_id)
3. `l.lease_id=ANY($)` (**count queries only**)
4. `l.tenant_profile_id=$`
5. `l.tenant_profile_id=ANY($)`
6. `l.property_id=ANY($)`
7. `EXTRACT(YEAR FROM l.pms_created_at)=$` (year)
8. `EXTRACT(MONTH FROM l.pms_created_at)=$` (month)
9. search on `lease_brand_mall`, `pms_tenant_code` or `lease_code`
10. `LOWER(l.pms_tenant_code) LIKE`
11. `LOWER(p.marketing_name)=LOWER($)` (mall)
12. `LOWER(p.city)=ANY($)`
13. `LOWER(p.region)=LOWER($)` (region)
14. `p.unique_property_id=$` (mall filter)
15. `l.pms_tenant_code=$`
16. `l.brand_id=$`
17. is_expiring block: `l.end_date BETWEEN now()-3 months AND now()+9 months 7 days AND contract_status = ANY({Activated,Superseded}) AND latest_amendment_status NOT IN ('Termination Activated','Renewal Activated')`
18. status: `ACTIVATED` with the listing flag → `(contract_status='Activated' OR 'Expired' OR 'Superseded')`
19. display_status → `LOWER(l.admin_display_status)=ANY($)` (admin) or `tenant_display_status` (tenant)
20. `p.unique_property_id=ANY($)`
21. `l.lease_type=ANY($)`
22. delay predicates

The year and month filters are on **`pms_created_at`**, not on the lease start date.

Final SQL for the funnel call: property-scoped admin, `year=2026&month=Jan&region=Central&unique_property_id=1457`.

```sql
-- GetContractCount
SELECT COUNT(distinct l.lease_id)
FROM cenomi.leases AS l LEFT JOIN cenomi.properties p ON l.property_id = p.property_id
WHERE LOWER(p.derived_unit_type) = ANY($1)          -- {store,media,specialty} ∩ permissions
  AND l.property_id = ANY($2)                        -- accessible ∩ (region/mall) properties
  AND EXTRACT(YEAR FROM l.pms_created_at) = $3       -- '2026'
  AND EXTRACT(MONTH FROM l.pms_created_at) = $4      -- 1
  AND LOWER(p.region) = LOWER($5)                    -- 'Central'
  AND p.unique_property_id = $6;                     -- 1457
-- (lease-scoped path adds  AND l.lease_id = ANY($n) )

-- List (ContractsListingFlag → scope CTE; IDs are inlined as literal CSV, not bound)
WITH filtered_lease_id AS (SELECT lease_id FROM cenomi.leases WHERE property_id = ANY(ARRAY[55,56,…]::bigint[]))
     -- lease-scoped: WITH filtered_lease_id as (SELECT unnest(ARRAY[1203,1204,…]::bigint[]) AS lease_id)
SELECT DISTINCT ON (l.lease_id) l.lease_id, l.pms_tid, l.pms_tenant_code, l.property_id, l.brand_id, l.tenant_profile_id, …,
       COALESCE(lua.amendment_status, l.contract_status) AS contract_status, …, p.marketing_name, p.marketing_name_ar,
       l.tenant_display_status, l.admin_display_status,
       COALESCE(NULLIF(TRIM(l.company_name),''), tp.company_name) AS company_name, …, p.region, … l.planned_fitout_end_date
FROM cenomi.leases AS l
JOIN filtered_lease_id as fl ON l.lease_id = fl.lease_id
LEFT JOIN cenomi.properties p ON l.property_id = p.property_id
LEFT JOIN cenomi.tenant_profiles tp ON l.tenant_profile_id = tp.tenant_profile_id
LEFT JOIN LATERAL (SELECT amendment_status FROM cenomi.leased_units_amendments
                   WHERE lease_id = l.lease_id AND amendment_status='Activated' ORDER BY pms_amendment_id DESC LIMIT 1) lua ON true
WHERE LOWER(p.derived_unit_type) = ANY($1) AND l.property_id = ANY($2)
  AND EXTRACT(YEAR FROM l.pms_created_at) = $3 AND EXTRACT(MONTH FROM l.pms_created_at) = $4
  AND LOWER(p.region) = LOWER($5) AND p.unique_property_id = $6
ORDER BY l.lease_id, pms_last_modified_at DESC    -- DISTINCT ON forces lease_id first => effectively ordered by lease_id ASC
LIMIT $7 OFFSET $8;                               -- 10, 0

-- FetchAllCounts (DisplayStatus cleared; note COUNT(admin_display_status) skips NULL statuses, no DISTINCT)
SELECT COUNT(l.admin_display_status) FROM cenomi.leases AS l LEFT JOIN cenomi.properties AS p ON l.property_id = p.property_id
WHERE <same 6 predicates>;

-- FetchSignedCounts
SELECT COUNT(l.admin_display_status) FROM cenomi.leases AS l LEFT JOIN cenomi.properties AS p ON l.property_id = p.property_id
WHERE <same 6 predicates>
  AND LOWER(l.admin_display_status) = ANY($7)    -- {'contract signed','contract active','contract terminated'}
  AND  LOWER(l.admin_display_status) IN ('contract signed','contract active','contract terminated');

-- FetchUnSignedCounts
… AND LOWER(l.admin_display_status) = ANY($7)    -- {'contract sent','pending contract','contract rejected'}
  AND  LOWER(l.admin_display_status) IN ('contract sent','pending contract','contract rejected');

-- FetchStatusCountSummary (total_required=true)
SELECT l.admin_display_status, COUNT(l.admin_display_status) FROM cenomi.leases AS l LEFT JOIN cenomi.properties AS p ON l.property_id = p.property_id
WHERE <same 6 predicates> GROUP BY l.admin_display_status;

-- FetchLocationFilters (:943, SQL :599; isFilterQuery => no unit-type/location/tenant_profile_ids predicates)
SELECT DISTINCT p.city FROM leases l INNER JOIN cenomi.properties p ON l.property_id = p.property_id
WHERE l.property_id = ANY($1) AND EXTRACT(YEAR FROM l.pms_created_at) = $2 AND EXTRACT(MONTH FROM l.pms_created_at) = $3
  AND LOWER(p.region) = LOWER($4) AND p.unique_property_id = $5;

-- FetchFilterDatas (global)
SELECT unit_type_array.unit_type, admin_status_array.admin_display_status, tenant_status_array.tenant_display_status, tenant_profile_id_array.tenant_profile_id
FROM (SELECT ARRAY_AGG(DISTINCT derived_unit_type) AS unit_type FROM cenomi.properties WHERE derived_unit_type IS NOT NULL) unit_type_array,
     (SELECT ARRAY_AGG(DISTINCT admin_display_status) FROM cenomi.leases) admin_status_array,
     (SELECT ARRAY_AGG(DISTINCT tenant_display_status) FROM cenomi.leases) tenant_status_array,
     (SELECT ARRAY_AGG(DISTINCT tenant_profile_id) FROM cenomi.leases) tenant_profile_id_array;
```

Notes:
- `all_counts` uses `COUNT(admin_display_status)`, while `total_count` uses `COUNT(DISTINCT lease_id)`. They differ when a lease has a NULL status.
- Signed and unsigned counts cover only the 6 listed statuses, so signed + unsigned ≤ all.
- The funnel card reads `all_counts`, `signed_count` and `un_signed_count`, each with `omitempty`.
- For the KPI expiring tile (`is_expiring=true`): after `List`, the handler also runs `FetchExpiringLeaseFilters` (usecase `:1328`, repo `:1709`).

Response struct (`domain/contractdto.go:297`). Note that the JSON keys are swapped relative to the Go names: `Filter` → `"filters"`, `Filters` → `"filter"`.

```json
{"current_page":1,"total_count":42,"limit":10,
 "filters":{"cities":["Riyadh","Jeddah"],"status":["…constants.ContractStatus…"]},
 "filter":{"tenant_status":["…"],"admin_status":["Contract Signed","Contract Sent","…"],"unit_type":["store","media","specialty"],"tenant_profile_id":[812,…]},
 "list":[{"contract_id":1203,"tenant_profile_id":812,"pms_tenant_code":"t0106369","property_id":55,"property_name":"Mall of Arabia",
          "brand_name":"ACME Shoes","company":"ACME","region":"Western","admin_display_status":"Contract Active", "…":"…"}],
 "all_counts":40,"signed_count":31,"un_signed_count":7,
 "status_count_summary":[{"status":"Contract Active","count":25},{"status":"Contract Sent","count":5},{"status":"Contract Signed","count":6}]}
```

---

#### 6. `GET /v1/sales-funnel?year=Y[&month=Mon][&region=R][&unique_property_id=N]`

- Route: `cenomi-api-2/sales_funnel/delivery/http/sales_funnel_handler.go:22`, registered at main.go:4253. This is the **admin-only group with no PermissionCheck** (see §0).
- Handler: `sales_funnel_handler.go:26`. Reads `month`, `year`, `region`, `mall` and `unique_property_id` as raw strings.
- Usecase: `sales_funnel/usecase/sales_funnel_usecase.go:35`.
  - Calls `GetPermittedItems` (full expansion, including lease and proposal ID materialisation that this endpoint never uses). Only `.Properties` is used, as `PropertyIDs`.
  - Then runs four repository queries and `batchExecutionHistoryRepo.Fetch("SALES_FUNNEL_GRAPH_SYNC")`.
  - **Nil-pointer risk** (`:83-85`): `salesFunnel.LastSynced = …` is assigned even when `year` is empty, because `salesFunnel` stays nil in that case. A request without `year` panics whenever a successful sync row exists. The dashboard always sends `year`.
- Repository: `sales_funnel/repository/postgres/sales_funnel_repository.go`
  - `FetchFilterDatas` at `:144`
  - `FetchRegions` at `:228`
  - `FetchPropertyFilterDatas` at `:172`
  - `FetchSalesFunnelData` at `:70`
  - `buildQueryCondition` at `:206`
  - The helper `common.AddQueryCondition` (`internal/common/util.go:176`) adds the condition whenever `paramValue != 0`. For slices that is always true.
- Batch history: `batch_execution_history/repository/postgres/batch_execution_history_repository.go:167`, SQL `:62`.
- **No live data is read:** every number comes from the pre-aggregated table `cenomi.sales_funnel`, filled by the `SALES_FUNNEL_GRAPH_SYNC` job.

```sql
-- 1. FetchFilterDatas  (year intentionally excluded; property filter only if PropertyIDs non-empty)
SELECT ARRAY_AGG(distinct by_year) as years, ARRAY_AGG(distinct mall) as malls FROM cenomi.sales_funnel
 WHERE property_id = ANY($1) AND LOWER(region) = LOWER($2) AND LOWER(by_month) = LOWER($3);

-- 2. FetchRegions  (property filter ALWAYS added, even for an empty slice => super-admin with AllProperties and no explicit list gets regions = [])
SELECT ARRAY_AGG(distinct region) as regions FROM cenomi.sales_funnel WHERE property_id = ANY($1);

-- 3. FetchPropertyFilterDatas  (year included)
SELECT ARRAY_AGG(DISTINCT unique_property_id) AS unique_property_id FROM cenomi.sales_funnel
 WHERE property_id = ANY($1) AND LOWER(region) = LOWER($2) AND LOWER(by_month) = LOWER($3) AND by_year = $4;

-- 4. FetchSalesFunnelData  (only when year != "")
SELECT lease_requests, lead, total_proposals, pending_proposals, signed_proposals, total_contracts, pending_contract, signed_contracts, mall, property_id
FROM cenomi.sales_funnel
 WHERE lower(by_month) = lower($1)          -- month ('Jan'), optional
   AND by_year = $2                         -- year
   AND lower(region) = lower($3)            -- optional
   AND lower(mall) = lower($4)              -- optional (`mall` param; dashboard sends unique_property_id instead)
   AND property_id = ANY($5)                -- only if accessible properties non-empty
   AND unique_property_id = $6              -- optional
 GROUP BY sales_funnel.lease_requests, sales_funnel.lead, sales_funnel.total_proposals, sales_funnel.pending_proposals,
          sales_funnel.signed_proposals, sales_funnel.total_contracts, sales_funnel.pending_contract, sales_funnel.signed_contracts,
          sales_funnel.by_month, sales_funnel.by_year, sales_funnel.region, sales_funnel.mall, sales_funnel.property_id;

-- 5. last_synced_at
SELECT batch_name, batch_run_start_at, batch_run_end_at, batch_status, summary FROM batch_execution_history
 WHERE batch_name = 'SALES_FUNNEL_GRAPH_SYNC' AND batch_status = TRUE ORDER BY batch_run_start_at desc /* LIMIT 1 */;
```

Go post-processing:
- `FetchSalesFunnelData` **sums every returned row in Go** (`:120-135`).
- The `GROUP BY` over all columns quietly collapses rows that are exact duplicates.
- With no year, `sales_funnel_data` is all zeros with `last_synced_at:null`, unless the panic above is hit.

Response struct (`domain/salesfunneldto.go:6,15,23,30,70`):

```json
{"filters":{"years":[2023,2024,2025,2026],"malls":["Mall of Arabia","…"],"regions":["Central","Eastern","Western"],"unique_property_ids":[1457,3327]},
 "sales_funnel_data":{"last_synced_at":"2026-10-13T01:00:12Z","lease_request":120,"lead":64,
   "proposal":{"total":40,"un_signed":12,"signed":28},"contract":{"total":30,"un_signed":6,"signed":24}}}
```

The dashboard reads only `last_synced_at` from this payload.

---

#### 7. `GET /v1/proposals?year=Y[&month][&region][&unique_property_id]&total_required=true&origin=sales_funnel&all_leases=true`

- Route: `cenomi-api-2/proposal/delivery/http/proposal_handler.go:36`, registered at main.go:2570. Permission: `VIEW_PROPOSALS`.
- Handler: `proposal_handler.go:61`; parsers `:247` and `:296`.
  - Defaults: page 1, limit 10.
  - `month` is mapped through `monthMap`.
  - **`all_leases` is ignored**: proposals have no visibility rule to disable.
  - `status` → `PMSProposalStatus`, with `StatusColumn = admin_display_status` for admins.
  - The handler sets `TenantProfileID = userData.TenantProfileID` if non-zero, plus `UserID`, `RoleIDs` and `UserType`.
- Usecase: `proposal/usecase/proposal_usecase.go:169` (`List`). Steps:
  1. `FetchFilterDatas` (global; repo `:1341`, SQL `:410`), then `augmentProposalAdminFilterStatuses` adds the AMC statuses (`:7335`).
  2. Unit-type gate over `ActivePermissions` with `VIEW_PROPOSAL_STORE|MEDIA|SPECIALITY`. If none match → `ErrInvalidUserRole` → **HTTP 500**. `params.UnitTypes` becomes the permitted set, so the gate is always non-empty.
  3. Because `UnitTypes` is always set, it **always** runs `FetchPropertyByFilters`: `SELECT … FROM properties WHERE LOWER(derived_unit_type)=ANY($1) [AND unique_property_id=$2] [AND LOWER(region)=LOWER($3)]` → `propertyIDs`.
  4. `GetPermittedItems` (full expansion). Then, by property override:

     | Property override | Accessible properties | Effect on `propertyIDs` |
     |---|---|---|
     | NULL | non-empty | intersect with accessible properties (or use them alone) |
     | 0 | any | return empty |
     | -1 | non-empty | **appended to** the filter set (a union, which widens a region or mall filter) |
     | -1 | empty | left as the unit-type/region filter set |

     Lease override 0 also returns empty.
  5. `params.TenantProfileIDs = accessible.Companies`. This is empty for most admins, or `[TenantProfileID]`.
  6. Repository calls: `GetProposalsCount`, then `List`, then `FetchPropertyNameByID` and `FetchBrandName`. If `Origin=sales_funnel`, also `FetchAllCounts`, `FetchSignedCounts` and `FetchUnSignedCounts`. If `TotalRequired`, also `FetchStatusCountSummary`.
- Repository: `proposal/repository/postgres/proposal_repository.go`
  - Builder `buildProposalsQuery`: `:598`
  - `GetProposalsCount`: `:438`
  - `List`: `:455` (SQL `:33`)
  - `FetchAllCounts`: `:893`
  - `FetchSignedCounts`: `:923`
  - `FetchUnSignedCounts`: `:960`
  - `FetchStatusCountSummary`: `:997`

```sql
-- GetProposalsCount
SELECT COUNT(pr.proposal_id) FROM cenomi.proposals pr LEFT JOIN cenomi.properties p ON pr.property_id = p.property_id
 WHERE (pr.pms_tenant_code IS NULL OR pr.pms_tenant_code NOT LIKE 'PREVIEW-%')
   AND LOWER(p.derived_unit_type) = ANY($1)                 -- permitted unit types
   [AND pr.tenant_profile_id = $2 | = ANY($2)]              -- TenantProfileID / Companies
   AND EXTRACT(YEAR FROM pr.pms_created_at) = $3            -- year
   [AND EXTRACT(MONTH FROM pr.pms_created_at) = $4]         -- month
   AND pr.property_id = ANY($5)                             -- propertyIDs (unit-type/region/mall ∩/∪ access)
   [AND p.unique_property_id = $6]                          -- mall
   [AND LOWER(admin_display_status)=ANY($)]                 -- status param
   [AND LOWER(pr.lease_brand_mall) LIKE LOWER($)]           -- search
   [AND LOWER(p.marketing_name)=LOWER($)]                   -- mall name
   [AND LOWER(p.region)=LOWER($7)]                          -- region
   [AND <delay predicate on pr.pms_created_at>];

-- List: SELECT pr.proposal_id, … p.marketing_name, p.region, p.marketing_name_ar, pr.pms_hmy, p.unique_property_id, … pr.finalize_signer_name
--       FROM cenomi.proposals pr LEFT JOIN cenomi.properties p ON pr.property_id = p.property_id <same WHERE>
--       ORDER BY  proposal_id  /* or ORDER BY <sort_by> <order> */  LIMIT $n OFFSET $n+1;   -- 10, 0

-- FetchAllCounts (status param cleared)
SELECT COUNT(pr.admin_display_status) FROM proposals AS pr LEFT JOIN properties AS p ON p.property_id = pr.property_id <same WHERE>;
-- FetchSignedCounts
… <same WHERE> AND LOWER(admin_display_status)=ANY($n) /* {'proposal signed'} */ AND  LOWER(pr.admin_display_status) = 'proposal signed';
-- FetchUnSignedCounts
… <same WHERE> AND LOWER(admin_display_status)=ANY($n) /* {'pending proposal','proposal sent','proposal review','proposal rejected'} */
              AND  LOWER(pr.admin_display_status) IN ('pending proposal','proposal sent','proposal review','proposal rejected','proposal expired');
              -- 'proposal expired' can never match because the ANY() list excludes it
-- FetchStatusCountSummary
SELECT pr.admin_display_status, COUNT(pr.admin_display_status) FROM proposals AS pr LEFT JOIN properties AS p ON p.property_id = pr.property_id
 <same WHERE> GROUP BY pr.admin_display_status;
```

The year and month filters are on **`pr.pms_created_at`**.

Response struct (`domain/proposaldto.go:151`). The keys are swapped here too: `Filter` → `"filters"`, holding unit_type and admin/tenant status lists; `Filters` → `"filter"`, holding `{status}`, which is always empty.

```json
{"current_page":1,"total_count":40,"limit":10,
 "list":[{"proposal_id":5521,"pms_tenant_code":"t0201111","brand_name":"ACME Shoes","company_name":"ACME","admin_display_status":"Proposal Sent","…":"…"}],
 "filters":{"tenant_status":["…"],"admin_status":["Pending Proposal","Proposal Sent","Proposal Signed","AMC Initiated","…"],"unit_type":["store","media","specialty"]},
 "filter":{},
 "all_counts":40,"signed_count":28,"un_signed_count":12,
 "status_count_summary":[{"status":"Proposal Signed","count":28},{"status":"Proposal Sent","count":9},{"status":"Pending Proposal","count":3}]}
```

---

#### 8. `GET /v1/lead-enquiries?year=Y[&month][&region][&unique_property_id]&total_required=true&origin=sales_funnel&all_leases=true`

- Route: `cenomi-api-2/lead_enquiry/delivery/http/lead_enquiry_handler.go:72` (`NewLeadEnquiryViewHandler`), registered at main.go:2442 in the private group. Permission: `LEAD_INQUIRY_LIST`.
  - Separately, `NewLeadEnquiryHandler` (`:52`, main.go:3447) registers only the POST, PUT and retry routes.
- Handler: `lead_enquiry_handler.go:212` (`Fetch`); parser `:1038`.
  - Defaults: page 1, limit 10, order ASC, no sort_by. **So the list has no ORDER BY, and paging is nondeterministic.**
  - `limit` must not exceed `MaxLimitForPagination`.
  - `month` and `year` are raw strings; `total_required` is a bool; `unique_property_id` is an integer.
  - **`all_leases` is ignored.**
  - Admins with no lead ID go to `usecase.Fetch`.
- Usecase: `lead_enquiry/usecase/lead_enquiry_usecase.go:1471`. Steps:
  1. `FetchRoleNames(RoleIDs)` (`:1426`). `RoleIDs` = the roles that grant `LEAD_INQUIRY_LIST`.
  2. `constants.UnitTypeRoleMap` (`internal/constants/constants.go:1552`): if the user holds `REGIONAL_LEASING_MANAGER_STORE`, `REGIONAL_PRODUCT_LINE_MANAGER_MEDIA` or `REGIONAL_PRODUCT_LINE_MANAGER_SPECIALTY`, then `params.UnitType` = the mapped types (for example `store,office`) and `AssignedUserID = user`. Otherwise there is no unit-type or assignee filter.
  3. ADMIN: `fetchUniquePropertyIDByLeaseID` (`:1442`):
     - Calls `GetPermittedItems` (full expansion).
     - If property override is NULL with properties, or ALL: `propertyRepo.Fetch{PropertyIDs}`, mapped to unique_property_ids. **An empty property list gives every property.**
     - If override is 0: `ErrUserHaveNoPermission` → 403.
     - Otherwise: nil, meaning no filter.
  4. If `unique_property_id` is in that list, `UniquePropertyIDs = [id]`. Otherwise `UniquePropertyIDs = []`.
     - **Scope bug:** the repository adds the filter only when `len != 0`. Asking for a mall outside your access therefore removes the property filter entirely and returns the **global** counts.
  5. If `tenant_profile_id` is sent: a second `GetPermittedItems` call and a company-override check.
  6. If `origin=sales_funnel`, with `tempParams` (Source and InquiryStatus cleared):
     - `lease_request_counts = GetLeadEnquiriesCount`
     - `leads_count = GetLeadsCount` (InquiryStatus forced to `LEAD_APPROVED`)
  7. `total_count = GetLeadEnquiriesCount(params)`. For the dashboard this is the same as `lease_request_counts`.
  8. `Fetch` (list, 10 rows), then `FetchBrandName`, `FetchPropertyNameByID`, `FetchTenantProfileByIDs`, and **one `FetchAdminStatus` query per row**.
  9. If `TotalRequired && ADMIN && origin=sales_funnel`: `GetAdminStatusCounts`.
- Handler post-processing (`:306-427`):
  - `FetchCompanyDocs` (usecase `:1710`)
  - per row: `EssentialData.FetchByTypeAndKey('SALES_CATEGORY')`, `UniqueProperty.FetchByID` for `unique_property_id` and for each `property_ids` entry
  - `FetchInquiryDisplayStatus` (usecase `:4741`) for `filters.status`
- Repository: `lead_enquiry/repository/postgres/lead_enquiry_repository.go`
  - `GetLeadEnquiriesCount`: `:1114` (SQL `:417`)
  - `GetLeadsCount`: `:1145`
  - `Fetch`: `:1178` (SQL `:438`)
  - `fetchStatusCombinations`: `:1271` (SQL `:713`)
  - `buildLeadEnquiryFilterQueryCondition`: `:1609`
  - `GetAdminStatusCounts`: `:2331` (SQL `:424`)
  - `FetchAdminStatus`: `:2377` (SQL `:725`)

**Every count and list call first runs the status-combination lookup** for `params.InquiryStatus`. When the status is empty it is called with `''`, normally returns no rows, and adds no filter.

```sql
SELECT i.inquiry_approval_status, i.share_contact_status FROM cenomi.inquiry_status_mapping i
 WHERE tenant_status = $1 OR admin_status = $1;
```

WHERE builder order (`:1609`):
1. `le.tenant_profile_id=$`
2. unit_type: `(LOWER(unit_type)=LOWER($) OR …)`
3. source
4. `property_id=ANY($)`
5. `unique_property_id=ANY($)`
6. lead IDs
7. `(assigned_user_id=$ OR assigned_user_id IS NULL)`
8. `approval_status` OR-list
9. `EXTRACT(MONTH FROM le.created_at AT TIME ZONE 'asia/riyadh')=$`, using `constants.MonthCountMap` (`:602`)
10. `EXTRACT(YEAR FROM le.created_at AT TIME ZONE 'asia/riyadh')=$` (int)
11. `LOWER(region)=LOWER($)`, on the **enquiry's** `region` column, not the property's
12. the status-combination OR-group
13. search

```sql
-- lease_request_counts / total_count  (admin without reviewer role, mall-scoped, year+month+region)
SELECT COUNT(lead_enquiry_id) FROM lead_enquiries le
WHERE unique_property_id = ANY($1)                                              -- accessible unique props (or [requested id])
  AND EXTRACT(MONTH FROM le.created_at AT TIME ZONE 'asia/riyadh') = $2         -- 1
  AND EXTRACT(YEAR  FROM le.created_at AT TIME ZONE 'asia/riyadh') = $3         -- 2026
  AND LOWER(region) = LOWER($4);                                                -- 'Central'
-- reviewer roles add: (LOWER(unit_type)=LOWER($a) OR LOWER(unit_type)=LOWER($b)) AND (assigned_user_id = $c OR assigned_user_id IS NULL)

-- leads_count: same + status combos resolved for 'LEAD_APPROVED'
  … AND ((le.approval_status = $5 AND le.share_contact_status = $6) OR (le.approval_status = $7 AND le.share_contact_status = $8) …)
  -- a mapping row with NULL share_contact_status becomes '' here, so it only matches rows where share_contact_status = '' (NULLs never match).
  -- if 'LEAD_APPROVED' maps to no row, the filter is dropped and leads_count = lease_request_counts.

-- list
SELECT lead_enquiry_id, lead_enquiry_number, first_name, last_name, company, cr_number, email, email_verified, brand_name, sales_category_id,
       company_headquarters_region, unit_type, region, country_code, phone, phone_verified, landline, approval_status, source, created_at,
       updated_at, created_by, updated_by, enquiry_approved_at, tenant_profile_id, unique_property_id, assigned_tenant_profile_id,
       assigned_brand_id, landline, share_contact_status, lead_enquiry_code, property_id, reference_number_brand_mall_company,
       property_ids, deal_reference_id, deal_details_id
FROM lead_enquiries le <same WHERE>  LIMIT 10 OFFSET 0;   -- no ORDER BY unless sort_by given; pagination interpolated

-- per row: admin status
SELECT admin_status FROM cenomi.inquiry_status_mapping
 WHERE inquiry_approval_status=$1 AND (Share_contact_status=$2 OR Share_contact_status IS NULL);

-- status_count_summary (total_required && admin && origin=sales_funnel)
SELECT i.admin_status, COUNT(*) AS admin_status_count
FROM cenomi.lead_enquiries le
JOIN cenomi.inquiry_status_mapping i ON le.approval_status = i.inquiry_approval_status
 AND (le.share_contact_status = i.share_contact_status OR (le.share_contact_status IS NULL AND i.share_contact_status IS NULL))
<same WHERE>
GROUP BY i.admin_status;
```

Response struct (`domain/leadEnquirydto.go:131`). `leads_count` and `lease_request_counts` have `omitempty`, so they are absent when 0.

```json
{"current_page":1,"total_count":120,"limit":10,"leads_count":64,"lease_request_counts":120,
 "status_count_summary":[{"status":"New Request","count":30},{"status":"Lead Approved","count":64},{"status":"Rejected","count":26}],
 "filters":{"status":["New Request","Under Review","Lead Approved","…"]},
 "list":[{"lead_enquiry_id":"…","lead_enquiry_number":10231,"first_name":"…","company":"ACME","unit_type":"store","region":"Central",
          "approval_status":"LEAD_APPROVED","inquiry_status":"Lead Approved","unique_property_name":"Mall of Arabia","documents":[], "…":"…"}]}
```

---

#### Cross-cutting findings

1. **Sales-funnel numbers come from two sources.** The `sales-funnel` endpoint reads the pre-aggregated, nightly-synced `cenomi.sales_funnel` table. The card's actual counts come from three live queries:
   - lead enquiries, filtered on `created_at` in Asia/Riyadh time
   - proposals, filtered on `pms_created_at`
   - contracts, filtered on `pms_created_at`, with the grace-period visibility rule switched off

   The card's numbers can therefore disagree with the sync table, and its `last_synced_at` label describes data the card does not display.
2. **The month filter is applied in a different time zone per source.** Lead enquiries convert to Asia/Riyadh. Proposals and contracts use the raw `pms_created_at` with no zone conversion.
3. **Mall-scoping semantics differ per source:**
   - Contracts: the filter is intersected with the user's accessible properties.
   - Proposals: the filter is **unioned** with the accessible properties when property_override is -1.
   - Lead enquiries: an inaccessible mall **drops the filter**.
4. **Overhead on count-only calls:**
   - All three list endpoints run their full 10-row list plus enrichment (3 to 30+ extra queries) even though the card reads only counts.
   - `GetPermittedItems` runs with full lease and proposal expansion in sales-funnel, proposals, lead-enquiries, notifications and unique-properties.
   - Only contracts and sales-data use the lighter `GetPermittedAccessItems`.
5. **Unit-type gates return HTTP 500.** Contracts and proposals return 500 (`ErrInvalidUserRole`), not 403, when the role that grants the route lacks `VIEW_LEASE_*` / `VIEW_PROPOSAL_*`.
6. **SQL built by string interpolation:**
   - Sales-data `status` values are concatenated into the query string.
   - Contract scope CTE IDs are inlined into the query.
   - Lead-enquiry and unique-property pagination is built with `Sprintf`. The values are ints, so this is safe.

---

### 3b. Backend trace — lease requests, approvals, amendments, service requests, fit-out units

This trace was read from the working tree on branch `rv/release-prod-api-v2.43.00`. The uncommitted local diffs in `servicerequest/` do not touch the code paths below. `$n` means a pgx positional parameter. "[...]" marks a fragment that is added only when its condition holds.

#### Shared building blocks

**Auth and middleware.** All admin-dashboard summary routes are registered in `adminDashboadRoutes` (`cenomi-api-2/app/main.go:4021`). That router group (`app/main.go:974-979`) uses `ValidateAccessToken(... SetContextAdminUser)`, so only admins get through, and then `PermissionCheck(permissionsConfig, SkipPermissionCheck)`.
- `SkipPermissionCheck` (`app/main.go:4590`) skips the path-permission check for every route except `GET /v1/service-request-summary` and `/v1/home-dashboard/*`.
- So `pending-approval`, `pending-amendments-summary`, `lease-requests-summary` and `units-with-fitout` have **no path-permission enforcement**, even though `internal/config/pathpermission.json` lists `PENDING_APPROVALS` for `/v1/pending-approval`. Widget permissions are enforced by the frontend only.
- For `service-request-summary`, `PermissionCheck` (`internal/middleware/middleware.go:587`) checks the route against `SERVICE_REQUEST_SUMMARY` or `SERVICE_REQUEST_WIDGET`. It then **overwrites** `userData.RoleIDs` and `userData.ActivePermissions` with only the roles (and their permissions) that grant this path. Every downstream "permission" check (`VIEW_ALL_SERVICE_REQUEST`, `VIEW_SR_*`, `VIEW_FITOUT_HANDOVER_CATEGORY`) therefore sees only permissions from those roles.
- `GET /v1/service-requests` is registered in `registerPrivateRoutes` (`app/main.go:1953`, handler wired at `:2341`). That group uses `PermissionCheck(permissionsConfig, SkipPrivateOperation)`, which enforces `SERVICE_REQUEST_LIST | VIEW_MARKETING_CONTENT | VIEW_ISSUE_LOD_SR` and narrows RoleIDs and permissions the same way.

**Property and lease scoping: `tenantContactUsecase.GetPermittedItems`.** Code is at `cenomi-api-2/tenant_contact/usecase/tenant_contact_usecase.go:852`, which calls `getPermittedItems` at `:868`. Steps:
1. `tenantContactRepo.GetPermittedItems` (`tenant_contact/repository/postgres/tenant_contacts_repository.go:2029`) runs `queryAggregateTenantContacts` (same file, line 60). It returns arrays of DISTINCT `lease_id`, `tenant_profile_id`, `property_id` and `region_id` from `tenant_contacts WHERE tenant_contact_user_id = $1`, plus the MAX of the `lease_override`, `property_override` and `company_override` flags.
2. For admins: `FetchPropertyAccessRows` + `resolveAdminAccessiblePropertyIDs` expand region- and property-level rows into `accessibleItems.Properties`, which are `properties.property_id` values.
3. If properties exist and the lease override is ALL (or unset with no explicit leases), the lease IDs are materialised with `leaseRepo.FetchLeaseIDsByPropertyIDs`. When the user is company-scoped, `FetchLeaseIDsByPropertyIDsAndTenantProfiles` is used instead.
4. Proposal IDs come from `proposalRepo.FetchProposalIdsByLeaseIDs`.

Every endpoint below except `units-with-fitout` calls this, sometimes twice per request. Nothing is cached in-process: there is no Redis or memo layer on these paths, apart from the session lookup in the middleware.

---

#### 1. `GET /lease-requests-summary` (Lease Requests donut)

| Layer | Location |
|---|---|
| Route | `cenomi-api-2/lease_request_summary/delivery/http/lease_request_summary_handler.go:24` (wired at `app/main.go:4283-4285`) |
| Handler | `lease_request_summary_handler.go:28` `FetchLeaseRequestSummary`; params parsed in `parseFilterParams` at `:80` |
| Usecase | `cenomi-api-2/lease_request_summary/usecase/lease_request_summary_usecase.go:66` (scoping helper at `:42`) |
| Repository | `cenomi-api-2/lease_request_summary/repository/postgres/lease_request_summary_repository.go:44`; WHERE builder at `:89` |
| Years | `cenomi-api-2/occupancy/repository/postgres/occupancy_repository.go:130` `FetchDistinctYear` |

**Parameter validation** (`handler:80-96`):
- Neither `year` nor `filter` → OK. The handler returns `filters.years` only, with an empty `list`, because the repository is not called when `Year == ""` (`usecase:95`).
- Only one of the two is present, or `filter` is not one of `by_unit_type` / `by_registration_source` → 400.
- `RoleIDs` are taken from `userData.Companies[].Roles[].RoleID`, which is the full session; the path-permission middleware does not narrow them here.

**Usecase steps:**
1. **Unit-type role lock.** `leadEnquiryUsecase.FetchRoleNames` (`lead_enquiry/usecase/lead_enquiry_usecase.go:1426`) calls `RoleRepo.FetchRoleInfoByRoleIDs` to get role names. Those names are matched against `constants.UnitTypeRoleMap` (`internal/constants/constants.go:1552`):
   - `store` and `office` → `REGIONAL_LEASING_MANAGER_STORE`
   - `media` → `REGIONAL_PRODUCT_LINE_MANAGER_MEDIA`
   - `specialty` → `REGIONAL_PRODUCT_LINE_MANAGER_SPECIALTY`

   The first match sets `params.UnitType`. **Bug:** this is a Go map iteration, so a `REGIONAL_LEASING_MANAGER_STORE` user gets `store` or `office` at random on each request.
2. **Property scope.** `GetPermittedItems` gives `accessibleItems.Properties`. Then `propertyRepo.Fetch(PropertyRequest{PropertyIDs})` (`property/repository/postgres/property_repository.go:870` `buildPropertiesQuery`) maps them to `unique_property_id`.
   - If `Properties` is empty, no `property_id = ANY` predicate is added, so **every** property's unique ID is returned. An admin with no tenant_contacts rows therefore sees everything.
3. **Years.** `FetchDistinctYear(LeadEnquiriesTable, LeadEnquiriesYearExpr, {UniquePropertyIDs, UnitType})`.
4. **Counts.** `FetchLeaseRequestSummary`, only if `year` was given.

**SQL: years (filters)**
```sql
SELECT DISTINCT EXTRACT(YEAR FROM (created_at AT TIME ZONE 'asia/riyadh')::timestamp WITHOUT TIME ZONE)::integer
FROM cenomi.lead_enquiries
 WHERE unique_property_id = ANY($1)        -- [if scope non-empty]
   AND unit_type ILIKE $2                  -- [if role-locked unit type]
-- no ORDER BY → years come back unordered
```

**SQL: `filter=by_unit_type`**
```sql
SELECT COUNT(*)::bigint, le.unit_type, NULL::text
FROM cenomi.lead_enquiries le
 WHERE EXTRACT(YEAR FROM (le.created_at AT TIME ZONE 'asia/riyadh')::timestamp WITHOUT TIME ZONE) = $1
   AND le.unique_property_id = ANY($2)     -- [scope]
   AND le.unit_type ILIKE $3               -- [role-locked unit type]
 GROUP BY le.unit_type
```

**SQL: `filter=by_registration_source`**
```sql
SELECT COUNT(*)::bigint, NULL::text, le.source
FROM cenomi.lead_enquiries le
 WHERE EXTRACT(YEAR FROM (le.created_at AT TIME ZONE 'asia/riyadh')::timestamp WITHOUT TIME ZONE) = $1
   AND le.source IS NOT NULL
   AND le.unique_property_id = ANY($2)     -- [scope]
   AND le.unit_type ILIKE $3               -- [role-locked unit type]
 GROUP BY le.source
```

**Notes:**
- Counts are live. The old `r_lead_summary` batch table is no longer used.
- There is no status, `deleted_at` or month filter, and no ORDER BY.
- A NULL `unit_type` group produces a row with only `count`, because `unit_type` is `omitempty`.
- **Post-processing:** none beyond mapping to the DTO. `last_synced_at` is `time.Now().UTC()` (repository line 68), so it is the request time, not a sync time. If the list is empty, `last_synced_at` is null.

**Response structs** (`domain/leaserequestsummarydto.go`, `domain/salesfunneldto.go:15`):
```go
type LeaseRequestSummaryResponse struct {
    Filters  FilterDTO                `json:"filters"`        // {years,malls,regions,unique_property_ids}, all omitempty; only years set
    SyncedAt *time.Time               `json:"last_synced_at"`
    List     []LeaseRequestSummaryDTO `json:"list"`
}
type LeaseRequestSummaryDTO struct {
    Source   string `json:"source,omitempty"`
    UnitType string `json:"unit_type,omitempty"`
    Count    int    `json:"count"`
}
```
```json
{"data":{"filters":{"years":[2025,2024,2026]},"last_synced_at":"2026-10-13T08:12:44.1Z",
 "list":[{"unit_type":"STORE","count":412},{"unit_type":"FOOD_COURT","count":37},{"count":5}]}}
```

---

#### 2. `GET /pending-approval` (Pending Approvals gauges)

| Layer | Location |
|---|---|
| Route | `cenomi-api-2/pending_approval/delivery/http/pending_approval_handler.go:23` (wired at `app/main.go:4248-4250`) |
| Handler | `pending_approval_handler.go:27` `FetchPendingApproval` |
| Usecase | `cenomi-api-2/pending_approval/usecase/pending_approval_usecase.go:47` `Fetch` |
| Repository | `cenomi-api-2/pending_approval/repository/postgres/pending_approval_repository.go`: `FetchPendingApprovalsData` at `:102`, `FetchFilterDatas` at `:179`, `FetchRegions` at `:206`, `FetchUniquePropertyIDs` at `:224`; SQL template `formatPendingApprovalLiveQuery` at `:350`; visibility rule at `:280`; region/mall/property predicates at `:333` |

**Parameters:** `region`, `mall` (marketing name, which the frontend does not send) and `unique_property_id` (uint, otherwise 400). Year and month are not supported.

**Usecase steps:**
- `GetPermittedItems` → `PropertyIDs`, `LeaseIDs`, `ProposalIDs` and `TenantProfileIDs` (= `accessibleItems.Companies`). If `Properties` is empty → **500** "no propertyids fetched from level based filter".
- **Unit-type permissions** (`usecase:15-25, 66-80`):
  - Leases: `VIEW_LEASE_STORE` / `VIEW_LEASE_MEDIA` / `VIEW_LEASE_SPECIALITY` → `UnitTypesWithAccess`.
  - Proposals: `VIEW_PROPOSAL_STORE` / `VIEW_PROPOSAL_MEDIA` / `VIEW_PROPOSAL_SPECIALITY` → `ProposalUnitTypesWithAccess`.
  - An empty list means no unit-type restriction.
  - `ActivePermissions` here is the full session set, because the path-permission check is skipped for this route.
- `isAdmin` is true when `UserType` is `""` or admin (repository line 128). Admins match `admin_display_status`; tenants match `tenant_display_status`.

**SQL: counts (live)**

Parameters:
- `$1` = leaseIDs, `$2` = propertyIDs, `$3` = tenant/company IDs
- `$4` = `{'pending proposal'}`
- `$5` = `{'contract sent'}` for admins, `{'pending contract'}` for tenants
- `$6` = `{'contract signed'}`
- `$7` = lease unit types, `$8` = proposal unit types
- `$9..` = region / mall / unique property

```sql
WITH
amendment_summary AS (
  SELECT ranked.lease_id,
    MAX(CASE WHEN ranked.amendment_type='Termination' THEN ranked.amendment_start END) AS termination_start_date,
    MAX(CASE WHEN ranked.amendment_type='Renewal'     THEN ranked.amendment_end   END) AS renewal_end_date,
    MAX(CASE WHEN ranked.amendment_type='HoldOver'    THEN ranked.amendment_start END) AS holdover_start_date
  FROM (SELECT lua.lease_id, lua.amendment_type, lua.amendment_start, lua.amendment_end,
               ROW_NUMBER() OVER (PARTITION BY lua.lease_id, lua.amendment_type ORDER BY lua.pms_amendment_id DESC NULLS LAST) rn
        FROM cenomi.leased_units_amendments lua
        WHERE lua.amendment_status='Activated' AND lua.amendment_type IN ('Termination','Renewal','HoldOver')) ranked
  WHERE ranked.rn = 1 GROUP BY ranked.lease_id),
effective_end_date_calc AS (
  SELECT l.lease_id, l.end_date AS original_end_date, l.contract_status,
         (ams.termination_start_date IS NOT NULL) has_active_termination, (ams.holdover_start_date IS NOT NULL) has_active_holdover,
         ams.termination_start_date, ams.holdover_start_date,
         (ams.renewal_end_date IS NOT NULL) has_active_renewal, ams.renewal_end_date
  FROM cenomi.leases l LEFT JOIN amendment_summary ams ON l.lease_id = ams.lease_id),
lease_classified AS (
  SELECT
    CASE WHEN LOWER(TRIM(COALESCE(l.admin_display_status,''))) = ANY($5::text[]) THEN 'contract'
         WHEN LOWER(TRIM(COALESCE(l.admin_display_status,''))) = ANY($6::text[]) THEN 'lease' END AS approval_type,
    CASE  -- d = date_part('days', (NOW() AT TIME ZONE 'asia/riyadh')::timestamp - l.pms_last_modified_at)::int
      WHEN d >= 0  AND d < 7  THEN '1 week delay'
      WHEN d >= 7  AND d < 14 THEN '2 week delay'
      WHEN d >= 14 AND d < 21 THEN '3 week delay'
      WHEN d >= 21 AND d < 31 THEN '1 month delay'
      WHEN d >= 31            THEN '1 month plus delay' END AS delay_by,
    p.region, p.marketing_name AS mall
  FROM cenomi.leases l
  JOIN cenomi.properties p ON l.property_id = p.property_id
  LEFT JOIN effective_end_date_calc eed ON l.lease_id = eed.lease_id
  WHERE ((cardinality($1::bigint[]) > 0 AND l.lease_id = ANY($1::bigint[]))
      OR (cardinality($1::bigint[]) = 0 AND cardinality($2::bigint[]) > 0 AND l.property_id = ANY($2::bigint[])))
    AND (cardinality($3::bigint[]) = 0 OR l.tenant_profile_id = ANY($3::bigint[]))
    AND (cardinality($7::text[]) = 0 OR LOWER(p.derived_unit_type) = ANY($7::text[]))
    AND (<display> = ANY($5::text[]) OR <display> = ANY($6::text[]))
    AND (<lease visibility rule, see below>)
    [AND LOWER(p.region) = LOWER($9)] [AND LOWER(p.marketing_name) = LOWER($n)] [AND p.unique_property_id = $n]),
lease_agg AS (
  SELECT approval_type, COUNT(*)::bigint total_count, delay_by, region, mall,
         MAX((NOW() AT TIME ZONE 'asia/riyadh')::timestamp) updated_at
  FROM lease_classified WHERE approval_type IS NOT NULL AND delay_by IS NOT NULL
  GROUP BY approval_type, delay_by, region, mall),
proposal_classified AS (
  SELECT <same 5-band CASE on pr.pms_created_at> AS delay_by, p.region, p.marketing_name AS mall
  FROM cenomi.proposals pr JOIN cenomi.properties p ON pr.property_id = p.property_id
  WHERE pr.property_id = ANY($2::bigint[])
    AND (cardinality($3::bigint[]) = 0 OR pr.tenant_profile_id = ANY($3::bigint[]))
    AND (cardinality($8::text[]) = 0 OR LOWER(p.derived_unit_type) = ANY($8::text[]))
    AND (LOWER(TRIM(COALESCE(pr.admin_display_status,''))) = ANY($4::text[]))
    AND (pr.pms_tenant_code IS NULL OR pr.pms_tenant_code NOT LIKE 'PREVIEW-%')
    [same region/mall/unique_property predicates, same $ numbers]),
proposal_agg AS (
  SELECT 'proposal'::text, COUNT(*)::bigint, delay_by, region, mall, MAX((NOW() AT TIME ZONE 'asia/riyadh')::timestamp)
  FROM proposal_classified WHERE delay_by IS NOT NULL GROUP BY delay_by, region, mall)
SELECT u.approval_type, u.total_count, u.delay_by, u.region, u.mall, u.updated_at
FROM (SELECT * FROM lease_agg UNION ALL SELECT * FROM proposal_agg) u
ORDER BY u.approval_type, u.delay_by, u.region, u.mall;
```
Tenants use `tenant_display_status` in place of `admin_display_status`.

**Lease visibility rule for admins** (`:280-311`). Let G = `LeaseGracePeriodDays` = 30. A lease is visible when:
- holdover and termination both exist: visible if holdover ≥ termination, otherwise if `NOW()::date <= termination + G`;
- renewal and termination both exist: visible if renewal_end > termination, otherwise if `NOW <= termination + 30`;
- holdover only: always visible;
- termination only: `NOW <= termination + G`;
- renewal only: `NOW <= renewal_end + G`;
- none of these: `end_date >= NOW` or `NOW <= end_date + G`.

For tenants, holdover means not visible; the other branches are the same.

**Status buckets:**
- `contract` = admin display status `Contract Sent` (tenant: `Pending Contract`).
- `lease` = `Contract Signed`.
- `proposal` = `Pending Proposal`.
- These match the frontend drill-down filters.

**Delay buckets:**
- Lease age is measured from `pms_last_modified_at`; proposal age from `pms_created_at`.
- Day bands are 0-6, 7-13, 14-20, 21-30 and ≥31.
- Negative ages (future timestamps) and NULL timestamps produce `delay_by` NULL, and those rows are dropped.

**SQL: filter lists.** These come from the **batch table** `r_pending_approvals_summary`, filled by the `pending_approval/delivery/sync` batch. Counts above are live, so the two can disagree.
```sql
SELECT ARRAY_AGG(DISTINCT mall) AS malls FROM cenomi.r_pending_approvals_summary
 [WHERE LOWER(region) = LOWER($1)] AND property_id = ANY($n);         -- mall/unique_id ignored (isFilter=true)
SELECT ARRAY_AGG(DISTINCT region) AS regions FROM cenomi.r_pending_approvals_summary WHERE property_id = ANY($1);
SELECT ARRAY_AGG(DISTINCT unique_property_id) FROM r_pending_approvals_summary
 [WHERE LOWER(region) = LOWER($1)] AND property_id = ANY($n);
```

**Post-processing:** none.
- Rows stay **per (type, delay_by, region, mall)**, so the frontend must sum across malls when no mall is selected.
- `count` is `omitempty`.
- `last_synced_at` is the `updated_at` of the last row = Riyadh wall-clock `NOW()` stored as a timestamp without time zone. It serialises with a `Z`, so it reads 3 hours ahead of real UTC.

**Response structs** (`domain/pendingApprovaldto.go`):
```go
type PendingApprovalResponse struct {
    Filters     PendingApprovalFilterDTO `json:"filters"`   // malls, regions []string; unique_property_ids []uint64
    LastSycedAt *time.Time               `json:"last_synced_at"`
    List        []PendingApprovalDTO     `json:"list"`
}
type PendingApprovalDTO struct {
    Type    string `json:"type"`               // proposal|contract|lease
    DelayBy string `json:"delay_by,omitempty"`
    Count   uint64 `json:"count,omitempty"`
    Region  string `json:"region,omitempty"`
    Mall    string `json:"mall,omitempty"`
}
```
```json
{"data":{"filters":{"malls":["Mall of Dhahran","Nakheel Mall"],"regions":["Eastern","Central"],"unique_property_ids":[101,204]},
 "last_synced_at":"2026-10-13T11:12:44Z",
 "list":[{"type":"contract","delay_by":"1 month plus delay","count":14,"region":"Central","mall":"Nakheel Mall"},
         {"type":"lease","delay_by":"1 week delay","count":2,"region":"Eastern","mall":"Mall of Dhahran"},
         {"type":"proposal","delay_by":"2 week delay","count":5,"region":"Central","mall":"Nakheel Mall"}]}}
```

---

#### 3. `GET /pending-amendments-summary` (Pending Amendments heatmap)

| Layer | Location |
|---|---|
| Route | `cenomi-api-2/pending_amendments/delivery/http/pending_amendments_handler.go:37` (wired at `app/main.go:4245-4247`) |
| Handler | `pending_amendments_handler.go:42` `FetchPendingAmendmentsSummary`; params parsed at `:89`; pivot at `:167` |
| Usecase | `cenomi-api-2/pending_amendments/usecase/pending_amendments_usecase.go:36` (filters and scope at `:76`) |
| Repository | `cenomi-api-2/leased_units_amendments/repository/postgres/leased_units_amendments_repository.go`: `FetchPendingAmendmentsSummary` at `:371`; WHERE builder `buildQueryConditions` at `:402`; SQL constant at `:102`; years at `:491`, malls at `:523`, regions/types at `:553` |
| Last sync | `cenomi-api-2/batch_execution_history/repository/postgres/batch_execution_history_repository.go:167` |

The `pending_amendments/repository/postgres` repository, which reads the `cenomi.pending_amendments` table, is wired but **not used** by this endpoint.

**Parameters:**
- `year` is required. A missing value, a non-integer or 0 → 400.
- `month` is matched against `TO_CHAR(...,'Mon')`, case-sensitive, e.g. `Jan`.
- `region` and `mall` are comma-split and lowercased.
- `unique_property_id` is comma-separated (multiple allowed).
- Pagination, sort and `filter_by` are parsed but unused by the summary.

**Scope** (`usecase:76-94`):
- `GetPermittedItems`. If the property override is unset and properties are non-empty, or the override is ALL → `PropertyIDs = accessibleItems.Properties`.
- If the override is NONE → `ErrUserHaveNoPermission`. The summary handler returns that as **500**; only the list handler maps it to 403.
- Otherwise there is no property predicate.

**SQL: counts**

Parameter order: status, unique IDs, mall, region, property IDs, year, month.
```sql
WITH lease_delays AS (
  SELECT amendment_type,
    CASE  -- d = date_part('days', (NOW() AT TIME ZONE 'asia/riyadh')::timestamp - la.pms_created_at)
      WHEN d >= 0  AND d < 7  THEN '1 week'
      WHEN d >= 7  AND d < 14 THEN '2 week'
      WHEN d >= 14 AND d < 21 THEN '3 week'
      WHEN d >= 21 AND d < 28 THEN '4 week'
      ELSE '4 week+' END AS delay_by            -- note: future-dated rows (d<0) also land in '4 week+'
  FROM cenomi.leased_units_amendments la
  LEFT JOIN cenomi.leases l ON l.lease_id = la.lease_id
  LEFT JOIN cenomi.properties p ON l.property_id = p.property_id
  WHERE amendment_status = ANY($1)                                  -- {'Ready','In Process'}
   [AND  p.unique_property_id = ANY($n)]
   [AND LOWER(p.marketing_name) = ANY($n)]                           -- mall CSV
   [AND LOWER(p.region) = ANY($n)]                                   -- region CSV
   [AND p.property_id = ANY($n)]                                     -- permission scope
    AND date_part('year', (la.pms_created_at AT TIME ZONE 'asia/riyadh')::timestamp) = $n
   [AND TO_CHAR((la.pms_created_at AT TIME ZONE 'asia/riyadh')::timestamp, 'Mon') = $n]
    AND la.pms_created_at IS NOT NULL
)
SELECT amendment_type, delay_by, COUNT(*) AS lease_count
FROM lease_delays GROUP BY delay_by, amendment_type;
```

**SQL: filters**
```sql
-- years (isFilter=true, isYearFilter=true → no unique_id/mall/year, but month IS still applied)
SELECT ARRAY_AGG(DISTINCT EXTRACT(YEAR FROM la.pms_created_at)) AS years   -- UTC year, not Riyadh
FROM cenomi.leased_units_amendments la LEFT JOIN cenomi.leases l ON l.lease_id = la.lease_id
LEFT JOIN cenomi.properties p ON l.property_id = p.property_id
WHERE amendment_status = ANY($1) [AND LOWER(p.region)=ANY($n)] [AND p.property_id=ANY($n)] [AND TO_CHAR(...,'Mon')=$n] AND la.pms_created_at IS NOT NULL;
-- malls + unique ids (isFilter=true → year/month/region/scope applied; mall/unique_id not)
SELECT ARRAY_AGG(DISTINCT p.marketing_name) malls, ARRAY_AGG(DISTINCT p.unique_property_id) unique_property_ids
FROM ...same joins... WHERE amendment_status = ANY($1) [region] [scope] AND date_part('year',...)=$n [month] AND la.pms_created_at IS NOT NULL;
-- regions + amendment types (scope only; no status filter)
SELECT ARRAY_AGG(DISTINCT p.region) regions, ARRAY_AGG(DISTINCT la.amendment_type) amendment_type
FROM ...same joins... [WHERE p.property_id = ANY($1)];
-- last sync
SELECT batch_name, batch_run_start_at, batch_run_end_at, batch_status, summary FROM batch_execution_history
WHERE batch_name = 'LEASED_UNITS_AMENDMENTS_SYNC_PHASE2' AND batch_status = TRUE ORDER BY batch_run_start_at DESC;  -- QueryRow → first row
```

**Post-processing** (handler `:167`):
- Rows are pivoted into one object per `amendment_type`. Delay strings map to fields: `1 week` → `one_week_delay`, … `4 week+` → `four_week_plus_delay`.
- Objects are **sorted alphabetically by amendment_type**, so "API order" in the frontend is alphabetical.
- Missing bands are 0.
- `last_synced_at` = `batch_run_end_at` of the latest successful `LEASED_UNITS_AMENDMENTS_SYNC_PHASE2` run, or null if there is none.
- The delay bands differ from pending-approval: here "4 week" is 21-27 days and "4 week+" is 28 days or more.

**Response structs** (`domain/pendingamendmentsdto.go:58-81`):
```go
type PendingAmendmentsResponse struct {
    Filters      PendingAmendmentsFilters `json:"filters"`  // malls, regions []string; unique_property_ids []uint64; years []int; amendment_types []string
    LastSyncedAt *time.Time               `json:"last_synced_at"`
    List         []AmendmentDelayDTO      `json:"list"`
}
type AmendmentDelayDTO struct {
    AmendmentType     string `json:"amendment_type"`
    OneWeekDelay      int    `json:"one_week_delay"`
    TwoWeekDelay      int    `json:"two_week_delay"`
    ThreeWeekDelay    int    `json:"three_week_delay"`
    FourWeekDelay     int    `json:"four_week_delay"`
    FourWeekPlusDelay int    `json:"four_week_plus_delay"`
}
```
```json
{"data":{"filters":{"malls":["Nakheel Mall"],"regions":["Central","Eastern"],"unique_property_ids":[204],"years":[2025,2026],
  "amendment_types":["Expansion","HoldOver","Renewal","Termination"]},
 "last_synced_at":"2026-10-13T02:00:41Z",
 "list":[{"amendment_type":"Renewal","one_week_delay":3,"two_week_delay":0,"three_week_delay":1,"four_week_delay":0,"four_week_plus_delay":12},
         {"amendment_type":"Termination","one_week_delay":0,"two_week_delay":2,"three_week_delay":0,"four_week_delay":1,"four_week_plus_delay":4}]}}
```

---

#### 4. `GET /service-request-summary` (Service Requests treemap)

| Layer | Location |
|---|---|
| Route | `cenomi-api-2/service_requests_summary/delivery/http/service_request_summary_handler.go:29` (wired at `app/main.go:4287-4289`) |
| Handler | `service_request_summary_handler.go:33` `FetchServiceRequestSummary` |
| Scope builder | `cenomi-api-2/servicerequest/usecase/service_request_usecase.go:1925` `FetchServiceRequestListIfTenantIDNotExists` (summary early-return at `:2008-2014`) → `cenomi-api-2/servicerequest/repository/service_request_repository.go:1737` `BuildServiceRequestQueryCondition` |
| Role scoping | `cenomi-api-2/servicerequest/usecase/contractor_list_access.go:149` `applyRoleScopedServiceRequestListAccessParams`; Soft FM part at `service_request_usecase.go:501` |
| Usecase | `cenomi-api-2/service_requests_summary/usecase/service_request_summary_usecase.go:35` |
| Repository | `cenomi-api-2/service_requests_summary/repository/postgres/service_request_summary_repository.go`: summary at `:191`, prefilter at `:172`, outer WHERE at `:113`, years at `:245`, regions/malls at `:274`, unique IDs at `:323` |

**Parameters:**
- `year` (uint), `month` (`jan`..`dec`, case-insensitive, via `constants.MonthCountMap`), `region`, `mall`, `unique_property_id` (string, passed as-is), `service_category` (CSV), `sub_category` (CSV), `start_date` / `end_date` (YYYY-MM-DD, Riyadh).
- **`unit_id` is ignored.** The legacy unit filter therefore has no effect on this endpoint.

**Scope** (handler `:52-109`). An `srFilter` is built with:
- `RoleIDs` and `UserPermissions` = the narrowed set from `PermissionCheck`;
- `Summary=true`, `YearExclude=true`, `CreatedFor=UserID`;
- `Roles` = the user's role names, **only if the user is INSPECTOR**.

`FetchServiceRequestListIfTenantIDNotExists` then:
1. Calls `GetPermittedItems` (built from UserID, RoleIDs and UserType only).
   - Lease override NONE or property override NONE → `ErrUserHaveNoPermission` → **500**.
   - Otherwise `leaseIDs = accessibleItems.Leases` and `propertyIDs = accessibleItems.Properties`.
   - Region, mall and unique property are **not** applied at this step for the summary; they are applied later on the outer query.
2. `PermissonCategory` is built from `VIEW_*` permissions via `constants.ServiceRequestPermissionMap` (`constants.go:5863`). `PermissonSubCategory` is built from `ServiceRequestSubPermissionMap` (`:5887`).
3. `applyRoleScopedServiceRequestListAccessParams`:
   - **Soft FM:** `CanViewSoftFmCategory` is true only with `VIEW_ALL_SERVICE_REQUEST`, because `Roles` is empty for non-Inspectors in the summary. As a result, Mall Manager, Operations and Soft FM Manager do **not** get Soft FM counts here, although they see them in the list.
   - **Facilities / RDD contractor category lock:** not applied in the summary, again because `Roles` is empty.
   - **Inspector:** `Category=[OPERATIONS]`, `SubCategory=[USER_JOURNEY_CHECKLIST]`.
4. Summary early return: `LeaseIDs` are kept, `UserID=0`, `GlobalAccess=true`, and only the WHERE clause plus its parameters are returned.

**Base WHERE `W`** (`BuildServiceRequestQueryCondition` with the summary parameters). Clauses in order, each only when its condition holds:
```sql
WHERE sr.category NOT IN ('SOFT_FM','SOFT_FM_CHECKLIST','SOFT_FM_AUDIT')            -- [admin && !CanViewSoftFm]
  AND sr.sub_category NOT IN ('HANDOVER','HANDED_OVER','FIT_OUT_CONFIRM_HO','FIT_OUT_CONFIRM_FOS','FIT_OUT_CONFIRM_END',
        'FIT_OUT_CONFIRM_TRADING','FITOUT_PROGRESS','CLOSE_CEILING_INSPECTION','OPEN_CEILING_INSPECTION',
        'PRE_OPENING_INSPECTION_MEP','PRE_OPENING_INSPECTION_ARCHITECTURAL')       -- [no VIEW_FITOUT_HANDOVER_CATEGORY / VIEW_ALL]
  AND sr.sub_category not in ('CLEANLINESS_CHECKLIST','WASHROOM_AND_ASSOCIATED_FACILITIES_CHECKLIST','PEST_CONTROL_CHECKLIST',
        'WASTE_MANAGEMENT_CHECKLIST','BICSC_COMPLIANCE_CHECKLIST','LANDSCAPE_CHECKLIST','USER_JOURNEY_CHECKLIST')
                                   -- [only if the user holds NONE of VIEW_MALL_OPENING/CLOSING/USER_JOURNEY_CHECKLIST;
                                   --  holding any one lifts the whole exclusion; entries in params.SubCategory are dropped from the list]
  AND sr.tenant_profile_id = $n                                                      -- [userData.TenantProfileID != 0]
  AND sr.category = ANY($n) AND sr.sub_category = ANY($n)                            -- [Inspector only]
  AND (sr.property_id = ANY($n) OR sr.property_ids && $n or sr.category in ('NEW_CUSTOMER','DEALS_FLOW'))  -- [propertyIDs non-empty]
  AND sr.updated_at >= $n  AND sr.updated_at <= $n                                   -- [start_date / end_date]
  AND (sr.lease_id = ANY($n) OR sr.service_request_id = ANY($n+1)                    -- $n+1 = nil CreatedServiceRequestIDs
       or sr.category in ('NEW_CUSTOMER','DEALS_FLOW'[, Soft FM cats if CanViewSoftFm]))  -- always (GlobalAccess=true)
  AND (sr.lease_id IS NULL OR sr.lease_id = 0)                                       -- [no leaseIDs but propertyIDs]
  AND NOT (sr.status = 'DRAFT' AND sr.created_by IS DISTINCT FROM $n)                -- always; $n = current user
```

**Consequences of the lease clause.** Because it is always present in the summary, any SR whose `lease_id` is not among the user's accessible leases is **excluded**, unless its category is NEW_CUSTOMER or DEALS_FLOW. That includes lease-less SRs such as HSE and mall-level work permits.
- This applies to super admins too. `VIEW_ALL_SERVICE_REQUEST` only stops the handler from skipping the query (`handler:142`).
- The skip guard never fires anyway, because the DRAFT clause always adds a parameter, so the WHERE clause is never empty.

**SQL: summary** (`FetchServiceRequestSummary`)
```sql
WITH service_request_summary AS (
  SELECT category, sub_category,
    COUNT(CASE WHEN status IN ('APPROVED','ACTIVE') THEN 1 END) AS approved,
    COUNT(CASE WHEN status IN ('IN_PROCESS','IN_PROGRESS','ACTION_REQUIRED','SUBMITTED','RE_SUBMITTED','REVIEWED_WITH_COMMENTS') THEN 1 END) AS in_process,
    COUNT(CASE WHEN status = 'PENDING' THEN 1 END) AS pending,
    COUNT(CASE WHEN status = 'REJECTED' THEN 1 END) AS rejected,
    COUNT(CASE WHEN status IN ('CLOSED','EXPIRED','COMPLETED','CANCELLED') THEN 1 END) AS closed,
    EXTRACT(YEAR  FROM MAX(sr.created_at AT TIME ZONE 'asia/riyadh')) AS summary_year,
    EXTRACT(MONTH FROM MAX(sr.created_at AT TIME ZONE 'asia/riyadh')) AS summary_month,
    sr.property_id, p.marketing_name AS mall, p.region AS region, p.unique_property_id
  FROM cenomi.service_request sr
  LEFT JOIN cenomi.properties p ON p.property_id = sr.property_id
  <W, or " WHERE TRUE" if empty>
    AND sr.category = ANY($c)                                                         -- [service_category] push-down
    AND sr.created_at >= make_timestamptz($y,1,1,0,0,0,'Asia/Riyadh')
    AND sr.created_at <  make_timestamptz($y+1,1,1,0,0,0,'Asia/Riyadh')              -- [year] push-down
  GROUP BY category, sub_category, sr.property_id, p.marketing_name, p.region, p.unique_property_id,
           EXTRACT(YEAR FROM sr.created_at AT TIME ZONE 'asia/riyadh'), EXTRACT(MONTH FROM sr.created_at AT TIME ZONE 'asia/riyadh'))
SELECT category, sub_category, SUM(in_process), SUM(approved), SUM(pending), SUM(rejected), SUM(closed), summary_year
FROM service_request_summary
 WHERE summary_year = $n            -- [year]
   AND region = $n                  -- [region]  exact, case-sensitive (pending-* endpoints use LOWER())
   AND mall = $n                    -- [mall]    exact marketing_name
   AND summary_month = $n           -- [month]
   AND unique_property_id = $n      -- [unique_property_id] (string bound to bigint column)
   AND category = ANY($n)           -- [service_category]
   AND sub_category = ANY($n)       -- [sub_category]
 group by category, sub_category, summary_year
 ORDER BY category, sub_category;
```
- Region, mall and unique property apply to `properties` joined by `sr.property_id` only. SRs whose mall is held only in `property_ids` or in the lease's property get NULL `p.*` and drop out when those filters are set.
- Statuses outside the five buckets are counted nowhere: REPORT_SUBMITTED, DOCUMENT_UPLOADED, RE_EXAMINE, REQUESTED_*, and the user's own DRAFTs.

**SQL: filters** (the same `W` is reused; none of them apply year/month/region)
```sql
SELECT DISTINCT EXTRACT(YEAR FROM sr.created_at AT TIME ZONE 'asia/riyadh')::int AS summary_year
FROM cenomi.service_request sr <W> [AND sr.property_id = ANY($n)] ORDER BY summary_year;   -- $n from a 2nd GetPermittedItems call
SELECT ARRAY_AGG(DISTINCT p.region)            FROM cenomi.service_request sr LEFT JOIN cenomi.properties p ON p.property_id = sr.property_id <W> AND p.region IS NOT NULL;
SELECT ARRAY_AGG(DISTINCT p.marketing_name)    FROM ... <W> AND p.marketing_name IS NOT NULL;
SELECT ARRAY_AGG(DISTINCT p.unique_property_id) FROM ... <W> AND p.unique_property_id IS NOT NULL;
```

**Post-processing and caching:**
- There is no caching.
- Rows are **per (category, sub_category, summary_year)**. When no year is selected, the same sub_category appears once per year, which is why the frontend merges rows per sub_category.
- `last_synced_at` is **always null**: `UpdatedAt` is never selected or scanned (`domain/servicerequestsummary_dao.go:28`).
- The batch tables in `service_request_summary_sync_repository.go` are not read by this endpoint.

**Response structs** (`domain/servicerequestsummary_dto.go`):
```go
type ServiceRequestSummaryResponse struct {
    FilterData FilterDTO                  `json:"filters"`        // years []int, malls/regions []string, unique_property_ids []int (all omitempty)
    UpdatedAt  *time.Time                 `json:"last_synced_at"`
    List       []ServiceRequestSummaryDTO `json:"list"`
}
type ServiceRequestSummaryDTO struct {
    Category    string `json:"service_category"`
    SubCategory string `json:"sub_category"`
    InProcess   int    `json:"in_process"`
    Approved    int    `json:"approved"`
    Closed      int    `json:"closed"`
    Pending     int    `json:"pending"`
    Rejected    int    `json:"rejected"`
}
```
```json
{"data":{"filters":{"years":[2024,2025,2026],"malls":["Nakheel Mall"],"regions":["Central"],"unique_property_ids":[204]},
 "last_synced_at":null,
 "list":[{"service_category":"COMPLAINTS","sub_category":"CLEANLINESS","in_process":4,"approved":11,"closed":2,"pending":0,"rejected":1},
         {"service_category":"WORK_PERMIT","sub_category":"CONSTRUCTION_HOT_WORK","in_process":9,"approved":30,"closed":17,"pending":0,"rejected":3}]}}
```

---

#### 5. `GET /service-requests` (list drill-down from the SR tile)

| Layer | Location |
|---|---|
| Route | `cenomi-api-2/servicerequest/delivery/http/service_request_handler.go:158` (wired at `app/main.go:2341` inside `registerPrivateRoutes`) |
| Handler | `service_request_handler.go:280` `List`; params parsed at `:524` `newServiceRequest`; user context at `:411`; SLA summary at `:765` |
| Usecase | `cenomi-api-2/servicerequest/usecase/service_request_usecase.go:1332` `ListAllServiceRequests` → admin path `:1925` `FetchServiceRequestListIfTenantIDNotExists`; tenant path `:1529` |
| Repository | `cenomi-api-2/servicerequest/repository/service_request_repository.go`: `GetServiceRequestsCount` at `:1420`, `ListAllServiceRequests` at `:1437`, `ListServiceRequestIDs` at `:1686`, `BuildServiceRequestQueryCondition` at `:1737`; SELECT constant at `:237`; ORDER BY at `servicerequest/repository/service_request_sla.go:150`; SLA summary at `service_request_sla.go:479`; role-ID query at `cenomi-api-2/service_request_operation/repository/service_request_operation_repository.go:778` (SQL at `:97`) |

**Parameters used by the dashboard modal:** `year`, `month` (`Jan`..`Dec`, case-sensitive map), `region`, `unique_property_id`, `service_category`, `sub_category`, `status=APPROVED,IN_PROCESS,REJECTED`, `page`, `limit`, `sort_by=updated_at`, `order=DESC`, and `search`.

Other supported parameters:
- `mall`, `brand`, `tenant_profile_id`, `self`, `property_id`, `lease_id`
- `start_date` / `end_date`: the range may not exceed 90 days
- `unit_id`: requires `unique_property_id`
- `document_status`, `source=WIDGET`, `sla_status`, `escalation_level`, `pending_over_hours`, `disable_pagination`

Defaults are page 1 and limit 10. `sort_by` is whitelisted (`:1522`); `order` must be ASC or DESC.

**User context:** `RoleIDs` and `UserPermissions` are narrowed by `PermissionCheck` to the roles granting `SERVICE_REQUEST_LIST | VIEW_MARKETING_CONTENT | VIEW_ISSUE_LOD_SR`. `Roles` = all role names plus `RoleName`. `ExcludeArchivedAgeFinalFromMainList` is true unless the user has `VIEW_ARCHIVED_SERVICE_REQUEST`.

**Admin path** (`:1925-2211`):
1. `GetPermittedItems` → lease and property IDs. Override NONE → `ErrUserHaveNoPermission` → **401**.
2. If `mall`, `region` or `unique_property_id` is set: `propertyRepo.FetchPropertyByFilters` (`property/repository/postgres/property_repository.go:1100`, WHERE `unique_property_id = $ AND marketing_name = $ AND LOWER(region) = LOWER($)`). Then `propertyIDs = CommonElements(propertyIDs, matched)`.
   - **Edge case:** if the user had no property scope, the intersection is empty and the property predicate disappears entirely.
3. `PermissonCategory` and `PermissonSubCategory` are derived from `VIEW_*` permissions. Then `applyRoleScopedServiceRequestListAccessParams` runs, and it **is** effective here because `Roles` is populated:
   - **Soft FM:** visible to SOFT_FM_MANAGER, HEAD_OF_FM, MALL_MANAGER, OPERATIONS, SUPER_ADMIN and VIEW_ALL. Soft FM Manager is forced onto Soft FM categories only.
   - **Facilities contractor / RDD contractor:** `Category` is intersected with categories allowed by their `VIEW_*` permissions. The fallback is WORK_PERMIT, or FIT_OUT_AND_HANDOVER plus FIT_OUT_DRAWING. A disallowed request → `__CATEGORY_RESTRICTED_NO_MATCH__`, which returns 0 rows.
   - **Inspector:** forced to OPERATIONS / USER_JOURNEY_CHECKLIST.
4. **SR-ID candidates** (role- and assignee-based):
   ```sql
   SELECT ARRAY_AGG(DISTINCT s.service_request_id)
   FROM service_request_operation s JOIN cenomi.service_request sr ON sr.service_request_id = s.service_request_id
   WHERE ((s.assigned_role = ANY($1) OR s.assigned_user_id = $4 OR sr.category = ANY($5)))   -- $5 only if PermissonCategory != nil
     AND (sr.lease_id = ANY($2) OR sr.lease_id IS NULL OR sr.category = 'HSE')
     AND (sr.property_id = ANY($3) OR sr.property_ids && $3);
   ```
   The user's own SRs and property-level lease-less SRs come from `ListServiceRequestIDs`:
   ```sql
   SELECT ARRAY_AGG(sr.service_request_id) FROM cenomi.service_request sr
   WHERE NOT (sr.status = 'DRAFT' AND sr.created_by IS DISTINCT FROM $1 [AND sr.category NOT IN (<soft fm>)])
     AND ( sr.created_by = $2
           OR ((sr.property_id = ANY($3) OR sr.property_ids && $3) AND (sr.lease_id IS NULL OR sr.lease_id = 0)) );
   ```
   Without `VIEW_ALL_SERVICE_REQUEST`, and unless this is a fit-out widget request:
   - `ServiceRequestIDs` = the union of both sets;
   - an empty union returns an empty list immediately.
5. Then `CreatedFor=user`, `UserID=0`, `CreatedServiceRequestIDs` = own and property SRs, and `GlobalAccess=true`. Count and list run concurrently in an errgroup.

**WHERE `W`** (`BuildServiceRequestQueryCondition`) for the dashboard modal request:
```sql
WHERE sr.service_request_id = ANY($1)                                   -- [non-VIEW_ALL: role/assignee/own SR IDs]
  AND sr.category NOT IN ('SOFT_FM','SOFT_FM_CHECKLIST','SOFT_FM_AUDIT') -- [!CanViewSoftFm]
  AND sr.sub_category NOT IN (<handover family>)                        -- [no VIEW_FITOUT_HANDOVER_CATEGORY]
  AND sr.sub_category not in (<checklists not explicitly requested>)    -- [no checklist view perm]
  AND sr.category = ANY($n)                                             -- service_category (after role intersection)
  AND sr.sub_category = ANY($n)                                         -- sub_category
  AND sr.status = ANY($n)   -- status expanded by expandStatusFiltersForSummarySync (:104):
                            -- APPROVED→{APPROVED,ACTIVE}; IN_PROCESS→{IN_PROCESS,IN_PROGRESS,ACTION_REQUIRED,SUBMITTED,RE_SUBMITTED,REVIEWED_WITH_COMMENTS};
                            -- REJECTED→{REJECTED}; CLOSED→{CLOSED,EXPIRED,COMPLETED,CANCELLED}; + REPORT_SUBMITTED when APPROVED & an inspection sub_category;
                            -- fit-out categories: COMPLETED → {APPROVED,REJECTED,COMPLETED}; PENDING/WIDGET variants use NOT IN (…)
  AND (sr.property_id = ANY($p) OR sr.property_ids && $p OR sr.service_request_id = ANY($own) OR sr.category in ('NEW_CUSTOMER','DEALS_FLOW'))
                            -- [propertyIDs; fit-out WIDGET / handover-alignment scope uses property-only form]
  AND EXTRACT(YEAR  FROM sr.created_at AT TIME ZONE 'asia/riyadh') = $n -- [year]
  AND EXTRACT(MONTH FROM sr.created_at AT TIME ZONE 'asia/riyadh') = $n -- [month, skipped when status = single 'PENDING']
  AND sr.updated_at >= $n AND sr.updated_at <= $n                       -- [start/end date]
  AND NOT (sr.status IN ('APPROVED','REJECTED') AND sr.updated_at < (NOW() - INTERVAL '90 days'))  -- [no VIEW_ARCHIVED_SERVICE_REQUEST]
  AND (COALESCE(sr.payload->>'mall','') = $m OR …payload mall_name/property_name… OR EXISTS(properties by property_id/property_ids
       with marketing_name|marketing_name_ar = $m) OR EXISTS(leases→properties …))                  -- [mall]
  AND <self EXISTS (IN_PROGRESS op for my role/user) OR my bounced-back/draft>                       -- [self=true]
  AND (sr.lease_id = ANY($l) OR sr.service_request_id = ANY($own) or sr.category in ('NEW_CUSTOMER','DEALS_FLOW'[,soft fm]))
                                                                        -- [always for admins, except fit-out WIDGET/alignment scope]
  AND (sr.lease_id IS NULL OR sr.lease_id = 0)                          -- [no lease IDs but property IDs]
  AND (sr.service_request_id::TEXT = $s OR sr.title ILIKE $sl OR payload brand/brand_name/mall/lease/lease_brand_mall ILIKE $sl
       OR EXISTS(leases/brands/properties: pms_tenant_code|lease_brand_mall|brand_name|marketing_name ILIKE $sl))  -- [search]
  AND NOT (sr.status = 'DRAFT' AND sr.created_by IS DISTINCT FROM $u [AND sr.category NOT IN (<soft fm>)])        -- always
  AND srs.status = ANY($n) AND COALESCE(srs.escalation_level, sr.sla_escalation_level, 0) = ANY($n)
  AND COALESCE(srs.pending_hours,0) >= $n                               -- [SLA filters]
```
Two further optional predicates: `unit_id` adds `fitoutdrawing.UnitFilterClause` (`internal/fitoutdrawing/document_status.go:68`), which matches `payload->>'unit_code' ILIKE` or `leased_units → units.pms_unit_code / unit_id`. `tenant_profile_id`, `lease_id`, `property_id` and `brand` add simple equality predicates.

**SQL: count / page / SLA summary**
```sql
SELECT COUNT(sr.service_request_id) FROM cenomi.service_request sr
  LEFT JOIN cenomi.service_request_sla srs ON srs.service_request_id = sr.service_request_id  <W>;

SELECT sr.service_request_id, sr.tenant_profile_id, tp.company_name, sr.property_id, sr.category, sr.sub_category, sr.title, sr.payload,
       sr.status, sr.document_id, sr.workflow_id, sr.created_at, sr.updated_at, sr.deleted_at, sr.created_by, sr.updated_by, sr.deleted_by,
       CONCAT(cru.first_name,' ',cru.last_name), CONCAT(upu…), CONCAT(dpu…), sr.pms_post_status, sr.pms_post_log, sr.lease_id,
       COALESCE(NULLIF(sr.payload->>'lease',''), l.pms_tenant_code, '') AS lease_code,
       COALESCE(NULLIF(sr.payload->>'brand',''), NULLIF(sr.payload->>'brand_name',''), b.brand_name, '') AS brand,
       COALESCE(NULLIF(sr.payload->>'mall',''), p.marketing_name, '') AS mall,
       COALESCE(NULLIF(sr.payload->>'lease_brand_mall',''), NULLIF(l.lease_brand_mall,''), <CONCAT_WS lease - brand - mall>) AS lease_brand_mall,
       sr.created_for, CONCAT(cfu…), sr.property_ids, sr.notify_roles,
       srs.status, srs.policy_id, srs.priority, srs.target_hours, srs.elapsed_hours, srs.remaining_hours, srs.consumed_pct, srs.due_at,
       srs.breached_at, srs.paused_since, srs.pending_since, srs.pending_hours, srs.pending_with_role, srs.pending_with_role_en,
       srs.pending_with_role_ar, srs.pending_workflow_level, srs.escalation_level, srs.escalated_at, srs.escalated_to_role, srs.escalated_to_role_ar
FROM cenomi.service_request sr
  LEFT JOIN tenant_profiles tp ON sr.tenant_profile_id = tp.tenant_profile_id
  LEFT JOIN users cru ON cru.user_id = sr.created_by   LEFT JOIN users upu ON upu.user_id = sr.updated_by
  LEFT JOIN users dpu ON dpu.user_id = sr.deleted_by   LEFT JOIN users cfu ON cfu.user_id = sr.created_for
  LEFT JOIN cenomi.leases l ON l.lease_id = sr.lease_id LEFT JOIN cenomi.brands b ON b.brand_id = l.brand_id
  LEFT JOIN cenomi.properties p ON p.property_id = COALESCE(NULLIF(sr.property_id,0), l.property_id)
  LEFT JOIN cenomi.service_request_sla srs ON srs.service_request_id = sr.service_request_id
<W>
ORDER BY COALESCE(sr.updated_at, sr.created_at) DESC, sr.service_request_id DESC     -- sort_by=updated_at&order=DESC
LIMIT 10 OFFSET 0;                                                                   -- literal values, not bind params

SELECT COUNT(*) FILTER (WHERE srs.status='on_track'), …'at_risk', …'overdue', …'paused', …'met',
       COUNT(*) FILTER (WHERE srs.status='not_applicable' OR srs.status IS NULL)
FROM cenomi.service_request sr LEFT JOIN cenomi.service_request_sla srs ON … <W built with SLAStatus=nil>;
```
The SLA summary reuses the same `request` pointer that the usecase has already mutated, so it carries the same scope.

**Go post-processing** (`:2075-2210`):
- `serviceRequestOperationRepository.List(ids)` loads the operations.
- `userRepo.FetchUserInfoByUserIDs` loads creators, updaters and operators.
- `roleRepository.FetchRoleInfoByRoleIDs`.
- `enrichHSEObservationApproversFromHistory`.
- For FIT_OUT_DRAWING and WORK_PERMIT rows: **one `GetServiceRequestOperationHistory` query per SR** (N+1), plus an extra user lookup. Work-permit rows also get `fillWorkPermitListHistoryRoles`.
- `tenantProfileRepo.FetchTenantProfileByIDs` fills `company_name`.
- `stripSoftFmAuditChildrenFromListPayload`.
- `applySLAToListDTO` copies the stored SLA snapshot, cloned in a reduced form for tenants. There is **no SLA calculation at request time**: snapshots in `service_request_sla` are written by the SLA refresh scheduler.
- There are no external HTTP calls and no caching.

**Counts can differ from the summary tile.** On the same filters the list can return a different number from the tile because:
1. it applies role, assignee and own-SR ID scoping for non-VIEW_ALL users;
2. it hides APPROVED and REJECTED SRs older than 90 days unless the user has `VIEW_ARCHIVED_SERVICE_REQUEST`;
3. it applies Soft FM and contractor role scoping, where the summary ignores it;
4. it is gated by a different path-permission role set (`SERVICE_REQUEST_LIST` versus `SERVICE_REQUEST_SUMMARY`/`WIDGET`);
5. it matches region, mall and unique property through `FetchPropertyByFilters` (`LOWER(region)`), where the summary uses exact `p.region = $`.

**Response structs** (`domain/serviceRequestdto.go:41, :286`; `domain/service_request_sla.go:63`):
```go
type ListServiceRequestResponse struct {
    CurrentPage    uint32                      `json:"current_page"`
    TotalCount     uint32                      `json:"total_count"`
    GuidelinesLink string                      `json:"guidelines_link"`   // "" for admins
    Limit          uint32                      `json:"limit"`
    List           []ServiceRequestListItemDTO `json:"list"`
    SLASummary     *ServiceRequestSLASummary   `json:"sla_summary,omitempty"` // on_track, at_risk, overdue, paused, met, not_applicable
}
type ServiceRequestListItemDTO struct {
    ID string `json:"service_request_id"`; TenantProfileID uint64 `json:"tenant_profile_id,omitempty"`; CompanyName string `json:"company_name"`
    PropertyID uint64 `json:"property_id,omitempty"`; Category string `json:"service_category"`; SubCategory string `json:"sub_category"`
    Title string `json:"title"`; CreatedAt *time.Time `json:"created_at,omitempty"`; CreatedByString string `json:"created_by,omitempty"`
    UpdatedByString string `json:"updated_by,omitempty"`; CreatedBy uint64 `json:"created_by_id,omitempty"`; UpdatedBy uint64 `json:"updated_by_id,omitempty"`
    CreatedFor uint64 `json:"created_for_id,omitempty"`; Payload json.RawMessage `json:"payload"`; Status string `json:"status"`
    WorkFlowID uint64 `json:"workflow_id,omitempty"`; Operations []ServiceRequestOperationsDTO `json:"operations"`
    UpdatedAt *time.Time `json:"updated_at,omitempty"`; LeaseID uint64 `json:"lease_id"`; LeaseCode string `json:"lease_code"`
    Brand string `json:"brand"`; Mall string `json:"mall"`; LeaseBrandMall string `json:"lease_brand_mall"`
    CreatedForString string `json:"created_for,omitempty"`; DocumentStatus string `json:"document_status"`; UserAction string `json:"user_action"`
    Comment string `json:"comment"`; PropertyIDs []uint64 `json:"property_ids,omitempty"`
    OperationHistory []ServiveRequestOperationHistoryDTO `json:"operation_history,omitempty"`; SLA *ServiceRequestSla `json:"sla"`
    // (DeletedByString / DeletedBy also present, omitempty)
}
```
```json
{"data":{"current_page":1,"total_count":42,"guidelines_link":"","limit":10,
 "list":[{"service_request_id":"318822","tenant_profile_id":5531,"company_name":"Alpha Retail Co","property_id":77,
   "service_category":"WORK_PERMIT","sub_category":"CONSTRUCTION_HOT_WORK","title":"Hot work - unit G12","created_at":"2026-10-02T07:15:00Z",
   "created_by":"Sara A","updated_by":"Omar K","created_by_id":901,"updated_by_id":455,"payload":{"unit_code":"G12"},"status":"IN_PROCESS",
   "workflow_id":12,"operations":[{"assigned_role":31,"workflow_level":1,"status":"IN_PROGRESS"}],"updated_at":"2026-10-09T10:01:00Z",
   "lease_id":8812,"lease_code":"t0012345","brand":"Alpha","mall":"Nakheel Mall","lease_brand_mall":"t0012345 - Alpha - Nakheel Mall",
   "document_status":"","user_action":"","comment":"",
   "sla":{"status":"at_risk","priority":"low","target_hours":48,"elapsed_hours":40.5,"remaining_hours":7.5,"consumed_pct":84,"due_at":"2026-10-11T07:15:00Z",
          "pending_with":{"role":"MALL_MANAGER","role_name_en":"Mall Manager","workflow_level":1}}}],
 "sla_summary":{"on_track":20,"at_risk":6,"overdue":9,"paused":0,"met":5,"not_applicable":2}}}
```
The `operations[]` and `sla` field names in this example are indicative. See `ServiceRequestOperationsDTO` and `domain.ServiceRequestSla` for the exact tags.

---

#### 6. `GET /units-with-fitout` (legacy SR card unit filter)

| Layer | Location |
|---|---|
| Route | `cenomi-api-2/fitout_summary/delivery/http/fitout_summary_handler.go:119` (wired at `app/main.go:4311-4313`) |
| Handler | `fitout_summary_handler.go:882` `FetchUnitsWithFitout` |
| Usecase | `cenomi-api-2/fitout_summary/usecase/fitout_summary_usecase.go:417` (pass-through) |
| Repository | `cenomi-api-2/fitout_summary/repository/postgres/fitout_summary_repository.go:2344`; WHERE builder at `:2319`; SQL `unitsWithFitoutQuery` at `:966` |

**Parameters:**
- `property_id` is **required**: missing → 400 "Please select a Mall first", non-uint → 400. Despite its name it is treated as a **`unique_property_id`**.
- `region` is parsed and then ignored.
- `unique_property_id` is optional and is ANDed on the same column.

**Scoping:** no permission or property scoping, and the path-permission check is skipped. Any admin can list any mall's units.

**SQL**
```sql
WITH all_property_ids AS (
  SELECT DISTINCT p.property_id FROM cenomi.properties p
  WHERE 1=1 AND unique_property_id = $1 [AND unique_property_id = $2]   -- $1 = ?property_id, $2 = ?unique_property_id
),
latest_lease_for_unit AS (
  SELECT DISTINCT ON (lu.unit_id) lu.unit_id, lu.lease_id
  FROM cenomi.leased_units lu LEFT JOIN cenomi.leases l ON l.lease_id = lu.lease_id
  ORDER BY lu.unit_id, l.created_at DESC NULLS LAST, lu.start_date DESC NULLS LAST, lu.created_at DESC NULLS LAST
)
SELECT DISTINCT u.unit_id, u.pms_unit_code, u.unit_type, u.property_id, p.marketing_name AS mall, p.region,
       l.lease_id, l.pms_tenant_code AS lease_code, tp.company_name
FROM cenomi.units u
JOIN all_property_ids api ON api.property_id = u.property_id
LEFT JOIN latest_lease_for_unit llfu ON llfu.unit_id = u.unit_id
LEFT JOIN cenomi.leases l ON l.lease_id = llfu.lease_id
LEFT JOIN cenomi.properties p ON p.property_id = u.property_id
LEFT JOIN cenomi.tenant_profiles tp ON tp.tenant_profile_id = l.tenant_profile_id
ORDER BY u.unit_id;
```

**Notes:**
- Despite its name and comments, the query does **not** check for any FIT_OUT_AND_HANDOVER or FIT_OUT_DRAWING service request. It returns **every unit** in the mall, each with its latest lease.
- `latest_lease_for_unit` scans the whole `leased_units` table (all malls) before the join.
- **Post-processing:** the response `region` is taken from the first unit.
- The `unit_id` the frontend then sends to `service-request-summary` is ignored there (see §4). It does filter `service-requests`, which requires `unique_property_id` alongside it.

**Response structs** (`domain/fitoutdto.go:351-367`):
```go
type UnitsWithFitoutResponse struct {
    List   []UnitsWithFitoutDTO `json:"list"`
    Region string               `json:"region,omitempty"`
}
type UnitsWithFitoutDTO struct {
    UnitID uint64 `json:"unit_id"`; UnitCode string `json:"unit_code"`; UnitType string `json:"unit_type"`; PropertyID uint64 `json:"property_id"`
    Mall string `json:"mall"`; Region string `json:"region"`; LeaseID uint64 `json:"lease_id"`; LeaseCode string `json:"lease_code"`; CompanyName string `json:"company_name"`
}
```
```json
{"data":{"list":[{"unit_id":55102,"unit_code":"G-012","unit_type":"STORE","property_id":77,"mall":"Nakheel Mall","region":"Central",
  "lease_id":8812,"lease_code":"t0012345","company_name":"Alpha Retail Co"},
 {"unit_id":55103,"unit_code":"G-013","unit_type":"KIOSK","property_id":77,"mall":"Nakheel Mall","region":"Central","lease_id":0,"lease_code":"","company_name":""}],
 "region":"Central"}}
```

---

#### Findings and gaps

**Behaviour that looks like bugs:**
- **No backend widget-permission enforcement.** `SkipPermissionCheck` (`app/main.go:4590`) means `pending-approval`, `pending-amendments-summary`, `lease-requests-summary` and `units-with-fitout` never check path permissions, even though `pathpermission.json` lists `PENDING_APPROVALS` for one of them.
- **Random unit-type lock.** `lease-requests-summary` resolves `UnitTypeRoleMap` by Go map iteration, so `REGIONAL_LEASING_MANAGER_STORE` users get `store` or `office` at random on each request.
- **`service-request-summary`:**
  - `last_synced_at` is always null.
  - `unit_id` is ignored.
  - Soft FM and contractor role scoping are not applied, because `Roles` is set only for Inspectors.
  - The lease clause drops lease-less SRs for every user, super admins included.
  - Region and mall matching is case-sensitive.
  - Status buckets leave REPORT_SUBMITTED, DOCUMENT_UPLOADED and similar statuses uncounted.
- **`pending-approval`:**
  - Counts are live, but the filter lists come from the batch table `r_pending_approvals_summary`.
  - `last_synced_at` is Riyadh wall clock serialised as UTC, so it reads 3 hours ahead.
  - Rows are returned per mall, not aggregated.
  - Empty property scope gives 500.
- **`pending-amendments-summary`:**
  - The year list uses the UTC year and is narrowed by `month`.
  - The ELSE branch puts future-dated rows into "4 week+".
  - Permission errors give 500.
  - The repository reading `cenomi.pending_amendments` is wired but unused.
- **`units-with-fitout`** does not filter for fit-out SRs and is not permission-scoped.

**Not traced:**
- The exact SQL inside `GetPermittedItems` → `resolveAdminAccessiblePropertyIDs`, `FetchPropertyAccessRows`, `FetchLeaseIDsByPropertyIDs*` and `FetchProposalIdsByLeaseIDs`. These are summarised in Shared building blocks only.
- The exact JSON tags of `ServiceRequestOperationsDTO`, `ServiveRequestOperationHistoryDTO` and `ServiceRequestSla`.
- The tenant path of `/service-requests` (`fetchServiceRequestListForTenant`), which the admin dashboard does not use.
- The SLA snapshot refresh job (`service_request_sla_snapshot.go`, `service_request_sla_escalation.go`), which writes `service_request_sla`.
- Whether pgx binds the string `unique_property_id` in the service-request summary to the bigint column without error. This was not verified at runtime.
- Nothing was verified against a live database; all row counts and values in the JSON examples are illustrative.

---

## 4. Admin Dashboard — Fit-out, Document Status & Unit Discrepancy Cards

Scope: V2 card ids `fitoutHandover`, `fitoutDrawings`, `documentStatus`, `unitDiscrepancy` and their legacy equivalents on `/dashboard` (admin users).

- Page: `cenomi-frontend-2/apps/cenomi-tenant-web/app/(state)/(main)/dashboard/page.tsx` renders `AdminDashboardV2` when the UI v2 flag is on, otherwise legacy `AdminDashboard`.
- V2 shell: `cenomi-frontend-2/libs/ui-web/src/lib/components/dashboards/admin/v2/AdminDashboardV2.tsx`
- Legacy shell: `cenomi-frontend-2/libs/ui-web/src/lib/components/dashboards/admin/adminDashboard.tsx`

**RDD check:** `RddDashboard` and `RddDocs` are not rendered from the admin dashboard. They live on the separate page `apps/cenomi-tenant-web/app/(state)/(main)/dashboard/rdd/page.tsx`, so they are out of scope here.

**Chart components not used by these cards:** `FitoutBarChart`, `groupedStackedBarChart`, `doughNutChart` and `SpiralChart` are not imported by any card in scope. `groupedStackedBarChart` belongs to ServiceRequests, `doughNutChart` to LeaseRequest and `SpiralChart` to Approvals.

---

### 0. Shared plumbing

#### 0.1 HTTP client
- Every call goes through `httpRequest(url, body, method, cache, headers, fromStaging)` in `cenomi-frontend-2/libs/api/src/lib/API_Handler/API_Handler.ts:2`.
- It calls `fetch(`${NEXT_PUBLIC_API_BASE_PATH}/${url}`)` with `credentials: 'include'` and the session cookie, straight to the Go API. No Next BFF route is involved.
- It adds `x-active-tenant-profile-id` only for TENANT users.
- The `fromStaging` argument is ignored.

#### 0.2 Endpoint constants
All in `cenomi-frontend-2/libs/api/src/lib/endPoints.ts`:

| Constant | Path | Line |
|---|---|---|
| `FITOUT_SUMMARY_ADMIN` | `fitout-summary` | 283 |
| `FITOUT_DRAWING_DOCUMENT_STATUS_BY_MALL` | `fitout-drawing-document-status-summary/by-mall` | 288 |
| `FITOUT_DRAWING_DOCUMENT_STATUS_BY_DOCUMENT_TYPE` | `fitout-drawing-document-status-summary/by-document-type` | 286 |
| `UNIT_FITOUT_STATUS_ENDPOINT` | `unit-fitout-status` | 321 |
| `UNITS_WITH_FITOUT_ENDPOINT` | `units-with-fitout` | 322 |
| `SERVICE_REQUEST_ENDPOINT` | `service-requests` | 36 |
| `DISCREPANCY_MONTHLY_GRAPH` | `discrepancy/monthly-graph` | 56 |
| `DISCREPANCY_MONTHLY_GRAPH_MISMATCH_UNITS` | `discrepancy/monthly-graph/mismatch-units` | 57 |

#### 0.3 Backend route registration
- `cenomi-api-2/app/main.go:4313` calls `NewFitoutSummaryHandler`, which registers the routes at `cenomi-api-2/fitout_summary/delivery/http/fitout_summary_handler.go:114-122`.
- `cenomi-api-2/app/main.go:2266` calls `NewDiscrepancyHandler`, which registers the routes at `cenomi-api-2/discrepancy/delivery/http/discrepancy_handler.go:29-37`.
- `cenomi-api-2/app/main.go:2341` calls `NewServiceRequestHandler`, which registers `GET /service-requests` at `cenomi-api-2/servicerequest/delivery/http/service_request_handler.go:158`.
- None of these routes has a route-level permission middleware; they only need the session (`constants.UserData` in context). Permission gating is client-side. Server-side data scoping uses the property access described below.

#### 0.4 Property scoping (server side)
**Fit-out summary and document status** use `tenantContactUseCase.GetPermittedItems` (`cenomi-api-2/tenant_contact/usecase/tenant_contact_usecase.go:852` → repo `cenomi-api-2/tenant_contact/repository/postgres/tenant_contacts_repository.go:2029`). Each usecase applies the same rule:

```go
if overRides.PropertyOverride == nil && len(accessibleItems.Properties) > 0 ||
   overRides.PropertyOverride != nil && *overRides.PropertyOverride == constants.OverrideAll {
    propertyIDs = accessibleItems.Properties          // -> p.property_id = ANY($n)
} else if overRides.PropertyOverride != nil && *overRides.PropertyOverride == constants.OverrideNone {
    return ErrUserHaveNoPermission                    // fitout-summary handler -> 500; doc-status handlers -> 403
}
// otherwise propertyIDs = nil -> no property restriction
```

**Discrepancy** uses `getPermittedPropertyGroupIDsForReport` (`cenomi-api-2/discrepancy/usecase/discrepancy_usecase.go:987`):
- A `SUPER_ADMIN` or `LEASING_ADMIN` role returns nil, which means all malls.
- `OverrideNone` returns `[]`, which means nothing.
- Accessible properties are mapped to property_group_ids by `queryGetPropertyGroupIDsByPropertyIDs`.
- Failing that, accessible regions are mapped to property_group_ids by `queryGetPropertyGroupIDsByRegion`.
- Otherwise it returns nil (all malls).

#### 0.5 V2 per-card filters
**`dashboardFilters.ts` / `useCardFilters.ts` / `CardFilters.tsx`** (in `.../admin/v2/`):
- Each card has its own `{year, month, region, mall}` state. The defaults are the current year and "all" for the rest. Nothing is stored in the URL.
- `CARD_FILTER_SUPPORT` decides which filters a card shows and sends:

| Card | year | month | region | mall |
|---|---|---|---|---|
| `fitoutHandover` | yes | yes | yes | yes |
| `fitoutDrawings` | yes | yes | yes | yes |
| `documentStatus` | yes | – | yes | – |
| `unitDiscrepancy` | yes | yes (seeds the card's own month select) | – | – |

- `cardParams()` maps the filters to query params: `year`, `month` as `Jan`…`Dec`, `region`, and `unique_property_id` for the mall.
- `filterQueryString()` serialises them in the order `year, month, region, unique_property_id`.
- Option sources:
  - Year options are the current year and the four before it (`defaultYearOptions`).
  - Region and mall options come from `useDashboardRegionOptions` / `useDashboardMallOptions`.
  - The mall list is narrowed to the chosen region using Redux `state.properties.uniquePropertyList`.
- Changing the region clears the mall.

#### 0.6 V2 permission gating
**`dashboardLayout.ts`, `visibleDashboardCards`:**

| Card id | Shown when the user has any of |
|---|---|
| `fitoutHandover` | `VIEW_FIT_OUT_SUMMARY` |
| `fitoutDrawings` | `VIEW_ARCH_DRAWING`, `VIEW_MEP_DRAWING`, `VIEW_ELECTRICAL_DRAWING` |
| `documentStatus` | Same three as `fitoutDrawings` (they always appear together) |
| `unitDiscrepancy` | `VIEW_DISCREPANCY_REPORT` |

Layout:
- Row 4 is `fitoutHandover` (span 7) beside `fitoutDrawings` (span 5).
- Row 3 is `leaseRequests` (4) beside `documentStatus` (8).
- Row 6 is `serviceRequests` (7) beside `unitDiscrepancy` (5).
- When one card of a row is hidden, its partner takes 12 columns.

Inside the cards:
- Drawing rows and document-status disciplines are filtered per permission (`fitout.ts` `DRAWINGS`):
  - `MEP_DRAWING` needs `VIEW_MEP_DRAWING` (label "Mechanical").
  - `ARCHITECTURAL_DRAWING` needs `VIEW_ARCH_DRAWING`.
  - `ELECTRICAL_DRAWING` needs `VIEW_ELECTRICAL_DRAWING`.

**Legacy gating (`adminDashboard.tsx`) is the same:**
- `VIEW_FIT_OUT_SUMMARY` shows `<FitoutHandoverWrapper/>`.
- Any of the three drawing permissions shows `<FitoutDrawing/>` and `<FitoutDrawingDocumentStatus/>`.
- `VIEW_DISCREPANCY_REPORT` shows `<UnitDiscrepancyReport/>`.

---

### 1. Card: Fit-out & Handover (`fitoutHandover`)

| | V2 | Legacy |
|---|---|---|
| Component | `v2/FitoutHandoverCard.tsx`, data hook `v2/useFitoutSummary.ts`, model `v2/fitout.ts`, drill-down `v2/FitoutRequestsPopup.tsx` → `components/v2/listModals/ServiceRequestsListModal.tsx` | `components/FitoutHandover/FitoutHandoverWrapper.tsx` (+ `FitoutLinkCard.tsx`, `Fitout/FitoutPopUp.tsx`, `Fitout/UnitFitoutPopUp.tsx`, `Fitout/UnitFitoutDetailsCard.tsx`, `DonutChart.tsx`) |
| Title key | `fitHandover` | `fitHandover` (in `ServiceStackedCard`) |
| Permission | `VIEW_FIT_OUT_SUMMARY` | same |
| Filters | year, month, region, mall | year, months, region, mall, **unit** (the unit dropdown appears once a mall is chosen) |

#### 1.1 Chart and mapping

**V2: four `ProgressRing`s plus a handover callout.**
- These are ui-kit custom SVG components (`@cenomi-frontend/ui-kit` `charts/ProgressRing`). No chart library is used.
- Ring order comes from `INSPECTIONS`: `PRE_OPENING_INSPECTION_MEP`, `PRE_OPENING_INSPECTION_ARCHITECTURAL`, `OPEN_CEILING_INSPECTION`, `CLOSE_CEILING_INSPECTION`.
- Ring colours are `chartPalettes.categorical4[i]` = `#8B5CF6`, `#14B8A6`, `#F59E0B`, `#F43F5E`.
- `inspectionRings(list)` builds each ring:
  - It finds `list` rows where `service_category==='FIT_OUT_AND_HANDOVER' && sub_category===id` (`fitoutCounts`).
  - `total = received + remaining + reviewed`.
  - `share = reviewed / total`, or `null` when `total` is 0. The code comment notes that the spec's `reviewed/received` does not hold because `received` is almost always 0.
  - The label is `t(`${id}_SHORT`)`. The sub-text is "{reviewed} of {total} reviewed".
- Callout: `pendingHandovers(list)` = `remaining` of the `FIT_OUT_AND_HANDOVER / HANDOVER` row. Label `dashboardV2.handovers` / `pendingTenantAccept`.

**Legacy: `HorizontalStackedChart` (recharts `BarChart` with horizontal bars, `graphs/horizontalStackedChart.tsx`).**
- Y axis: four inspection sub-categories, formatted as "Pre opening inspection mep" and so on.
- Bars:
  - `Received` `#3B82F6`, shown only when the summed `received` is greater than 0.
  - `Remaining` `#F7BA00`.
  - `Reviewed` `#00B303`.
- The values come from `received` / `remaining` / `reviewed` of each row (`getModifedData`). The `HANDOVER` row is excluded from the bars.
- X domain is `[0, max(row total) + 10]`.
- `FitoutLinkCard` shows the `HANDOVER.remaining` count ("pendingTenantAccept"). It is clickable when the count is non-zero.
- **Unit view (legacy only):** when a unit is selected, the card shows instead:
  - `UnitFitoutDetailsCard`, built from `unit_details`.
  - A `HorizontalStackedChart` of the unit's inspections. Each SR is counted as "Reviewed" when its status is COMPLETED, APPROVED, REVIEWED_WITH_COMMENTS or REVIEW_AND_APPROVE; otherwise it is "Remaining".
  - A `DonutChart` "Site Progress" (custom SVG, `components/DonutChart.tsx`). Its value is computed client-side: `approvedCount / 7 × 100`, where approvedCount counts the 4 inspections plus 3 drawings that have at least one SR in an approved-like status. Colours `#EC4899` / `#E5E7EB`.
  - Client-side derivations from `unit_details`:
    - `handover_date` falls back to `lease_start_date`.
    - `fitout_complete_date` falls back to `fitout_start_date + 3 months`, flagged as a forecast.
    - `running_days` falls back to today − handover.

#### 1.2 APIs called

| # | Frontend fn | Method + path | Query params | When |
|---|---|---|---|---|
| A | V2 `useFitoutSummary` (`httpRequest`) / legacy `useFetchData(FITOUT_SUMMARY_ADMIN, …)` | `GET /fitout-summary` | V2: `year` (always), `month=Jan..Dec`, `region`, `unique_property_id`. Legacy also sends `unit_id`, which **the handler ignores**. | On mount and on every filter change. V2 fetches it **twice**: once for `fitoutHandover` and once for `fitoutDrawings`, each with its own filters. |
| B | `ServiceRequestsListModal` → `getServiceRequestsFromQuery` (V2); legacy `FitoutPopUp` → Redux `fetchServiceRequests` → `getServiceRequestsFromQuery` | `GET /service-requests` | `year, month, region, unique_property_id, service_category=FIT_OUT_AND_HANDOVER, sub_category=<ring id or HANDOVER>, status=<see below>, source=WIDGET, page, limit, sort_by, order, search`. Legacy also sends `unit_id`. | Clicking a ring with `remaining>0` or the "Review" link. Legacy: clicking a bar segment or the link card. |
| C | `getUnitsWithFitout(propertyId, region)` (`libs/api/src/lib/unitDetails/unitdetailsapi.ts:68`) | `GET /units-with-fitout` | `property_id=<mall unique_property_id>`, `region` | Legacy only, when a mall is selected (fills the unit dropdown) |
| D | `getUnitFitoutStatus(unitId)` (`unitdetailsapi.ts:63`) | `GET /unit-fitout-status` | `unit_id` | Legacy only, when a unit is selected |
| – | "View Details" link | navigates to `/dashboard/servicerequest?{filters}&service_category=FIT_OUT_AND_HANDOVER&sort_by=updated_at&order=DESC&sub_category=<4 inspections>` (`fitoutListHref`) | | |

Status mapping for the popup:
- Ring or callout "Remaining" sends the base status `ACTION_REQUIRED,IN_PROCESS,PENDING`.
- `fitoutStatusParam` / legacy `FitoutPopUp` expand that to `ACTION_REQUIRED,IN_PROCESS,PENDING,REVIEWED_WITH_COMMENTS,REQUESTED_RE_UPLOAD,REQUESTED,IN_PROGRESS,REPORT_SUBMITTED`.
- Legacy "Received" sends `SUBMITTED`. Legacy "Reviewed" sends `COMPLETED`.

`UnitFitoutPopUp` makes no API call. It renders the `unit-fitout-status` rows already loaded.

#### 1.3 Backend: `GET /fitout-summary`

**Chain:**
- Route: `cenomi-api-2/fitout_summary/delivery/http/fitout_summary_handler.go:114`.
- Handler `FetchFitoutSummary` (`fitout_summary_handler.go:136`):
  - `filter_type` defaults to `fixed`.
  - When `filter_type=range`, `date_from` and `date_to` are required in DD-MM-YYYY. The `from > to` check is a **string** compare.
  - When `fixed`, `year` is required (400 if missing). `month` is looked up case-insensitively in `constants.MonthCountMap` (`jan`…`dec`), so numeric months fail with 400.
  - It reads `unique_property_id` and `region`. **`unit_id` is never read.**
- Usecase `FetchFitoutSummary` (`cenomi-api-2/fitout_summary/usecase/fitout_summary_usecase.go:27`) applies property scoping (§0.4), then calls `FetchFilterData` and then `FetchFitoutSummary`.
- Repository:
  - `FetchFitoutSummary` (`cenomi-api-2/fitout_summary/repository/postgres/fitout_summary_repository.go:1008`)
  - `buildFitoutSummaryQuery` (`:1161`)
  - SQL constants `fitoutQuery` (`:32`) and `summaryQuery` (`:102`)
  - `FetchFilterData` (`:1043`)

**Fixed arguments:** `$1='REJECTED'`, `$2='Asia/Riyadh'`, `$3='APPROVED'`, `$4='SUBMITTED'`, `$5='COMPLETED'`. Dynamic WHERE parameters start at `$6`.

```sql
WITH fitout_summary AS (
  SELECT
    category, sub_category,
    COUNT(CASE WHEN status = $4::text THEN 1 END) AS received,                                   -- SUBMITTED
    COUNT(CASE WHEN status != $4::text AND status != $3::text
                AND status != $1::text AND status != $5::text THEN 1 END) AS remaining,           -- anything else (non-DRAFT)
    COUNT(CASE WHEN status = $3::text OR status = $1::text OR status = $5::text THEN 1 END) AS reviewed, -- APPROVED|REJECTED|COMPLETED
    EXTRACT(YEAR  FROM MAX(sr.created_at AT TIME ZONE $2)) AS summary_year,
    EXTRACT(MONTH FROM MAX(sr.created_at AT TIME ZONE $2)) AS summary_month,
    sr.property_id, p.marketing_name AS mall, p.region AS region, p.unique_property_id AS unique_property_id
  FROM (SELECT sr.*,
               EXTRACT(YEAR  FROM sr.created_at AT TIME ZONE $2) AS summary_year,
               EXTRACT(MONTH FROM sr.created_at AT TIME ZONE $2) AS summary_month
        FROM cenomi.service_request sr) sr
  LEFT JOIN cenomi.properties p ON p.property_id = sr.property_id
  WHERE category = 'FIT_OUT_AND_HANDOVER'
    AND status != 'DRAFT'
    /* %s dynamic */  AND summary_year = $6 [AND summary_month = $7] [AND p.property_id = ANY($n)]
                      [AND region = $n] [AND unique_property_id = $n]
  GROUP BY category, sub_category, sr.property_id, p.marketing_name, p.region, p.unique_property_id,
           status, summary_year, summary_month
  UNION ALL
  SELECT ... identical ...
  WHERE category = 'FIT_OUT_DRAWING'
    AND status != 'DRAFT'
    /* same %s dynamic clause */
  GROUP BY ...
)
SELECT category, sub_category,
       SUM(received) AS received, SUM(remaining) AS remaining, SUM(reviewed) AS reviewed,
       summary_year
FROM fitout_summary
GROUP BY category, sub_category, summary_year;
```

Dynamic parts (`buildFitoutSummaryQuery`):
- `filter_type=range` adds `sr.created_at >= TO_DATE($a,'DD-MM-YYYY') AND sr.created_at <= TO_DATE($b,'DD-MM-YYYY')` in place of year/month. The end date is exclusive of that day after midnight.
- `fixed` adds `summary_year = $n` and, optionally, `summary_month = $n`, both in Riyadh time.
- `p.property_id = ANY($n)` is added when the usecase resolved scoped property IDs.
- `region = $n` and `unique_property_id = $n` are added when passed.

Notes:
- The query reads only `cenomi.service_request`, not the archive tables, and has **no `deleted_at IS NULL` filter**.
- Every sub_category of the two categories is returned, including HANDOVER, ISSUE_LOD and others. The frontend picks out the rows it needs.

**Filter data (`FetchFilterData`, `:1043`).** It runs three more queries over the same `fitoutQuery`, with inner WHERE `AND p.property_id = ANY($6)` plus an optional date range:

```sql
WITH fitout_summary AS (<fitoutQuery>) SELECT ARRAY_AGG(distinct summary_year) AS years FROM fitout_summary;
WITH fitout_summary AS (<fitoutQuery>) SELECT ARRAY_AGG(distinct region) AS regions FROM fitout_summary WHERE region IS NOT NULL;
WITH fitout_summary AS (<fitoutQuery>) SELECT ARRAY_AGG(distinct mall) AS malls, ARRAY_AGG(distinct unique_property_id) AS unique_property_ids
  FROM fitout_summary WHERE mall IS NOT NULL [AND summary_year = $n] [AND summary_month = $n];
```

`$6` is always bound to `params.PropertyIDs`. When it is nil, `ANY(NULL)` matches no rows, so unrestricted users get empty filter arrays. This is harmless: V2 ignores `filters`, and legacy only uses them for the dropdowns.

Post-processing: the DTO mapping only (`domain/fitoutdto.go:8-30`). Nothing is cached.

**Response (`domain.FitoutSummaryResponse`, `cenomi-api-2/domain/fitoutdto.go:17`; TS `FitoutSummaryItemDataType` in `libs/api/src/lib/adminDashboard/adminDashboardTypes.ts:177`):**

```json
{
  "success": true,
  "data": {
    "filters": { "years": [2026], "malls": ["Mall of Dhahran"], "regions": ["EASTERN"], "unique_property_ids": [12] },
    "list": [
      { "service_category": "FIT_OUT_AND_HANDOVER", "sub_category": "PRE_OPENING_INSPECTION_MEP", "received": 0, "remaining": 29, "reviewed": 7 },
      { "service_category": "FIT_OUT_AND_HANDOVER", "sub_category": "HANDOVER", "received": 0, "remaining": 5, "reviewed": 40 },
      { "service_category": "FIT_OUT_DRAWING", "sub_category": "MEP_DRAWING", "received": 15, "remaining": 3, "reviewed": 7 }
    ]
  }
}
```

The `filters` keys use `omitempty`, so an empty filter key is dropped from the JSON.

#### 1.4 Backend: `GET /service-requests` (drill-down popup, fit-out branches)

**Chain:**
- Handler `List` (`cenomi-api-2/servicerequest/delivery/http/service_request_handler.go:280`). `newServiceRequest` parses `month` with a case-sensitive `Jan..Dec` map (`:597`), `region` (`:568`), `unique_property_id` (`:697`) and `source` (`:724`).
- Usecase `ListAllServiceRequests` (`cenomi-api-2/servicerequest/usecase/service_request_usecase.go:1332`) → `FetchServiceRequestListIfTenantIDNotExists` (`:1925`):
  - It applies property scoping.
  - It intersects that with properties matching `region` / `unique_property_id` via `propertyRepo.FetchPropertyByFilters` (`:1961`).
- Repository `ListAllServiceRequests` (`cenomi-api-2/servicerequest/repository/service_request_repository.go:1437`) builds its WHERE in `BuildServiceRequestQueryCondition` (`:1737`). The shared list SQL is documented with the Service Requests card.

Fit-out-specific branches:
- **Property scope** (`:1938-1940`): for `source=WIDGET` with only FIT_OUT categories (`isFitoutSummaryWidgetScope`, `:221`), or for FIT_OUT_AND_HANDOVER with one summary sub-category, scoping is property-only:

  ```sql
  (sr.property_id = ANY($n) OR sr.property_ids && $n)
  ```

  The lease and SR-ID OR clauses are skipped (`:2055`) so the counts line up with fitout-summary.
- **Year and month:**

  ```sql
  EXTRACT(YEAR FROM sr.created_at AT TIME ZONE 'asia/riyadh') = $n
  [AND EXTRACT(MONTH FROM sr.created_at AT TIME ZONE 'asia/riyadh') = $n]
  ```

  The month condition is skipped when `status` is the single value `PENDING`.
- **"Remaining" bucket** (`:1862-1878`): the status list has several values and none of SUBMITTED, APPROVED, REJECTED or COMPLETED, with `source=WIDGET`:

  ```sql
  sr.status NOT IN ('DRAFT','SUBMITTED','APPROVED','REJECTED','COMPLETED','ACTIVE')
  ```

  This differs slightly from the summary, which counts `ACTIVE` as remaining.
- **"Reviewed" / "Approved" bucket** (`:1879-1885`): when the status contains `COMPLETED`, `mergeFitoutReviewedReplacingCompleted` (`:179`) widens the filter to `sr.status = ANY('{APPROVED,REJECTED,COMPLETED}')`.
- **`unit_id` (legacy)** uses `fitoutdrawing.UnitFilterClause`; see §3.4.
- Rows older than 90 days in APPROVED or REJECTED are hidden when the user lacks `VIEW_ARCHIVED_SERVICE_REQUEST` (`:1983`), so "reviewed" popup counts can be lower than the summary.

Response rows used by the modal: `service_request_id, title, company_name, mall, service_category, sub_category, created_by, updated_at, status, operations[]`, plus `data.total_count`.

#### 1.5 Backend: `GET /units-with-fitout` (legacy unit dropdown)

**Chain:**
- Handler `FetchUnitsWithFitout` (`fitout_summary_handler.go:882`) requires `property_id`, which is the unique_property_id. It accepts `region` but does not use it, and accepts an optional `unique_property_id`.
- Usecase `:417`
- Repository `FetchUnitsWithFitout` (`fitout_summary_repository.go:2344`), `buildUnitsWithFitoutQuery` (`:2314`), `unitsWithFitoutQuery` (`:966`)

```sql
WITH all_property_ids AS (
  SELECT DISTINCT p.property_id FROM cenomi.properties p
  WHERE 1=1 AND unique_property_id = $1 [AND unique_property_id = $2]
),
latest_lease_for_unit AS (
  SELECT DISTINCT ON (lu.unit_id) lu.unit_id, lu.lease_id
  FROM cenomi.leased_units lu LEFT JOIN cenomi.leases l ON l.lease_id = lu.lease_id
  ORDER BY lu.unit_id, l.created_at DESC NULLS LAST, lu.start_date DESC NULLS LAST, lu.created_at DESC NULLS LAST
)
SELECT DISTINCT u.unit_id, u.pms_unit_code, u.unit_type, u.property_id, p.marketing_name AS mall, p.region,
       l.lease_id, l.pms_tenant_code AS lease_code, tp.company_name
FROM cenomi.units u
JOIN all_property_ids api ON api.property_id = u.property_id
LEFT JOIN latest_lease_for_unit llfu ON llfu.unit_id = u.unit_id
LEFT JOIN cenomi.leases l ON l.lease_id = llfu.lease_id
LEFT JOIN cenomi.properties p ON p.property_id = u.property_id
LEFT JOIN cenomi.tenant_profiles tp ON tp.tenant_profile_id = l.tenant_profile_id
ORDER BY u.unit_id;
```

- Despite its name, the query returns **every unit in the mall**; nothing filters for fit-out SRs.
- No user scoping is applied.
- Response: `{list:[{unit_id,unit_code,unit_type,property_id,mall,region,lease_id,lease_code,company_name}], region}`. `region` is taken from the first row.

#### 1.6 Backend: `GET /unit-fitout-status` (legacy unit view)

**Chain:**
- Handler `FetchUnitFitoutStatus` (`fitout_summary_handler.go:615`) requires `unit_id`.
- Usecase `FetchUnitFitoutStatus` (`:383`) and `FetchUnitDetails` (`:400`).
- Repository `FetchUnitFitoutStatus` (`:2276`, SQL `unitFitoutStatusQuery` `:721`) and `FetchUnitDetails` (`:2400`, SQL `unitDetailsQuery` `:817`).

```sql
-- unitFitoutStatusQuery ($1 = unit_id): latest SR per (category, sub_category) on the unit's newest lease
WITH latest_lease_for_unit AS (
  SELECT DISTINCT ON (lu.unit_id) lu.unit_id, lu.lease_id
  FROM cenomi.leased_units lu LEFT JOIN cenomi.leases l ON l.lease_id = lu.lease_id
  WHERE lu.unit_id = $1
  ORDER BY lu.unit_id, l.created_at DESC NULLS LAST, lu.start_date DESC NULLS LAST, lu.created_at DESC NULLS LAST),
service_requests_for_lease AS (
  SELECT sr.service_request_id, sr.category, sr.sub_category, sr.status, sr.created_at, sr.updated_at, sr.created_by
  FROM latest_lease_for_unit llfu JOIN cenomi.service_request sr ON sr.lease_id = llfu.lease_id
  WHERE sr.category IN ('FIT_OUT_AND_HANDOVER','FIT_OUT_DRAWING') AND sr.deleted_at IS NULL),
latest_sr_per_combination AS (
  SELECT DISTINCT ON (category, sub_category) * FROM service_requests_for_lease
  ORDER BY category, sub_category, updated_at DESC)
-- (unit_details / fo_status_calc CTEs are declared but unused by the final SELECT)
SELECT lsrc.category, lsrc.sub_category,
       CASE WHEN lsrc.status = 'COMPLETED' THEN 1 ELSE 0 END AS completed,
       CASE WHEN lsrc.status != 'COMPLETED' THEN 1 ELSE 0 END AS pending,
       lsrc.service_request_id, lsrc.status,
       COALESCE(CONCAT(u.first_name,' ',u.last_name),'System') AS created_by,
       lsrc.updated_at AS updated_on
FROM latest_sr_per_combination lsrc LEFT JOIN cenomi.users u ON u.user_id = lsrc.created_by
ORDER BY lsrc.category, lsrc.sub_category;
```

`unitDetailsQuery` (`:817`) resolves one lease per unit, preferring the newest leased_units lease and falling back to the newest lease that has fit-out SRs. It returns:
- `unit_code` (pms_unit_code), `unit_area` (GLA), `brand_name`, `lease_start_date` (COALESCE(start_date, contract_start_date)) and `lease_brand_mall`.
- `handover_date`: the earliest `FIT_OUT_AND_HANDOVER/HANDOVER` SR `payload.startDate`.
- `fitout_start_date`: the earliest `WORK_PERMIT` SR, taken from `payload.planneddate.worktimedate`, else `effective_starting.datefrom`, else `planneddate.worktimefrom`.
- `fitout_complete_date`: the latest `payload.endDate` on a PRE_OPENING_INSPECTION_ARCHITECTURAL or PRE_OPENING_INSPECTION_MEP SR.
- `running_days` = today − handover_date.
- `fo_status`:
  - `DID_NOT_START` when there is no fit-out start.
  - Otherwise the first match in priority order, over the latest SR per sub-category: DOCUMENT_UPLOADED > ACTION_REQUIRED > IN_PROCESS > SUBMITTED > APPROVED.
  - COMPLETED only when every SR is COMPLETED.
  - Otherwise IN_PROGRESS.

Go post-processing:
- When the details query errors or returns no row, the handler substitutes `unit_details = {unit_code:"", brand_name:"", lease_brand_mall:"", fo_status:"IN_PROGRESS"}`.
- No user scoping is applied.

Response:

```json
{ "list": [ { "service_category": "FIT_OUT_DRAWING", "sub_category": "MEP_DRAWING", "completed": 0, "pending": 1,
              "service_request_id": 123, "status": "APPROVED", "created_by": "Jane Doe", "updated_on": "2026-09-01T10:00:00Z" } ],
  "unit_details": { "unit_code": "G-012", "brand_name": "X", "unit_area": 120.5, "running_days": 40, "fo_status": "IN_PROCESS",
                    "lease_start_date": "...", "lease_brand_mall": "...", "handover_date": "...", "fitout_start_date": "...", "fitout_complete_date": null } }
```

---

### 2. Card: Fit-out Drawings (`fitoutDrawings`)

| | V2 | Legacy |
|---|---|---|
| Component | `v2/FitoutDrawingsCard.tsx` (+ `fitout.ts` `drawingRows`, `useFitoutSummary`, `FitoutRequestsPopup`) | `components/Fitout/FitoutDrawing.tsx` (+ `FitoutPopUp`, `UnitFitoutPopUp`, `UnitFitoutDetailsCard`, `DonutChart`) |
| Title key | `fitDrawings` | `fitDrawings` |
| Permission | any of `VIEW_ARCH_DRAWING`, `VIEW_MEP_DRAWING`, `VIEW_ELECTRICAL_DRAWING`; rows filtered per discipline permission | same |
| Filters | year, month, region, mall | year, months, region, mall, unit, **plus a Monthly/Custom toggle** (custom sends `filter_type=range&date_from=DD-MM-YYYY&date_to=DD-MM-YYYY&region&unique_property_id&unit_id`) |

#### 2.1 Chart and mapping

**V2: `StackedBars`** (ui-kit custom, horizontal stacked bars).
- One row per permitted discipline, in the order MEP ("Mechanical"), ARCHITECTURAL, ELECTRICAL.
- Segments use `chartPalettes.pipeline3`:
  - `Submitted` = `received`, `#0284C7`
  - `Pending` = `remaining`, `#F59E0B`
  - `Approved` = `reviewed`, `#059669`
- The rows are filtered from the same `GET /fitout-summary` response (category `FIT_OUT_DRAWING`).
- An empty state shows when every value is 0.

**Legacy: `HorizontalStackedChart`** (recharts).
- Bars `Submitted` `#3B82F6`, `Pending` `#F7BA00`, `Approved` `#00B303`, mapped from `received` / `remaining` / `reviewed` (`FitoutModifedData`).
- The Y labels are the sub-category with `_DRAWING` stripped, and "Mep" becomes "Mechanical".
- The unit view mirrors §1.1. It uses drawing SRs, the "Site Progress" donut and `UnitFitoutStatusChart`'s `FitoutStatusItem` type.

#### 2.2 APIs called
- **`GET /fitout-summary`:** the same endpoint and backend as §1.3. V2 sends its own request with the drawings card's filters. Legacy can also send `filter_type=range&date_from&date_to`, which the handler supports through the range branch of `buildFitoutSummaryQuery`.
- **`GET /service-requests`** (popup on segment click):
  - Params: `service_category=FIT_OUT_DRAWING`, `sub_category=<MEP_DRAWING|ARCHITECTURAL_DRAWING|ELECTRICAL_DRAWING>`, `source=WIDGET`, plus the card's filters.
  - Status mapping (`POPUP_STATUS.drawing`):
    - Submitted sends `SUBMITTED`.
    - Pending sends the expanded open-status list, which is handled by the "remaining" NOT IN branch.
    - Approved sends `APPROVED,REJECTED,COMPLETED`. Because it contains COMPLETED, it is merged to the APPROVED, REJECTED, COMPLETED set.
  - Backend as in §1.4.
- **Legacy unit drill-down:** `GET /units-with-fitout` and `GET /unit-fitout-status`, as in §1.5 and §1.6.
- **"View Details" link:** `/dashboard/servicerequest?{filters}&sort_by=updated_at&order=DESC&service_category=FIT_OUT_DRAWING`.

Response fields used: `list[].service_category === 'FIT_OUT_DRAWING'`, `sub_category`, `received`, `remaining`, `reviewed`.

---

### 3. Card: Fit-out Drawings Document Status (`documentStatus`)

| | V2 | Legacy |
|---|---|---|
| Component | `v2/DocumentStatusCard.tsx`, hook `v2/useDocumentStatus.ts`, model `v2/documentStatus.ts`, drill-down `components/v2/listModals/DocumentTypeStatusModal.tsx` | `components/Fitout/FitoutDrawingDocumentStatus.tsx`, chart `Fitout/FitoutDrawingDocumentStatusByMallChart.tsx`, popup `Fitout/FitoutDrawingDocumentPopUp.tsx` |
| Title key | `fitDrawingsDocumentStatus`; meta `Last Synced: {last_synced_at}` | same |
| Permission | any of the three drawing permissions; the discipline switch only lists permitted disciplines | same |
| Filters | year, region (the API takes no month or mall); discipline `SegmentedControl`; Chart/Table toggle, which defaults to Table on mobile | year, region, Monthly/Custom range toggle (`filter_type=range`, `date_from`, `date_to`), discipline buttons |

#### 3.1 Chart and mapping

**V2: `StackedColumns`** (ui-kit custom), one column per mall, with a `DataTable` alternative.
- `mallGrades(list, discipline, arabic)`:
  - For each `list[]` mall, take the `sub_categories[]` row whose normalised `sub_category` equals the chosen discipline.
  - `grades = {A: status_a, B: status_b, C: status_c, D: status_d}` and `total` is their sum.
  - The label is `mall_ar` in Arabic, otherwise `mall`.
  - Sort by total descending, then by name.
- Malls with `total===0` are left out of the chart or table and listed in the footnote (`dashboardV2.noDrawingsYet`).
- Colours are `chartPalettes.outcome4`: A `#059669`, B `#8B5CF6`, C `#F59E0B`, D `#DC2626`. Legend labels use `ADetail`…`DDetail`.
- Clicking a column or row opens `DocumentTypeStatusModal` for that mall (`unique_property_id`) and discipline.

**Legacy: recharts stacked `BarChart`** (`FitoutDrawingDocumentStatusByMallChart`).
- X axis is `mallLabel`. `Bar` series `A`, `B`, `C`, `D` use `GRADE_COLORS` = A `#00B303`, B `#3B82F6`, C `#F7BA00`, D `#DC2626`.
- `mallDocumentStatusModifiedData` has the same mapping as V2. `applyMinSegmentVisibility` pads tiny segments for display.
- Clicking a mall with a non-zero total opens `FitoutDrawingDocumentPopUp`.

**Drill-down modal (both versions):**
- A table of document types with columns A, B, C, D and a totals footer from `data.totals`.
- Labels come from `formatDocumentTypeLabel(document_name_en, document_type_id)`. The Arabic name comes from `document_name_ar` (the API never sends it) or from the master-data lookup `buildArabicNameByTypeIdFromMasterData`. `UNTRUSTED_ARABIC_TYPE_IDS` are skipped.

#### 3.2 APIs called

| # | Frontend fn | Method + path | Query params | When |
|---|---|---|---|---|
| A | `getFitoutDrawingDocumentStatusByMall` (`libs/api/src/lib/adminDashboard/fitoutDrawingDocumentStatusApi.ts:51`); V2 via `useDocumentStatus(year, region)`; legacy via `useFetchData` | `GET /fitout-drawing-document-status-summary/by-mall` | V2: `year`, `region`. Legacy: `year`, `region`, or `filter_type=range&date_from&date_to&region`. | On mount and when the filters change. Switching discipline is client-side only. |
| B | `getFitoutDrawingDocumentStatusByDocumentType` (`fitoutDrawingDocumentStatusApi.ts:22`) | `GET /fitout-drawing-document-status-summary/by-document-type` | `unique_property_id=<mall uid>`, `sub_category=<discipline>` (required), `year`, `region`; legacy can add `unit_id`, `filter_type`, `date_from`, `date_to` | When the drill-down modal opens |

`GET /fitout-drawing-document-status-summary` (without a suffix) exists at handler `:706` but is not called by these cards.

#### 3.3 Backend: `GET /fitout-drawing-document-status-summary/by-mall`

**Chain:**
- Route: `fitout_summary_handler.go:122`.
- Handler `FetchFitoutDrawingDocumentStatusByMall` (`:819`):
  - It parses params with `parseFitoutDrawingDocumentStatusParams` (`cenomi-api-2/fitout_summary/delivery/http/fitout_drawing_document_status_params.go:14`).
  - `year` is optional.
  - `month` may be a name (`jan`) or a number from 1 to 12.
  - `unit_id` requires `unique_property_id`.
  - `range` requires DD-MM-YYYY dates.
  - It sets `last_synced_at = time.Now().UTC()`, which is the request time and not a real sync time.
- Usecase `FetchFitoutDrawingDocumentStatusByMall` (`cenomi-api-2/fitout_summary/usecase/fitout_summary_usecase.go:554`):
  1. Property scoping (§0.4); `OverrideNone` returns 403.
  2. `FetchFitoutDrawingDocumentStatusFilterData` (repo `:2758`).
  3. `FetchFitoutDrawingDocumentStatusByMall` (repo `:2898`).
  4. **Go post-filter:** when `region` is set, it keeps only malls where `strings.EqualFold(TrimSpace(mall.Region), region)`. This drops malls outside the region that would otherwise appear with zero counts.
  5. `normalizeFitoutDrawingDocumentStatusByMall` (`:509`) makes sure every mall has all three disciplines in the order ARCHITECTURAL, MEP, ELECTRICAL. Missing ones are zero-filled. It also recomputes the per-mall `total` and the overall `totals`.

**Repository** (`cenomi-api-2/fitout_summary/repository/postgres/fitout_summary_repository.go`):
- Step 1, `resolveScopedMallUIDs` (`:2864`): when the user has scoped `PropertyIDs`, map them to the primary mall uid.

  ```sql
  WITH mall_rollup AS (<mall rollup body>)
  SELECT DISTINCT COALESCE(mr.rollup_uid, p.unique_property_id)::bigint AS mall_uid
  FROM cenomi.properties p LEFT JOIN mall_rollup mr ON mr.unique_property_id = p.unique_property_id
  WHERE p.property_id = ANY($1) AND COALESCE(mr.rollup_uid, p.unique_property_id) IS NOT NULL;
  ```

- Step 2, the main query (`fitoutDrawingDocumentStatusByMallQuery`, `:2617`, with the CTE builders at `:2471-2600`).
  - Fixed arguments: `$1='FIT_OUT_DRAWING'`, `$2='{ARCHITECTURAL_DRAWING,MEP_DRAWING,ELECTRICAL_DRAWING}'`, `$3='DRAFT'`, `$4=scopedMallUIDs`. Dynamic parameters start at `$5`.

```sql
WITH mall_rollup AS (
  SELECT up.unique_property_id::bigint AS unique_property_id,
         COALESCE(
           (SELECT up2.unique_property_id::bigint FROM cenomi.unique_properties up2
             WHERE up.property_group_id IS NOT NULL AND up2.property_group_id = up.property_group_id AND up2.is_primary IS TRUE
             ORDER BY up2.unique_property_id LIMIT 1),
           (SELECT up3.unique_property_id::bigint FROM cenomi.unique_properties up3
             WHERE up.property_group_id IS NOT NULL AND up3.unique_property_id = up.property_group_id AND up3.is_primary IS TRUE LIMIT 1),
           (SELECT up4.unique_property_id::bigint FROM cenomi.unique_properties up4
             WHERE NULLIF(TRIM(up.property_group_name),'') IS NOT NULL
               AND LOWER(TRIM(up4.property_group_name)) = LOWER(TRIM(up.property_group_name))
               AND LOWER(TRIM(COALESCE(up4.region,''))) = LOWER(TRIM(COALESCE(up.region,'')))
               AND up4.is_primary IS TRUE ORDER BY up4.unique_property_id LIMIT 1),
           up.unique_property_id::bigint) AS rollup_uid
  FROM cenomi.unique_properties up
),
scoped_sr AS (
  -- one branch per table: service_request, service_request_archive_recent, service_request_archive_cold
  SELECT sr.service_request_id, sr.sub_category, sr.payload, sr.lease_id,
         COALESCE(mr.rollup_uid, p.unique_property_id) AS mall_uid
  FROM cenomi.service_request sr
  LEFT JOIN cenomi.properties p ON p.property_id = sr.property_id
  LEFT JOIN mall_rollup mr ON mr.unique_property_id = p.unique_property_id
  WHERE sr.category = $1 AND sr.sub_category = ANY($2) AND sr.status != $3 AND sr.deleted_at IS NULL
    /* dynamic */ [AND p.property_id = ANY($5)]
                  [AND COALESCE(mr.rollup_uid, p.unique_property_id) = $n]          -- unique_property_id
                  [AND (COALESCE(sr.payload->>'unit_code','') ILIKE '%'||$n||'%'
                        OR EXISTS (SELECT 1 FROM cenomi.leased_units lu JOIN cenomi.units u ON u.unit_id = lu.unit_id
                                   WHERE lu.lease_id = sr.lease_id AND (u.pms_unit_code = $n OR u.unit_id::text = $n)))] -- unit_id
                  [AND p.region = $n]
                  [AND EXTRACT(YEAR  FROM (sr.created_at AT TIME ZONE 'Asia/Riyadh')) = $n]
                  [AND EXTRACT(MONTH FROM (sr.created_at AT TIME ZONE 'Asia/Riyadh')) = $n]
                  -- or, for filter_type=range:
                  [AND sr.created_at >= TO_DATE($a,'DD-MM-YYYY') AND sr.created_at < (TO_DATE($b,'DD-MM-YYYY') + INTERVAL '1 day')]
  UNION ALL SELECT ... FROM cenomi.service_request_archive_recent sr ...
  UNION ALL SELECT ... FROM cenomi.service_request_archive_cold sr ...
),
document_rows AS (
  SELECT s.service_request_id, s.sub_category, s.mall_uid,
         lower(trim(COALESCE(elem->>'status',''))) AS status_norm,
         COALESCE(NULLIF(trim(elem->>'documentTypeId'),''), NULLIF(trim(elem->>'document_type_id'),'')) AS document_type_id,
         regexp_replace(COALESCE(NULLIF(trim(elem->>'documentTypeId'),''), NULLIF(trim(elem->>'document_type_id'),'')), '^DR_', '') AS canonical_document_type_id,
         NULLIF(trim(elem->>'document_name_en'),'') AS document_name_en,
         ord
  FROM scoped_sr s
  CROSS JOIN LATERAL jsonb_array_elements(
    CASE WHEN jsonb_typeof(s.payload->'document_status_list') = 'array' THEN s.payload->'document_status_list'
         WHEN jsonb_typeof(s.payload->'drawing_type_obj'->'documents') = 'array' THEN s.payload->'drawing_type_obj'->'documents'
         ELSE '[]'::jsonb END) WITH ORDINALITY AS t(elem, ord)
),
deduped AS (   -- latest entry per (SR, canonical document type); approved IDs win over DR_ drafts
  SELECT DISTINCT ON (service_request_id, canonical_document_type_id)
         service_request_id, sub_category, mall_uid, canonical_document_type_id AS document_type_id, document_name_en, status_norm
  FROM document_rows
  WHERE status_norm IN ('a','b','c','d') AND canonical_document_type_id IS NOT NULL AND canonical_document_type_id != ''
  ORDER BY service_request_id, canonical_document_type_id, ord DESC, (document_type_id LIKE 'DR_%') ASC
),
agg AS (
  SELECT mall_uid, sub_category,
         COUNT(*) FILTER (WHERE status_norm='a') AS status_a,
         COUNT(*) FILTER (WHERE status_norm='b') AS status_b,
         COUNT(*) FILTER (WHERE status_norm='c') AS status_c,
         COUNT(*) FILTER (WHERE status_norm='d') AS status_d
  FROM deduped WHERE mall_uid IS NOT NULL GROUP BY mall_uid, sub_category
),
malls AS (
  SELECT up.unique_property_id,
         COALESCE(NULLIF(TRIM(up.marketing_name),''),'')    AS marketing_name,
         COALESCE(NULLIF(TRIM(up.marketing_name_ar),''),'') AS marketing_name_ar,
         COALESCE(NULLIF(TRIM(up.region),''),'')            AS region
  FROM cenomi.unique_properties up
  WHERE up.is_primary IS TRUE
    AND (array_length($4::bigint[], 1) IS NULL OR up.unique_property_id = ANY($4))
)
SELECT m.unique_property_id, m.marketing_name, m.marketing_name_ar, m.region,
       COALESCE(a.sub_category,'') AS sub_category,
       COALESCE(a.status_a,0), COALESCE(a.status_b,0), COALESCE(a.status_c,0), COALESCE(a.status_d,0)
FROM malls m LEFT JOIN agg a ON a.mall_uid = m.unique_property_id
ORDER BY LOWER(m.marketing_name) ASC, m.unique_property_id ASC;
```

Notes:
- **Every primary mall in scope** is returned, including malls with no drawings. Those malls get `sub_category=''`, which Go skips, then zero-fills during normalisation.
- In Go (`:2898-2990`), rows are grouped by mall uid into `SubCategories` and the per-mall `Total` is summed.
- The SR→mall link rolls a sub-property's `unique_property_id` up to the primary mall of its `property_group_id`, so a mall's sub-properties are counted under it.

**Filter data (`:2758`).** It uses property scope only and ignores year, region and date. It runs three queries, each a UNION over the 3 SR tables with `sr.category=$1 AND sr.sub_category=ANY($2) AND sr.status!=$3 AND sr.deleted_at IS NULL [AND p.property_id=ANY($4)]`:

```sql
SELECT COALESCE(ARRAY_AGG(DISTINCT unique_property_id ORDER BY unique_property_id) FILTER (WHERE unique_property_id IS NOT NULL),'{}')
FROM (SELECT p.unique_property_id FROM cenomi.<table> sr JOIN cenomi.properties p ON p.property_id = sr.property_id WHERE ... UNION ALL ...) malls;
SELECT COALESCE(ARRAY_AGG(DISTINCT summary_year ORDER BY summary_year DESC) FILTER (WHERE summary_year IS NOT NULL),'{}')
FROM (SELECT EXTRACT(YEAR FROM (sr.created_at AT TIME ZONE 'Asia/Riyadh'))::int AS summary_year FROM ... ) years_src;
SELECT COALESCE(ARRAY_AGG(DISTINCT region ORDER BY region) FILTER (WHERE region IS NOT NULL),'{}')
FROM (SELECT NULLIF(TRIM(p.region),'') AS region FROM ... ) regions_src;
```

Caching: none.

**Response (`domain.FitoutDrawingDocumentStatusByMallResponse`, `cenomi-api-2/domain/fitoutdto.go:492`; TS `FitoutDrawingDocumentStatusByMallSummaryType`):**

```json
{
  "last_synced_at": "2026-10-13T08:00:00Z",
  "filters": { "unique_property_ids": [12, 34], "years": [2026, 2025], "regions": ["CENTRAL", "EASTERN"] },
  "totals": { "status_a": 120, "status_b": 30, "status_c": 12, "status_d": 4 },
  "list": [
    { "unique_property_id": 12, "mall": "Mall of Arabia", "mall_ar": "مول العرب", "region": "WESTERN",
      "total": { "status_a": 40, "status_b": 10, "status_c": 3, "status_d": 1 },
      "sub_categories": [
        { "service_category": "FIT_OUT_DRAWING", "sub_category": "ARCHITECTURAL_DRAWING", "status_a": 20, "status_b": 4, "status_c": 1, "status_d": 0 },
        { "service_category": "FIT_OUT_DRAWING", "sub_category": "MEP_DRAWING", "status_a": 12, "status_b": 5, "status_c": 2, "status_d": 1 },
        { "service_category": "FIT_OUT_DRAWING", "sub_category": "ELECTRICAL_DRAWING", "status_a": 8, "status_b": 1, "status_c": 0, "status_d": 0 } ] }
  ]
}
```

Each `status_x` is the number of distinct (SR, document type) pairs whose latest grade is A, B, C or D. The grades are A approved, B approved with comments, C change request, D rejected.

#### 3.4 Backend: `GET /fitout-drawing-document-status-summary/by-document-type` (drill-down)

**Chain:**
- Handler `FetchFitoutDrawingDocumentStatusByDocumentType` (`fitout_summary_handler.go:757`). `sub_category` is required and must be ARCHITECTURAL_DRAWING, MEP_DRAWING or ELECTRICAL_DRAWING.
- Usecase `:464` applies property scoping. After the repository call it sums `totals` in Go and sets `service_category='FIT_OUT_DRAWING'`.
- Repository `FetchFitoutDrawingDocumentStatusByDocumentType` (`:2716`), SQL `fitoutDrawingDocumentStatusByDocumentTypeQuery` (`:2601`).
- Arguments: `$1..$3` as above, `$4=sub_category`. The dynamic WHERE starts at `$5`.

```sql
<mall_rollup, scoped_sr (3-table UNION with dynamic WHERE incl. COALESCE(mr.rollup_uid,p.unique_property_id) = $n), document_rows, deduped — identical to §3.3>
SELECT document_type_id,
       MAX(document_name_en) AS document_name_en,
       COUNT(*) FILTER (WHERE status_norm='a') AS status_a,
       COUNT(*) FILTER (WHERE status_norm='b') AS status_b,
       COUNT(*) FILTER (WHERE status_norm='c') AS status_c,
       COUNT(*) FILTER (WHERE status_norm='d') AS status_d
FROM deduped
WHERE sub_category = $4
GROUP BY document_type_id
ORDER BY MAX(document_name_en);
```

Response (`domain/fitoutdto.go:456`). `document_name_ar` is **not** returned, even though the TS type marks it as optional.

```json
{ "service_category": "FIT_OUT_DRAWING", "sub_category": "MEP_DRAWING",
  "list": [ { "document_type_id": "HVAC_LAYOUT", "document_name_en": "HVAC Layout", "status_a": 5, "status_b": 2, "status_c": 0, "status_d": 1 } ],
  "totals": { "status_a": 5, "status_b": 2, "status_c": 0, "status_d": 1 } }
```

---

### 4. Card: Unit Discrepancy Report (`unitDiscrepancy`)

| | V2 | Legacy |
|---|---|---|
| Component | `v2/UnitDiscrepancyCard.tsx`, model `v2/unitDiscrepancy.ts`, drill-down `components/v2/listModals/MismatchUnitsModal.tsx` | `components/UnitDiscrepancyReport.tsx`, drill-down `components/UnitDiscrepancyMismatchModal.tsx` |
| Title key | `Unit Discrepancy Report` | same |
| Permission | `VIEW_DISCREPANCY_REPORT` | same |
| Filters | Card filter: year, plus month which seeds the card's own **month select** (1–12). A **Mall-wise / Month-wise** toggle shows only when more than one mall is in the list. In month-wise mode a mall select uses `property_group_id`. Global region and mall do not apply. | Year select, month select, Mall-wise / Month-wise toggle, mall select. Single-mall users are forced to month-wise. |

#### 4.1 Chart and mapping

**V2: `DivergingBars`** (ui-kit custom).
- Mismatch grows left from the centre in `chartPalettes.binary[1]` `#DC2626`. Match grows right in `binary[0]` `#8B5CF6`.
- **Mall-wise** (`mallWiseRows`):
  - Keep rows with `match_count + mismatch_count > 0`.
  - Sort by `mismatch_count` descending, then `match_count` descending.
  - `id = property_group_id`, `label = marketing_name` (or `marketing_name_ar` in Arabic), `start = mismatch_count`, `end = match_count`.
  - `quiet` is the number of list rows with no reports. It drives the footnote "No reports this month from the other {n} malls".
- **Month-wise** (`monthWiseRows`): 12 rows keyed by `month_index`, labelled with `Intl` short month names.
- Clicking a row opens `MismatchUnitsModal` with `{year, month, propertyGroupId}`.

**Legacy: recharts stacked vertical `BarChart`.**
- X axis is the mall (or the month in month-wise mode). Series `match` is `#00B303`; `mismatch` is `#C72000` with a radius on top. Both share `stackId="units"`.
- It scrolls horizontally, with a minimum width of 650px or 110px per bar.
- Clicking a bar opens `UnitDiscrepancyMismatchModal`.

**API-layer reshaping** (`libs/api/src/lib/discrepancy/discrepancyApi.ts`):
- `getUnitDiscrepancyReport` (`:297`) reads `data.list`, or `data.series` when that is non-empty. Mall rows go through `parseAsMallRows`, which falls back across `match_count/match`, `mismatch_count/mismatch` and `property_group_id/propertyGroupId/property-group-id`. A legacy month-bucket shape (`counts[]`) is also handled by `parseAsMonthMatrix`.
- `getUnitDiscrepancyReportMonthAxis` (`:376`) reads `data.series`. The `month` value `"YYYY-MM"` is parsed by `extractMonthIndex`, then `parseAsTwelveMonthRows` fills all 12 months.
- `getUnitDiscrepancyMonthlyGraphMalls` (`:136`) builds the mall dropdown from `data.summary`, falling back to `data.malls` and then the list.

#### 4.2 APIs called

| # | Frontend fn | Method + path | Query params | When |
|---|---|---|---|---|
| A | `getUnitDiscrepancyMonthlyGraphMalls(year, month)` | `GET /discrepancy/monthly-graph` | `year`, `month` (1–12) | When year or month changes. Uses `data.summary` for the mall list, the toggle and the select. |
| B | `getUnitDiscrepancyReport(year, month)` | `GET /discrepancy/monthly-graph` | `year`, `month` | Mall-wise chart. In V2 this duplicates the request in A. |
| C | `getUnitDiscrepancyReportMonthAxis(year, pgId)` | `GET /discrepancy/monthly-graph` | `year`, `property-group-id` (no month) | Month-wise chart |
| D | `getUnitDiscrepancyMismatchUnits({year, month, propertyGroupId, type:'graph'})` (`discrepancyApi.ts:477`) | `GET /discrepancy/monthly-graph/mismatch-units` | `year`, `month`, `property-group-id`, `type=graph`; `type` is **ignored by the backend**; optional `filter` | Bar or row click |
| – | "View All" link | navigates to `/dashboard/unit-discrepancy-month-wise-report` | | |

#### 4.3 Backend: `GET /discrepancy/monthly-graph`

**Chain:**
- Route: `cenomi-api-2/discrepancy/delivery/http/discrepancy_handler.go:36`.
- Handler `GetMonthlyGraph` (`:137`):
  - `year` must be between 2000 and 2100.
  - `month` is optional (1–12).
  - `property_group_id` / `property-group-id` / `property_group_ids[0]` is read by `parseOptionalPropertyGroupIDQuery` (`:301`).
  - Without a month, a property group id is required.
- Usecase `GetMonthlyGraphData` (`cenomi-api-2/discrepancy/usecase/discrepancy_usecase.go:1296`):
  1. `permitted := getPermittedPropertyGroupIDsForReport` (§0.4).
  2. `summary` is `GetAllMallInfo` when permitted is nil, otherwise `GetMallInfoByPropertyGroupIDs(permitted)`. Errors here are only logged.
  3. With a month: `effective = intersect(permitted, [pgId if given])`. When permitted is non-nil and the intersection is empty, it returns an empty list. Otherwise it calls `GetMallCountsByMonth(year, month, effective)`.
  4. Without a month: it intersects the requested pgId with permitted. When the pgId is not permitted, it returns 12 empty `series` rows. Otherwise it calls `GetMallSeriesByYearPropertyGroup(year, pgId)`.
- Repository (`cenomi-api-2/discrepancy/repository/postgres/discrepancy_repository.go`):
  - `GetMallCountsByMonth` (`:1755`, SQL `queryGetMallCountsByMonth` `:851`). The window is `[YYYY-MM-01, +1 month)` in **UTC**. Arguments: `$1='OPERATIONS'` (sr.category), `$2='DISCREPANCY'` (sr.sub_category), `$3=monthStart`, `$4=monthEnd`, `$5=pq.Array(propertyGroupIDs)` (NULL or empty means all).
  - `GetMallSeriesByYearPropertyGroup` (`:1784`, SQL `queryGetMallCountsByYearPropertyGroup` `:901`). The window is the calendar year in UTC; `$5 = property_group_id`. Go formats `month` as `"YYYY-MM"` and takes the name from the first non-empty row.
  - `GetMallInfoByPropertyGroupIDs` (`:1867`, SQL `:974`) and `GetAllMallInfo` (`:1889`, SQL `:985`).

The predicate `sqlDiscrepancyPayloadIsMismatch` (`:669`) is:

```sql
LOWER(TRIM(COALESCE(d.payload->>'status',''))) = 'mismatch'
OR COALESCE(d.payload->>'store_closed','')          IN ('true','True','1')
OR COALESCE(d.payload->>'wrong_location','')        IN ('true','True','1')
OR COALESCE(d.payload->>'open_without_contract','') IN ('true','True','1')
OR COALESCE(d.payload->>'brand_changed','')         IN ('true','True','1')
```

```sql
-- queryGetMallCountsByMonth (mall-wise). Only the LATEST discrepancy SR per mall in the month counts.
WITH latest_sr_per_mall AS (
  SELECT d.property_group_id, MAX(d.service_request_id) AS latest_sr_id
  FROM cenomi.discrepancy d
  JOIN cenomi.service_request sr ON sr.service_request_id = d.service_request_id AND sr.category = $1 AND sr.sub_category = $2
  WHERE sr.deleted_at IS NULL
    AND sr.created_at >= $3::timestamptz AND sr.created_at < $4::timestamptz
    AND (array_length($5::bigint[], 1) IS NULL OR d.property_group_id = ANY($5))
  GROUP BY d.property_group_id
)
SELECT d.property_group_id, up.marketing_name, up.marketing_name_ar,
       COUNT(*) FILTER (WHERE NOT (<IsMismatch>)
                          AND ( LOWER(TRIM(COALESCE(d.payload->>'status',''))) = 'match'
                                OR ( LOWER(TRIM(COALESCE(d.payload->>'status',''))) NOT IN ('mismatch','pending')
                                     AND UPPER(TRIM(COALESCE(sr.status::text,''))) = 'SUBMITTED')))::bigint AS match_count,
       COUNT(*) FILTER (WHERE <IsMismatch>)::bigint AS mismatch_count,
       COUNT(*)::bigint AS total_count
FROM latest_sr_per_mall lsm
JOIN cenomi.discrepancy d ON d.service_request_id = lsm.latest_sr_id AND d.property_group_id = lsm.property_group_id
JOIN cenomi.service_request sr ON sr.service_request_id = lsm.latest_sr_id
JOIN LATERAL (SELECT u.marketing_name, u.marketing_name_ar FROM cenomi.unique_properties u
              WHERE u.property_group_id = d.property_group_id
              ORDER BY CASE WHEN u.is_primary IS TRUE THEN 0 ELSE 1 END, u.unique_property_id NULLS LAST LIMIT 1) up ON TRUE
WHERE NULLIF(TRIM(up.marketing_name),'') IS NOT NULL
GROUP BY d.property_group_id, up.marketing_name, up.marketing_name_ar
ORDER BY d.property_group_id;
```

```sql
-- queryGetMallCountsByYearPropertyGroup (month-wise, one mall). Latest SR per calendar month.
WITH latest_sr_per_mall_month AS (
  SELECT d.property_group_id, EXTRACT(MONTH FROM (sr.created_at AT TIME ZONE 'UTC'))::int AS cal_month,
         MAX(d.service_request_id) AS latest_sr_id
  FROM cenomi.discrepancy d
  JOIN cenomi.service_request sr ON sr.service_request_id = d.service_request_id AND sr.category = $1 AND sr.sub_category = $2
  WHERE sr.deleted_at IS NULL AND sr.created_at >= $3::timestamptz AND sr.created_at < $4::timestamptz
    AND d.property_group_id = $5
  GROUP BY d.property_group_id, cal_month
),
agg AS (
  SELECT lsm.cal_month,
         COUNT(*) FILTER (WHERE <same match predicate>)::bigint AS match_count,
         COUNT(*) FILTER (WHERE <IsMismatch>)::bigint            AS mismatch_count,
         COUNT(*)::bigint AS total_count
  FROM latest_sr_per_mall_month lsm
  JOIN cenomi.discrepancy d ON d.service_request_id = lsm.latest_sr_id AND d.property_group_id = lsm.property_group_id
  JOIN cenomi.service_request sr ON sr.service_request_id = lsm.latest_sr_id
  GROUP BY lsm.cal_month
)
SELECT m.m::int AS cal_month, COALESCE(n.marketing_name,''), COALESCE(n.marketing_name_ar,''),
       COALESCE(a.match_count,0), COALESCE(a.mismatch_count,0), COALESCE(a.total_count,0)
FROM generate_series(1,12) AS m(m)
LEFT JOIN LATERAL (SELECT u.marketing_name, u.marketing_name_ar FROM cenomi.unique_properties u
                   WHERE u.property_group_id = $5
                   ORDER BY CASE WHEN u.is_primary IS TRUE THEN 0 ELSE 1 END, u.unique_property_id NULLS LAST LIMIT 1) n ON TRUE
LEFT JOIN agg a ON a.cal_month = m.m
ORDER BY m.m;
```

```sql
-- summary (mall dropdown)
SELECT DISTINCT ON (up.property_group_id) up.property_group_id, up.marketing_name, COALESCE(up.marketing_name_ar,'') AS marketing_name_ar
FROM cenomi.unique_properties up
WHERE up.is_primary = true AND up.property_group_id IS NOT NULL      -- GetAllMallInfo
   -- or: WHERE up.property_group_id = ANY($1) AND up.is_primary = true   (GetMallInfoByPropertyGroupIDs)
ORDER BY up.property_group_id;

-- permission helpers
SELECT DISTINCT up.property_group_id FROM cenomi.properties p
JOIN cenomi.unique_properties up ON p.unique_property_id = up.unique_property_id
WHERE p.property_id = ANY($1) AND up.property_group_id IS NOT NULL;           -- queryGetPropertyGroupIDsByPropertyIDs (:966)
SELECT DISTINCT up.property_group_id FROM cenomi.unique_properties up
JOIN cenomi.regions r ON LOWER(up.region) = LOWER(r.region_code)
WHERE r.region_id = ANY($1) AND up.property_group_id IS NOT NULL;             -- queryGetPropertyGroupIDsByRegion (:958)
```

Pending units count only toward `total_count`, not toward `match_count` or `mismatch_count`. The month window is UTC, while other dashboard cards use Asia/Riyadh.

**Response (`domain.DiscrepancyMonthlyGraphResponse`, `cenomi-api-2/domain/discrepancy.go:177`):**

```json
// ?year=2026&month=9
{ "year": 2026, "month": 9,
  "summary": [ { "property_group_id": 3, "marketing_name": "Mall of Dhahran", "marketing_name_ar": "..." } ],
  "list":    [ { "property_group_id": 3, "marketing_name": "Mall of Dhahran", "marketing_name_ar": "...", "match_count": 120, "mismatch_count": 8, "total_count": 131 } ] }
// ?year=2026&property-group-id=3
{ "year": 2026, "property_group_id": 3, "marketing_name": "Mall of Dhahran", "marketing_name_ar": "...",
  "summary": [ ... ],
  "series":  [ { "month": "2026-01", "match_count": 110, "mismatch_count": 4, "total_count": 115 }, ... 12 rows ] }
```

`month`, `summary`, `list` and `series` all use `omitempty`. The `list` only contains malls that have a discrepancy SR in the month, so V2's `quiet` count is usually 0 and the "other malls" footnote rarely shows.

#### 4.4 Backend: `GET /discrepancy/monthly-graph/mismatch-units` (drill-down)

**Chain:**
- Handler `GetMonthlyGraphMismatchUnits` (`discrepancy_handler.go:215`):
  - `year`, `month` and `property_group_id` are required.
  - `filter` must be one of `all|match|mismatch|trading|not_trading`.
  - `type` is not read.
- Usecase `GetMonthlyGraphMismatchUnits` (`discrepancy_usecase.go:1379`):
  1. Permission intersect. When the mall is not permitted, it returns an empty list.
  2. `serviceRequestRepo.GetServiceRequestForDiscrepancyByFilters(year, month, [pgId])` (`cenomi-api-2/servicerequest/repository/service_request_repository.go:2741`, SQL `:816`).
  3. Sort the SRs by id descending.
  4. For each SR, call `GetDiscrepancyForServiceRequest(srID)` (`discrepancy_usecase.go:321`). That runs repo `GetDiscrepancyBreakdown` (`discrepancy_repository.go:1367`, SQL `queryGetDiscrepancyBreakdown` `:271`), plus `GetModifiedDiscrepancies` for EXPANSION or CONTRACTION leases. This is **N+1 queries**, one per SR.
  5. Deduplicate units by `unit_code + pms_property_code`; the newest SR wins.
  6. Set `discrepancy_status` with `graphDiscrepancyStatusLabel` (`:1513`):
     - Mismatch when the status is "mismatch" or any of `store_closed`, `wrong_location`, `open_without_contract` or `brand_changed` is set.
     - Match when the payload or row status is "match".
     - Pending when the status is "pending".
     - Match when the payload status is empty.
     - Otherwise Pending.
  7. Mismatch rows get `discrepancy_sr_number` / `mismatch_sr_number` from `payload.discrepancy_mismatch_service_request_id`.
  8. `trading_status` comes from `payload.trading_status`.
  9. `applyDiscrepancyUnitFilter` applies `filter`.
  10. `parent_sr_number` is the newest SR id.

```sql
-- queryGetServiceRequestForDiscrepancyByFilters ($1='OPERATIONS', $2='DISCREPANCY', $3/$4 = UTC month window, $5 = pg ids)
SELECT sr.service_request_id, sr.tenant_profile_id, sr.property_id, sr.property_ids, sr.category, sr.sub_category, sr.title,
       sr.payload, sr.status, document_id, sr.workflow_id, sr.created_at, sr.updated_at, sr.deleted_at, sr.created_by,
       sr.updated_by, sr.created_for, sr.deleted_by, sr.pms_post_status, sr.pms_post_log, sr.notify_roles
FROM cenomi.service_request sr
WHERE sr.category = $1 AND sr.sub_category = $2
  AND sr.created_at >= $3::timestamptz AND sr.created_at < $4::timestamptz
  AND (array_length($5::bigint[],1) IS NULL
       OR EXISTS (SELECT 1 FROM cenomi.discrepancy d WHERE d.service_request_id = sr.service_request_id AND d.property_group_id = ANY($5)));
```

**`queryGetDiscrepancyBreakdown` (`discrepancy_repository.go:271-592`), summarised:**
- Starting from `cenomi.discrepancy WHERE service_request_id=$1`, it picks the best current lease per unit. It excludes cancelled and future leases. Past-ended leases are kept only when an activated amendment extends them or is HOLDOVER, MODIFICATION or EXPANSION. When several leases remain, occupying leases win.
- It derives `is_currently_active` from the amendment type (TERMINATION, ASSIGNMENT or other) or the lease dates.
- It outputs `jsonb_agg` of discrepancy rows: payload with `trading_start_date` prefilled, `status` (match / mismatch / pending), `pms_unit_code`, `pms_unit_status` (Occupied / Vacant), `unit_type`, brand, lease and the payload flags.
- It also outputs `jsonb_agg` of modified leases.
- Go maps the rows with `mapRawToDiscrepancyServiceRequest`.

The modal is a `DataTable` with these columns:
- Unit Code: `unit_code`
- Unit Type: `unit_type`
- Unit Status: `occupancy_status`
- Status: `discrepancy_status`
- Mismatch SR number: `discrepancy_sr_number`, linked to the SR details page.

**Response (`domain.DiscrepancyMismatchUnitsResponse`, `cenomi-api-2/domain/discrepancy.go:202`):**

```json
{ "year": 2026, "month": 9, "property_group_id": 3, "parent_sr_number": "45678",
  "list": [ { "unit_code": "G-012", "unit_type": "RETAIL", "occupancy_status": "Occupied", "discrepancy_status": "Mismatch",
              "trading_status": "Trading", "discrepancy_sr_number": "45999", "mismatch_sr_number": "45999" } ] }
```

The frontend `mergeGraphUnitLists` would also accept `mismatch_list`, `match_list` or `matched_list`, but the backend only returns `list`.

---

### 5. Observations, quirks and differences

1. **`unit_id` is ignored by `/fitout-summary`.** The legacy unit filter therefore changes nothing in the summary request. The unit view relies on `/unit-fitout-status` instead.
2. **V2 calls `/fitout-summary` twice**, once per fit-out card with independent filters. The `useFitoutSummary` doc comment still says it is shared.
3. **Fit-out summary versus the popup list:**
   - The summary reads only `service_request`, with no `deleted_at` filter.
   - The list drops `ACTIVE` from the remaining bucket and hides APPROVED and REJECTED rows older than 90 days for users without the archive permission.
   - Popup totals can therefore differ from ring and bar counts.
4. **The `/fitout-summary` filter queries bind `$6 = PropertyIDs`.** When that is nil (unrestricted users), `p.property_id = ANY(NULL)` returns no rows, so `filters.*` comes back empty. Legacy dropdowns may then be empty, which V2 does not depend on.
5. **Range validation compares `DD-MM-YYYY` strings lexically** (`dateFromParam > dateToParam`), which is wrong across months and years. This affects both the fitout-summary and document-status handlers.
6. **Document status `last_synced_at` is always the request time.**
7. **Document status reads the 3 SR tables** (hot plus 2 archive tables), uses Asia/Riyadh for year and month, and rolls sub-properties up to the primary mall. The fitout summary uses only the hot table and the raw `unique_property_id`, so the two cards' mall attribution can differ.
8. **The by-document-type response has no `document_name_ar`.** Arabic labels come from master data on the client.
9. **The discrepancy graph uses UTC month windows and only the latest SR per mall and month.** Pending units count only toward `total_count`.
10. **V2 discrepancy fetches `discrepancy/monthly-graph?year&month` twice** in mall-wise mode: once for the malls and once for the chart.
11. **The mismatch-units drill-down is N+1.** It runs the heavy breakdown query once per discrepancy SR in the month. The `type=graph` param is unused.
12. **`/units-with-fitout` and `/unit-fitout-status` apply no user property scoping**, and `units-with-fitout` returns every unit in the mall regardless of fit-out SRs.
13. **Nothing in these endpoints is cached** (no Redis or in-memory caching found) and none calls an external service.

---

## 5. Tenant Dashboard

Route: `/dashboard` in the tenant web app. Page component: `cenomi-frontend-2/apps/cenomi-tenant-web/app/(state)/(main)/dashboard/page.tsx`.

### 0. Page-level wiring

**Render decision** (`page.tsx`):

| Condition | Renders |
|---|---|
| `VIEW_DASHBOARD` permission missing | redirects to `/dashboard/servicerequest?sort_by=updated_at&order=DESC` and renders `<Forbidden/>` |
| `user.userType === 'TENANT' && !user.IsProspective && isUiV2Enabled()` | `<SurveyIndicator variant="v2"/>` + `<TenantDashboardV2 summary={summary}/>` |
| `user.userType === 'TENANT' && !user.IsProspective` (v2 flag off) | `<SurveyIndicator/>` + legacy `<TenantDashboard summary={summary}/>` |
| `user.userType === 'TENANT' && user.IsProspective` | `<SurveyIndicator/>` + `<ProspectiveTenant summary={summary}/>` (legacy only, no v2; spec decision 7) |

`isUiV2Enabled()` comes from `apps/cenomi-tenant-web/app/(state)/(main)/_shell/isUiV2Enabled.ts` (feature flag with a localStorage override).

**The page makes one call itself**: `getSummary(tenantProfileId)` (see §1 below), when `state.auth.user.TenantProfileID` is set, and passes `data.list` down as `summary`. Both V2 and legacy reuse it.

**How requests reach the Go API** — every call goes through `httpRequest` (`cenomi-frontend-2/libs/api/src/lib/API_Handler/API_Handler.ts:2`):
- URL = `${NEXT_PUBLIC_API_BASE_PATH}/${url}`. In dev `NEXT_PUBLIC_API_BASE_PATH='/backend_api'`, and `apps/cenomi-tenant-web/next.config.js:38` rewrites `/backend_api/:path*` → `http://localhost:8000/v1/:path*`. In staging and prod it is an absolute `https://<host>/api/v1`. **So every dashboard call goes straight to the Go backend under `/v1/...`.**
- `credentials: 'include'` (session cookie), `cache: 'no-store'`.
- When `localStorage.user_type === 'TENANT'`, it adds the header `x-active-tenant-profile-id: <localStorage.tenant_profile_id>`. On the Go side, `cenomi-api-2/internal/middleware/middleware.go:292-300` (`SetContextUserData`) **overwrites `SSOUser.TenantProfileID` with this header value**. The session itself comes from `resolveUserInfo` (`middleware.go:331`), which reads the Redis session cache, or the in-memory `RequestIDToDataMap` when the cache is off. The middleware does not check that the header's profile belongs to the user; later checks such as `GetPermittedItems` limit what that profile can see.
- If the response says `failed to extract cookies: http: named cookie not present`, the browser is sent to `/signin`.
- The client does not cache anything. Redux holds notifications and announcements.

**Next.js BFF routes are NOT used by the dashboard.** The routes under `apps/cenomi-tenant-web/app/api/**` (for example `app/api/dashboard/route.ts`, `app/api/summary-data/[tenant_id]/route.ts`, `app/api/service-request-summary`) serve `/api/...`. They are **static mock routes** that return hard-coded JSON: `dashboard/route.ts` POST returns `{dashboarddata:[{tenant_dues:3134,service_requests:212,lease_expiries:2}]}`, and `summary-data/[tenant_id]` returns a fixed summary with `leases:16, units:77, …`. The `httpRequest` base path never points at them, so they are dead code for this page. There is also no `app/api/announcements-events/dashboard-summary` route. That call goes to Go.

**Popups.** `LoyaltyPopup`, `LoyaltyEmailPopup`, `SukukPromotionalPopup`, `RamadanPromotionalPopup` and `AnnouncementPopup` (`libs/ui-web/src/lib/components/dashboards/common/*`) are **not mounted**. Their uses and the matching `getConfigData('LOYALTY_CONFIG' | 'SUKUK_CONFIG')` calls in `apps/cenomi-tenant-web/app/(state)/app.tsx:30-135,264-281` are commented out. `ServiceHistory.tsx` (`getServiceRequests(1,5)`) and `Notifications.tsx` (`getNotifications(1,5,false)`) under `dashboards/tenant/` are not referenced by either dashboard.

#### Call inventory

| # | Frontend fn (file) | Method + path (Go, under `/v1`) | Caller(s) | When |
|---|---|---|---|---|
| A | `getSummary` (`libs/api/src/lib/summary/summaryApi.ts:4`) | `GET /summary-data/{tenantProfileId}` | page.tsx (V2 + legacy + prospective) | mount, when TenantProfileID is set |
| B | `getServiceRequestsFromQuery` (`libs/api/src/lib/service_requests/serviceRequestApi.ts:31`) | `GET /service-requests?page=1&limit=200[&mall=<property_name>]` | V2 `useTenantServiceRequests` | mount + each mall change (needs `SERVICE_REQUEST_LIST`) |
| B' | `getServiceRequestsPaginated` (`serviceRequestApi.ts:59`) | `GET /service-requests?page=1&limit=1` then `GET /service-requests?page=1&limit=<total_count>` | legacy `PieChart` and `SRPieChart` (each one does both calls) | mount of each pie (toggling By status / By SR type remounts the pie and refetches) |
| C | `getSalesListingData` (`libs/api/src/lib/salesdata/salesdataApi.ts:28`) | `GET /sales-data?page=1&limit=1&tenant_profile_id=X&sales_period_start=Y-01-01&sales_period_end=Y-12-31&status=PENDING,NEED_REUPLOAD,NEED_UPLOAD_SUPPORTING_DOCUMENT,NEED_UPLOAD_AUDITED_SALES` and the same with `status=APPROVED` | V2 `useTenantSalesCounts` (2 parallel calls) | mount + year change (needs `SALES_DATA_LIST`) |
| C' | same | `GET /sales-data?page=1&limit=200&tenant_profile_id=X&sales_period_start=Y-01-01&sales_period_end=Y-12-31[&lease_code=<pms_tenant_code>]` | V2 `useTenantSales` | mount + year or lease change |
| C'' | same | `GET /sales-data?page=1&limit=1&status=PENDING,NEED_REUPLOAD,NEED_UPLOAD_SUPPORTING_DOCUMENT,NEED_UPLOAD_AUDITED_SALES&tenant_profile_id=X` and `...&status=APPROVED&...` (no period) | legacy `TenantDashboard` | mount (always, even without permission) |
| C''' | `getSalesGraphData` (`salesdataApi.ts:36`, `GET_SALES_GRAPH_DATA`) | `GET /sales-data?page=1&limit=100&sales_period_start=YYYY-01-01&sales_period_end=YYYY-12-31&lease_code=<code>&tenant_profile_id=X` | legacy `SaleBarChart` | after the lease list loads; on lease or year change |
| D | `getLeases` (`libs/api/src/lib/tenantProfileLeases/leasesApi.ts:15`) | `GET /contracts?limit=200` | V2 `useTenantLeaseMalls` | mount (always) |
| D' | same | `GET /contracts?status=ACTIVATED,SUPERSEDED&limit=1000` | legacy `SaleBarChart` | mount |
| E | `getNotifications(page,limit,true)` (`libs/api/src/lib/notifications/notificationApi.ts:10`) via the redux thunk `fetchNotification` (`libs/app-state/src/lib/features/Notification/notificationSlice.ts:23`) | `GET /notifications?page=1&limit=15&is_action_required=true` | V2 `TenantActionRequiredCard`, legacy `ActionRequired`, prospective | mount; legacy infinite scroll asks for `page=2,3,…` |
| F | `getAnnouncementAndEventsDashboardData` (`libs/api/src/lib/anouncementAndEvents/anouncementAndEvents.ts:18`) via the thunk `fetchAnnouncementAndEventsDashboardSummary` (`libs/app-state/src/lib/features/AnnouncementAndEvents/AnnouncementAndEventsSlice.tsx:106`) | `GET /announcements-events/dashboard-summary?announcement_limit=5` | V2 `TenantAnnouncementsCard`, legacy `AnnouncementAndEventsSection` | mount |
| G | `getUniquePropertiesData` (`libs/api/src/lib/properties/propertiesApi.ts:32`) | `GET /unique-properties?page=1&limit=100` | V2 `useTenantOpportunities` | mount |
| G' | same | `GET /unique-properties?page=N&limit=6` (N=1,2,… on "View More") | legacy `LeasingOpportunities`, prospective | mount + View More |
| H | `getConfigData('NEW_SURVEY')` (`libs/api/src/lib/configuration/configurationApi.ts:8`) | `GET /configuration/NEW_SURVEY` | `SurveyIndicator` (both variants) | mount, tenants only |
| I | raw `httpRequest(LEAD_ENQUIRIES…)` in `TenantStatus` | `GET /lead-enquiries?tenant_profile_id=X` then `GET /lead-enquiries/details?lead_enquiry_code=..&lead_enquiry_id=..` | prospective only | mount |

Endpoint constants: `cenomi-frontend-2/libs/api/src/lib/endPoints.ts` (`SUMMARY_ENDPOINT:144`, `SERVICE_REQUEST_ENDPOINT:36`, `SERVICE_REQUEST_ENDPOINT_PAGINATED:61`, `SALES_DATA:79`, `GET_SALES_GRAPH_DATA:135`, `CONTRACTS_ENDPOINT:133`, `NOTIFICATION_ENDPOINTS:27`, `ANNOUNCEMENT_AND_EVENTS_DASHBOARD_SUMMARY:278`, `UNIQUE_PROPERTIES_SEARCH_ENDPOINT:17`, `CONFIGURATION:290`, `LEAD_ENQUIRIES:72`, `GET_ADMIN_LEADS:71`).

#### V2 layout & gating

`cenomi-frontend-2/libs/ui-web/src/lib/components/dashboards/tenant/v2/tenantDashboardLayout.ts`:

| Row | Cards (12-column span) |
|---|---|
| 1 | `tiles` (8), `actionRequired` (4) |
| 2 | `sales` (7), `serviceRequests` (5) |
| 3 | `documents` (5), `announcements` (7) |
| 4 | `opportunities` (12) |

When one card in a row is hidden, its partner takes 12 columns. An empty row is dropped. Between 1024 and 1279px every card spans 6 (12 for full-width cards).

`visibleTenantCards(permissions)`:
- `tiles`: when at least one tile is visible (always true, because Profile is never gated)
- `actionRequired`: `canViewActionRequiredWidget(perms)` (`libs/ui-web/src/lib/utils/contractorPermissionCatalog.ts:33`). It is true unless the "contractor permission catalog" is provisioned (that is, the user holds any of `VIEW_NOTIFICATIONS`, `VIEW_DASHBOARD_WORK_PERMIT_CHART`, …). When provisioned it needs `ACTION_REQUIRED_WIDGET`.
- `serviceRequests`: `SERVICE_REQUEST_LIST`
- `sales`: `SALES_DATA_LIST`
- `documents`: `VIEW_DOCUMENT`
- `announcements`, `opportunities`: always shown

Greeting (V2): `Hi, <first name>` plus the company name. The company name is `companyName(leases)` from `tenantFilters.ts`: the first non-empty `company`/`company_ar` on the `/contracts` rows (call D). The fallback is the translation `TenantPlatformTitle`. The right-hand line is `"{summary.leases} leases · {summary.units} units"`.

There is no page-level filter bar. State lives in `TenantDashboardV2.tsx`:
- `requestsMall` (string | null): the Service Requests card's mall select
- `salesYear` (number, default current year): the Sales card's year select
- `salesLease` (string | null): the Sales card's lease select

---
### 1. KPI tiles / link cards (+ the shared `summary-data` call)

| | V2 | Legacy |
|---|---|---|
| Component | `TenantTiles` in `v2/TenantTileRow.tsx`; model `v2/tenantTiles.ts` | `cards[]` in `tenant/tenantDashboard.tsx` rendered by `LinkCards.tsx` / `LinkCardDetails.tsx` |
| Visual | `StatTile` (ui-kit, plain HTML) grid: 3 across on xl, 2 on sm, sideways scroll on phones. One big value, a description, a hue and an icon | White cards with an image icon and `label: value` detail lines |
| Visibility | `visibleTenantTiles` (below) | filtered twice (spec bug #5): by `item.permission` (any-of), then by a render-time `Map` (Sales Data→`SALES_DATA_LIST`, Leases→`VIEW_CONTRACTS`, Service Requests→`SERVICE_REQUEST_LIST`) |

**V2 tiles** (order, value, description, link, gate):

| Tile | Value | Description | href | Gate |
|---|---|---|---|---|
| leases (violet) | `summary.leases` | "`{units}` units · `{brands}` brands" | `/dashboard/leases` | `VIEW_CONTRACTS` |
| documents (rose) | `summary.pending_documents` | static | `#tenant-documents` (scrolls to the Documents card) | `VIEW_DOCUMENT` |
| serviceRequests (sky) | `requests.open`, from call B (not the summary) | "of `{total}`", where total = `counts.total`; help tip | `/dashboard/servicerequest` | `SERVICE_REQUEST_LIST` |
| sales (teal) | `sales.pending` (call C, PENDING bucket, selected year) | "`{approved}` approved" (call C, APPROVED) | `/dashboard/salesdata` | `SALES_DATA_LIST` |
| leaseRequests (violet) | `summary.pending_inquiries` | "`{approved_inquiries}` approved" | `/dashboard/leaserequest` | any of `LEAD_INQUIRY_LIST`, `VIEW_PROPOSALS`, `VIEW_CONTRACTS` |
| profile (teal) | `summary.brands` | static | `/tenantprofile` | none |
| payments (no hue) | always `—` (the API's payment fields are hard zeros, ticket T1) | static + help | `/dashboard/payment` | `VIEW_BILLING_AND_PAYMENTS` |

`formatTileValue`: null, undefined or non-finite becomes `—`; otherwise `formatCount` (Intl). Tiles show a loading state while B or C is in flight.

Derivations:
- `requests.open` = rows whose `status` (trimmed, upper-cased) is non-empty and not in {APPROVED, REJECTED, CLOSED, COMPLETED, CANCELLED, EXPIRED} (`serviceRequestModel.ts isOpen`).
- `requests.total` = `max(total_count, rows.length)`.
- `sales.pending` / `sales.approved` = `countOf(res)`: `data.total_count` when it is > 0, otherwise `data.list.length`.

**Legacy cards**:

| Card | Detail lines | Link | Gate |
|---|---|---|---|
| Leases | Leases=`summary.leases`, Units=`summary.units` | `dashboard/leases` | `VIEW_CONTRACTS` |
| Documents | Pending=`summary.pending_documents`. The info-icon tooltip lists Inquiry (`pending_inquiry_documents.pending_count`) → `/dashboard/inquirydetails?inquiryId={enquiry_id}`, Operations (`pending_operations_documents.pending_count`) → `/dashboard/leases/leasedetails?contractId={lease_id}&active_tab=Documents`, and Fit-out (`pending_drawing_documents.pending_count`, needs `VIEW_FIT_OUT_HANDOVER`) → `...&active_tab=Fitout` | `dashboard/tenant/document?tenantId=X` | `VIEW_DOCUMENT` |
| Payments | Completed=0, Pending=0 (literals) | `dashboard/payment` | `VIEW_BILLING_AND_PAYMENTS` |
| Service Requests | Approved=`summary.approved_service_requests`, Pending=`summary.pending_service_requests` | `dashboard/servicerequest?sort_by=updated_at&order=DESC` | `SERVICE_REQUEST_LIST` (Map only) |
| Sales Data | Approved / Pending = `total_count` of call C'' (no year filter, all time) | `dashboard/salesdata` | `SALES_DATA_LIST` |
| Lease Requests | Approved=`approved_inquiries`, Pending=`pending_inquiries` | `dashboard/leaserequest` | `LEAD_INQUIRY_LIST`/`VIEW_PROPOSALS`/`VIEW_CONTRACTS` |
| Tenant Profile | Brands=`summary.brands` | `/tenantprofile?tenantId=X` | none |

#### API A — `GET /v1/summary-data/{tenant-profile-id}`

- Frontend: `getSummary(tenantId)` → `SUMMARY_ENDPOINT 'summary-data/{0}'`. Called once in `page.tsx`. The result is `res.data.list` (typed `SummaryType` in `@cenomi-frontend/api`).
- Route: `cenomi-api-2/tenantsummary/delivery/http/tenant_summary_handler.go:23`, wired in `cenomi-api-2/app/main.go:2575-2577`.
- Handler `List`: `tenant_summary_handler.go:27`.
  - It needs `SSOUser` in the context (401 otherwise).
  - The path id must parse and be non-zero (400 otherwise).
  - **`userData.TenantProfileID` (from the `x-active-tenant-profile-id` header) must equal the path id**, or the handler returns 401.
  - It maps the result with `TenantSummaryDTO.MapFromDomain`.
- Usecase `Fetch`: `cenomi-api-2/tenantsummary/usecase/tenant_summary_usecase.go:26`. It calls `tenantContactUsecase.GetPermittedItems(ctx,user)` and passes `permittedItems.Leases` as `$9`.
- Repository `Fetch`: `cenomi-api-2/tenantsummary/repository/postgres/tenant_summary_repository.go:291`. It runs one `QueryRow` with 12 params.

**Lease-permission pre-query** (`GetPermittedItems`):
- Usecase `cenomi-api-2/tenant_contact/usecase/tenant_contact_usecase.go:852` → `getPermittedItems:868`.
- Repository `cenomi-api-2/tenant_contact/repository/postgres/tenant_contacts_repository.go:2029`, using `queryAggregateTenantContacts` at `:60`.

```sql
-- $1 = user_id; tenant users add the "%s" exclusion; $2 = active tenant_profile_id
SELECT
  ARRAY(SELECT DISTINCT lease_id FROM tenant_contacts
        WHERE tenant_contact_user_id = $1 AND lease_id IS NOT NULL
          AND tenant_profile_id NOT IN (SELECT tenant_profile_id FROM tenant_contacts
                                        WHERE tenant_contact_user_id = $1 AND lease_override = 0)) AS lease_ids,
  ARRAY(SELECT DISTINCT tenant_profile_id FROM tenant_contacts
        WHERE tenant_contact_user_id = $1 AND tenant_profile_id = $2) AS tenant_profile_ids,
  ARRAY(SELECT DISTINCT property_id FROM tenant_contacts WHERE tenant_contact_user_id = $1 AND property_id IS NOT NULL) AS property_ids,
  ARRAY(SELECT DISTINCT region_id   FROM tenant_contacts WHERE tenant_contact_user_id = $1 AND region_id IS NOT NULL)   AS region_ids,
  MAX(lease_override) AS lease_override, MAX(property_override) AS property_override, MAX(company_override) AS company_override
FROM tenant_contacts
WHERE tenant_contact_user_id = $1 AND tenant_profile_id = $2
GROUP BY tenant_contact_user_id;
```

How the `%s` placeholders are filled (`tenant_contacts_repository.go:2029-2056`):
- `ScopeAllCompanies` sessions use `tenant_profile_id = ANY($2::bigint[])`.
- When there is no active profile, the filter is `tenant_profile_id IS NOT NULL`.

Non-admin follow-up in Go: when the user has no explicit leases and no override, or `lease_override = OverrideAll`, Go also runs `queryFetchLeasesByCompany` (`cenomi-api-2/lease/repository/postgres/lease_repository.go:507`):

```sql
SELECT lease_id, property_id FROM cenomi.leases WHERE tenant_profile_id = ANY($1);  -- $1 = companies[]
```

It appends those lease ids to the list. It then fetches proposal ids by lease (`proposal_repository.go:1369`; not used here) and forces `Companies = [TenantProfileID]`.

**Summary SQL** (`tenant_summary_repository.go:27-287`, verbatim):

```sql
WITH amendment_summary AS (
  SELECT lua.lease_id,
    MIN(CASE WHEN lua.amendment_type = 'Termination' AND lua.amendment_status = 'Activated' THEN lua.amendment_start END) AS termination_start_date,
    MAX(CASE WHEN lua.amendment_type = 'Renewal' AND lua.amendment_status = 'Activated' THEN lua.amendment_end END) AS renewal_end_date
  FROM cenomi.leased_units_amendments lua
  WHERE lua.amendment_status = 'Activated' AND lua.amendment_type IN ('Termination', 'Renewal')
  GROUP BY lua.lease_id
),
effective_end_date_calc AS (
  SELECT l.lease_id, l.end_date AS original_end_date, l.contract_status,
    (ams.termination_start_date IS NOT NULL) AS has_active_termination, ams.termination_start_date,
    (ams.renewal_end_date IS NOT NULL) AS has_active_renewal, ams.renewal_end_date
  FROM cenomi.leases l LEFT JOIN amendment_summary ams ON l.lease_id = ams.lease_id
),
lease_summary AS (
  SELECT COUNT(l.lease_id) AS number_of_leases
  FROM cenomi.leases l
  JOIN effective_end_date_calc eed ON l.lease_id = eed.lease_id AND (
    CASE WHEN eed.has_active_termination THEN NOW()::date <= eed.termination_start_date + INTERVAL '30 days'
         WHEN eed.has_active_renewal     THEN NOW()::date <= eed.renewal_end_date + INTERVAL '30 days'
         ELSE (l.contract_status = 'Activated' AND l.end_date >= NOW()::date) OR NOW()::date <= l.end_date + INTERVAL '30 days'
    END)
  WHERE l.tenant_profile_id = $1 AND l.lease_id = ANY($9) AND l.contract_status = 'Activated'
),
lease_units_count AS (
  WITH extracted_leases AS ( /* same lease filter as lease_summary, selecting l.lease_id */
    SELECT l.lease_id FROM cenomi.leases l
    JOIN effective_end_date_calc eed ON l.lease_id = eed.lease_id AND ( /* same CASE */ )
    WHERE l.tenant_profile_id = $1 AND l.lease_id = ANY($9) AND l.contract_status = 'Activated')
  SELECT COUNT(leased_units.leased_unit_id) AS number_of_units
  FROM cenomi.leased_units
  WHERE leased_units.lease_id = ANY(SELECT lease_id FROM extracted_leases)
),
approved_document_summary AS (
  WITH extracted_data AS (
    SELECT jsonb_array_elements(value::jsonb) ->> 'id' AS id_value
    FROM essential_data WHERE key = 'REQUIRED_DOCUMENTS')
  SELECT count(DISTINCT document_type_id) AS approved_document_count
  FROM documents
  WHERE document_type_id IN (SELECT id_value FROM extracted_data) AND tenant_profile_id = $1
),
lead_enquiry_summary AS (
  SELECT COUNT(CASE WHEN approval_status = $2  THEN lead_enquiry_id END) AS lead_enquiry_approved_count,
         COUNT(CASE WHEN approval_status != $2 THEN lead_enquiry_id END) AS lead_enquiry_pending_count
  FROM lead_enquiries WHERE tenant_profile_id = $1
),
brand_summary AS (
  SELECT COUNT(DISTINCT b.pms_brand_code) AS brands
  FROM brands b LEFT JOIN leases l ON l.brand_id = b.brand_id
  WHERE l.tenant_profile_id = $1 AND LOWER(l.contract_status) = ANY(ARRAY['activated'])
    AND l.end_date > now() AND l.lease_id = ANY($9)
),
sales_data_summary AS (
  SELECT COUNT(CASE WHEN status = ANY($3) THEN sales_data_id END) AS pending_sales_data_count,
         COUNT(CASE WHEN status = $4      THEN sales_data_id END) AS approved_sales_data_count
  FROM sales_data WHERE tenant_profile_id = $1
),
service_request_summary AS (
  SELECT COUNT(CASE WHEN status = $5 THEN service_request_id END) AS pending_service_request_count,
         COUNT(CASE WHEN status = $5 AND category = $7 AND sub_category = $8 THEN service_request_id END) AS pending_profile_update_service_request_count,
         COUNT(CASE WHEN status = $6 THEN service_request_id END) AS approved_service_request_count
  FROM service_request WHERE tenant_profile_id = $1
),
pending_lease_documents_summary AS (
  SELECT COUNT(dd.request_id) AS pending_count,
    COALESCE((SELECT dd.lease_id FROM draft_documents dd
              JOIN leases l ON dd.lease_id = l.lease_id
              JOIN document_types dt ON dd.document_type_id = dt.document_type_id
              WHERE l.tenant_profile_id = $1 AND dd.status = ANY($10) AND dt.category = 'Operations_Draft'
              ORDER BY COALESCE(dd.updated_at, dd.created_at) DESC LIMIT 1), 0) AS latest_lease_id
  FROM draft_documents dd
  JOIN leases l ON dd.lease_id = l.lease_id
  JOIN document_types dt ON dd.document_type_id = dt.document_type_id
  WHERE l.tenant_profile_id = $1 AND dt.category = 'Operations_Draft' AND dd.status = ANY($10) AND dd.lease_id = ANY($9)
),
pending_inquiry_documents_summary AS (
  SELECT COUNT(document_id) AS pending_count,
    COALESCE((SELECT cd.enquiry_id::text FROM company_documents cd
              WHERE cd.tenant_profile_id = $1 AND cd.approval_status = ANY($11)
              ORDER BY cd.updated_at DESC LIMIT 1), '') AS latest_enquiry_id
  FROM company_documents
  WHERE is_additional_document = true AND approval_status = ANY($11) AND tenant_profile_id = $1
),
pending_fitout_drawings_summary AS (
  SELECT COUNT(dd.request_id) AS pending_count,
    COALESCE((SELECT dd.lease_id FROM draft_documents dd JOIN leases l ON dd.lease_id = l.lease_id
              WHERE l.tenant_profile_id = $1 AND dd.status = ANY($12) AND dd.document_type_id ILIKE('DR%DRW%')
              ORDER BY COALESCE(dd.updated_at, dd.created_at) DESC LIMIT 1), 0) AS latest_lease_id
  FROM draft_documents dd JOIN leases l ON dd.lease_id = l.lease_id
  WHERE l.tenant_profile_id = $1 AND dd.status = ANY($12) AND dd.document_type_id ILIKE('DR%DRW%')
)
SELECT number_of_leases, number_of_units, approved_document_count, lead_enquiry_approved_count, lead_enquiry_pending_count,
       brands, approved_sales_data_count, pending_sales_data_count, pending_service_request_count, approved_service_request_count,
       pending_profile_update_service_request_count,
       pending_lease_documents_summary.pending_count, pending_lease_documents_summary.latest_lease_id,
       pending_inquiry_documents_summary.pending_count, pending_inquiry_documents_summary.latest_enquiry_id,
       pending_fitout_drawings_summary.pending_count, pending_fitout_drawings_summary.latest_lease_id
FROM lease_summary, lease_units_count, approved_document_summary, lead_enquiry_summary, brand_summary,
     sales_data_summary, service_request_summary, pending_lease_documents_summary,
     pending_inquiry_documents_summary, pending_fitout_drawings_summary;
```

Parameters (`tenant_summary_repository.go:296-330`; values from `cenomi-api-2/internal/constants/constants.go`):

| Param | Value |
|---|---|
| `$1` | tenantProfileID |
| `$2` | `'LEAD_APPROVED'` |
| `$3` | `{PENDING, NEED_REUPLOAD, UPLOADED_SUPPORTING_DOCUMENT, NEED_UPLOAD_AUDITED_SALES}` (this differs from the frontend's pending bucket, which uses NEED_UPLOAD_SUPPORTING_DOCUMENT; ticket T4) |
| `$4` | `'APPROVED'` |
| `$5` | `'IN_PROCESS'` |
| `$6` | `'APPROVED'` |
| `$7` | `'TENANT_PROFILE'` |
| `$8` | `'COMPANY_DOC_REQUEST_UPDATE'` |
| `$9` | permitted lease ids |
| `$10` | `{'Requested','Requested Re-upload','Pending'}` |
| `$11` | `{'REQUESTED','RE_REQUESTED','NEED_REUPLOAD'}` |
| `$12` | `{'Requested','Requested Re-upload','Submitted'}` |

Scoping notes:
- Leases, units, brands and operations documents are limited to the permitted leases (`$9`).
- Lead enquiries, sales data, service requests, inquiry documents, fit-out drawings and approved documents are scoped by `tenant_profile_id` only.
- The `latest_*` deep-link subqueries leave out some of their count's filters. The operations subquery drops `$9`, and the inquiry subquery drops `is_additional_document` (ticket T6).

Go post-processing:
- `TenantSummaryDTO.MapFromDomain` (`cenomi-api-2/domain/tenantsummarydto.go:30`) sets `pending_documents = operations.pending_count + inquiry.pending_count + drawings.pending_count`.
- `completed_payments` and `pending_payments` are never selected, so they are always 0.
- No caching. No external calls.

Response (`domain/tenantsummarydto.go:4`, `domain/tenantsummary.go:8-23`):

```json
{ "success": true, "data": { "list": {
  "leases": 3, "units": 5, "approved_documents": 4, "pending_documents": 3,
  "pending_operations_documents": { "pending_count": 1, "lease_id": 9312 },
  "pending_inquiry_documents":    { "pending_count": 1, "enquiry_id": "bf95c45a-..." },
  "pending_drawing_documents":    { "pending_count": 1, "lease_id": 9312 },
  "completed_payments": 0, "pending_payments": 0,
  "approved_service_requests": 5, "pending_service_requests": 43,
  "pending_profile_update_service_requests": 0,
  "approved_sales_data": 10, "pending_sales_data": 2,
  "approved_inquiries": 0, "pending_inquiries": 1, "brands": 2 } } }
```

---
### 2. Documents to upload

| | V2 | Legacy |
|---|---|---|
| Component | `v2/TenantDocumentsCard.tsx`; model `v2/tenantDocuments.ts` | Tooltip under the "Documents" link card in `tenantDashboard.tsx` (opens from the info icon; `hoveredCard` is one boolean shared by every card, spec bug #6) |
| Visibility | `VIEW_DOCUMENT` | `VIEW_DOCUMENT` |
| Visual | `ChartCard` with a list of linked rows (label, count, arrow), plus a violet footer band showing the total. Anchor id `tenant-documents` | List of three clickable rows |
| API | none of its own; reads `summary` (API A) | same |

V2 `documentGroups(summary, permissions, t)` builds three rows and drops any row whose count is 0:

| Row | Count | Deep link (only when count == 1 and the id is truthy) | Otherwise |
|---|---|---|---|
| Operations | `pending_operations_documents.pending_count` | `/dashboard/leases/leasedetails?contractId={lease_id}&active_tab=Documents` | `/dashboard/leases` |
| Inquiry | `pending_inquiry_documents.pending_count` | `/dashboard/inquirydetails?inquiryId={enquiry_id}` | `/dashboard/leaserequest?section=Inquiry&page=1&limit=10&sort_by=created_at&order=DESC` |
| Drawings (only with `VIEW_FIT_OUT_HANDOVER`) | `pending_drawing_documents.pending_count` | `.../leasedetails?contractId={lease_id}&active_tab=Fitout` | `/dashboard/leases` |

- Band value: `documentsWaiting(summary) = summary.pending_documents`, or `—` when there is no summary.
- The card is empty only when there are no rows and `pending_documents` is falsy. When there is a total but no visible row (fit-out hidden by permission), it shows a "hidden" note.
- Legacy always deep-links with the summary id, whatever the count.

---
### 3. Service requests (By status / By category)

| | V2 | Legacy |
|---|---|---|
| Component | `v2/TenantServiceRequestsCard.tsx`; hook `v2/useTenantServiceRequests.ts`; model `v2/serviceRequestModel.ts` | `CardLayout` "Service Requests" in `tenantDashboard.tsx` with a toggle between `StatusPieChart` (wraps `tenant/PieChart.tsx`) and `TypePieChart` (wraps `tenant/SRPieChart.tsx`) |
| Visibility | `SERVICE_REQUEST_LIST` | `SERVICE_REQUEST_LIST` |
| Filters | Mall `Select`, built from the `/contracts` rows (call D) by `mallOptions()`. It offers "All my malls" plus each distinct `property_name`; the label is `property_name_ar` in Arabic and the value is always the English `property_name`. It only shows when there is more than one option. Choosing a mall refetches with `&mall=<value>`. The `SegmentedControl` view switch is client-side only | none |
| Chart | By status: ui-kit `Donut` (in-house SVG, size 236) with a centre total. By category: ui-kit `Treemap` (in-house, `minShare=0.08`) plus a category/count strip underneath | `react-chartjs-2` `Doughnut` (chart.js + `chartjs-plugin-datalabels`) |
| Header meta | "`{total}` total · `{open}` open" (from `counts`) | — |
| Links | "All" → `/dashboard/servicerequest` | — |

**V2 data mapping** (`serviceRequestModel.ts`). The rows come from `data.list[]` of call B; fields read are `status`, `service_category`, `mall`, `service_request_id`.
- `statusKey(status)` = trimmed upper-case, with aliases `IN_PROCESS`/`IN_PROGRESS` → `PENDING`.
- **Donut slices** (`statusSlices`) follow the fixed reading order SUBMITTED, RE_SUBMITTED, PENDING, ACTION_REQUIRED, REPORT_SUBMITTED, APPROVED, REJECTED, EXPIRED. Each slice has value = count of rows, label = `t(status)`, and colour from `STATUS_COLORS`:
  - SUBMITTED and RE_SUBMITTED: `pipeline3[0]` #0284C7
  - PENDING: `pipeline3[1]` #F59E0B
  - ACTION_REQUIRED: `categorical4[3]` #F43F5E
  - REPORT_SUBMITTED: `categorical4[0]` #8B5CF6
  - APPROVED: `pipeline3[2]` #059669
  - REJECTED: `outcome4[3]` #DC2626
  - EXPIRED: token `ink-3`
  - Every other status is summed into an "Other" slice coloured `chartNeutral` #E5E7EB, so the ring always equals `rows.length`.
- **Treemap** (`categoryGroups`): one group per `service_category` (blank → Other), sorted by size descending. Each group has one leaf per status key, value = count, coloured with `statusColor(status)`.
- **Category strip** (`categoryCounts`): `[{label: t(category), value}]`, sorted descending.
- **Counts** (`countServiceRequests`):
  - `open` = rows not in the terminal set {APPROVED, REJECTED, CLOSED, COMPLETED, CANCELLED, EXPIRED}
  - `total` = `max(total_count, rows.length)`
  - `truncated` = `total > rows.length`
- The tile and the card share this one call.
- Card states: `loading`, `error` (retry re-runs `load`), and `empty` when the list is ready with 0 rows.

**Legacy data mapping**:
- `PieChart`: calls B' twice (limit=1 to read `total_count`, then limit=total_count to get every row). It counts only `status` ∈ {IN_PROCESS, APPROVED, REJECTED, ACTION_REQUIRED}.
  - Labels: In Process / Approved / Rejected / Action Required
  - Colours: `#8316FF`, `#C030D6`, `#FF8680`, `#BB7FFF`
  - Zero slices are removed, and the total is the sum of these four only.
- `SRPieChart`: the same two calls again. It counts `service_category` ∈ {INQUIRY, WORK_PERMIT, COMPLAINTS, WORK_REQUEST, LEASE_AMENDEMENT}.
  - Colours: `#8316FF`, `#BB7FFF`, `#FF8680`, `#C030D6`, `#FFBFAC`
  - Every other category is ignored.
- The legend chips under each pie repeat these counts. When there is no data, a grey `#CCCCCC` "No Data Available" chip is shown.

#### API B / B' — `GET /v1/service-requests`

- V2 calls `?page=1&limit=200[&mall=<property_name>]`. The query string is built with `URLSearchParams`, so the mall name is URL-encoded.
- Legacy calls `?page=1&limit=1` and then `?page=1&limit=<total_count>`.

**Chain:**
- Route: `cenomi-api-2/servicerequest/delivery/http/service_request_handler.go:158`. It is mounted in `registerPrivateRoutes` (`cenomi-api-2/app/main.go:1953`, `:2341`). That group runs `ValidateAccessToken`/`SetContextUserData` → `PermissionCheck` → `InjectAuditLogger` (`main.go:933-938`).
- `PermissionCheck` (`internal/middleware/middleware.go:587`, tenant branch `:633`) uses only the roles on the **active** profile, which comes from the header. If no role on that profile grants the path, the response is 403. This is the only check that the header's profile belongs to the user.
- Handler `List`: `service_request_handler.go:280`.
  - `newServiceRequest` (`:524`) parses the query; `mall` is read at `:563-566` with no trim.
  - Defaults are page=1 and limit=10. **There is no cap on `limit`.** Note that `limit=0` from the legacy pies (when the total is 0) becomes 10.
  - `applyServiceRequestListUserContext` (`:411`) copies the session data.
  - `ExcludeArchivedAgeFinalFromMainList = !VIEW_ARCHIVED_SERVICE_REQUEST` (`:314`).
  - `attachSLASummary` (`:765`).
- Usecase: `ListAllServiceRequests` at `cenomi-api-2/servicerequest/usecase/service_request_usecase.go:1332`. For TENANT it goes to `fetchServiceRequestListForTenant` (`:1529`):
  - It sets `CreatedFor = UserID` (used only for DRAFT visibility) and `UserID = 0`.
  - **There is no lease, contact or property scoping.** Every contact of the active profile sees all of that profile's service requests.
  - The count and list queries run in parallel (errgroup, `:1540-1553`).
  - **If the page is empty, the usecase returns `total_count = 0`** (`:1586-1589`; ticket T7).
- Repository: `cenomi-api-2/servicerequest/repository/service_request_repository.go`.
  - `ListAllServiceRequests` `:1437` (SELECT constant `queryListAllServiceRequests:237`)
  - `GetServiceRequestsCount` `:1420` (`queryCountServiceRequests:308`)
  - The shared WHERE comes from `BuildServiceRequestQueryCondition` (`:1737`)
  - ORDER BY from `serviceRequestListOrderSQL` (`servicerequest/repository/service_request_sla.go:150`, default at `:173`)
  - SLA summary at `service_request_sla.go:479`

```sql
SELECT
  sr.service_request_id, sr.tenant_profile_id, tp.company_name AS company_name, sr.property_id,
  sr.category, sr.sub_category, sr.title, sr.payload, sr.status, sr.document_id, sr.workflow_id,
  sr.created_at, sr.updated_at, sr.deleted_at, sr.created_by, sr.updated_by, sr.deleted_by,
  CONCAT(cru.first_name,' ',cru.last_name) AS created_by_string,
  CONCAT(upu.first_name,' ',upu.last_name) AS updated_by_string,
  CONCAT(dpu.first_name,' ',dpu.last_name) AS deleted_by_string,
  sr.pms_post_status, sr.pms_post_log, sr.lease_id,
  COALESCE(NULLIF(sr.payload->>'lease',''), l.pms_tenant_code, '') AS lease_code,
  COALESCE(NULLIF(sr.payload->>'brand',''), NULLIF(sr.payload->>'brand_name',''), b.brand_name, '') AS brand,
  COALESCE(NULLIF(sr.payload->>'mall',''), p.marketing_name, '') AS mall,
  COALESCE(NULLIF(sr.payload->>'lease_brand_mall',''), NULLIF(l.lease_brand_mall,''),
           NULLIF(TRIM(BOTH ' -' FROM CONCAT_WS(' - ', /* lease, brand, mall as above */)), '')) AS lease_brand_mall,
  sr.created_for, CONCAT(cfu.first_name,' ',cfu.last_name) AS created_for_string,
  sr.property_ids, sr.notify_roles,
  srs.status AS sla_status, srs.policy_id AS sla_policy_id, srs.priority AS sla_priority,
  srs.target_hours AS sla_target_hours, srs.elapsed_hours AS sla_elapsed_hours, srs.remaining_hours AS sla_remaining_hours,
  srs.consumed_pct AS sla_consumed_pct, srs.due_at AS sla_due_at, srs.breached_at AS sla_breached_at,
  srs.paused_since AS sla_paused_since, srs.pending_since AS sla_pending_since, srs.pending_hours AS sla_pending_hours,
  srs.pending_with_role AS sla_pending_with_role, srs.pending_with_role_en AS sla_pending_with_role_en,
  srs.pending_with_role_ar AS sla_pending_with_role_ar, srs.pending_workflow_level AS sla_pending_workflow_level,
  srs.escalation_level AS sla_snapshot_escalation_level, srs.escalated_at AS sla_snapshot_escalated_at,
  srs.escalated_to_role AS sla_escalated_to_role, srs.escalated_to_role_ar AS sla_escalated_to_role_ar
FROM cenomi.service_request sr
  LEFT JOIN tenant_profiles tp ON sr.tenant_profile_id = tp.tenant_profile_id
  LEFT JOIN users cru ON cru.user_id = sr.created_by
  LEFT JOIN users upu ON upu.user_id = sr.updated_by
  LEFT JOIN users dpu ON dpu.user_id = sr.deleted_by
  LEFT JOIN users cfu ON cfu.user_id = sr.created_for
  LEFT JOIN cenomi.leases l ON l.lease_id = sr.lease_id
  LEFT JOIN cenomi.brands b ON b.brand_id = l.brand_id
  LEFT JOIN cenomi.properties p ON p.property_id = COALESCE(NULLIF(sr.property_id, 0), l.property_id)
  LEFT JOIN cenomi.service_request_sla srs ON srs.service_request_id = sr.service_request_id
WHERE
  -- [A] only when the role lacks VIEW_FITOUT_HANDOVER_CATEGORY / VIEW_ALL_SERVICE_REQUEST (:1755)
  sr.sub_category NOT IN ('HANDOVER','HANDED_OVER','FIT_OUT_CONFIRM_HO','FIT_OUT_CONFIRM_FOS','FIT_OUT_CONFIRM_END',
                          'FIT_OUT_CONFIRM_TRADING','FITOUT_PROGRESS','CLOSE_CEILING_INSPECTION','OPEN_CEILING_INSPECTION',
                          'PRE_OPENING_INSPECTION_MEP','PRE_OPENING_INSPECTION_ARCHITECTURAL')
  -- [B] TENANT only (:1758-1778)
  AND sr.sub_category NOT IN ('ISSUE_LOD','FIT_OUT_CONFIRM_HO','FIT_OUT_CONFIRM_FOS','FIT_OUT_CONFIRM_END',
                              'FIT_OUT_CONFIRM_TRADING','HANDED_OVER','FITOUT_PROGRESS')
  AND (sr.sub_category NOT IN ('HANDOVER','CLOSE_CEILING_INSPECTION','OPEN_CEILING_INSPECTION',
                               'PRE_OPENING_INSPECTION_MEP','PRE_OPENING_INSPECTION_ARCHITECTURAL')
       OR (sr.status IN ('REPORT_SUBMITTED','COMPLETED','APPROVED') AND NOT EXISTS (
             SELECT 1 FROM service_request_operation sro_tenant_gate
             WHERE sro_tenant_gate.service_request_id = sr.service_request_id
               AND sro_tenant_gate.status NOT IN ('FINISHED','SUBMITTED','APPROVED','REJECTED','SKIPPED',
                                                  'REVIEWED_WITH_COMMENTS','REVIEW_AND_APPROVE'))))
  AND sr.category NOT IN ('HSE','DISCREPANCY','METER_READING','MALL_CHECKLIST','NEW_CUSTOMER','DEALS_FLOW',
                          'SOFT_FM','SOFT_FM_CHECKLIST','SOFT_FM_AUDIT')
  AND sr.sub_category NOT IN ('USER_JOURNEY_CHECKLIST')
  -- [C] checklist sub-categories hidden (:1781)
  AND sr.sub_category NOT IN ('CLEANLINESS_CHECKLIST','WASHROOM_AND_ASSOCIATED_FACILITIES_CHECKLIST','PEST_CONTROL_CHECKLIST',
                              'WASTE_MANAGEMENT_CHECKLIST','BICSC_COMPLIANCE_CHECKLIST','LANDSCAPE_CHECKLIST','USER_JOURNEY_CHECKLIST')
  -- [D] tenant scope (:1799)
  AND sr.tenant_profile_id = $1                              -- active profile (x-active-tenant-profile-id)
  -- [E] only without VIEW_ARCHIVED_SERVICE_REQUEST (:1986)
  AND NOT (sr.status IN ('APPROVED','REJECTED') AND sr.updated_at < (NOW() - INTERVAL '90 days'))
  -- [F] only when &mall= is sent (:2004-2028); exact, case-sensitive; EN or AR names match
  AND ( COALESCE(sr.payload->>'mall','') = $2
        OR COALESCE(sr.payload->>'mall_name','') = $2
        OR COALESCE(sr.payload->>'property_name','') = $2
        OR EXISTS (SELECT 1 FROM cenomi.properties p
                   WHERE ((NULLIF(sr.property_id,0) IS NOT NULL AND p.property_id = sr.property_id)
                          OR (sr.property_ids IS NOT NULL AND p.property_id = ANY(sr.property_ids)))
                     AND (p.marketing_name = $2 OR p.marketing_name_ar = $2))
        OR EXISTS (SELECT 1 FROM cenomi.leases l JOIN cenomi.properties p ON p.property_id = l.property_id
                   WHERE l.lease_id = sr.lease_id AND (p.marketing_name = $2 OR p.marketing_name_ar = $2)) )
  -- [G] drafts visible only to their creator (:2102-2114); $2 without mall, $3 with mall
  AND NOT (sr.status = 'DRAFT' AND sr.created_by IS DISTINCT FROM $2)
ORDER BY COALESCE(sr.updated_at, sr.created_at) DESC, sr.service_request_id DESC
LIMIT 200 OFFSET 0;      -- limit/offset are sprintf'd ints; offset=(page-1)*limit
```

```sql
-- total_count
SELECT COUNT(sr.service_request_id)
FROM cenomi.service_request sr
LEFT JOIN cenomi.service_request_sla srs ON srs.service_request_id = sr.service_request_id
WHERE <identical WHERE>;

-- sla_summary (service_request_sla.go:479)
SELECT COUNT(*) FILTER (WHERE srs.status='on_track') AS on_track, COUNT(*) FILTER (WHERE srs.status='at_risk') AS at_risk,
       COUNT(*) FILTER (WHERE srs.status='overdue') AS overdue, COUNT(*) FILTER (WHERE srs.status='paused') AS paused,
       COUNT(*) FILTER (WHERE srs.status='met') AS met,
       COUNT(*) FILTER (WHERE srs.status='not_applicable' OR srs.status IS NULL) AS not_applicable
FROM cenomi.service_request sr LEFT JOIN cenomi.service_request_sla srs ON srs.service_request_id = sr.service_request_id
WHERE <identical WHERE>;
```

**Enrichment queries** run per page, only when it has rows:
- Workflow operations for the page's ids (`service_request_operation/repository/service_request_operation_repository.go:528`, SQL `:29`, a UNION of `service_request_operation` and `service_request_operation_archive_recent` with `service_request_id = ANY($1)`).
- User names (`users/repository/postgres/users_repository.go:509`).
- Role names (`roles/repository/postgres/roles_repository.go:227`).
- One `GetServiceRequestOperationHistory` query **per** FIT_OUT_AND_DRAWING or WORK_PERMIT row (N+1). With the legacy `limit=<total_count>` this means one history query for every such row in the tenant's whole history, twice per page load.

Other optional filters on this handler, not sent by the dashboard: `service_category`, `sub_category`, `status` (IN_PROCESS also matches IN_PROGRESS), `document_status`, `unit_id`, `lease_id`, `property_id`, `year`/`month` (on `created_at` in Riyadh time), `start_date`/`end_date` (at most 90 days), `brand`, `search`, `sla_status`, `escalation_level`, `pending_over_hours`, `sort_by`/`order` (whitelist at `service_request_handler.go:1522`), and `disable_pagination`.

**Go post-processing:**
- `status` is the **raw DB value**. There is no display mapping; the V2 model aliases IN_PROCESS/IN_PROGRESS on the client.
- DTO mapping: `ServiceRequestListItemDTO.MapFromDomain` (`cenomi-api-2/domain/serviceRequestdto.go:122`).
- Operation role names come from `ServiceRequestApproverDisplayNameEn/Ar`.
- For tenants, `CloneSLAForTenant` (`domain/service_request_sla.go:162`) blanks the escalation fields.
- No response caching. No external calls.
- **The displayed `mall` uses fewer sources than the `mall` filter.** The column is `payload.mall` or the marketing name of the SR's or lease's property. The filter also matches `property_ids`, `mall_name` and `property_name`. So a row can match the filter and still show a blank or different `mall`.

Response (`cenomi-api-2/domain/serviceRequestdto.go:286` `ListServiceRequestResponse`; item at `:41-73`):

```json
{ "success": true, "data": {
  "current_page": 1, "limit": 200, "total_count": 123, "guidelines_link": "",
  "sla_summary": { "on_track": 3, "at_risk": 1, "overdue": 0, "paused": 0, "met": 10, "not_applicable": 109 },
  "list": [ {
    "service_request_id": "18734",          // string
    "tenant_profile_id": 512, "company_name": "Acme Retail", "property_id": 21,
    "service_category": "WORK_PERMIT",      // = sr.category
    "sub_category": "…", "title": "…", "status": "IN_PROCESS",
    "payload": { /* raw */ }, "workflow_id": 7,
    "created_at": "…", "updated_at": "…", "created_by": "First Last", "created_by_id": 9,
    "lease_id": 9312, "lease_code": "T0001234", "brand": "Brand", "mall": "Mall of Dhahran",
    "lease_brand_mall": "T0001234 - Brand - Mall of Dhahran",
    "document_status": "", "user_action": "", "comment": "",
    "operations": [ { "service_request_operation_id": 1, "assigned_role": "…", "workflow_level": 1, "status": "PENDING",
                      "role_name_en": "…", "role_name_ar": "…", "operator_name": "…" } ],
    "operation_history": [ /* FIT_OUT_AND_DRAWING / WORK_PERMIT only */ ],
    "sla": { "status": "on_track", "priority": "low", "target_hours": 48, "due_at": "…", "pending_with": { "role": "…" } } } ] } }
```

The dashboard reads only `status`, `service_category` and `data.total_count`. V2 also types `service_request_id` and `mall`.

---
### 4. Sales data (reported sales by month)

| | V2 | Legacy |
|---|---|---|
| Component | `v2/TenantSalesCard.tsx`; hooks `v2/useTenantSales.ts` (chart rows) and `v2/useTenantSalesCounts.ts` (tile counts); model `v2/tenantSales.ts` | `libs/ui-web/src/lib/components/salesBarChart/SaleBarChart.tsx` rendering `Charts/BarChart/BarChart.tsx` |
| Visibility | `SALES_DATA_LIST` | `SALES_DATA_LIST` |
| Filters | **Lease** `Select` (`leaseOptions(leases)` from `/contracts` rows (call D): "All leases" plus one entry per distinct `pms_tenant_code`, labelled "`code - brand - mall`"; value = `pms_tenant_code` sent as `lease_code`). **Year** `Select` from `defaultYearOptions()` (`dashboards/admin/v2/dashboardFilters`), with the current `year` prepended when it is missing. Year → `sales_period_start=Y-01-01&sales_period_end=Y-12-31` | **Lease** `SelectInputWithSearch` from call D' (`/contracts?status=ACTIVATED,SUPERSEDED&limit=1000`), keeping leases whose `start_date` year ≤ the current year. Label `formatTenantCode({pms_tenant_code, property_name, brand_name})`; the first lease is preselected. **Year** options run from the lease's `start_date` year to its `end_date` year (capped at the current year); the default is the current year when it is in range, otherwise the first |
| Chart | ui-kit `StackedColumns` (in-house, `fluid`), one segment per column, colour `chartPalettes.categorical4[1]` #14B8A6. Compact SAR labels on the bars, compact numbers on the axis, and a teal footer band with the year total (full SAR). The footnote explains which statuses count, plus a "skipped" count | **recharts** `BarChart`: bars use the gradient `rgba(219,46,109)`→`rgba(89,43,138)`. A month with no value is drawn as a placeholder bar (min value, or 100) in grey dashed `#F5F5F7`/`#A7A9B4`, except for QUARTERLY/HALF_YEARLY. Y-axis is in `k`; height 380 |
| Actions | "Upload" → `/dashboard/salesdata/upload` | — |

**V2 mapping** (`tenantSales.ts`). The rows are `data.list[]` from call C'; fields read are `sales_period_end`, `sales_period_start`, `sales_amt`, `status`.
- Only rows whose `status` (upper-cased) is `SUBMITTED` or `APPROVED` are kept (`REPORTED_STATUSES`).
- Month = `new Date(sales_period_end ?? sales_period_start).getMonth()`. Rows without a parsable date go to `skipped`.
- `salesMonths` sums `sales_amt` per month. Only months that have data are drawn (no zero bars), in calendar order.
- `salesTotal` = the sum of the drawn months, shown in the band.
- The empty state shows when no month has data.

**V2 tile counts** (`useTenantSalesCounts`): two parallel calls C with `limit=1`, the selected year's period, and status either `PENDING,NEED_REUPLOAD,NEED_UPLOAD_SUPPORTING_DOCUMENT,NEED_UPLOAD_AUDITED_SALES` or `APPROVED`. Each count is `total_count` when it is > 0, otherwise `list.length`.

**Legacy mapping** (`SaleBarChart`):
- Each row of call C''' becomes `{month: moment(sales_period_end).month(), amount: sales_amt||0, status}`.
- `findAmount` sums the amounts of SUBMITTED + APPROVED rows per month.
- The bucket layout depends on `list[0].sales_report_frequency`:
  - `MONTHLY`: 12 buckets.
  - `QUARTERLY` / `HALF_YEARLY`: buckets run up to the maximum month. A bucket is flagged `NEED_DOCUMENT` when its month closes a quarter or half and it has no data.
  - Any other value gives an empty chart.
- Labels are `MMM` plus the frequency. The dataset is named "Total Sales" with currency SAR.
- Legacy also fetches the all-time tile counts (call C'') directly in `TenantDashboard`.

#### API C / C' / C'' / C''' — `GET /v1/sales-data`

**Chain:**
- Route: `cenomi-api-2/sales_data/delivery/http/sales_data_handler.go:34`, mounted at `app/main.go:2475` in the private group.
- Handler `List`: `sales_data_handler.go:122`.
  - Params come from `parseSalesDataListRequestParameters:1102` and `parseSalesDataFilterParams:1123`.
  - Defaults are page 1, limit 10, order DESC. There is no limit cap.
  - `status` is the raw comma string. `lease_code` is read as repeated params and is not comma-split.
- Tenant check: `enforceTenantProfileAccessForSalesDataList` (`:1039`) and `salesDataTenantProfileAllowed` (`:1090`).
  - For a TENANT, the query `tenant_profile_id` **must equal the header's active profile**, otherwise the response is **403**. With `all_my_companies=true` it may be any company in the session.
- Usecase `Fetch`: `cenomi-api-2/sales_data/usecase/sales_data_usecase.go:711`.
  - It calls `GetPermittedAccessItems`.
  - Because a `tenant_profile_id` is present, `applySalesDataListAccessScope` (`:816-819`) returns early. **No lease or property scoping is added.** A contact limited to certain leases still sees every sales row of the company.
- Repository: `cenomi-api-2/sales_data/repository/postgres/sales_data_repository.go`.
  - `GetSalesDataCount:430` (`queryCountSalesData:96`)
  - `Fetch:637` (`queryListSalesData:175`)
  - `GetDistinctLeaseCodes:485`
  - The WHERE builder is `buildLeadEnquiryFilterQueryCondition:950` (sic), with `appendCaseInsensitiveLeaseCodeIn:906` and `appendSalesPeriodOverlap:925`.

Status constants (`internal/constants/constants.go:1101-1127`): PENDING, NEED_REUPLOAD, SUBMITTED, UPLOADED_SUPPORTING_DOCUMENT, RE_UPLOADED, UPLOADED_AUDITED_SALES, APPROVED, NEED_UPLOAD_AUDITED_SALES, NEED_UPLOAD_SUPPORTING_DOCUMENT. The four "pending" values the dashboard sends all exist.

```sql
-- C (V2 tile counts): count + list(limit 1)
SELECT COUNT(sales_data_id) FROM sales_data
WHERE  status IN ('PENDING','NEED_REUPLOAD','NEED_UPLOAD_SUPPORTING_DOCUMENT','NEED_UPLOAD_AUDITED_SALES')  -- or IN ('APPROVED')
  AND tenant_profile_id = $1
  AND sales_period_start <= $2 AND sales_period_end >= $3;      -- $2='YYYY-12-31', $3='YYYY-01-01'

SELECT sales_data_id, tenant_profile_id, lease_id, lease_code, sales_period_start, sales_period_end,
       sales_amt, status, document_id, created_by, updated_by, approved_by, submitted_by,
       submitted_by_email, created_at, updated_at, approved_at
FROM sales_data
WHERE <same>
ORDER BY sales_period_start DESC LIMIT 1 OFFSET 0;

-- C' (V2 chart) / C''' (legacy chart): no status filter
SELECT ...same 17 columns... FROM sales_data
WHERE tenant_profile_id = $1
  [AND LOWER(lease_code) IN (LOWER($2))]                        -- only when lease_code is sent
  AND sales_period_start <= $end AND sales_period_end >= $start
ORDER BY sales_period_start DESC LIMIT 200 /* legacy: 100 */ OFFSET 0;

-- C'' (legacy tile counts, all time): WHERE status IN (...) AND tenant_profile_id = $1 ... LIMIT 1

-- always run as well: lease_codes (ignores period and lease_code)
SELECT DISTINCT sd.lease_code, COALESCE(b.brand_name,'') AS brand_name, COALESCE(p.marketing_name,'') AS mall_name,
       COALESCE(b.brand_name_arabic,'') AS brand_name_arabic, COALESCE(p.marketing_name_ar,'') AS mall_name_arabic
FROM sales_data sd
LEFT JOIN leases l ON sd.lease_code = l.pms_tenant_code
LEFT JOIN brands b ON l.brand_id = b.brand_id
LEFT JOIN properties p ON l.property_id = p.property_id
WHERE sd.lease_code IS NOT NULL AND sd.lease_code != '' [AND sd.status IN ('...')]
  AND sd.tenant_profile_id = $1 AND sd.tenant_profile_id = $1;
```

Dynamic notes:
- The `status` values are **concatenated into the SQL as quoted literals**, not bound (`:954-967`). This is an injection risk.
- The period filter is an **overlap** test (`start <= :end AND end >= :start`), not containment as the frontend comments assume. A period that crosses the year boundary is counted in both years.
- `ORDER BY sales_period_start DESC` has no tie-break (ticket T11).
- LIMIT and OFFSET are `Sprintf`'d into the SQL.

**Go post-processing** (N+1 per row):
- Usecase `:739-809`:
  - Comments are fetched to build `unread_comments_count`.
  - When `document_id` is set: the document row is fetched and signed with `storage.GetSignedURL` (SharePoint path for YARDI sources). A missing document makes the whole request 404.
  - User names are resolved.
- Repository `:756-768`: the dates are moved to Riyadh time with `ChangeToArabicTimeZone`.
- Handler `:186-235`, per row:
  - Calls `FetchLeaseByLeaseID` (`lease/repository/postgres/lease_repository.go:1022`), `GetPropertyByID` and `GetTenantProfileByID`. A missing lease, property or profile makes the whole response 404.
  - **`sales_report_frequency` comes from `leases.sales_report_frequency`** (`:227`); the legacy chart's bucket layout depends on it.
  - `property_name` is the property's `marketing_name`; `brand_name` and `company_name` are also filled here.
- No caching. No Yardi or SAP calls on this read path.

Response (`cenomi-api-2/domain/salesdatadto.go:124-130` `SalesDataResponse`; item `SalesDataDTO :22-53`, all fields `omitempty`):

```json
{ "success": true, "data": {
  "current_page": 1, "limit": 200, "total_count": 14,      // total_count omitted when 0 (ticket T7)
  "lease_codes": [ { "lease_code": "T0001234", "brand_name": "Brand", "mall_name": "Mall of Dhahran",
                     "brand_name_arabic": "…", "mall_name_arabic": "…" } ],
  "list": [ {
    "sales_data_id": "5531", "tenant_profile_id": 512, "lease_id": 9312, "lease_code": "T0001234",
    "sales_period_start": "2026-01-01T00:00:00+03:00", "sales_period_end": "2026-01-31T00:00:00+03:00",
    "sales_amt": 482000.5,                                 // omitted when 0
    "status": "APPROVED", "property_name": "Mall of Dhahran", "property_id": 21,
    "document_id": "…", "signed_url": "https://…", "need_supporting_docs": false, "source": "PORTAL",
    "sales_report_frequency": "MONTHLY", "company_name": "Acme Retail", "brand_name": "Brand",
    "created_by_name": "…", "approved_by_name": "…", "submitted_by_email": "…", "unread_comments_count": 0,
    "created_at": "…", "updated_at": "…", "approved_at": "…" } ] } }
```

The dashboard reads `total_count`, `list[].sales_amt`, `sales_period_end` (falling back to `sales_period_start`), `status`, and (legacy) `sales_report_frequency`.

---
### 5. Action required (notifications)

| | V2 | Legacy |
|---|---|---|
| Component | `v2/TenantActionRequiredCard.tsx`; tone and label map in `v2/tenantNotifications.ts` | `tenant/ActionRequired.tsx` (infinite scroll via `react-infinite-scroll-component`) |
| Visibility | `canViewActionRequiredWidget(permissions)` | same |
| Visual | `ChartCard` with a list (max height 17.6rem, scrolls). Each row: a `StatusPill` (tone from `notificationTone(notification_type)`), the text `text_content.en` or `text_content.ar`, and the relative time `getRelativeTime(created_at)`. Footer link "All" → `/dashboard/notifications` | Card list with formatted date |
| State | Redux `state.notification.list` / `status` (`notificationSlice.ts`) | same slice |

**Pill tones** (`tenantNotifications.ts`):

| Tone | `notification_type` values |
|---|---|
| error | PAYMENT, EXPIRING_LEASE, EXPIRING_LEASE_OCCUPANCY_STATUS_UPDATE |
| warning | SALES_DATA, ESTIMATED_SALES_DATA, DOCUMENT, COMPANY_DOCUMENT, LEASE_DOCUMENT |
| info | SERVICE_REQUEST, SERVICE_REQUEST_COMMENTS, MESSAGE, ENQUIRY, PROPOSAL, CONTRACT, AMENDMENT, AMENDMENT_DETAILS, FIT_OUT_HANDOVER |
| success | ACTIVATED_LEASE_NOTIFICATION |
| neutral | LETTER_DETAILS, ANNOUNCEMENT_DETAILS, EVENT_DETAILS, SHARE_CONTACTS, and any unknown type |

The pill label key is `tenantDashboardV2.notificationKind.<TYPE>`, or `.default` for an unknown type.

**Click behaviour.** Clicking a row opens the item it is about.
- If `notification.tenant_profile_id` differs from `localStorage.tenant_profile_id`, the item belongs to another company. The card stores `temporary_id` and opens the company-switch dialog (`CompanySwitchDialogV2`; legacy uses `CompanySwitchModal`).
- Otherwise it calls `handleNotificationNavigation(type, text_content.id, navigationMap[type], text_content.category, …, lease_id, text_content.contract_id, text_content.entity_id, salesSection, …, text_content.en, {start: text_content.sales_period_start, end: text_content.sales_period_end})` (`libs/ui-web/src/lib/utils/Util.ts`).
- `salesSection` maps the sales category to a sales-data tab:
  - PENDING tab: PENDING, NEED_REUPLOAD, NEED_UPLOAD_SUPPORTING_DOCUMENT, NEED_UPLOAD_AUDITED_SALES
  - SUBMITTED tab: SUBMITTED, UPLOADED_SUPPORTING_DOCUMENT, RE_UPLOADED, UPLOADED_AUDITED_SALES
  - APPROVED tab: everything else

#### API E — `GET /v1/notifications?page=1&limit=15&is_action_required=true`

- Frontend: thunk `fetchNotification({page:1,limit:15})` → `getNotifications(page, limit, true)`, using `NOTIFICATION_ENDPOINTS 'notifications?page={0}&limit={1}&is_action_required=true'`. The thunk stores only `response.data.list`.
- Legacy `fetchMoreData` dispatches page 2, 3, … with limit 15.
- Middleware: the private `/v1` group (`cenomi-api-2/app/main.go:933-936`) runs `ValidateAccessToken(SetContextUserData…)` → `PermissionCheck` → `InjectAuditLogger`. Wiring is at `main.go:2290-2291`.
- Route: `cenomi-api-2/notification/delivery/http/notification_handler.go:28`.
- Handler `List`: `notification_handler.go:34`, with `parsePaginationParams` at `:92-158`.
  - Defaults are page=1 and limit=10.
  - `is_action_required` is parsed with `ParseBool`. **Only `true` adds a filter.**
  - Other optional params: `include_archived`, `search`, `notification_type`, `status=unread|read`, `from`/`to`.
- **Scoping** (`:43-62`): the handler loops over **every** `userData.Companies` entry and collects their `TenantProfileID`s and role permissions. **The `x-active-tenant-profile-id` header has no effect here**, which is why notifications for other companies (and the company-switch prompt) appear. It also passes `UserID`, `RoleIDs` and `UserType`.
- Usecase `List`: `cenomi-api-2/notification/usecase/notification_usecase.go:42`.
  - The ADMIN-only lease/property scoping is skipped for tenants.
  - The permission list is intersected with `constants.NotifictaionPermissions` (`internal/constants/constants.go:5945`).
  - It makes three repository calls: List, `FetchNotificationsCount`, and `FetchUnreadNotificationsCount`.
- Repository: `cenomi-api-2/notification/repository/postgres/notification_repository.go`.
  - `List` is at `:353` and `buildQuery` at `:595`.
  - The active-lifecycle filter is at `:583`/`:587`.
  - Count functions are at `:812` and `:830`.
  - SQL constants: `notificationListSelect:171`, `queryListUserNotifications:187`, `queryNotificationCount:262`.

```sql
WITH distinct_notifications AS (
  SELECT DISTINCT ON (COALESCE(n.group_id, n.notification_id))
    n.notification_id, n.tenant_profile_id, n.notification_type, n.text_content,
    n.created_at, n.read_at, n.target_type, n.target_user_id, n.target_role_id,
    n.action_required, n.lease_id, n.unique_property_id,
    NULL::timestamp AS archived_at, NULL::text AS archive_reason
  FROM notifications n
  WHERE n.action_required = $1                                      -- true; only when is_action_required=true
    AND (n.tenant_profile_id = ANY($2)                              -- all session company tenant_profile_ids
         OR (n.tenant_profile_id IS NULL AND n.target_user_id = $3))-- TENANT users only
    AND ((n.target_user_id = $4 OR n.target_role_id = ANY($5) OR target_permissions && $6::text[])
         AND (n.target_type = 'TENANT' OR n.target_type IS NULL))
    AND n.action_state IS DISTINCT FROM 'ACTION_DONE'
  ORDER BY COALESCE(n.group_id, n.notification_id)
)
SELECT * FROM distinct_notifications
ORDER BY created_at DESC
LIMIT $7 OFFSET $8;   -- 15, 15*(page-1)
```

Dynamic parts:
- `LIMIT` is added only when limit ≠ 0. **`limit=0` returns every row.**
- `OFFSET` comes from `common.GetOffset` (`internal/common/util.go:32`).
- Optional filters, each AND'ed in:
  - `status=unread` → `n.read_at IS NULL`; `status=read` → `n.read_at IS NOT NULL`
  - `notification_type` → `trim(n.text_content->>'type') = $`
  - `from` / `to` → bounds on `n.created_at`
  - `search` → `text_content->>'en'` / `'ar'` ILIKE
- `include_archived=true` UNIONs `notifications_archive` (`:207`).
- Infinite scroll is plain OFFSET paging ordered by `created_at DESC` with no tie-break, so pages can drift.
- Inside a group, `DISTINCT ON` keeps an arbitrary row.

Count queries:

```sql
-- total_count (FetchNotificationsCount) and un_read_notifications_count (+ AND n.read_at IS NULL)
WITH distinct_notifications AS (
  SELECT DISTINCT ON (COALESCE(n.group_id, n.notification_id)) n.notification_id, n.group_id
  FROM notifications n
  WHERE <same conditions> AND n.action_state IS DISTINCT FROM 'ACTION_DONE')
SELECT COUNT(notification_id) FROM distinct_notifications;
```

Both counts inherit `action_required = true`.

Post-processing:
- `text_content` is passed through as raw JSON (`domain/notificationdao.go:30`).
- No caching. No signed URLs.
- Quirk: the repository reuses one struct across rows (`:383-409`), so a row with NULL `text_content` inherits the previous row's content.

Response (`cenomi-api-2/domain/notificationdto.go:9-27`, `:84`):

```json
{ "success": true, "data": {
  "current_page": 1, "total_count": 42, "limit": 15, "un_read_notifications_count": 7,
  "list": [ {
    "id": "6f1c…uuid", "tenant_profile_id": 512, "notification_type": "SALES_DATA",
    "text_content": { "key": "…", "en": "Sales data for Jan 2026 needs re-upload", "ar": "…",
                      "type": "…", "category": "NEED_REUPLOAD", "sub_category": "…", "id": "…",
                      "document_type_id": "…", "entity_id": "…", "contract_id": "…",
                      "sales_period_start": "2026-01-01", "sales_period_end": "2026-01-31" },
    "created_at": "2026-10-01T09:12:00Z", "read_at": null,
    "target_type": "TENANT", "target_user_id": 0, "target_role_id": 33,
    "action_required": true, "lease_id": 9312, "unique_property_id": 4 } ] } }
```

- The `text_content` keys follow `config.NotificationConfig` (`internal/config/notificationconfig.go:12-25`).
- There is no `is_read` field. Read state is `read_at` being null or not.

---

### 6. Announcements & events

| | V2 | Legacy |
|---|---|---|
| Component | `v2/TenantAnnouncementsCard.tsx`; model `v2/announcementsModel.ts` | `tenant/AnnouncementAndEventsSection.tsx`, which holds two `CardLayout`s: `EventsDashboardCard.tsx` (Today and Upcoming lists of `EventCard`) and `AnnouncementsDashboardCard.tsx` |
| Visibility | always | always |
| Visual | One merged list. Each row: a `StatusPill` (today = success, upcoming = info, announcement = neutral), a title, and the relative date. Footer link "All" → `/dashboard/announcements` | Events card ("View All" → `/dashboard/events?time_period=today&page=1`; clicking an event dispatches `setActiveSection` / `setSelectedEvent(announcement_event_id)` and goes to `/dashboard/events`). Announcements card ("View All" → `/dashboard/announcements`; shows `published_at` as relative time) |
| State | Redux `state.announcementAndEvents.{announcementsData, eventsData.today/upcoming, status}` | same |

**V2 merge** (`announcementFeed`):
- Builds items from `announcements` (kind `announcement`, date `published_at ?? start_date`), `events.today` (kind `today`, date `start_date`) and `events.upcoming` (kind `upcoming`).
- Drops upcoming items whose `announcement_event_id` is already in today's list (the API overlap, ticket T9).
- Title = `title_en` or `title_ar` by locale, falling back to the other.
- Sorted by date, newest first.

#### API F — `GET /v1/announcements-events/dashboard-summary?announcement_limit=5`

- Frontend: thunk `fetchAnnouncementAndEventsDashboardSummary({announcement_limit: 5})` (`AnnouncementAndEventsConstants.ANNOUNCEMENTS_LIMIT`) → `getAnnouncementAndEventsDashboardData`. On fulfilled, the reducer stores `announcements`, `events.today` and `events.upcoming`.
- Route: `cenomi-api-2/announcement/delivery/http/announcement_handler.go:36`. Same private group; wiring at `main.go:3155-3156`.
- Handler `FetchAnnouncementsEventsDashboardSummary`: `announcement_handler.go:160`. `announcement_limit` defaults to 5; a non-integer or a value below 1 returns 400. There is no upper cap.
- Usecase `FetchAnnouncementDashboardSummary`: `cenomi-api-2/announcement/usecase/announcement_usecase.go:103`.
  - Scoping comes from `addFiltersToParams` (`:152-193`).
  - It fetches announcements (limit = `announcement_limit`), today's events (**hard-coded limit 6**) and upcoming events (**hard-coded limit 3**).
  - `populateMallsAndAttachments` (`:196`) then runs two queries per item (N+1).
- Repository: `cenomi-api-2/announcement/repository/postgres/announcement_repository.go`. The base query is at `:31`, the company-level block at `:82`, announcements at `:515` and events at `:576`.

**Scoping inputs** (`addFiltersToParams`):
1. `GetPermittedItems` (SQL in §1) gives the lease ids.
   - `LeaseIDs` is used only when override is nil with leases > 0, or override is OverrideAll (-1). Otherwise it is `[]`.
   - Note: the explicit `lease_ids` subquery is not limited to the active profile.
2. `FetchPropertyIDsAndStoreTypes(LeaseIDs)` (`lease/repository/postgres/lease_repository.go:1826`, SQL `:672`) gives the malls (`$3`) and store types (`$4`):
   ```sql
   SELECT p.unique_property_id, l.lease_type FROM leases l LEFT JOIN properties p ON l.property_id = p.property_id WHERE lease_id = ANY($1);
   ```
   `lease_type` is mapped through `constants.LeaseTypeDisplayNames`.
3. Company-level roles (`getCompanyLevelLeases`, `:224`):
   - Finds the active profile's `tenant_contacts` rows with `is_company_level = true` and collects their roles.
   - Checks them with `SELECT ARRAY_AGG(role_id) FROM announcement_event_roles WHERE role_id = ANY($1) AND is_company_level = true` (`announcement_repository.go:775`).
   - If any match, it takes every current lease of the active profile (`lease_repository.go:757`), plus their malls and store types, as `$5-$7`.

```sql
SELECT DISTINCT a.announcement_event_id, a.is_announcement, a.is_event, a.title_en, a.title_ar,
       a.description_en, a.description_ar, a.start_date, a.end_date, a.published_at, a.applies_to_all_malls
FROM announcements_events a
LEFT JOIN announcement_event_leases al      ON al.announcement_event_id = a.announcement_event_id
LEFT JOIN announcement_event_malls am       ON am.announcement_event_id = a.announcement_event_id
LEFT JOIN announcement_event_store_types aes ON aes.announcement_event_id = a.announcement_event_id
LEFT JOIN announcement_event_roles ar       ON ar.announcement_event_id = a.announcement_event_id
WHERE (
  ( ((ar.role_id = ANY($1) AND ar.is_lease_level = true) OR a.applies_to_all_roles = true)
    AND ( al.lease_id = ANY($2)
          OR (a.applies_to_all_leases = true
              AND ((aes.store_type = ANY($4) OR a.applies_to_all_store_types = true)
                   AND (am.unique_property_id = ANY($3) OR a.applies_to_all_malls = true)))) )
  -- only when company-level leases exist:
  OR ( ((ar.role_id = ANY($1) AND ar.is_company_level = true) OR a.applies_to_all_roles = true)
       AND ( al.lease_id = ANY($5)
             OR (a.applies_to_all_leases = true
                 AND ((aes.store_type = ANY($6) OR a.applies_to_all_store_types = true)
                      AND (am.unique_property_id = ANY($7) OR a.applies_to_all_malls = true)))) )
)
-- announcements:
 AND is_announcement = true AND deleted_at IS NULL ORDER BY published_at DESC LIMIT $n   -- announcement_limit
-- events, today (limit 6):
-- AND is_event = true AND deleted_at IS NULL
-- AND ((CURRENT_DATE AT TIME ZONE 'Asia/Riyadh')::date BETWEEN start_date AND end_date)
-- ORDER BY start_date ASC, published_at DESC LIMIT $n
-- events, upcoming (limit 3):
-- AND is_event = true AND deleted_at IS NULL
-- AND end_date > (CURRENT_DATE AT TIME ZONE 'Asia/Riyadh')::date
-- ORDER BY start_date ASC LIMIT $n
```

`$1` = the session's `RoleIDs` across all companies.

Per-item queries:

```sql
SELECT p.unique_property_id, p.marketing_name, p.marketing_name_ar
FROM announcement_event_malls a JOIN unique_properties p ON p.unique_property_id = a.unique_property_id
WHERE a.announcement_event_id = $1 ORDER BY p.unique_property_id;

SELECT sa.document_id
FROM announcements_events a JOIN sr_attachments sa ON sa.service_request_id = a.sr_id
WHERE a.announcement_event_id = $1 AND a.deleted_at IS NULL ORDER BY sa.document_id;
```

Caveats:
- There is no published or status filter; only soft-deleted rows are excluded.
- Announcements have no date window.
- `upcoming` (`end_date > today`) includes events that are running now, so they overlap with `today`.
- No caching, no external calls, no signed URLs.

Response (`cenomi-api-2/domain/announcementdto.go:37` `DashboardSummaryResponse`, `:43` `EventListDTO`, `:49-62` `AnnouncementEventDataDTO`):

```json
{ "success": true, "data": {
  "announcements": [ {
    "announcement_event_id": 81, "is_announcement": true, "is_event": false,
    "title_en": "Mall maintenance window", "title_ar": "…",
    "description_en": "…", "description_ar": "…",
    "start_date": "2026-10-10", "end_date": "2026-10-12",
    "published_at": "2026-10-01T12:00:00+03:00",
    "malls": "All Locations",
    "attachments": [ { "document_id": "…" } ] } ],
  "events": {
    "today":    [ { "announcement_event_id": 90, "is_event": true, "title_en": "…", "start_date": "2026-10-12", "end_date": "2026-10-15",
                    "malls": [ { "mall_id": 4, "mall_name_en": "Mall of Dhahran", "mall_name_ar": "…" } ], "attachments": [] } ],
    "upcoming": [ ] } } }
```

- `start_date` and `end_date` are formatted `YYYY-MM-DD` (Riyadh time zone); `published_at` is RFC3339 in Riyadh time.
- `malls` is the string `"All Locations"` when `applies_to_all_malls` is set, otherwise an array of `{mall_id, mall_name_en, mall_name_ar}`.
- There is no `image` field.

---

### 7. Tenant lease list (feeds the greeting, the mall filter, the lease filter and the legacy sales chart)

There is no card for this call. It supplies:
- **V2:** `useTenantLeaseMalls(true)` → `getLeases(undefined, undefined, 200)` → `GET /v1/contracts?limit=200`. The rows (`TenantLeaseRow`) feed `companyName()` (greeting), `mallOptions()` (Service Requests mall select) and `leaseOptions()` (Sales lease select). A failure leaves the list `undefined`.
- **Legacy:** `SaleBarChart` → `getLeases(undefined, 'ACTIVATED,SUPERSEDED', 1000)` → `GET /v1/contracts?status=ACTIVATED,SUPERSEDED&limit=1000`. This feeds the lease picker and its year range.

#### API D / D' — `GET /v1/contracts`

**Chain:**
- Route: `cenomi-api-2/contract/delivery/http/contract_handler.go:62`, mounted at `app/main.go:2608` in the private group.
- Handler `List`: `contract_handler.go:72`.
  - Params come from `parseContractRequestParameters:447` and `parseContractFilterParams:220`.
  - Defaults are page 1, limit 10, sort `pms_last_modified_at DESC`. There is no limit cap.
  - `tenant_profile_id`: when the query has one it is used **without validation**; otherwise the header value is used. The dashboard never sends it.
- Usecase `List`: `cenomi-api-2/contract/usecase/contract_usecase.go:105`.
  - Unit-type gate (`:115-133`): `UnitTypesWithAccess` is built from the store, media and specialty lease-type permissions. If it is empty, the response is 500.
  - `GetPermittedAccessItems` (`tenant_contact/usecase/tenant_contact_usecase.go:861`). With `OverrideNone` it returns an empty list (`:157-159`).
  - Tenant branch (`:216-228`): `params.LeaseIDs` = the de-duplicated accessible leases.
  - `fetchLocationFiltersWithAccess` (`:762`): when no cities are found it returns an empty list.
  - `mapToContractsDTO` (`:463`) runs batched property, brand and company lookups.
- Repository: `cenomi-api-2/contract/repository/postgres/contract_repository.go`.
  - `List:761` with `buildListContractsQuery:1278`
  - `GetContractCount:681`
  - Visibility logic at `:649-679`
  - Effective-end-date CTE at `:229-294`
  - `FetchFilterDatas:1758` (SQL `:573`)

```sql
WITH filtered_lease_id AS ( SELECT unnest(ARRAY[<accessible lease ids>]::bigint[]) AS lease_id )
, amendment_summary AS (...), top_activated_amendment AS (...), effective_end_date_calc AS (...)  -- :229-294
SELECT DISTINCT ON (l.lease_id)
  l.lease_id, l.pms_tid, l.pms_tenant_code, l.property_id, l.brand_id, l.tenant_profile_id, l.contracted_area,
  l.gross_budget, l.pms_unit_codes, l.start_date, l.end_date, l.sales_report_frequency, l.free_period,
  COALESCE(lua.amendment_status, l.contract_status) AS contract_status, l.lease_type, /* … */
  p.marketing_name, p.marketing_name_ar, l.tenant_display_status, l.admin_display_status,
  COALESCE(NULLIF(TRIM(l.company_name), ''), tp.company_name)       AS company_name,
  COALESCE(NULLIF(TRIM(l.company_name_ar), ''), tp.company_name_ar) AS company_name_ar,
  /* …, */ l.lease_code, l.latest_amendment_status, l.occupancy_status, p.region /* … (:35-121) */
FROM cenomi.leases AS l
JOIN filtered_lease_id AS fl ON l.lease_id = fl.lease_id
LEFT JOIN effective_end_date_calc eed ON l.lease_id = eed.lease_id
LEFT JOIN cenomi.properties p ON l.property_id = p.property_id
LEFT JOIN cenomi.tenant_profiles tp ON l.tenant_profile_id = tp.tenant_profile_id
LEFT JOIN LATERAL (SELECT amendment_status FROM cenomi.leased_units_amendments
                   WHERE lease_id = l.lease_id AND amendment_status = 'Activated'
                   ORDER BY pms_amendment_id DESC LIMIT 1) lua ON true
WHERE LOWER(p.derived_unit_type) = ANY($1)                -- unit types the user's permissions allow
  AND l.tenant_profile_id = $2                            -- active profile
  [AND LOWER(l.contract_status) = ANY($3)]               -- legacy only: {'activated','superseded'}
  AND (COALESCE(eed.has_active_holdover, false) = false
       AND NOW()::date <= COALESCE(eed.effective_end_date, l.end_date) + INTERVAL '30 days')   -- tenant visibility
ORDER BY l.lease_id, pms_last_modified_at DESC
LIMIT 200 /* legacy 1000 */ OFFSET 0;

-- total_count
SELECT COUNT(DISTINCT l.lease_id) FROM cenomi.leases l
LEFT JOIN cenomi.properties p ON l.property_id = p.property_id
JOIN filtered_lease_id fl ON l.lease_id = fl.lease_id
LEFT JOIN effective_end_date_calc eed ON l.lease_id = eed.lease_id
WHERE LOWER(p.derived_unit_type) = ANY($1) AND l.lease_id = ANY($2) AND l.tenant_profile_id = $3
  [AND LOWER(l.contract_status) = ANY($4)] AND <same visibility predicate>;
```

Notes:
- `DISTINCT ON` makes the real order `lease_id ASC`.
- Tenants never see leases whose top activated amendment is a HoldOver, nor leases more than 30 days past their effective end (`LeaseGracePeriodDays`, `constants.go:4442`).
- If `LeaseIDs` is empty, the scope CTE is dropped and only the `tenant_profile_id` filter applies.
- **Go post-processing:**
  - `stripContractedRent` (`contract_handler.go:828-835`) runs unless the user has `VIEW_CONTRACTS_FINANCIAL`. It zeroes the rent fields and **blanks `sales_report_frequency`**.
  - `company` and `company_ar` come from the SQL `COALESCE` above (`domain/contractdto.go:173-174`).
  - The handler de-duplicates rows by `contract_id`.
- `FetchFilterDatas` returns the global `filter.tenant_profile_id` list (every profile id in `leases`) to tenants. This is an information leak.
- No caching. No external calls.

Response (`cenomi-api-2/domain/contractdto.go:297-308` `ContractResponse`; item `ContractDTO :65-148`):

```json
{ "success": true, "data": {
  "current_page": 1, "limit": 200, "total_count": 3,
  "filters": { "cities": ["Dhahran"], "status": ["…"] },
  "filter": { "tenant_profile_id": [ … ] },
  "list": [ {
    "contract_id": 9312, "tenant_profile_id": 512, "pms_tenant_code": "T0001234",
    "property_id": 21, "property_name": "Mall of Dhahran", "property_name_ar": "…",
    "brand_id": 77, "brand_name": "Brand", "brand_name_ar": "…",
    "company": "Acme Retail", "company_ar": "…",
    "start_date": "2023-01-01T00:00:00Z", "end_date": "2028-12-31T00:00:00Z",
    "contract_status": "Activated", "current_status": "Active", "sales_report_frequency": "",
    "mall_name": "Mall of Dhahran", "region": "Eastern", "city": "Dhahran", "lease_type": "…" } ] } }
```

The dashboard reads `property_name`, `property_name_ar`, `company`, `company_ar`, `pms_tenant_code`, `brand_name`, `brand_name_ar`, and (legacy) `start_date` and `end_date`.

---
### 8. Leasing opportunities (malls open to tenants)

| | V2 | Legacy |
|---|---|---|
| Component | `v2/TenantOpportunitiesCard.tsx`; hook `v2/useTenantOpportunities.ts`; model `v2/opportunitiesModel.ts` | `tenant/LeasingOpportunities.tsx` → `property/PropertyListing.tsx` (makes no calls of its own) |
| Visibility | always | always |
| Visual | Two-column grid of mall rows: an image (plain `<img>`, falling back to `MallIcon` on error), the name, "region · city", "`{units}` units available" (tooltip = per-type breakdown), plus "Mall Map" and "Send Enquiry" links. Shows 6 at a time; "View More" adds 6 on the client | `CardLayout` with a property card grid; "View More" requests the next server page |
| Drilldowns | "Mall Map" (only when `mallmapid` is set) opens a `Modal` with an `<iframe src="/mappedin-map?venue={mallmapid}&language=en|ar">`. "Send Enquiry" → `/propertydetails/enquiry?region={region lower-cased}&propertyId={unique_property_id}` | equivalent links in `PropertyListing` |

**V2 mapping** (`opportunities(rows, lng)`):
- Rows without `unique_property_id` are dropped.
- `name` = `marketing_name` or `marketing_name_ar` by locale, falling back to the other.
- `place` = "`region` · `city`".
- `units` = the sum of the values in `available_units`.
- `breakdown` = "`Type N` · …" ordered largest first.
- `venue` = `mallmapid`.
- Sorted by name with `Intl.Collator`, **then** paged on the client, because the API has no ORDER BY.

**Legacy:** `getUniquePropertiesData(page, 6, tenantProfileId)`. `tenantProfileId` is undefined on the dashboard, so it is not sent. "View More" appends page+1 while `items < total_count`.

#### API G / G' — `GET /v1/unique-properties?page=1&limit=100` (V2) · `?page=N&limit=6` (legacy)

**Chain:**
- Route: `cenomi-api-2/unique_property/delivery/http/unique_property_handler.go:35`, registered at `app/main.go:1775` in **`registerPublicRoutes`** (`main.go:1688`). That group only has `OptionalUserAuth` (`main.go:922-924`, `internal/middleware/middleware.go:794-820`). **There is no permission check, and no login is required.**
- Handler `Fetch`: `unique_property_handler.go:50`.
  - `parseRequestParameters` (`:184-275`): defaults are page 1, limit 10, `AllowPagination=true`.
  - `IsFilteredByAccess` is forced on only for ADMIN users (`:60-64`). **For tenants the result is not scoped at all; it is the whole portfolio** (ticket T12).
  - `region`, `status`, `sort_by`, `order`, `brand_id` and `tenant_profile_id` are parsed but never used.
- Usecase `Fetch`: `cenomi-api-2/unique_property/usecase/unique_property_usecase.go:40`.
  - It runs the count first. When the count is 0 it returns an empty `list` and `cities`, and omits `total_count`.
  - Then it runs `GetCities` and the list query.
- Repository: `cenomi-api-2/unique_property/repository/postgres/unique_property_repository.go`.
  - Count `:285` (`queryCountUniqueProperties:37`)
  - Cities `:321` (`:54`)
  - `Fetch:379` (`queryFetchUniqueProperties:112-141`)

```sql
SELECT COUNT(up.unique_property_id)
FROM unique_properties up
WHERE up.property_status = 'TENANT_VISIBLE' AND up.is_primary = true
  AND EXISTS (SELECT 1 FROM properties p WHERE p.unique_property_id = up.unique_property_id
                AND p.property_status::text = 'TENANT_VISIBLE');

SELECT DISTINCT(city) FROM unique_properties WHERE property_status = 'TENANT_VISIBLE';

SELECT up.unique_property_id, up.marketing_name, up.marketing_name_ar, up.image, up.region,
       up.address1, up.address2, up.address3, up.city, up.state, up.country, up.pincode,
       up.total_floors, up.status, up.pms_property_status, up.property_status,
       up.available_units, up.created_at, up.updated_at, up.created_by, up.updated_by,
       up.unique_pms_code, up.property_group_id,
       COALESCE(up.mall_information->>'mallmapid', up.mall_information->>'MallMapID') AS mallmapid
FROM unique_properties up
WHERE up.property_status = 'TENANT_VISIBLE' AND up.is_primary = true
  AND EXISTS (SELECT 1 FROM properties p WHERE p.unique_property_id = up.unique_property_id
                AND p.property_status::text = 'TENANT_VISIBLE')
LIMIT $1 OFFSET $2;          -- NO ORDER BY (T11); $1 = 100 or 6, $2 = (page-1)*limit
-- optional, not sent: AND LOWER(city)=LOWER($n); AND (marketing_name ILIKE $n OR marketing_name_ar ILIKE $n);
--                     admin only: AND unique_property_id = ANY($n); allow_pagination=false drops LIMIT/OFFSET
```

**How `available_units` is filled.** It is not computed per request. It is the stored JSON column `unique_properties.available_units`, maintained by the unit sync job (`unit/usecase/unit_sync_usecase.go:112,136`):

```sql
-- property/repository/postgres/property_sync_repository.go:76-104
UPDATE properties SET available_unit_types = (
  SELECT jsonb_object_agg(unit_type, unit_count) FROM (
    SELECT unit_type, COUNT(*) AS unit_count FROM units
    WHERE unit_type IS NOT NULL AND unit_type <> '' AND property_id = properties.property_id
      AND unit_status = 'AVAILABLE'
    GROUP BY unit_type) AS unit_counts)
WHERE EXISTS (SELECT 1 FROM units WHERE unit_type IS NOT NULL AND unit_type <> '' AND property_id = properties.property_id);

-- unique_property/repository/postgres/unique_property_sync_repository.go:197-233
UPDATE unique_properties u SET available_units = units.available_units
FROM (SELECT u.region, u.marketing_name, u.city, u.unique_pms_code, jsonb_object_agg(u.key, u.value_sum) AS available_units
      FROM (SELECT DISTINCT marketing_name, city, region, SPLIT_PART(pms_property_code,'-',1) AS unique_pms_code, key,
                   SUM(value::INTEGER) OVER (PARTITION BY marketing_name, city, region, SPLIT_PART(pms_property_code,'-',1), key) AS value_sum
            FROM properties, jsonb_each_text(available_unit_types) AS units(key, value)
            WHERE properties.pms_property_status = 'ACTIVE') u
      GROUP BY u.region, u.marketing_name, u.city, u.unique_pms_code) units
WHERE u.region = units.region AND u.marketing_name = units.marketing_name
  AND u.city = units.city AND u.unique_pms_code = units.unique_pms_code;
```

A mall whose properties no longer have any AVAILABLE units drops out of the subquery, so its old `available_units` value is never cleared.

**Go post-processing and caveats:**
- `image` is returned exactly as stored, with no signing. No Go code writes it.
- **Repository quirk:** `Fetch` reuses one DAO and one domain struct across rows (`:430-431`; `domain/uniquepropertydao.go:78-86`).
  - A mall with no map id **inherits the previous row's `mallmapid`**. The V2 map button could open another mall's map.
  - Every row reports the last row's `created_at`/`updated_at`.
- No caching.

Response (`cenomi-api-2/domain/uniquepropertydto.go:66-78` `UniquePropertyResponse`; item `:9-43`):

```json
{ "success": true, "data": {
  "current_page": 1, "limit": 100, "total_count": 24, "cities": ["Riyadh", "Jeddah", "…"],
  "list": [ {
    "unique_property_id": 4, "marketing_name": "Mall of Dhahran", "marketing_name_ar": "…",
    "image": "/assets/malls/mod.jpg", "region": "Eastern", "city": "Dhahran",
    "address1": "", "address2": "", "address3": "", "state": "", "country": "", "pincode": "", "total_floors": 0,
    "status": "ACTIVE", "pms_property_status": "ACTIVE", "property_status": "TENANT_VISIBLE",
    "available_units": { "Store": 34, "KIOSK": 8 },     // omitted when NULL
    "unique_pms_code": "MOD", "property_group_id": 2, "mallmapid": "mall-of-dhahran" } ] } }
```

---
### 9. Survey banner (`SurveyIndicator`)

- Component: `cenomi-frontend-2/libs/ui-web/src/lib/components/dashboards/common/SurveyIndicator.tsx`.
  - V2 renders it as a ui-kit `Callout` (tone info).
  - Legacy renders a pink banner with a link to `surveylink`.
- It is shown above both dashboards, for TENANT users only.
- The frontend calls `getConfigData('NEW_SURVEY')` → `GET /v1/configuration/NEW_SURVEY` and destructures `data.value` into `{EMAIL, ...rest}`.
  - If the user's email is **not** in `EMAIL[].email`, it shows `rest` when `rest.display` is true, using `texten`/`textar` and `surveylink`.
  - If `rest.popup` is set it calls `fetchPopupData()`. The dashboard page does not pass that prop, so this would throw. The error is caught and logged after the state has already been set.

**Chain:**
- Route: `cenomi-api-2/configuration/delivery/http/configuration_handler.go:36`, registered at `app/main.go:2087` in the private group.
- `/v1/configuration/{key}` is not listed in `internal/config/pathpermission.json`, so any authenticated tenant with a role on the active profile passes `PermissionCheck`.
- Handler `GetConfiguration`: `configuration_handler.go:136` → usecase `configuration/usecase/configuration_usecase.go:31` (pass-through) → repository `configuration/repository/postgres/configuration_repository.go:87`.

```sql
SELECT configuration_id, key, value, description, created_by, updated_by, created_at, updated_at
FROM configuration WHERE key = $1;      -- 'NEW_SURVEY'
```

- A missing key returns 500, not 404.
- No caching.
- The response (`cenomi-api-2/domain/configuration.go:9-18`) returns `value` as raw JSON. Its shape is **not defined anywhere in the backend repo**; it is admin-maintained data:

```json
{ "success": true, "data": { "configuration_id": 12, "key": "NEW_SURVEY", "description": "…",
  "value": { "display": true, "popup": false, "texten": "Tell us how we are doing", "textar": "…",
             "surveylink": "https://…", "EMAIL": [ { "email": "already.answered@example.com" } ] },
  "created_by": 1, "updated_by": 1, "created_at": "…", "updated_at": "…" } }
```

---
### 10. Prospective tenant dashboard (`ProspectiveTenant`)

- Component: `cenomi-frontend-2/libs/ui-web/src/lib/components/dashboards/prospectiveTenant/prospectiveDashboard.tsx`. It is legacy only; there is no V2 version.
- Shown when `userType === TENANT && IsProspective`.

Sections:
- **Link cards**, all fed by the `summary` (API A):
  - Lease Requests: `approved_inquiries` / `pending_inquiries`
  - Documents: `pending_documents` → `/tenantprofile?tenantId=X`
  - Service Requests: `approved_service_requests` / `pending_service_requests`
  - Tenant Profile: `brands`
- **`TenantStatus`** (`libs/ui-web/src/lib/components/tenantStatus/TenantStatus.tsx`):
  1. `GET /v1/lead-enquiries?tenant_profile_id=X` → takes `list[0].{lead_enquiry_id, lead_enquiry_code}`.
  2. `GET /v1/lead-enquiries/details?lead_enquiry_code=..&lead_enquiry_id=..` → `ApplicationStatusBody`, which shows:
     - `receivedDocuments` = `documents.length >= 1`
     - `applicationStatus` = `approval_status`
     - `verified` = every `documents[].approval_status === 'APPROVED'`
     - `source`
     - `share_status` = `share_contact_status`
- **`ActionRequired`**: same as API E.
- **`LeasingOpportunities`**: same as API G'.

Backend chains:
- `GET /lead-enquiries`:
  - Route `cenomi-api-2/lead_enquiry/delivery/http/lead_enquiry_handler.go:72`, handler `Fetch :212`. Needs `LEAD_INQUIRY_LIST`.
  - The query `tenant_profile_id` is not pre-validated. After the query, any row belonging to a profile other than the header's returns 401 (`:330-338`).
  - Usecase `lead_enquiry/usecase/lead_enquiry_usecase.go:1471`.
  - Repository `lead_enquiry/repository/postgres/lead_enquiry_repository.go`: count `:1114`, list `:1178` (query `:438-477`).
  - Enrichment:
    - Signed document URLs (`lead_enquiry_usecase.go:1710-1742`) for documents fetched by `company_document_repository.go:260`.
    - Brand, property and company names.
    - Per-row `FetchTenantStatus` (`:2454`, query `:734-741`). If `share_contact_status` is NULL, or the combination is missing from the mapping table, this raises ErrNoRows and the **whole list returns 500**.
    - Per-row `UniquePropertyUsecase.FetchByID`.
  - **DTO reuse bug** (handler `:328`): `unique_property_names` keeps accumulating across rows.

  ```sql
  SELECT COUNT(lead_enquiry_id) FROM lead_enquiries le WHERE le.tenant_profile_id = $1;
  SELECT lead_enquiry_id, lead_enquiry_number, first_name, last_name, company, cr_number, email, email_verified,
         brand_name, sales_category_id, company_headquarters_region, unit_type, region, country_code, phone,
         phone_verified, landline, approval_status, source, created_at, updated_at, created_by, updated_by,
         enquiry_approved_at, tenant_profile_id, unique_property_id, assigned_tenant_profile_id, assigned_brand_id,
         landline, share_contact_status, lead_enquiry_code, property_id, reference_number_brand_mall_company,
         property_ids, deal_reference_id, deal_details_id
  FROM lead_enquiries le WHERE le.tenant_profile_id = $1 LIMIT 10 OFFSET 0;   -- no ORDER BY, so list[0] is arbitrary
  SELECT document_id, tenant_profile_id, enquiry_id, document_number, document_type, document_path, uploaded_on,
         expiry_date, approval_status, version, comments, text1, updated_by, created_by, is_additional_document,
         pms_post_status, pms_post_log, updated_at
  FROM company_documents WHERE enquiry_id = ANY($1);
  ```

- `GET /lead-enquiries/details`:
  - Route `lead_enquiry_handler.go:69`, handler `FetchPublic :431`. It is **fully public**: `SkipPrivateOperation` (`app/main.go:4579-4582`) bypasses the token and permission checks, so knowing the code is enough.
  - Usecase `lead_enquiry_usecase.go:1644`.
  - Repository `FetchByEnquiryCode :1911` (query `:314-373`):

  ```sql
  SELECT le.lead_enquiry_id, le.lead_enquiry_number, le.first_name, le.last_name, le.company, /* … */
         le.approval_status, le.source, le.tenant_profile_id,
         equ.first_name || ' ' || equ.last_name AS enquiry_approved_by, le.enquiry_approved_at, le.enquiry_comment,
         lu.first_name || ' ' || lu.last_name AS lead_approved_by, le.lead_approved_at, le.lead_comment,
         le.share_contact_status, le.lead_enquiry_code, le.assigned_tenant_profile_id, le.assigned_brand_id /* , … */
  FROM lead_enquiries le
  LEFT JOIN users equ ON le.enquiry_approved_by = equ.user_id
  LEFT JOIN users lu  ON le.lead_approved_by   = lu.user_id
  WHERE lead_enquiry_code = $1;   -- then lead_enquiry_id / email must match if sent; otherwise 404
  ```

  - Documents use the same SQL as above, with signed `document_path`.
  - Response: `domain.LeadEnquiryStatusCheckResponse` (`domain/leadEnquirydto.go:166-169`), which embeds `LeadEnquiryDTO`. Fields: `approval_status`, `source`, `share_contact_status`, and `documents[]` (`CompanyDocumentsDTO`, `domain/companyDocumentdto.go:10-30`) with `approval_status` and `document_path`.

---
### 11. Design references

- Spec: `cenomi-frontend-2/docs/ui-v2/ui-v2-tenant-dashboard-redesign.md`. §3.1 lists the 14 legacy bugs fixed, §5 the per-card specs, §6 the data sources and backend rules, and §6.4 the backend tickets T1–T12.
- Mockup: `cenomi-frontend-2/docs/ui-v2/reference/tenant-dashboard.html`, with `tenant-dashboard-overview.png`, `tenant-dashboard-categories.png` and `tenant-dashboard-dock.png`.
- Note: some spec text still describes the year as "the page's filter bar" and the mall filter as covering the tiles. In the code there is no page bar. The year lives on the Sales card, the mall on the Service Requests card, and the tiles share their state.

### 12. Cross-cutting findings

| # | Finding | Where |
|---|---|---|
| 1 | `completed_payments` / `pending_payments` are never selected, so they are always 0 (T1) | `tenantsummary/repository/postgres/tenant_summary_repository.go`, `domain/tenantsummarydto.go:30` |
| 2 | Sales "pending" bucket: the summary uses `UPLOADED_SUPPORTING_DOCUMENT`, the dashboard uses `NEED_UPLOAD_SUPPORTING_DOCUMENT` (T4) | `tenant_summary_repository.go:296-301` vs `useTenantSalesCounts.ts` |
| 3 | `pending_service_requests` counts `IN_PROCESS` over every category with no 90-day rule. It cannot match the list, so V2 computes "open" from the list instead (T3) | summary SQL `service_request_summary` |
| 4 | `/service-requests` returns `total_count=0` on an empty page (`service_request_usecase.go:1586`). `/sales-data` and `/unique-properties` omit `total_count` when it is 0 (T7) | |
| 5 | `/sales-data` builds `status IN (...)` by string concatenation (injection risk). Its period filter is an overlap test, not containment | `sales_data_repository.go:954-967, 925-948` |
| 6 | `/sales-data` with a `tenant_profile_id` skips lease-level access scoping, so a lease-restricted contact sees the whole company's sales | `sales_data_usecase.go:816-819` |
| 7 | `/unique-properties` is public and unscoped, has no ORDER BY, and leaks `mallmapid` between rows | `unique_property_repository.go:112-141, 430` |
| 8 | Notifications ignore the active profile and span every company of the contact (hence the company-switch prompt). `limit=0` returns the whole table | `notification_handler.go:43-62`, `notification_repository.go:362-372` |
| 9 | Announcements: `upcoming` overlaps `today`; event limits are hard-coded (6 and 3); there is no date window for announcements | `announcement_usecase.go:103`, `announcement_repository.go:576` |
| 10 | `/contracts` returns the global `filter.tenant_profile_id` list to tenants, blanks `sales_report_frequency` without `VIEW_CONTRACTS_FINANCIAL`, and does not validate a query `tenant_profile_id` | `contract_repository.go:1758`, `contract_handler.go:94-100, 828-835` |
| 11 | Legacy SR pies download the tenant's whole SR history twice per pie (`limit=total_count`), including N+1 history queries per work-permit or fit-out row | `PieChart.tsx`, `SRPieChart.tsx`, `service_request_usecase.go:1529` |
| 12 | The SR `mall` filter matches more sources than the displayed `mall` column | `service_request_repository.go:2004-2028` vs the `queryListAllServiceRequests` select |
| 13 | `/lead-enquiries/details` is fully public (code only). `/lead-enquiries` list can return 500 when `share_contact_status` is NULL | `app/main.go:4579`, `lead_enquiry_repository.go:2454` |
| 14 | The Next BFF routes under `apps/cenomi-tenant-web/app/api/*` (dashboard, summary-data, …) are static mocks that the dashboard never calls | |

---

## 6. Consolidated findings and risks

These are pulled together from the sections above. File references point to `cenomi-api-2` unless marked otherwise.

### 6.1 Security and access

| # | Finding | Where |
|---|---|---|
| S1 | **SQL injection:** `/sales-data` builds `status IN ('…')` by concatenating the comma-split `status` param into the query | `sales_data/repository/postgres/sales_data_repository.go` (`buildLeadEnquiryFilterQueryCondition`, `buildSalesDataFilterQueryCondition`, `buildDistinctLeaseCodesFilterQueryCondition`) |
| S2 | No backend path-permission check for `sales-funnel` (so `SALES_FUNNEL_LIST` is never enforced), `pending-approval`, `pending-amendments-summary`, `lease-requests-summary` or `units-with-fitout` (`SkipPermissionCheck`) | `app/main.go:~4590` |
| S3 | `summary-data`, `notifications` and `unique-properties` have no `pathpermission.json` entry, so any logged-in user can call them. `lead-enquiries/details` is fully public. | `internal/config/pathpermission.json` |
| S4 | `/lead-enquiries` drops the property filter when the requested `unique_property_id` is outside the admin's scope (an empty list means no filter) | `lead_enquiry/usecase/lead_enquiry_usecase.go:1519-1525` |
| S5 | A non-numeric `year` on `/lead-enquiries` makes the WHERE builder return `""`, which removes **all** scoping | `lead_enquiry_repository.go:1680` |
| S6 | `/sales-data` with `tenant_profile_id` drops lease-level scoping. `lease_codes` ignores access scope. | `sales_data_usecase.go:816` |
| S7 | `/units-with-fitout` and `/unit-fitout-status` apply no user scoping | `fitout_summary_handler.go:882/615` |
| S8 | `/contracts` returns the global `filter.tenant_profile_id` list, even to tenants | `contract_repository.go:1758` |
| S9 | Frontend widget permissions and backend endpoint permissions differ, so a card can be visible while its API returns 403 | §1.3 |
| S10 | `/contracts` and `/proposals` return **500**, not 403, when the user lacks the per-unit-type view permissions | `contract/usecase/contract_usecase.go:50-54`, `proposal/usecase/proposal_usecase.go:179-197` |

### 6.2 Numbers that disagree between cards, popups and sources

| # | Finding |
|---|---|
| D1 | **Sales funnel:** the live `/contracts`, `/proposals` and `/lead-enquiries` counts (`admin_display_status`) do not match the batch `cenomi.sales_funnel` table (PMS `contract_status` / `pms_proposal_status`). V2 shows the live counts and uses `/sales-funnel` only for `last_synced_at`. |
| D2 | **Signed + unsigned ≠ total:** for proposals and contracts, statuses outside the two lists, and NULL statuses, appear only in `all_counts`. `un_signed_count` for proposals never includes "proposal expired". |
| D3 | **Service requests:** the summary tile and the drilldown list are scoped differently. The list restricts by role / operation / creator SR IDs, contractor and Soft-FM rules, and hides APPROVED/REJECTED older than 90 days; the summary does none of this. A `status=PENDING` drilldown on a non-fit-out category applies **no** status filter. |
| D4 | **Fit-out:** the summary counts deleted rows and buckets `ACTIVE` differently from the popup list. |
| D5 | **Delay bands:** pending approvals uses [21,31) and ≥31 and drops future-dated rows; pending amendments uses [21,28) and 28+ and puts future-dated rows into "4 week+". |
| D6 | **Pending sales:** `summary-data` counts `UPLOADED_SUPPORTING_DOCUMENT`, while the dashboard `/sales-data` call uses `NEED_UPLOAD_SUPPORTING_DOCUMENT`. |
| D7 | **"Active leases"** KPI (`status=ACTIVATED`) also counts Expired leases within the 30-day grace period, and Superseded leases. |
| D8 | **Time zones are inconsistent:** proposals and contracts use the raw `pms_created_at`; lead enquiries and SRs use `AT TIME ZONE 'asia/riyadh'`, which may shift the wrong way on `timestamp` columns; discrepancy uses UTC month windows. |
| D9 | **Region means different things:** in lead enquiries it is the enquirer's free-text `lead_enquiries.region`; elsewhere it is `properties.region`. The SR summary match is case-sensitive and only covers SRs with `sr.property_id` set. |

### 6.3 Correctness and robustness bugs

| # | Finding | Where |
|---|---|---|
| B1 | `/sales-funnel` without `year` hits a nil-pointer panic once any successful sync exists (the dashboard always sends `year`, so it is not hit today) | `sales_funnel/usecase/sales_funnel_usecase.go:83-85` |
| B2 | `/lease-requests-summary`: the store/office unit type is chosen by Go map order, so it changes randomly between requests | `constants.UnitTypeRoleMap` |
| B3 | `/unique-properties/details`: admins with all-properties access and no region get an **empty** result (`AllProperties` is never consulted) | `unique_property_usecase.go:104` |
| B4 | `/unique-properties`: one row struct is reused, so `mallmapid` leaks from the previous row and the V2 "Mall Map" button can open the wrong mall | tenant §8 |
| B5 | Many count fields are `omitempty` and vanish at 0 (`all_counts`, `signed_count`, `un_signed_count`, `leads_count`, `lease_request_counts`, `total_count` on sales-data and unique-properties). The frontend must default them. | DTOs |
| B6 | `last_synced_at` is unreliable: always null on `service-request-summary`; Riyadh wall-clock time labelled `Z` on `pending-approval`; request time on `lease-requests-summary` and document status | |
| B7 | `service-request-summary` without `year` returns duplicate category/sub-category rows, one per year | |
| B8 | `summary-data`: `completed_payments` and `pending_payments` are always 0 | `tenantsummary/repository/postgres/tenant_summary_repository.go` |
| B9 | `/fitout-summary` ignores `unit_id`. The fit-out handlers compare `DD-MM-YYYY` dates as strings. | `fitout_summary_handler.go` |
| B10 | Pagination without `ORDER BY` (lead enquiries without `sort_by`, `unique-properties`) can repeat or skip rows | |
| B11 | `/notifications` `DISTINCT ON` picks an arbitrary row per group, and `text_content` can leak between rows | `notification_repository.go:353` |

### 6.4 Performance

- V2 fetches `/fitout-summary` twice (once per fit-out card), and `/discrepancy/monthly-graph` twice in mall-wise mode.
- The KPI tiles and the funnel ask for counts only (`limit=1`), but each endpoint still runs the full list query, N+1 enrichment, signed-URL generation (`sales-data`) and global filter queries.
- `GetPermittedItems` (expand variant) materialises every lease ID for all-access admins. These are then bound as `ANY($n)` (`notifications`) or inlined as CSV in CTEs (`contracts`).
- The legacy tenant SR pies download the tenant's full SR history twice each.
- The `/unique-properties/details` list computes the occupancy CTE for every eligible mall, even with `limit=1`.

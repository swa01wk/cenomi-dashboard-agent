"""DX6 refinement 1 — canonical KPI reconciliation and golden-data invariants (design verification, not app code).

Builds record-level cohorts that reproduce (a) the 20 Oct snapshot shown on the DX2 dashboard and (b) every
declared weekly series, then recomputes the series from the records with the V2 band rules. If a series could
not be produced by any record lifecycle, construction fails. Writes dx6/recon.json.
"""
import json, sys, datetime as dt, statistics as st
sys.path.insert(0, sys.argv[1] + '/dx6')
import history as H
S = sys.argv[1]
D, D3 = H.load(S)
ROWS = {r['mall']: r for r in D['rows']}
CENTRAL = D['mallsByRegion']['Central']
K = len(H.WEEKS) - 1
DAY = dt.timedelta(days=1)
checks = []
def check(gid, name, ok, detail):
    checks.append({'id': gid, 'name': name, 'ok': bool(ok), 'detail': detail}); return ok

# ---------------------------------------------------------------- approvals cohorts
AP_BANDS = [(0, 6), (7, 13), (14, 20), (21, 30)]          # V2: 0-6, 7-13, 14-20, 21-30, >=31 (Asia/Riyadh days)
def ap_band(age):
    if age is None or age < 0: return None                # V2: future or NULL timestamps are dropped
    for i, (a, b) in enumerate(AP_BANDS):
        if a <= age <= b: return i
    return 4
def build_ap(mall, series):
    """Items: dict(type, start, end) where start = pms_created_at (proposals) or pms_last_modified_at (contracts,
    leases) and end = resolution date (None = still pending on as_of). No modification inside the window."""
    snap = ROWS[mall]['ap']; items = []
    n1 = sum(snap[t][4] for t in snap)
    # pending items in the lower bands: deterministic ages spread inside each band
    for t in ('proposal', 'contract', 'lease'):
        for bi, (a, b) in enumerate(AP_BANDS):
            for j in range(snap[t][bi]):
                age = a + (j * 3) % (b - a + 1)
                items.append({'type': t, 'start': H.AS_OF - age * DAY, 'end': None, 'cohort': 'pending'})
    # pending items in 1m+: as many as possible already old at each earlier checkpoint (minimal churn)
    T = [min(n1, min(series[j:])) for j in range(K + 1)]
    ages = []
    for k in range(K + 1):
        new = T[k] - (T[k - 1] if k else 0)
        lo = 31 + 7 * (K - k)
        for j in range(new): ages.append(lo + (j % 7) if k else lo + 2 * j)
    types = [t for t in ('proposal', 'contract', 'lease') for _ in range(snap[t][4])]
    for t, age in zip(types, sorted(ages, reverse=True)):
        items.append({'type': t, 'start': H.AS_OF - age * DAY, 'end': None, 'cohort': 'pending'})
    # resolved items fill the gap between the series and what the still-pending items explain
    G = [series[k] - T[k] for k in range(K + 1)]
    assert all(g >= 0 for g in G), (mall, G)
    active = []
    for k in range(K + 1):
        tk = H.WEEKS[k]
        while len(active) > G[k]:
            it = active.pop(0); it['end'] = H.WEEKS[k - 1] + 3 * DAY       # counted at t(k-1), gone by t(k)
        while len(active) < G[k]:
            start = tk - (31 + 2) * DAY if k else tk - 60 * DAY           # crosses 31 days between t(k-1) and t(k)
            it = {'type': 'proposal', 'start': start, 'end': None, 'cohort': 'resolved'}; items.append(it); active.append(it)
    assert not active, mall
    return items
def ap_count(items, t, band=4, typ=None):
    n = 0
    for it in items:
        if typ and it['type'] != typ: continue
        if it['start'] <= t and (it['end'] is None or it['end'] > t) and ap_band((t - it['start']).days) == band: n += 1
    return n

AP_ITEMS = {m: build_ap(m, H.AP1M[m]) for m in CENTRAL}
for m in CENTRAL:
    rec = [ap_count(AP_ITEMS[m], t) for t in H.WEEKS]
    check('GI-03', 'Approvals 1m+ series reconstructed from records · ' + m, rec == H.AP1M[m], {'declared': H.AP1M[m], 'from_records': rec})
    snap_ok = all(ap_count(AP_ITEMS[m], H.AS_OF, b, t) == ROWS[m]['ap'][t][b] for t in ('proposal', 'contract', 'lease') for b in range(5))
    check('GI-01', 'Approvals snapshot by type and band equals the DX2 card · ' + m, snap_ok, ROWS[m]['ap'])
    check('GI-02', 'Approvals series ends on the snapshot · ' + m, H.AP1M[m][-1] == ROWS[m]['apOldTot'], {'last': H.AP1M[m][-1], 'snapshot': ROWS[m]['apOldTot']})
c_series = [sum(H.AP1M[m][k] for m in CENTRAL) for k in range(K + 1)]
check('GI-05', 'Central 1m+ = Σ malls at every checkpoint; 62 on 20 Oct, 61 on 13 Oct', c_series[-1] == sum(D['apReg']['Central'][t][4] for t in D['apReg']['Central']) == 62 and c_series[-2] == 61, {'central': c_series})
rawdah = AP_ITEMS['Rawdah Point Mall']
check('GI-01', 'Rawdah Point all pending on 20 Oct = 71 (32 proposals · 23 contracts · 16 leases); 1m+ = 41 (19 · 15 · 7)',
      sum(ap_count(rawdah, H.AS_OF, b) for b in range(5)) == 71 and [sum(ap_count(rawdah, H.AS_OF, b, t) for b in range(5)) for t in ('proposal', 'contract', 'lease')] == [32, 23, 16]
      and [ap_count(rawdah, H.AS_OF, 4, t) for t in ('proposal', 'contract', 'lease')] == [19, 15, 7], {})
cohort_summary = {m: {'pending': sum(1 for i in AP_ITEMS[m] if i['cohort'] == 'pending'), 'resolved_in_window': sum(1 for i in AP_ITEMS[m] if i['cohort'] == 'resolved'),
                      'oldest_days': max((H.AS_OF - i['start']).days for i in AP_ITEMS[m] if i['end'] is None) if AP_ITEMS[m] else None,
                      'pending_aged_122_plus': sum(1 for i in AP_ITEMS[m] if i['end'] is None and (H.AS_OF - i['start']).days >= 122)} for m in CENTRAL}

# ---------------------------------------------------------------- renewal amendment cohorts (records fixed by DX4)
AM_BANDS = [(0, 6), (7, 13), (14, 20), (21, 27)]          # V2: 0-6, 7-13, 14-20, 21-27, >=28; future-dated -> 4 wk+
def am_is4(age): return age is None or age < 0 or age >= 28
VISIBLE = {r[0]: {'mall': r[1], 'lease': r[2], 'age': int(r[4])} for r in D['amRecords']['rows']}
UNSHOWN_AGES = {'Rawdah Point Mall': [30, 29, 29, 28, 28], 'Sandstone Galleria': [30, 29, 28], 'Qasr Plaza': [30, 29]}
def build_ren(mall, series):
    ages = [v['age'] for v in VISIBLE.values() if v['mall'] == mall] + UNSHOWN_AGES[mall]
    assert len(ages) == ROWS[mall]['renewal4'], (mall, ages)
    items = [{'start': H.AS_OF - a * DAY, 'end': None, 'cohort': 'pending'} for a in ages]
    P = [sum(1 for a in ages if a >= 28 + 7 * (K - k)) for k in range(K + 1)]
    G = [series[k] - P[k] for k in range(K + 1)]
    feasible = all(g >= 0 for g in G)
    active = []
    if feasible:
        for k in range(K + 1):
            tk = H.WEEKS[k]
            while len(active) > G[k]:
                it = active.pop(0); it['end'] = H.WEEKS[k - 1] + 3 * DAY
            while len(active) < G[k]:
                it = {'start': tk - (28 + 2) * DAY if k else tk - 50 * DAY, 'end': None, 'cohort': 'resolved'}; items.append(it); active.append(it)
        feasible = not active
    return items, P, G, feasible
def ren_count(items, t):
    return sum(1 for it in items if it['start'] <= t and (it['end'] is None or it['end'] > t) and am_is4((t - it['start']).days))
REN_ITEMS = {}
for m, ser in H.REN4.items():
    items, P, G, ok = build_ren(m, ser); REN_ITEMS[m] = items
    rec = [ren_count(items, t) for t in H.WEEKS] if ok else None
    check('GI-03', 'Renewal 4 wk+ series reconstructed from records (visible DX4 records fixed) · ' + m, ok and rec == ser,
          {'declared': ser, 'explained_by_pending_records': P, 'resolved_cohort_needed': G, 'resolved_items': sum(1 for i in items if i['cohort'] == 'resolved')})
    check('GI-02', 'Renewal 4 wk+ series ends on the snapshot · ' + m, ser[-1] == ROWS[m]['renewal4'], {'last': ser[-1], 'snapshot': ROWS[m]['renewal4']})
am4_c = [sum(H.REN4[m][k] for m in H.REN4) + H.OTHER4_CENTRAL for k in range(K + 1)]
check('GI-05', 'Central amendments 4 wk+ (all types) = Σ renewals + 7 others; 25 on 20 Oct', am4_c[-1] == sum(D['amReg']['Central'][t][0] for t in D['amReg']['Central']) == 25, {'central': am4_c})
raw_res = [i for i in REN_ITEMS['Rawdah Point Mall'] if i['cohort'] == 'resolved']
ren_cohort = {'resolved': len(raw_res), 'resolved_between': [min(i['end'] for i in raw_res).isoformat(), max(i['end'] for i in raw_res).isoformat()] if raw_res else None}

# ---------------------------------------------------------------- vacancy, discrepancy, tenant
units = {m: ROWS[m]['units'] for m in CENTRAL}
for m, ser in H.VAC.items():
    check('GI-02', 'Vacancy series ends on the snapshot · ' + m, ser[-1] == ROWS[m]['vacant'], {'last': ser[-1], 'snapshot': ROWS[m]['vacant']})
check('GI-15', 'Central vacant units = Σ malls = 408 of 3,420 on 20 Oct', sum(ROWS[m]['vacant'] for m in CENTRAL) == D['pu']['Central'][2] == 408 and sum(units.values()) == D['pu']['Central'][0], {})
g = next(u for u in D['ud'] if u['mall'] == 'Gulf Gate Mall')
check('GI-02', 'Gulf Gate September report = 11 mismatched of 142 (DX2 card)', H.UD_GULF['mm'][-1] == g['mm'] and H.UD_GULF['units'][-1] == g['total'], g)
allm = sum((D['mallsByRegion'][r] for r in ('Central', 'Eastern', 'Western')), [])
check('GI-16', 'September coverage: 18 reported + 7 missing = 25 malls', len(D['ud']) + len(H.UD_MISSING) == len(allm) == 25 and sorted(H.UD_MISSING) == sorted(D['quiet']), {})
check('GI-11', 'September reports are ingested 19 Oct 18:30: invisible to the 13 Oct checkpoint, visible from the 19 Oct event run', H.SEP_REPORTS_INGESTED.date() > dt.date(2026, 10, 13), {'ingested_at': H.SEP_REPORTS_INGESTED.isoformat()})
TS = H.tenant_sales(D)
check('GI-02', 'Tenant T-31206 2026 sales equal the DX2 tenant card', TS['2026'] == [c['v'] for c in D['tenant']['cols']], {})
yoy_sep = (TS['2026'][8] - TS['2025'][8]) / TS['2025'][8]
d25 = (TS['2025'][8] - TS['2025'][5]) / TS['2025'][5]; d26 = (TS['2026'][8] - TS['2026'][5]) / TS['2026'][5]
check('GI-10', 'Prior-year baseline exists for T-31206 (2024 and 2025 in the dataset, DR-004)', all(v is not None for v in TS['2025'][:9]), {'2025_jan_sep': TS['2025'][:9], 'yoy_sep': round(yoy_sep, 4), 'jun_sep_2025': round(d25, 4), 'jun_sep_2026': round(d26, 4)})
sandstone_sr = H.TENANT_SR_ACTION_REQUIRED['Sandstone Galleria']; company_sr = sum(H.TENANT_SR_ACTION_REQUIRED.values())
check('GI-09', 'Tenant-audience facts use lease T-31206 only: SR in Action required = 0 for the lease (2 is the company-wide count)', sandstone_sr == 0 and company_sr == next(s['v'] for s in D3['tsr']['status'] if s['label'] == 'Action required'), {'lease': sandstone_sr, 'company': company_sr, 'lease_actions': [a['what'] for a in H.TENANT_ACTIONS]})
# share and denominators
shares = {m: ROWS[m]['apOldTot'] / ROWS[m]['apTot'] for m in CENTRAL}
med = st.median(shares.values()); small = [m for m in CENTRAL if ROWS[m]['apTot'] < 10]
check('GI-06', 'Share facts use one checkpoint for numerator and denominator; Rawdah 41/71 = 57.7%', abs(shares['Rawdah Point Mall'] - 41 / 71) < 1e-12, {'central_median_share': round(med, 4), 'malls_with_fewer_than_10_pending': small})

# ---------------------------------------------------------------- cross-phase discrepancies found and how they are resolved
WK = dict(zip(H.WL, H.AP1M['Rawdah Point Mall']))
DISC = [
 ('C1', 'DX1 shell insight i1', '“41 of 71 pending items are older than 31 days” dated to the 30 Sep checkpoint', f'41 of 71 is the 20 Oct snapshot. On 29 Sep the series is {WK["29 Sep"]}.', 'DX1 shell insights are superseded by the DX6 canonical insights; the DX1 board now shows INS-107 values with their dates.', 'Fixed'),
 ('C2', 'DX1 shell insight i1', '“rose from 22% to 58% between the 31 Jul and 30 Sep checkpoints” (a share)', 'DX6 uses a count (22 on 1 Sep). 22% and 22 are different measures on different dates; the earlier share has no source.', 'Insights report the count; the share is reported only at the checkpoint where both parts exist (57.7% on 20 Oct).', 'Fixed'),
 ('C3', 'DX1 shell insight i1', '“Central median 19%”', f'Recomputed median share of pending approvals waiting 31+ days across Central malls: {med * 100:.1f}%. {len(small)} malls have fewer than 10 pending items (Mirage Commons: 1 of 1 = 100%).', 'Statement withdrawn. Shares need a minimum denominator of 10 (detector configuration).', 'Fixed'),
 ('C4', 'DX1 shell, DX6 text', '“older than 31 days” and “approvals over a month”', 'V2 band is ≥ 31 days (“1 month plus delay”); “older than 31 days” would mean ≥ 32.', 'Canonical label: “waiting 31+ days (1m+)”. Contracts and leases count from their last change, proposals from creation.', 'Fixed'),
 ('C5', 'DX5 sample I3, review language', '“overdue approvals”, “12 overdue renewals”', 'No SLA exists in the dataset; DX2 caveat: age bands are not SLA breaches. Canonical Rawdah renewals in 4 wk+: 9.', '“Overdue” is banned in generated text (verifier word list). I3 stays a rejection test; its number is deliberately ungrounded and labelled so.', 'Fixed'),
 ('C6', 'DX6 history', 'Weekly “approvals over a month” history', 'V2 computes approvals live against NOW(); there is no history in REF. A history is a new as-of metric.', 'New metrics approvals.pending_by_delay.asof v1 and amendments.pending_by_age_band.asof v1 (kind: new), computed from seeded status history. At the as-of date they must equal the parity metrics (GI-01).', 'Needs KPI-catalog approval (M0)'),
 ('C7', 'DX6 text', '“waiting”', 'Contracts and leases age from pms_last_modified_at: any change resets the age.', 'Insight definitions and limitations say so; cohorts in the seed do not modify 1m+ contracts unless a scenario requires it.', 'Fixed'),
 ('C8', 'INS-090', 'Generated by D2 with a level threshold of 8 after three increases; resolved “5 on 22 Sep”', 'D2 needs ≥ 4 increases in 6 changes and a net change ≥ 5. The series is 7 on 22 Sep (5 is 29 Sep).', 'Regenerated by the replay: fires on 1 Sep (3 → 9 since 21 Jul), clears on 22 Sep (8, then 7).', 'Fixed'),
 ('C9', 'INS-101', 'D1 concentration first generated 13 Oct', 'Replaying the declared history, D1 already holds on 15 Sep (27 of 53, 50.9%).', 'Regenerated: INS-101 opens on 1 Sep (D2), D1 joins on 15 Sep, merged into INS-107 on 20 Oct.', 'Fixed'),
 ('C10', 'INS-103', 'D3 improvement first generated 20 Oct', 'Replay: D3 holds on 6 Oct (4 against a window maximum of 9).', 'Regenerated: generated 6 Oct, updated silently on 13 and 20 Oct.', 'Fixed'),
 ('C11', 'Renewals history', 'Rawdah renewals 4 wk+ 4 → 9', f'The visible DX4 records fix the ages of the pending renewals; the series needs {ren_cohort["resolved"]} renewals that were 4 wk+ and were resolved in the window ({ren_cohort["resolved_between"][0] if ren_cohort["resolved_between"] else "—"} to {ren_cohort["resolved_between"][1] if ren_cohort["resolved_between"] else "—"}).', 'Recorded as a required seed cohort (golden scenario manifest). Without it D6 cannot fire.', 'Fixed (seed requirement)'),
 ('C12', 'INS-108 / T-201, thread answer', '“No prior-year data”; “Sales for 2025 are not in the dataset”', f'DX2 tenant board and DR-004 include 2024–2025. September is {yoy_sep * 100:+.1f}% against September 2025; June→September fell {abs(d25) * 100:.1f}% in 2025 and {abs(d26) * 100:.1f}% in 2026.', 'D7 uses the prior year when ≥ 13 months exist. Result: not generated, seasonal pattern (N9). S6 expected outcome corrected — needs your confirmation.', 'Fixed · decision GDQ'),
 ('C13', 'T-202 and tenant dashboard card', '“2 service requests are waiting for your action” for lease T-31206', 'The 2 are company-wide (Rawdah 1, Gulf Gate 1). Lease T-31206 (Sandstone Galleria) has 0.', 'D8 counts lease-scoped action items: 2 fit-out drawings to upload (Lighting layout since 12 Oct; Shopfront details re-upload since 17 Oct).', 'Fixed'),
 ('C14', 'INS-104 hypothesis', '“the dataset holds no lease-expiry schedule”', 'Lease end dates exist (expiring-leases KPI, DX2).', 'Hypothesis kept as a hypothesis with a checkable question: which Mirage Commons leases ended since April without renewal.', 'Fixed'),
 ('C15', 'INS-104', 'Created 20 Sep by run_m_2026-10-20', 'Creation and run disagree.', 'Version 1 from run_m_2026-09-20; version 2 from run_m_2026-10-20.', 'Fixed'),
 ('C16', 'INS-107 limitation', '“no earlier history in the POC”', 'DR-004: transactional history from 2024-01-01.', 'Limitation states the detector window (7 weekly checkpoints) instead.', 'Fixed'),
 ('C17', 'DR-005 vs DX6', 'Month-end checkpoints (DR-005 example) vs weekly + monthly-on-the-20th + events', 'Different calendars.', 'DXQ-12 A: weekly Tuesday checkpoints, monthly on the as-of day for stock metrics, calendar months for monthly reports, plus data-load and status-change events. DR-005 note updated.', 'Fixed'),
 ('C18', 'DX6 detectors', 'Coverage thresholds 90% (D5) and 80% (regional evaluation) unnamed', 'Two different purposes.', 'Config keys coverage.alert_below = 0.90 and coverage.min_for_regional_eval = 0.80.', 'Fixed'),
 ('C19', 'DX6 contract D4', '“double the trailing average; robust z ≥ 3” (and/or unclear)', 'Two tests with different meanings.', 'D4a temporal and D4b cross-sectional, each stated in the evidence.', 'Fixed'),
 ('C20', 'DX6 contract D6', '“both fire D2-type rules”', 'Renewals had a flat week (7 → 7); strict D2 would not fire.', 'Formal D2: ≥ 4 increases in the last 6 changes, no decrease, net change ≥ minimum.', 'Fixed'),
 ('C21', 'DX2 approvals drill-down', 'Records with random ages (31–140) and random mall labels', f'A fixture, not the seeded population. The reconstructed cohort needs, for example, {cohort_summary["Rawdah Point Mall"]["pending_aged_122_plus"]} Rawdah items aged ≥ 122 days.', 'Drill-down records come from the seed in M2 (DXD-49); the prototype fixture stays labelled (DXD-50).', 'Carried to M1/M2'),
]
out = {'checks': checks, 'passed': sum(c['ok'] for c in checks), 'total': len(checks), 'discrepancies': [dict(zip(['id', 'where', 'claim', 'finding', 'resolution', 'status'], d)) for d in DISC],
       'cohorts': {'approvals': cohort_summary, 'renewals_rawdah': ren_cohort, 'renewals': {m: {'resolved_in_window': sum(1 for i in REN_ITEMS[m] if i['cohort'] == 'resolved')} for m in REN_ITEMS}},
       'canonical': {'rawdah_pending_total': 71, 'rawdah_1mplus': 41, 'rawdah_by_type_1mplus': [19, 15, 7], 'central_1mplus': 62, 'central_pending_total': 130, 'rawdah_share': 41 / 71, 'central_median_share': med,
                     'tenant_yoy_sep': yoy_sep, 'tenant_jun_sep_2025': d25, 'tenant_jun_sep_2026': d26, 'weeks': H.WL, 'central_1mplus_series': c_series, 'central_am4_series': am4_c}}
json.dump(out, open(S + '/dx6/recon.json', 'w'), indent=1, default=str)
bad = [c for c in checks if not c['ok']]
print('recon checks', out['passed'], '/', out['total'], '· discrepancies', len(DISC))
for b in bad: print('FAIL', b['id'], b['name'], json.dumps(b['detail'], default=str)[:300])
print('cohorts', json.dumps(out['cohorts'], default=str)[:900])

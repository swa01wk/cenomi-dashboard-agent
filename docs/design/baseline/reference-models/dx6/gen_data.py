"""DX6 scenario data, detectors and insight records.

Deterministic. Series are a synthetic history extension of sd-2026.10.20-01: every series ends exactly
on the value the shared dataset holds for 20 Oct 2026 (asserted below), so the inbox, the dashboard and
the agent workspace agree. Detectors, scoring, suppression and lifecycle are applied here (the analytics
layer); the prototype only renders and records user actions.
"""
import json, statistics as st, sys, hashlib
S = sys.argv[1]
D = json.load(open(S + '/dx4/raw.json'))
D3 = json.load(open(S + '/dx3/data.json'))
ROWS = {r['mall']: r for r in D['rows']}
CENTRAL = D['mallsByRegion']['Central']
REGION_OF = D['regionOf']
DSV = 'sd-2026.10.20-01'

def n0(v): return f'{v:,.0f}'
def pct(v, d=1): return f'{v * 100:.{d}f}%'
def pts(v): return f'{v * 100:+.1f} pts'.replace('-', '−')
def sar(v): return 'SAR ' + n0(v)
def fmt(v, unit):
    if v is None: return '—'
    return {'count': n0, 'rate': pct, 'pts': pts, 'SAR': sar, 'change': lambda x: f'{x * 100:+.1f}%'.replace('-', '−'), 'weeks': lambda x: f'{x:.0f}', 'z': lambda x: f'{x:.1f}', 'r': lambda x: f'{x:.2f}'}[unit](v)
def hid(*a): return hashlib.sha1('|'.join(map(str, a)).encode()).hexdigest()[:8]

WEEKS = ['2026-08-11', '2026-08-18', '2026-08-25', '2026-09-01', '2026-09-08', '2026-09-15', '2026-09-22', '2026-09-29', '2026-10-06', '2026-10-13', '2026-10-20']
WL = ['11 Aug', '18 Aug', '25 Aug', '1 Sep', '8 Sep', '15 Sep', '22 Sep', '29 Sep', '6 Oct', '13 Oct', '20 Oct']
MONTHS = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
# ---------- history extension (weekly, 11 Tuesdays) ----------
AP1M = {  # approvals older than one month, all types, per Central mall
 'Rawdah Point Mall': [18, 20, 21, 22, 24, 27, 29, 32, 35, 39, 41], 'Qasr Plaza': [6, 7, 8, 9, 9, 8, 7, 5, 4, 3, 2],
 'Sandstone Galleria': [4, 4, 4, 4, 5, 4, 4, 5, 4, 4, 4], 'Najd Gate Mall': [3, 3, 4, 3, 4, 4, 3, 4, 4, 4, 4], 'Wadi Crescent Centre': [3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3],
 'Falcon Square': [2] * 11, 'Oasis Row': [2] * 11, 'Cedar Park Mall': [2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2], 'Amber Heights': [1] * 11, 'Mirage Commons': [1] * 11}
REN4 = {'Rawdah Point Mall': [4, 4, 4, 4, 4, 5, 6, 7, 7, 8, 9], 'Sandstone Galleria': [8, 8, 8, 8, 8, 7, 7, 6, 6, 6, 6], 'Qasr Plaza': [4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3]}
OTHER4_CENTRAL = 7  # Expansion 1 + HoldOver 2 + Termination 4 over 4 weeks, constant in the window
VAC = {'Mirage Commons': [47, 48, 50, 51, 53, 56, 58], 'Sandstone Galleria': [54, 53, 54, 54, 55, 54, 54], 'Oasis Row': [41, 41, 40, 41, 41, 41, 41], 'Wadi Crescent Centre': [49, 49, 48, 49, 49, 49, 49]}
UD_GULF = {'mm': [3, 4, 3, 11], 'units': [140, 141, 142, 142], 'months': ['Jun', 'Jul', 'Aug', 'Sep']}
UD_MISSING = {'Oasis Row': ['Aug', 'Sep'], 'Amber Heights': ['Sep'], 'Mirage Commons': ['Sep'], 'Lantern Quay': ['Sep'], 'Mangrove Mall': ['Sep'], 'Marina Square West': ['Sep'], 'Hijaz Crossing': ['Sep']}
TEN = [c['v'] for c in D['tenant']['cols']]; TEN_M = [c['m'] for c in D['tenant']['cols']]
TSR_ACTION = next(s['v'] for s in D3['tsr']['status'] if s['label'] == 'Action required')

# ---------- anchors: every series ends on the shared dataset ----------
for m in CENTRAL: assert AP1M[m][-1] == ROWS[m]['apOldTot'], m
for m, s in REN4.items(): assert s[-1] == ROWS[m]['renewal4'], m
for m in CENTRAL:
    if m not in REN4: assert ROWS[m]['renewal4'] == 0
for m, s in VAC.items(): assert s[-1] == ROWS[m]['vacant'], m
g = next(u for u in D['ud'] if u['mall'] == 'Gulf Gate Mall'); assert UD_GULF['mm'][-1] == g['mm'] and UD_GULF['units'][-1] == g['total']
assert sorted(UD_MISSING) == sorted(D['quiet'])
c_tot = [sum(AP1M[m][i] for m in CENTRAL) for i in range(11)]; assert c_tot[-1] == 62
am4_c = [sum(REN4[m][i] for m in REN4) + OTHER4_CENTRAL for i in range(11)]; assert am4_c[-1] == 25

# ---------- facts ----------
class Facts:
    def __init__(self): self.f = {}
    def obs(self, k, v, unit, label, src):
        self.f[k] = {'id': k, 'v': v, 'unit': unit, 'fmt': fmt(v, unit), 'kind': 'observed', 'label': label, 'src': src}; return k
    def cfg(self, k, v, unit, label):
        self.f[k] = {'id': k, 'v': v, 'unit': unit, 'fmt': fmt(v, unit), 'kind': 'config', 'label': label, 'src': 'detector configuration v1'}; return k
    def der(self, k, method, ops, unit, label, formula):
        vals = [self.f[o]['v'] for o in ops]
        v = {'ratio': lambda: vals[0] / vals[1], 'change': lambda: (vals[0] - vals[1]) / vals[1], 'diff': lambda: vals[0] - vals[1], 'count': lambda: len(vals), 'mean': lambda: sum(vals) / len(vals), 'zscore': lambda: (vals[0] - vals[1]) / vals[2], 'pct_below': lambda: (vals[0] - vals[1]) / vals[1]}[method]()
        self.f[k] = {'id': k, 'v': v, 'unit': unit, 'fmt': fmt(v, unit), 'kind': 'derived', 'label': label, 'calc': {'method': method, 'formula': formula, 'operands': [{'fact': o, 'label': self.f[o]['label'], 'value': self.f[o]['v']} for o in ops], 'status': 'verified', 'verifier': 'derive v1 · recomputed by the evidence verifier'}}; return k

def verify(facts):
    bad = []
    for f in facts.values():
        if f['kind'] != 'derived': continue
        c = f['calc']; ops = [o['value'] for o in c['operands']]
        want = {'ratio': lambda: ops[0] / ops[1], 'change': lambda: (ops[0] - ops[1]) / ops[1], 'diff': lambda: ops[0] - ops[1], 'count': lambda: len(ops), 'mean': lambda: sum(ops) / len(ops), 'zscore': lambda: (ops[0] - ops[1]) / ops[2], 'pct_below': lambda: (ops[0] - ops[1]) / ops[1]}[c['method']]()
        if abs(want - f['v']) > 1e-9: bad.append(f['id'])
    return bad

AUD = {'admin': {'label': 'Portfolio admin', 'regions': ['Central', 'Eastern', 'Western']}, 'central': {'label': 'Regional manager · Central', 'regions': ['Central']}, 'tenant': {'label': 'Tenant · lease T-31206', 'leases': ['T-31206']}}
LEASE_MALL = {r[2]: r[1] for r in D['amRecords']['rows']}

def priority(impact, urgency, confidence, kind):
    score = impact * urgency
    if kind == 'positive': band = 'P3'
    elif confidence == 'Low': band = 'Watch'
    else: band = 'P1' if score >= 6 else 'P2' if score >= 3 else 'P3'
    return {'impact': impact, 'urgency': urgency, 'score': score, 'band': band, 'confidence': confidence, 'rule': f'impact {impact} × urgency {urgency} = {score}; P1 ≥ 6, P2 3–5, P3 ≤ 2; Low confidence → Watch; positive findings are P3'}

INS = []; CANDS = []; RUNS = []

def add_ins(**k):
    k.setdefault('related', []); k.setdefault('hyp', []); k.setdefault('lims', []); k.setdefault('notConcluded', []); k.setdefault('cards', [])
    k.setdefault('history', [(k['created'], 'Generated by ' + k['run'], 'system')])
    k['dedupKey'] = '|'.join([k['detector'], k['entity'], k['metricId'], k['audience']])
    k['facts'] = k['F'].f; del k['F']
    bad = verify(k['facts']); assert not bad, (k['id'], bad)
    INS.append(k); return k

def series_facts(F, prefix, labels, vals, unit, src):
    return [F.obs(f'{prefix}{i}', v, unit, labels[i], src) for i, v in enumerate(vals)]

# ===== INS-107 · Rawdah Point · approvals and renewals rising together (cross-KPI cluster) =====
F = Facts(); src_a = 'get_trend · approvals.pending_by_delay v1 · band 1m+ · Rawdah Point Mall · weekly'; src_r = 'get_trend · amendments.pending_by_age_band v1 · Renewal · 4 wk+ · Rawdah Point Mall · weekly'
sa = series_facts(F, 'a', WL[3:], AP1M['Rawdah Point Mall'][3:], 'count', src_a); sr = series_facts(F, 'n', WL[3:], REN4['Rawdah Point Mall'][3:], 'count', src_r)
F.obs('a_now', 41, 'count', 'approvals over a month, 20 Oct', src_a); F.obs('a_8w', AP1M['Rawdah Point Mall'][3], 'count', 'approvals over a month, 1 Sep', src_a)
F.obs('c_now', 62, 'count', 'Central approvals over a month, 20 Oct', 'get_metric · approvals.pending_by_delay v1 · band 1m+ · Central')
F.der('share', 'ratio', ['a_now', 'c_now'], 'rate', 'Rawdah share of Central', 'Rawdah ÷ Central')
F.der('a_chg', 'change', ['a_now', 'a_8w'], 'change', 'change since 1 Sep', '(20 Oct − 1 Sep) ÷ 1 Sep')
F.obs('r_now', 9, 'count', 'renewal amendments 4 wk+, 20 Oct', src_r); F.obs('r_8w', REN4['Rawdah Point Mall'][3], 'count', 'renewal amendments 4 wk+, 1 Sep', src_r)
F.der('r_chg', 'change', ['r_now', 'r_8w'], 'change', 'change since 1 Sep', '(20 Oct − 1 Sep) ÷ 1 Sep')
F.obs('weeks_up', 7, 'weeks', 'consecutive weekly increases (approvals)', src_a)
F.obs('oldest', 171, 'count', 'age in days of the oldest renewal amendment', 'get_underlying_records · amendments · Rawdah Point Mall · Renewal · 4 wk+')
F.cfg('th_share', 0.5, 'rate', 'concentration threshold'); F.cfg('th_min', 20, 'count', 'minimum backlog'); F.cfg('th_weeks', 4, 'weeks', 'minimum consecutive increases')
add_ins(id='INS-107', audience='admin', audiences=['admin', 'central'], scope={'level': 'mall', 'regions': ['Central'], 'malls': ['Rawdah Point Mall'], 'leases': []}, type='Risk', kind='risk', detector='D6 · Cross-KPI co-movement', detectors=['D1 · Concentration', 'D2 · Sustained deterioration', 'D6 · Cross-KPI co-movement'], entity='Rawdah Point Mall', metricId='approvals.pending_by_delay+amendments.pending_by_age_band', metrics=['approvals.pending_by_delay v1 (band 1m+)', 'amendments.pending_by_age_band v1 (Renewal, 4 wk+)'],
  title='Rawdah Point Mall · approval and renewal backlogs are both rising', created='2026-10-20 06:04', run='run_w_2026-10-20', status='new', version=1, prio=priority(3, 3, 'High', 'risk'), F=F,
  why=[('Concentration (D1)', 'Rawdah Point holds [[a_now]] of Central’s [[c_now]] approvals over a month ([[share]]); the rule fires at a share of at least [[th_share]] and at least [[th_min]] approvals.'), ('Sustained deterioration (D2)', 'Approvals over a month rose [[weeks_up]] weeks in a row, from [[a_8w]] on 1 Sep to [[a_now]] ([[a_chg]]); the rule needs [[th_weeks]] consecutive increases.'), ('Cross-KPI co-movement (D6)', 'Renewal amendments over four weeks rose over the same weeks, from [[r_8w]] to [[r_now]] ([[r_chg]]). Two signals on one mall are merged into this single insight.')],
  stmts=[('Observed', 'Approvals over a month at Rawdah Point: [[a_now]] on 20 Oct, [[share]] of Central.'), ('Derived', 'Up [[a_chg]] since 1 Sep; renewal amendments over four weeks up [[r_chg]] over the same period.'), ('Observed', 'The oldest pending renewal amendment is [[oldest]] days old.')],
  hyp=['Both backlogs may share one approval queue at Rawdah Point. The data shows the two backlogs rising together; it does not show why.'],
  lims=['Weekly snapshots start on 11 Aug; no earlier history in the POC.', 'Co-movement over seven weeks is not evidence of a common cause.'],
  notConcluded=['No cause is concluded.', 'No revenue impact is estimated: lease values for the pending items are not in the dataset.'],
  questions=['Why are Rawdah Point’s approval and renewal backlogs rising together?', 'Which approvals at Rawdah Point have waited longest?', 'How does Rawdah Point compare with other Central malls on all four KPIs?'],
  series=[{'label': 'Approvals over a month', 'facts': sa, 'x': WL[3:]}, {'label': 'Renewal amendments 4 wk+', 'facts': sr, 'x': WL[3:]}],
  related=[{'id': 'INS-101', 'rel': 'merged into this insight'}], cards=['approvals', 'amendments'], envelope={'cls': 'Derived', 'scope': 'Central · Rawdah Point Mall', 'coverage': 'Coverage: complete'})
# INS-101 (history: merged)
F = Facts(); F.obs('a_now', 39, 'count', 'approvals over a month, 13 Oct', src_a); F.obs('c_now', 61, 'count', 'Central approvals over a month, 13 Oct', 'get_metric · approvals.pending_by_delay v1'); F.der('share', 'ratio', ['a_now', 'c_now'], 'rate', 'share of Central', 'Rawdah ÷ Central'); F.cfg('th_share', 0.5, 'rate', 'concentration threshold'); F.cfg('th_min', 20, 'count', 'minimum backlog')
add_ins(id='INS-101', audience='admin', audiences=['admin', 'central'], scope={'level': 'mall', 'regions': ['Central'], 'malls': ['Rawdah Point Mall'], 'leases': []}, type='Risk', kind='risk', detector='D1 · Concentration', detectors=['D1 · Concentration'], entity='Rawdah Point Mall', metricId='approvals.pending_by_delay', metrics=['approvals.pending_by_delay v1 (band 1m+)'], title='Rawdah Point Mall holds most of Central’s old approvals', created='2026-10-13 06:03', run='run_w_2026-10-13', status='merged', version=1, prio=priority(3, 2, 'High', 'risk'), F=F,
  why=[('Concentration (D1)', 'Rawdah Point held [[a_now]] of Central’s [[c_now]] approvals over a month ([[share]]); threshold [[th_share]] and at least [[th_min]].')], stmts=[('Observed', 'Approvals over a month at Rawdah Point: [[a_now]] on 13 Oct ([[share]] of Central).')], questions=[], series=[], related=[{'id': 'INS-107', 'rel': 'merged into INS-107 on 20 Oct'}], cards=['approvals'], envelope={'cls': 'Observed', 'scope': 'Central · Rawdah Point Mall', 'coverage': 'Coverage: complete'},
  history=[('2026-10-13 06:03', 'Generated by the weekly evaluation', 'system'), ('2026-10-13 06:05', 'Notified in app (P1)', 'system'), ('2026-10-14 09:20', 'Acknowledged', 'Portfolio admin'), ('2026-10-20 06:04', 'Merged into INS-107 (cross-KPI cluster)', 'system')])

# ===== INS-104 · Mirage Commons vacancy rising (monthly) =====
F = Facts(); src_v = 'get_trend · units.vacant v1 · Mirage Commons · monthly snapshot on the 20th'
sv = series_facts(F, 'v', MONTHS, VAC['Mirage Commons'], 'count', src_v)
F.obs('units', 299, 'count', 'units at Mirage Commons', 'get_metric · units v1 · Mirage Commons')
F.der('rate_now', 'ratio', ['v6', 'units'], 'rate', 'vacancy, 20 Oct', 'vacant ÷ units'); F.der('rate_apr', 'ratio', ['v0', 'units'], 'rate', 'vacancy, 20 Apr', 'vacant ÷ units')
F.der('chg_pts', 'diff', ['rate_now', 'rate_apr'], 'pts', 'change since April', '20 Oct − 20 Apr'); F.obs('months_up', 6, 'weeks', 'consecutive monthly increases', src_v)
F.cfg('th_months', 4, 'weeks', 'minimum consecutive monthly increases'); F.cfg('th_pts', 0.02, 'pts', 'minimum rise')
add_ins(id='INS-104', audience='admin', audiences=['admin', 'central'], scope={'level': 'mall', 'regions': ['Central'], 'malls': ['Mirage Commons'], 'leases': []}, type='Risk', kind='risk', detector='D2 · Sustained deterioration', detectors=['D2 · Sustained deterioration'], entity='Mirage Commons', metricId='units.vacant', metrics=['units.vacant v1'], title='Mirage Commons · vacancy has risen six months in a row', created='2026-09-20 06:10', run='run_m_2026-10-20', status='seen', version=2, prio=priority(2, 2, 'High', 'risk'), F=F,
  why=[('Sustained deterioration (D2)', 'Vacant units rose [[months_up]] months in a row, from [[v0]] in April to [[v6]] in October; the rule needs [[th_months]] consecutive monthly increases and a rise of at least [[th_pts]].')],
  stmts=[('Observed', 'Vacancy at Mirage Commons is [[rate_now]] ([[v6]] of [[units]] units), the highest in Central.'), ('Derived', 'Change since April: [[chg_pts]] (from [[rate_apr]]).')], hyp=['Leases expiring without renewal could explain the rise; the dataset holds no lease-expiry schedule to check this.'], lims=['Monthly snapshots on the 20th; churn within a month is not visible.'], notConcluded=['No cause is concluded.'],
  questions=['Which units at Mirage Commons became vacant since April?', 'How does Mirage Commons’ vacancy compare with other Central malls?'], series=[{'label': 'Vacant units', 'facts': sv, 'x': MONTHS}], cards=['vacancy'], envelope={'cls': 'Derived', 'scope': 'Central · Mirage Commons', 'coverage': 'Coverage: complete'},
  history=[('2026-09-20 06:10', 'Generated by the monthly evaluation (v1, 56 vacant)', 'system'), ('2026-09-20 06:12', 'Included in the daily digest (P2)', 'system'), ('2026-09-22 10:41', 'Seen', 'Portfolio admin'), ('2026-10-20 06:10', 'Updated to v2 without notification: +2 units is below the 10% re-notify threshold', 'system')])

# ===== INS-105 / INS-105C · discrepancy reports missing (event-triggered) =====
def coverage_ins(iid, aud, malls_all, regions):
    F = Facts(); src = 'get_data_coverage · unit_discrepancy.units v1 · month 2026-09'
    missing = [m for m in malls_all if m in UD_MISSING]; rep = len(malls_all) - len(missing)
    F.obs('miss', len(missing), 'count', 'malls without a September report', src); F.obs('all', len(malls_all), 'count', 'malls in scope', src); F.obs('rep', rep, 'count', 'malls that reported', src)
    F.der('cov', 'ratio', ['rep', 'all'], 'rate', 'coverage', 'reported ÷ malls'); F.obs('oasis', 2, 'weeks', 'consecutive months Oasis Row has not reported', src); F.cfg('th_cov', 0.9, 'rate', 'coverage needed for regional comparisons')
    return add_ins(id=iid, audience=aud, audiences=[aud], scope={'level': 'portfolio' if len(regions) == 3 else 'region', 'regions': regions, 'malls': missing, 'leases': []}, type='Data quality', kind='data', detector='D5 · Coverage gap', detectors=['D5 · Coverage gap'], entity=('Portfolio' if len(regions) == 3 else 'Central') + ' · unit discrepancy reports', metricId='unit_discrepancy.units', metrics=['unit_discrepancy.units v1'],
      title=('Seven malls' if len(missing) == 7 else 'Three Central malls') + ' have not filed September unit-discrepancy reports', created='2026-10-19 18:32', run='run_e_2026-10-19', status='new', version=1, prio=priority(2, 2, 'High', 'data'), F=F,
      why=[('Coverage gap (D5)', 'Only [[rep]] of [[all]] malls reported ([[cov]]); regional comparisons need at least [[th_cov]]. Oasis Row has now missed [[oasis]] months in a row, which raises urgency.')],
      stmts=[('Observed', 'Missing: ' + ', '.join(missing) + '.'), ('Derived', 'Coverage for September: [[cov]] ([[rep]] of [[all]] malls).')], hyp=[], lims=['Totals and rates for the region use the observed subset only and are labelled partial.'], notConcluded=['No mismatch count is estimated for the missing malls.'],
      questions=['Which malls have missed discrepancy reports this year?', 'What is the mismatch rate among malls that reported?'], series=[], cards=['discrepancy'], envelope={'cls': 'Observed', 'scope': ('All regions' if len(regions) == 3 else 'Central'), 'coverage': 'Coverage: partial — ' + str(rep) + ' of ' + str(len(malls_all)) + ' malls reported'})
ALL_MALLS = sum((D['mallsByRegion'][r] for r in ['Central', 'Eastern', 'Western']), [])
coverage_ins('INS-105', 'admin', ALL_MALLS, ['Central', 'Eastern', 'Western']); coverage_ins('INS-105C', 'central', CENTRAL, ['Central'])

# ===== INS-106 · Gulf Gate mismatch spike (event-triggered, ambiguous → Watch) =====
F = Facts(); src = 'get_trend · unit_discrepancy.units v1 · Gulf Gate Mall · monthly'
for i, m in enumerate(UD_GULF['months']): F.obs(f'm{i}', UD_GULF['mm'][i], 'count', f'mismatched units, {m}', src); F.obs(f'u{i}', UD_GULF['units'][i], 'count', f'units checked, {m}', src)
for i, m in enumerate(UD_GULF['months']): F.der(f'r{i}', 'ratio', [f'm{i}', f'u{i}'], 'rate', f'mismatch rate, {m}', 'mismatched ÷ checked')
F.der('base', 'mean', ['r0', 'r1', 'r2'], 'rate', 'June–August average rate', 'mean of three months')
F.der('lift', 'change', ['r3', 'base'], 'change', 'September versus the average', '(Sep − average) ÷ average')
F.cfg('th_lift', 1.0, 'change', 'anomaly threshold (relative to the 3-month average)'); F.obs('periods', 1, 'weeks', 'months above the threshold', src)
add_ins(id='INS-106', audience='admin', audiences=['admin'], scope={'level': 'mall', 'regions': ['Eastern'], 'malls': ['Gulf Gate Mall'], 'leases': []}, type='Risk', kind='watch', detector='D4 · Anomaly', detectors=['D4 · Anomaly'], entity='Gulf Gate Mall', metricId='unit_discrepancy.units', metrics=['unit_discrepancy.units v1'],
  title='Gulf Gate Mall · September unit mismatches jumped', created='2026-10-19 18:32', run='run_e_2026-10-19', status='new', version=1, prio=priority(2, 2, 'Low', 'watch'), F=F,
  why=[('Anomaly (D4)', 'September’s mismatch rate [[r3]] is [[lift]] above the June–August average of [[base]]; the rule fires above [[th_lift]]. Only [[periods]] month is above the threshold, so confidence is Low and the insight is a Watch, not an alert.')],
  stmts=[('Observed', '[[m3]] mismatched units of [[u3]] checked in September ([[r3]]).'), ('Derived', 'June to August averaged [[base]].')], hyp=['A one-month jump can come from a change in how the audit was done rather than from the units themselves. The data cannot tell these apart.'], lims=['One month of evidence. The October report will confirm or clear it.'], notConcluded=['Not treated as a trend.'],
  questions=['Which units at Gulf Gate were mismatched in September?', 'Did other Eastern malls change in September?'], series=[{'label': 'Mismatch rate', 'facts': ['r0', 'r1', 'r2', 'r3'], 'x': UD_GULF['months']}], cards=['discrepancy'], envelope={'cls': 'Derived', 'scope': 'Eastern · Gulf Gate Mall', 'coverage': 'Coverage: complete for Gulf Gate'},
  resurface='Resurfaces only if the October report is again at least double the June–August average.')

# ===== INS-103 · Qasr Plaza backlog cleared (positive) =====
F = Facts(); sq = series_facts(F, 'q', WL, AP1M['Qasr Plaza'], 'count', 'get_trend · approvals.pending_by_delay v1 · band 1m+ · Qasr Plaza · weekly')
F.der('q_chg', 'change', ['q10', 'q3'], 'change', 'change since 1 Sep', '(20 Oct − 1 Sep) ÷ 1 Sep'); F.cfg('th_drop', -0.5, 'change', 'improvement threshold'); F.cfg('th_start', 5, 'count', 'minimum starting backlog')
add_ins(id='INS-103', audience='admin', audiences=['admin', 'central'], scope={'level': 'mall', 'regions': ['Central'], 'malls': ['Qasr Plaza'], 'leases': []}, type='Opportunity', kind='positive', detector='D3 · Sustained improvement', detectors=['D3 · Sustained improvement'], entity='Qasr Plaza', metricId='approvals.pending_by_delay', metrics=['approvals.pending_by_delay v1 (band 1m+)'],
  title='Qasr Plaza · old approvals are down to [[q10]] from [[q3]]', created='2026-10-20 06:04', run='run_w_2026-10-20', status='new', version=1, prio=priority(1, 1, 'High', 'positive'), F=F,
  why=[('Sustained improvement (D3)', 'Approvals over a month fell from [[q3]] on 1 Sep to [[q10]] on 20 Oct ([[q_chg]]); the rule needs a drop of at least [[th_drop]] from a starting backlog of at least [[th_start]].')],
  stmts=[('Observed', 'Approvals over a month at Qasr Plaza: [[q10]] on 20 Oct.'), ('Derived', 'Down [[q_chg]] since 1 Sep.')], hyp=['What changed at Qasr Plaza could help Rawdah Point. The data records the improvement, not its cause.'], lims=['Weekly snapshots only.'], notConcluded=['No cause is concluded.'],
  questions=['What changed in Qasr Plaza’s approval process since September?'], series=[{'label': 'Approvals over a month', 'facts': sq, 'x': WL}], related=[{'id': 'INS-090', 'rel': 'earlier risk insight, resolved automatically on 22 Sep'}], cards=['approvals'], envelope={'cls': 'Derived', 'scope': 'Central · Qasr Plaza', 'coverage': 'Coverage: complete'})
# INS-090 (history: auto-resolved)
F = Facts(); F.obs('q_then', 9, 'count', 'approvals over a month, 1 Sep', 'get_trend · approvals.pending_by_delay v1 · Qasr Plaza'); F.obs('q_res', 5, 'count', 'approvals over a month, 22 Sep', 'get_trend · approvals.pending_by_delay v1 · Qasr Plaza'); F.cfg('th_hi', 8, 'count', 'risk threshold')
add_ins(id='INS-090', audience='admin', audiences=['admin', 'central'], scope={'level': 'mall', 'regions': ['Central'], 'malls': ['Qasr Plaza'], 'leases': []}, type='Risk', kind='risk', detector='D2 · Sustained deterioration', detectors=['D2 · Sustained deterioration'], entity='Qasr Plaza', metricId='approvals.pending_by_delay', metrics=['approvals.pending_by_delay v1 (band 1m+)'], title='Qasr Plaza · old approvals rising', created='2026-09-01 06:03', run='run_w_2026-09-01', status='resolved', version=1, prio=priority(2, 1, 'High', 'risk'), F=F,
  why=[('Sustained deterioration (D2)', 'Approvals over a month reached [[q_then]] on 1 Sep after three weekly increases; risk threshold [[th_hi]].')], stmts=[('Observed', 'Resolved automatically: [[q_res]] on 22 Sep, below the threshold for two evaluations.')], questions=[], series=[], cards=[], envelope={'cls': 'Observed', 'scope': 'Central · Qasr Plaza', 'coverage': 'Coverage: complete'},
  history=[('2026-09-01 06:03', 'Generated by the weekly evaluation', 'system'), ('2026-09-02 08:15', 'Acknowledged', 'Portfolio admin'), ('2026-09-22 06:03', 'Resolved automatically: condition cleared for two evaluations', 'system')])

# ===== INS-108 / T-201 · lease T-31206 sales declining (Watch) =====
def tenant_sales_ins(iid, aud):
    F = Facts(); src = 'get_trend · tenant_sales.reported_monthly v1 · lease T-31206'
    s = series_facts(F, 's', TEN_M, TEN, 'SAR', src)
    F.der('chg_jun', 'change', ['s8', 's5'], 'change', 'September versus June', '(Sep − Jun) ÷ Jun')
    F.der('avg', 'mean', [f's{i}' for i in range(8)], 'SAR', 'January–August average', 'mean of eight months')
    F.der('below', 'pct_below', ['s8', 'avg'], 'change', 'September versus the average', '(Sep − average) ÷ average')
    F.obs('down_n', 3, 'weeks', 'consecutive monthly declines', src); F.cfg('th_down', 3, 'weeks', 'minimum consecutive declines'); F.cfg('th_below', -0.1, 'change', 'minimum gap below the average')
    tenant = aud == 'tenant'
    return add_ins(id=iid, audience=aud, audiences=[aud] if tenant else ['admin', 'central'], scope={'level': 'lease', 'regions': ['Central'], 'malls': ['Sandstone Galleria'], 'leases': ['T-31206']}, type='Risk', kind='watch', detector='D7 · Lease trend', detectors=['D7 · Lease trend'], entity='Lease T-31206' + (' (your lease)' if tenant else ' · Lumen Retail Co.'), metricId='tenant_sales.reported_monthly', metrics=['tenant_sales.reported_monthly v1'],
      title=('Your reported sales fell three months in a row' if tenant else 'Lease T-31206 · reported sales fell three months in a row'), created='2026-10-20 06:06', run='run_w_2026-10-20', status='new', version=1, prio=priority(2, 1, 'Low', 'watch'), F=F,
      why=[('Lease trend (D7)', 'Reported sales fell [[down_n]] months in a row to [[s8]] in September, [[below]] against the January–August average of [[avg]]; the rule needs [[th_down]] declines and a gap of at least [[th_below]].')],
      stmts=[('Observed', 'September reported sales: [[s8]]; June: [[s5]].'), ('Derived', 'Change since June: [[chg_jun]].')], hyp=[] if tenant else ['A seasonal summer dip is possible; there is no prior-year data in the POC to check it.'],
      lims=['No prior-year data, so seasonality cannot be ruled out: confidence Low.'] + (['Only your own lease is analysed. Other tenants’ sales are never used in insights you can see.'] if tenant else []), notConcluded=['Not compared with other tenants.' if tenant else 'No cause is concluded.'],
      questions=['How do my monthly sales compare with the same months last year?' if tenant else 'Which other leases at Sandstone Galleria show the same pattern?'], series=[{'label': 'Reported sales', 'facts': s, 'x': TEN_M}], cards=['sales'] if tenant else [], envelope={'cls': 'Derived', 'scope': 'Lease T-31206', 'coverage': 'Coverage: complete (Jan–Sep)'})
tenant_sales_ins('INS-108', 'admin'); tenant_sales_ins('T-201', 'tenant')
# ===== T-202 · tenant service requests need action (event) =====
F = Facts(); F.obs('act', TSR_ACTION, 'count', 'service requests in Action required', 'get_breakdown · tenant_service_requests.by_status v1 · lease T-31206'); F.cfg('th_act', 1, 'count', 'notify from')
add_ins(id='T-202', audience='tenant', audiences=['tenant'], scope={'level': 'lease', 'regions': ['Central'], 'malls': ['Sandstone Galleria'], 'leases': ['T-31206']}, type='Action needed', kind='action', detector='D8 · Tenant action required', detectors=['D8 · Tenant action required'], entity='Lease T-31206 (your lease)', metricId='tenant_service_requests.by_status', metrics=['tenant_service_requests.by_status v1'], title='[[act]] service requests are waiting for your action', created='2026-10-19 11:20', run='run_e_2026-10-19_sr', status='new', version=1, prio=priority(1, 3, 'High', 'action'), F=F,
  why=[('Tenant action required (D8)', '[[act]] of your service requests are in Action required; you are notified from [[th_act]].')], stmts=[('Observed', '[[act]] requests are waiting for information or a response from you.')], hyp=[], lims=['Request details open in Service requests.'], notConcluded=[], questions=['Which of my service requests need my action?'], series=[], cards=['requests'], envelope={'cls': 'Observed', 'scope': 'Lease T-31206', 'coverage': 'Coverage: complete'})

# ---------- evaluation runs and the candidate log (including the decisions not to generate) ----------
corr_v = [ROWS[m]['vacant'] / ROWS[m]['units'] for m in CENTRAL]; corr_a = [ROWS[m]['apOldTot'] for m in CENTRAL]
def pear(x, y):
    mx, my = st.mean(x), st.mean(y); return sum((a - mx) * (b - my) for a, b in zip(x, y)) / ((sum((a - mx) ** 2 for a in x) ** .5) * (sum((b - my) ** 2 for b in y) ** .5))
r_all = pear(corr_v, corr_a); i = CENTRAL.index('Rawdah Point Mall'); r_loo = pear(corr_v[:i] + corr_v[i + 1:], corr_a[:i] + corr_a[i + 1:])
rates = {u['mall']: u['mm'] / u['total'] for u in D['ud']}; med = st.median(rates.values()); mad = st.median([abs(x - med) for x in rates.values()]); z_cedar = (rates['Cedar Park Mall'] - med) / (1.4826 * mad)
def cand(run, det, entity, aud, decision, reason, ins=None, values=None):
    CANDS.append({'run': run, 'detector': det, 'entity': entity, 'audience': aud, 'decision': decision, 'reason': reason, 'insight': ins, 'values': values or {}})
W = 'run_w_2026-10-20'
a_prev, a_now = AP1M['Rawdah Point Mall'][-2], AP1M['Rawdah Point Mall'][-1]
q0, q1 = AP1M['Qasr Plaza'][3], AP1M['Qasr Plaza'][-1]
ten_avg = sum(TEN[:8]) / 8; ten_gap = (TEN[8] - ten_avg) / ten_avg
g_rates = [UD_GULF['mm'][i] / UD_GULF['units'][i] for i in range(4)]; g_base = sum(g_rates[:3]) / 3
v_prev, v_now = VAC['Mirage Commons'][-2], VAC['Mirage Commons'][-1]
rep_all = len(ALL_MALLS) - len(UD_MISSING); rep_c = len(CENTRAL) - sum(1 for m in CENTRAL if m in UD_MISSING)
east = D['mallsByRegion']['Eastern']; rep_e = len(east) - sum(1 for m in east if m in UD_MISSING)
sand_v = ROWS['Sandstone Galleria']['vacant'] / ROWS['Sandstone Galleria']['units']
cand(W, 'D1 · Concentration', 'Rawdah Point Mall', 'admin, central', 'Merged', 'Fired (share ' + pct(a_now / c_tot[-1]) + ' ≥ 50%, ' + str(a_now) + ' ≥ 20). Same entity also fired D2 and D6, so the signals are merged into one cluster insight.', 'INS-107')
cand(W, 'D2 · Sustained deterioration', 'Rawdah Point Mall · approvals', 'admin, central', 'Merged', 'Fired (7 consecutive weekly increases ≥ 4). Merged into INS-107.', 'INS-107')
cand(W, 'D6 · Cross-KPI co-movement', 'Rawdah Point Mall · approvals + renewals', 'admin, central', 'Generated', 'Two KPIs rising since 1 Sep on one mall. One insight per audience; INS-101 (open, acknowledged) is folded in.', 'INS-107')
cand(W, 'D1 · Concentration', 'Rawdah Point Mall', 'admin', 'Suppressed · duplicate', 'Open insight INS-101 covered this signal (' + str(a_prev) + ' → ' + str(a_now) + ', ' + fmt((a_now - a_prev) / a_prev, 'change') + ', below the 10% re-notify threshold). It is merged into INS-107; no separate notification.', 'INS-101')
cand(W, 'D3 · Sustained improvement', 'Qasr Plaza · approvals', 'admin, central', 'Generated', 'Fell from ' + str(q0) + ' to ' + str(q1) + ' (' + fmt((q1 - q0) / q0, 'change') + ') from a starting backlog ≥ 5.', 'INS-103')
cand(W, 'D7 · Lease trend', 'Lease T-31206 · sales', 'admin, central, tenant', 'Generated', 'Three consecutive monthly declines, ' + fmt(ten_gap, 'change') + ' against the Jan–Aug average. No prior-year data: confidence Low → Watch. One instance per audience (INS-108, T-201).', 'INS-108')
cand(W, 'D2 · Sustained deterioration', 'Central · amendments 4 wk+ (all types)', 'admin, central', 'Not generated · not material', 'Rose from ' + str(am4_c[3]) + ' to ' + str(am4_c[-1]) + ' in seven weeks (+' + str(am4_c[-1] - am4_c[3]) + '). Below the minimum absolute change of 5.', None, {'from': am4_c[3], 'to': am4_c[-1]})
cand(W, 'D2 · Sustained deterioration', 'Sandstone Galleria · vacancy', 'admin, central', 'Not generated · no change', 'Vacancy is high (' + pct(sand_v) + ') but flat for seven months. A high but stable level is already visible on the dashboard; no new information.', None)
cand(W, 'D4 · Anomaly', 'Cedar Park Mall · mismatch rate', 'admin, central', 'Not generated · within normal range', 'Highest in Central (' + pct(rates['Cedar Park Mall']) + ') but within the portfolio’s normal range: robust z ' + f'{z_cedar:.1f}' + ' < 3.', None)
cand(W, 'D6 · Cross-KPI co-movement', 'Central malls · vacancy vs old approvals', 'admin, central', 'Not generated · correlation only', 'Across 10 Central malls the correlation is weak (r = ' + f'{r_all:.2f}' + '; ' + f'{r_loo:.2f}' + ' without Rawdah Point), with no shared movement over time and no mechanism in the data. Not reported as a relationship.', None)
cand(W, 'D7 · Lease trend', 'Lease T-31206 vs other tenants', 'tenant', 'Not evaluated · isolation', 'Tenant-audience detectors use only the tenant’s own lease. Benchmarks against other tenants are never computed for a tenant audience.', None)
cand('run_m_2026-10-20', 'D2 · Sustained deterioration', 'Mirage Commons · vacancy', 'admin, central', 'Updated silently', 'Open insight INS-104 (seen). ' + str(v_prev) + ' → ' + str(v_now) + ' vacant (' + fmt((v_now - v_prev) / v_prev, 'change') + ') is below the 10% re-notify threshold: evidence updated to v2, no notification.', 'INS-104')
E = 'run_e_2026-10-19'
cand(E, 'D5 · Coverage gap', 'Portfolio · discrepancy reports', 'admin', 'Generated', str(rep_all) + ' of ' + str(len(ALL_MALLS)) + ' malls reported (' + pct(rep_all / len(ALL_MALLS), 0) + ') < 90%. Oasis Row missed two months in a row.', 'INS-105')
cand(E, 'D5 · Coverage gap', 'Central · discrepancy reports', 'central', 'Generated', str(rep_c) + ' of ' + str(len(CENTRAL)) + ' Central malls reported. Separate instance scoped to Central for the regional manager.', 'INS-105C')
cand(E, 'D4 · Anomaly', 'Gulf Gate Mall · mismatch rate', 'admin', 'Generated · Watch', 'September ' + pct(g_rates[3]) + ' vs a ' + pct(g_base) + ' average (more than double). One period only: confidence Low → Watch.', 'INS-106')
cand(E, 'D2 · Sustained deterioration', 'Eastern · mismatch rate', 'admin', 'Not concluded · coverage', 'Only ' + str(rep_e) + ' of ' + str(len(east)) + ' Eastern malls reported (' + pct(rep_e / len(east), 0) + '), below the 80% needed to evaluate a regional trend. Re-evaluated when reports arrive.', None)
cand('run_e_2026-10-19_sr', 'D8 · Tenant action required', 'Lease T-31206 · service requests', 'tenant', 'Generated', str(TSR_ACTION) + ' requests moved to Action required.', 'T-202')
RUNS = [
 {'id': W, 'trigger': 'Scheduled · weekly, Tuesday 06:00', 'started': '2026-10-20 06:00', 'finished': '2026-10-20 06:06', 'dataset': DSV, 'detectors': ['D1', 'D2', 'D3', 'D6', 'D7'], 'audiences': ['admin', 'central', 'tenant'], 'note': 'Waited for dataset sd-2026.10.20-01 (published 05:41) before evaluating.'},
 {'id': 'run_m_2026-10-20', 'trigger': 'Scheduled · monthly, 20th 06:00 (vacancy snapshot)', 'started': '2026-10-20 06:07', 'finished': '2026-10-20 06:10', 'dataset': DSV, 'detectors': ['D2'], 'audiences': ['admin', 'central'], 'note': ''},
 {'id': E, 'trigger': 'Event · September discrepancy reports loaded', 'started': '2026-10-19 18:30', 'finished': '2026-10-19 18:32', 'dataset': 'sd-2026.10.20-01 (discrepancy partition)', 'detectors': ['D2', 'D4', 'D5'], 'audiences': ['admin', 'central'], 'note': 'Triggered by the load event, not by a schedule.'},
 {'id': 'run_e_2026-10-19_sr', 'trigger': 'Event · tenant service-request status changed', 'started': '2026-10-19 11:20', 'finished': '2026-10-19 11:20', 'dataset': DSV, 'detectors': ['D8'], 'audiences': ['tenant'], 'note': ''}]
for r in RUNS:
    cs = [c for c in CANDS if c['run'] == r['id']]
    r['counts'] = {'evaluated': len(cs), 'generated': sum(1 for c in cs if c['decision'].startswith('Generated')), 'merged': sum(1 for c in cs if c['decision'] == 'Merged'), 'updated': sum(1 for c in cs if c['decision'].startswith('Updated') or c['decision'].startswith('Suppressed')), 'not': sum(1 for c in cs if c['decision'].startswith('Not'))}
def apSum(reg): return sum(sum(D['apReg'][reg][t]) for t in D['apReg'][reg])
def apOld(reg): return sum(D['apReg'][reg][t][-1] for t in D['apReg'][reg])
def amSum(reg): return sum(sum(D['amReg'][reg][t]) for t in D['amReg'][reg])
def am4(reg): return sum(D['amReg'][reg][t][0] for t in D['amReg'][reg])
R3 = ['Central', 'Eastern', 'Western']
pu = D['pu']; vac_all = sum(pu[r][2] for r in R3); units_all = sum(pu[r][0] for r in R3)
ud_c = [u for u in D['ud'] if u['mall'] in CENTRAL]
CARDS = {
 'admin': {'ap': n0(sum(apSum(r) for r in R3)), 'apSub': n0(sum(apOld(r) for r in R3)) + ' older than a month · all regions', 'am': n0(sum(amSum(r) for r in R3)), 'amSub': n0(sum(am4(r) for r in R3)) + ' waiting 4 weeks or more', 'ud': n0(sum(u['mm'] for u in D['ud'])), 'udSub': 'mismatched units · ' + str(len(D['ud'])) + ' of 25 malls reported (observed subset)', 'vac': pct(vac_all / units_all), 'vacSub': n0(vac_all) + ' of ' + n0(units_all) + ' units vacant'},
 'central': {'ap': n0(apSum('Central')), 'apSub': n0(apOld('Central')) + ' older than a month · Central', 'am': n0(amSum('Central')), 'amSub': n0(am4('Central')) + ' waiting 4 weeks or more', 'ud': n0(sum(u['mm'] for u in ud_c)), 'udSub': 'mismatched units · ' + str(len(ud_c)) + ' of 10 Central malls reported', 'vac': pct(pu['Central'][2] / pu['Central'][0]), 'vacSub': n0(pu['Central'][2]) + ' of ' + n0(pu['Central'][0]) + ' units vacant'},
 'tenant': {'tenantSales': sar(sum(TEN)), 'tenantAction': n0(TSR_ACTION)}}
assert sum(apSum(r) for r in R3) == 232 and apOld('Central') == 62
out = {'dsv': DSV, 'cards': CARDS, 'insights': INS, 'cands': CANDS, 'runs': RUNS, 'aud': AUD, 'weeks': WL, 'months': MONTHS, 'stats': {'r_all': r_all, 'r_loo': r_loo, 'z_cedar': z_cedar, 'central_ap1m': c_tot, 'central_am4': am4_c}}
json.dump(out, open(S + '/dx6/insights.json', 'w'), ensure_ascii=False, indent=1)
print('insights', len(INS), 'candidates', len(CANDS), 'runs', len(RUNS), 'r', round(r_all, 2), round(r_loo, 2), 'z', round(z_cedar, 2))

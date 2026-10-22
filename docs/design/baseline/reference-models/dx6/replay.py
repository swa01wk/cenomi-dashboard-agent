"""DX6 v2 — deterministic detector replay over the checkpoint calendar (design-verification oracle, not app code).

Replays detectors-1.1 against sd-2026.10.20-01 at every checkpoint (DR-005 synthetic historical replay) and derives
insights, versions, notifications, the candidate log and runs. Nothing about an insight is hand-authored except the
sentence templates; every number in them is a fact token. Writes dx6/insights.json (prototype input).
"""
import json, sys, hashlib, statistics as st, datetime as dt
S = sys.argv[1]; sys.path.insert(0, S + '/dx6')
import history as H
D, D3 = H.load(S)
RECON = json.load(open(S + '/dx6/recon.json'))
ROWS = {r['mall']: r for r in D['rows']}
REG = D['mallsByRegion']; CENTRAL = REG['Central']; ALL = REG['Central'] + REG['Eastern'] + REG['Western']
REGION_OF = D['regionOf']
DSV = H.DSV
CONFIG = {
 'version': 'detectors-1.1',
 'D1': {'share_min': 0.50, 'value_min': 20, 'parent_min': 30, 'siblings_min': 3, 'screen_share': 0.25},
 'D2': {'window': {'W': 7, 'M': 6}, 'min_increases': 4, 'decrease_allowed': 0, 'min_abs': {'count': 5, 'rate': 0.02}, 'min_rel': 0.10},
 'D3': {'window': 7, 'drop_min': 0.50, 'start_min': 5, 'recent_decreases': 3, 'recent_changes': 4, 'screen_drop': 0.25},
 'D4a': {'ratio_min': 2.0, 'baseline_periods': 3, 'abs_min': 5, 'denominator_min': 50},
 'D4b': {'z_min': 3.0, 'peers_min': 15},
 'D5': {'alert_below': 0.90, 'repeat_months_raise_urgency': 2},
 'coverage': {'min_for_regional_eval': 0.80},
 'D6': {'min_metrics': 2, 'association_screen_abs_r': 0.30, 'association_min_entities': 8, 'associations_generate': False},
 'D7': {'declines': 3, 'below_trailing': 0.10, 'trailing_months': 8, 'prior_year_required_months': 13, 'yoy_max': -0.10},
 'D8': {'items_min': 1, 'urgency_days': [7, 14]},
 'share': {'denominator_min': 10},
 'priority': {'P1': 6, 'P2': 3, 'impact_share': [0.25, 0.50], 'rate_impact': [0.15, 0.20], 'rate_rise_impact': 0.03, 'coverage_impact_below': 0.75},
 'renotify': {'worsen_rel': 0.10, 'measured_against': 'value at the last notified version'},
 'resolve': {'clear_evaluations': 2},
 'watch': {'promote_after_periods': 2}}
CFGV = CONFIG['version']
def n0(v): return f'{v:,.0f}'
def pct(v, d=1): return f'{v * 100:.{d}f}%'
def fmt(v, unit):
    if v is None: return '—'
    return {'count': n0, 'rate': pct, 'pts': lambda x: f'{x * 100:+.1f} pts'.replace('-', '−'), 'SAR': lambda x: 'SAR ' + n0(x),
            'change': lambda x: f'{x * 100:+.1f}%'.replace('-', '−'), 'n': lambda x: f'{x:.0f}', 'days': lambda x: f'{x:.0f}',
            'x': lambda x: f'{x:.1f}×', 'z': lambda x: f'{x:.1f}', 'r': lambda x: f'{x:.2f}'.replace('-', '−')}[unit](v)
class Facts:
    def __init__(self): self.f = {}
    def obs(self, k, v, unit, label, src):
        self.f[k] = {'id': k, 'v': v, 'unit': unit, 'fmt': fmt(v, unit), 'kind': 'observed', 'label': label, 'src': src}; return k
    def cfg(self, k, v, unit, label, key):
        self.f[k] = {'id': k, 'v': v, 'unit': unit, 'fmt': fmt(v, unit), 'kind': 'config', 'label': label, 'src': CFGV + ' · ' + key}; return k
    def der(self, k, method, ops, unit, label, formula):
        vals = [self.f[o]['v'] for o in ops]
        v = CALC[method](vals)
        self.f[k] = {'id': k, 'v': v, 'unit': unit, 'fmt': fmt(v, unit), 'kind': 'derived', 'label': label,
                     'calc': {'method': method, 'formula': formula, 'operands': [{'fact': o, 'label': self.f[o]['label'], 'value': self.f[o]['v']} for o in ops], 'status': 'verified', 'verifier': 'derive v1 · recomputed by the evidence verifier'}}
        return k
CALC = {'ratio': lambda a: a[0] / a[1], 'change': lambda a: (a[0] - a[1]) / a[1], 'diff': lambda a: a[0] - a[1], 'mean': lambda a: sum(a) / len(a), 'times': lambda a: a[0] / a[1]}
def verify(facts):
    return [f['id'] for f in facts.values() if f['kind'] == 'derived' and abs(CALC[f['calc']['method']]([o['value'] for o in f['calc']['operands']]) - f['v']) > 1e-9]

# ---------------------------------------------------------------- detector primitives (pure functions)
def d2(series, cad, unit):
    c = CONFIG['D2']; w = c['window'][cad]
    if len(series) < w: return {'ok': False, 'eval': False, 'why': 'insufficient history'}
    win = series[-w:]; ch = [b - a for a, b in zip(win, win[1:])]
    inc = sum(1 for x in ch if x > 0); dec = sum(1 for x in ch if x < 0); net = win[-1] - win[0]
    rel = net / win[0] if win[0] else None
    ok = inc >= c['min_increases'] and dec <= c['decrease_allowed'] and net >= c['min_abs'][unit] and rel is not None and rel >= c['min_rel']
    fail = []
    if inc < c['min_increases']: fail.append(f'{inc} increases (needs {c["min_increases"]})')
    if dec > c['decrease_allowed']: fail.append(f'{dec} decrease' + ('s' if dec > 1 else ''))
    if net < c['min_abs'][unit]: fail.append('net change ' + (fmt(net, 'pts') if unit == 'rate' else f'{net:+d}') + ' (needs ' + (fmt(c['min_abs'][unit], 'pts') if unit == 'rate' else f'+{c["min_abs"][unit]}') + ')')
    screened = inc >= 2 or abs(net) >= c['min_abs'][unit] / 2
    return {'ok': ok, 'eval': True, 'inc': inc, 'dec': dec, 'net': net, 'rel': rel, 'w0': win[0], 'win': win, 'screened': screened, 'fail': fail, 'changes': len(ch)}
def d3(series):
    c = CONFIG['D3']; w = c['window']
    if len(series) < w: return {'ok': False, 'screened': False}
    win = series[-w:]; mx = max(win); cur = win[-1]; drop = (cur - mx) / mx if mx else 0
    ch = [b - a for a, b in zip(win, win[1:])][-c['recent_changes']:]; decs = sum(1 for x in ch if x < 0)
    ok = mx >= c['start_min'] and cur <= (1 - c['drop_min']) * mx and decs >= c['recent_decreases']
    return {'ok': ok, 'screened': mx >= c['start_min'] and drop <= -c['screen_drop'], 'max': mx, 'cur': cur, 'drop': drop, 'decs': decs}
def share_impact(sh):
    a, b = CONFIG['priority']['impact_share']; return 3 if sh >= b else 2 if sh >= a else 1
def band_of(impact, urgency, confidence, kind):
    score = impact * urgency
    if kind == 'positive': return score, 'P3'
    if confidence == 'Low': return score, 'Watch'
    return score, ('P1' if score >= CONFIG['priority']['P1'] else 'P2' if score >= CONFIG['priority']['P2'] else 'P3')
RULE = 'impact × urgency; P1 ≥ 6, P2 3–5, P3 ≤ 2; Low confidence → Watch; positive findings are P3 (' + CFGV + ')'
BRANK = {'Watch': 0, 'P3': 1, 'P2': 2, 'P1': 3}

# ---------------------------------------------------------------- checkpoint calendar and series lookup
WIDX = {d: i for i, d in enumerate(H.WEEKS)}; MIDX = {d: i for i, d in enumerate(H.MDATES)}
def wser(series, t): return series[:WIDX[t] + 1]
def mser(series, t): return series[:MIDX[t] + 1]
AP = {m: H.AP1M[m] for m in CENTRAL}
CTOT = [sum(AP[m][k] for m in CENTRAL) for k in range(len(H.WEEKS))]
REN = {m: H.REN4.get(m, [0] * len(H.WEEKS)) for m in CENTRAL}
AM4C = RECON['canonical']['central_am4_series']
VACS = {m: H.VAC.get(m, [ROWS[m]['vacant']] * 7) for m in CENTRAL}
UNITS = {m: ROWS[m]['units'] for m in CENTRAL}
def cap(x): return x[:1].upper() + x[1:]
def dlabel(d): return f'{d.day} {d.strftime("%b")}'
def stamp(d, hm='06:00'): return d.isoformat() + ' ' + hm

# ---------------------------------------------------------------- insight store (what the publisher would hold)
INS = {}; CANDS = []; RUNS = []; NOTIFS = []
def cand(run, det, entity, aud, decision, reason, ins=None):
    CANDS.append({'run': run, 'detector': det, 'entity': entity, 'audience': aud, 'decision': decision, 'reason': reason, 'insight': ins})
def upsert(key, iid, run, when, primary, prio, build, meta, notify_policy=True):
    """Publish one insight version. Returns the decision text for the candidate log."""
    cur = INS.get(iid)
    if cur is None:
        ins = dict(meta); ins.update({'id': iid, 'dedupKey': key, 'versions': [], 'status': 'open', 'history': [], 'created': stamp(when[0], when[1]), 'run': run})
        INS[iid] = ins; cur = ins; new = True
    else: new = False
    last_n = next((v for v in reversed(cur['versions']) if v['notified']), None)
    vnum = len(cur['versions']) + 1
    band = prio['band']
    if new: notified, why = band != 'Watch', ('new insight' if band != 'Watch' else 'Watch: inbox only, no badge')
    else:
        prev_band = cur['versions'][-1]['band']
        if BRANK[band] > BRANK[prev_band]: notified, why = True, f'band rose {prev_band} → {band}'
        elif last_n is not None and cur['kind'] != 'positive' and last_n['primary'] and (primary - last_n['primary']) / last_n['primary'] >= CONFIG['renotify']['worsen_rel']:
            notified, why = True, f'worsened {fmt((primary - last_n["primary"]) / last_n["primary"], "change")} since the last notified version ({last_n["primary"]} → {primary})'
        else:
            ch = (primary - last_n['primary']) / last_n['primary'] if last_n and last_n['primary'] else None
            notified, why = False, 'silent update' + (f': {fmt(ch, "change")} since the last notified version ({last_n["primary"]} → {primary}), below 10%' if ch is not None and cur['kind'] != 'positive' else ': positive findings update without notifying' if cur['kind'] == 'positive' else '')
    channel = None
    if notified: channel = 'in-app now' if band == 'P1' else 'daily digest'
    cur['versions'].append({'v': vnum, 'checkpoint': when[0].isoformat(), 'run': run, 'primary': primary, 'band': band, 'score': prio['score'], 'confidence': prio['confidence'], 'notified': notified, 'channel': channel, 'why': why, 'dataset': DSV, 'config': CFGV})
    cur['history'].append([stamp(when[0], when[1]), ('Generated' if new else 'Version ' + str(vnum)) + ' by ' + run + ' · ' + band + (' · notified (' + channel + ')' if notified else ' · ' + why), 'system'])
    cur.update(build()); cur['prio'] = prio; cur['version'] = vnum; cur['last_checkpoint'] = when[0].isoformat()
    if notified:
        for a in cur['audiences']: NOTIFS.append({'key': f'{iid}|v{vnum}|{a}|in-app', 'insight': iid, 'version': vnum, 'recipient': a, 'channel': channel, 'run': run})
    return ('Generated' if new else 'Updated') + (' · notified' if notified and not new else '') + ('' if notified or new else ' silently')
def close(iid, status, run, when, what):
    i = INS[iid]; i['status'] = status; i['history'].append([stamp(when[0], when[1]), what, 'system']); i['closed'] = when[0].isoformat()

# ---------------------------------------------------------------- per-insight builders (sentence templates + facts)
SRC_A = 'get_trend · approvals.pending_by_delay.asof v1 (new) · band 1m+ · weekly'
SRC_R = 'get_trend · amendments.pending_by_age_band.asof v1 (new) · Renewal · 4 wk+ · weekly'
def cfg_d2(F, cad, unit):
    c = CONFIG['D2']; F.cfg('th_inc', c['min_increases'], 'n', 'minimum increases in the window', 'D2.min_increases'); F.cfg('th_changes', c['window'][cad] - 1, 'n', 'changes in the window', 'D2.window.' + cad)
    F.cfg('th_abs', c['min_abs'][unit], 'pts' if unit == 'rate' else 'count', 'minimum rise', 'D2.min_abs.' + unit); F.cfg('th_rel', c['min_rel'], 'rate', 'minimum relative rise', 'D2.min_rel')
def cfg_d1(F):
    c = CONFIG['D1']; F.cfg('th_share', c['share_min'], 'rate', 'concentration threshold', 'D1.share_min'); F.cfg('th_min', c['value_min'], 'count', 'minimum items at the mall', 'D1.value_min'); F.cfg('th_parent', c['parent_min'], 'count', 'minimum regional total', 'D1.parent_min')
def series_facts(F, prefix, xs, vals, unit, src):
    return [F.obs(f'{prefix}{i}', v, unit, xs[i], src) for i, v in enumerate(vals)]
def ins101_builder(t, has_d1):
    def b():
        k = WIDX[t]; F = Facts(); a = AP['Rawdah Point Mall'][k]; c = CTOT[k]; r2 = d2(wser(AP['Rawdah Point Mall'], t), 'W', 'count')
        F.obs('a_now', a, 'count', 'approvals waiting 31+ days, ' + dlabel(t), SRC_A + ' · Rawdah Point Mall'); F.obs('a_w0', r2['w0'], 'count', 'approvals waiting 31+ days, ' + dlabel(H.WEEKS[k - 6]), SRC_A + ' · Rawdah Point Mall')
        F.obs('c_now', c, 'count', 'Central approvals waiting 31+ days, ' + dlabel(t), SRC_A + ' · Central'); F.der('share', 'ratio', ['a_now', 'c_now'], 'rate', 'Rawdah share of Central', 'Rawdah ÷ Central')
        F.der('a_chg', 'change', ['a_now', 'a_w0'], 'change', 'change over the window', '(latest − window start) ÷ window start'); F.obs('a_inc', r2['inc'], 'n', 'weekly increases in the window', SRC_A)
        cfg_d2(F, 'W', 'count');
        why = [('Sustained deterioration (D2)', 'Approvals waiting 31+ days rose in [[a_inc]] of the last [[th_changes]] weekly changes with no decrease, from [[a_w0]] to [[a_now]] ([[a_chg]]); D2 needs at least [[th_inc]] increases, no decrease, a rise of at least [[th_abs]] and [[th_rel]].')]
        if has_d1: cfg_d1(F); why.append(('Concentration (D1)', 'Rawdah Point holds [[a_now]] of Central’s [[c_now]] ([[share]]); D1 fires at a share of at least [[th_share]], at least [[th_min]] items and a regional total of at least [[th_parent]].'))
        return {'facts': F.f, 'why': why, 'detectors': ['D2 · Sustained deterioration'] + (['D1 · Concentration'] if has_d1 else []),
                'title': 'Rawdah Point Mall · approvals waiting 31+ days keep rising',
                'stmts': [('Observed', 'Approvals waiting 31+ days at Rawdah Point: [[a_now]] on ' + dlabel(t) + ', [[share]] of Central’s [[c_now]].'), ('Derived', 'Up [[a_chg]] since ' + dlabel(H.WEEKS[k - 6]) + '.')],
                'series': [{'label': 'Approvals waiting 31+ days', 'facts': series_facts(F, 'a', H.WL[k - 6:k + 1], AP['Rawdah Point Mall'][k - 6:k + 1], 'count', SRC_A), 'x': H.WL[k - 6:k + 1]}]}
    return b
def ins107_builder(t):
    def b():
        k = WIDX[t]; F = Facts(); m = 'Rawdah Point Mall'; ra = d2(wser(AP[m], t), 'W', 'count'); rr = d2(wser(REN[m], t), 'W', 'count'); ap = ROWS[m]['ap']
        F.obs('a_now', AP[m][k], 'count', 'approvals waiting 31+ days, ' + dlabel(t), SRC_A + ' · ' + m); F.obs('a_w0', ra['w0'], 'count', 'approvals waiting 31+ days, ' + dlabel(H.WEEKS[k - 6]), SRC_A + ' · ' + m)
        F.obs('a_p', ap['proposal'][4], 'count', 'proposals waiting 31+ days', 'get_metric · approvals.pending_by_delay v1 (parity) · ' + m); F.obs('a_c', ap['contract'][4], 'count', 'contracts waiting 31+ days', 'get_metric · approvals.pending_by_delay v1 (parity) · ' + m); F.obs('a_l', ap['lease'][4], 'count', 'leases waiting 31+ days', 'get_metric · approvals.pending_by_delay v1 (parity) · ' + m)
        F.obs('a_tot', ROWS[m]['apTot'], 'count', 'pending approvals of all ages', 'get_metric · approvals.pending_by_delay v1 (parity) · ' + m)
        F.obs('c_now', CTOT[k], 'count', 'Central approvals waiting 31+ days, ' + dlabel(t), SRC_A + ' · Central'); F.der('share', 'ratio', ['a_now', 'c_now'], 'rate', 'Rawdah share of Central', 'Rawdah ÷ Central')
        F.der('a_chg', 'change', ['a_now', 'a_w0'], 'change', 'change over the window', '(latest − window start) ÷ window start'); F.obs('a_inc', ra['inc'], 'n', 'weekly increases (approvals)', SRC_A)
        F.obs('r_now', REN[m][k], 'count', 'renewal amendments 4 wk+, ' + dlabel(t), SRC_R + ' · ' + m); F.obs('r_w0', rr['w0'], 'count', 'renewal amendments 4 wk+, ' + dlabel(H.WEEKS[k - 6]), SRC_R + ' · ' + m)
        F.der('r_chg', 'change', ['r_now', 'r_w0'], 'change', 'change over the window', '(latest − window start) ÷ window start'); F.obs('r_inc', rr['inc'], 'n', 'weekly increases (renewals)', SRC_R)
        res = sum(1 for _ in range(RECON['cohorts']['renewals']['Rawdah Point Mall']['resolved_in_window']))
        F.obs('r_res', res, 'count', 'renewals resolved after reaching 4 wk+, 21 Jul–20 Oct', 'get_underlying_records · amendments · Rawdah Point Mall · Renewal · resolved in window')
        F.obs('oldest', 171, 'days', 'age of the oldest pending renewal amendment', 'get_underlying_records · amendments · Rawdah Point Mall · Renewal · 4 wk+')
        cfg_d1(F); cfg_d2(F, 'W', 'count')
        return {'facts': F.f, 'title': 'Rawdah Point Mall · approval and renewal backlogs are both rising', 'detectors': ['D1 · Concentration', 'D2 · Sustained deterioration', 'D6 · Cross-KPI co-movement'],
                'why': [('Concentration (D1)', 'Rawdah Point holds [[a_now]] of Central’s [[c_now]] approvals waiting 31+ days ([[share]]); D1 fires at a share of at least [[th_share]], at least [[th_min]] items and a regional total of at least [[th_parent]].'),
                        ('Sustained deterioration (D2) · approvals', 'Rose in [[a_inc]] of the last [[th_changes]] weekly changes with no decrease, from [[a_w0]] to [[a_now]] ([[a_chg]]); D2 needs at least [[th_inc]] increases, no decrease, a rise of at least [[th_abs]] and [[th_rel]].'),
                        ('Sustained deterioration (D2) · renewals', 'Renewal amendments in the 4 wk+ band rose in [[r_inc]] of the same [[th_changes]] changes with no decrease, from [[r_w0]] to [[r_now]] ([[r_chg]]).'),
                        ('Cross-KPI co-movement (D6)', 'Two metrics on one mall meet D2 at the same checkpoint, so the signals form one cluster insight. INS-101, open since 1 Sep for approvals alone, is merged into it.')],
                'stmts': [('Observed', 'On 20 Oct, [[a_now]] approvals at Rawdah Point have waited 31+ days ([[a_p]] proposals, [[a_c]] contracts, [[a_l]] leases) out of [[a_tot]] pending.'), ('Derived', '[[share]] of Central’s [[c_now]]; up [[a_chg]] since 8 Sep.'),
                          ('Observed', 'Renewal amendments in the 4 wk+ band: [[r_now]], from [[r_w0]] on 8 Sep; the oldest has waited [[oldest]] days.'), ('Observed', '[[r_res]] renewal amendments that had reached the 4 wk+ band were resolved between 21 Jul and 20 Oct, so the queue is moving, but more slowly than items arrive.')],
                'series': [{'label': 'Approvals waiting 31+ days', 'facts': series_facts(F, 'a', H.WL[k - 7:k + 1], AP[m][k - 7:k + 1], 'count', SRC_A), 'x': H.WL[k - 7:k + 1]},
                           {'label': 'Renewal amendments 4 wk+', 'facts': series_facts(F, 'n', H.WL[k - 7:k + 1], REN[m][k - 7:k + 1], 'count', SRC_R), 'x': H.WL[k - 7:k + 1]}]}
    return b
def ins090_builder(t, cleared=None):
    def b():
        k = WIDX[t]; F = Facts(); s = AP['Qasr Plaza']; r2 = d2(wser(s, t), 'W', 'count')
        F.obs('q_then', s[k], 'count', 'approvals waiting 31+ days, ' + dlabel(t), SRC_A + ' · Qasr Plaza'); F.obs('q_w0', r2['w0'], 'count', 'approvals waiting 31+ days, ' + dlabel(H.WEEKS[k - 6]), SRC_A + ' · Qasr Plaza')
        F.der('q_chg', 'change', ['q_then', 'q_w0'], 'change', 'change over the window', '(latest − window start) ÷ window start'); F.obs('q_inc', r2['inc'], 'n', 'weekly increases in the window', SRC_A); cfg_d2(F, 'W', 'count')
        st_ = [('Observed', 'Approvals waiting 31+ days at Qasr Plaza: [[q_then]] on ' + dlabel(t) + '.')]
        if cleared:
            F.obs('q_c1', s[WIDX[cleared[0]]], 'count', 'approvals waiting 31+ days, ' + dlabel(cleared[0]), SRC_A + ' · Qasr Plaza'); F.obs('q_c2', s[WIDX[cleared[1]]], 'count', 'approvals waiting 31+ days, ' + dlabel(cleared[1]), SRC_A + ' · Qasr Plaza')
            F.cfg('th_clear', CONFIG['resolve']['clear_evaluations'], 'n', 'evaluations below the last firing value to resolve', 'resolve.clear_evaluations')
            st_ = [('Observed', 'Resolved automatically on ' + dlabel(cleared[1]) + ': [[q_c1]] on ' + dlabel(cleared[0]) + ' and [[q_c2]] on ' + dlabel(cleared[1]) + ', below the last firing value of [[q_then]] at [[th_clear]] consecutive evaluations.')]
        return {'facts': F.f, 'title': 'Qasr Plaza · approvals waiting 31+ days rising', 'detectors': ['D2 · Sustained deterioration'],
                'why': [('Sustained deterioration (D2)', 'Rose in [[q_inc]] of the last [[th_changes]] weekly changes with no decrease, from [[q_w0]] to [[q_then]] ([[q_chg]]); D2 needs at least [[th_inc]] increases, no decrease, a rise of at least [[th_abs]] and [[th_rel]].')], 'stmts': st_, 'series': []}
    return b
def ins103_builder(t):
    def b():
        k = WIDX[t]; F = Facts(); s = AP['Qasr Plaza']; r3 = d3(wser(s, t))
        F.obs('q_now', r3['cur'], 'count', 'approvals waiting 31+ days, ' + dlabel(t), SRC_A + ' · Qasr Plaza'); F.obs('q_max', r3['max'], 'count', 'maximum in the window', SRC_A + ' · Qasr Plaza')
        F.der('q_chg', 'change', ['q_now', 'q_max'], 'change', 'change from the window maximum', '(latest − maximum) ÷ maximum'); F.obs('q_dec', r3['decs'], 'n', 'decreases in the recent changes', SRC_A)
        F.cfg('th_drop', CONFIG['D3']['drop_min'], 'rate', 'minimum drop', 'D3.drop_min'); F.cfg('th_start', CONFIG['D3']['start_min'], 'count', 'minimum starting backlog', 'D3.start_min'); F.cfg('th_dec', CONFIG['D3']['recent_decreases'], 'n', 'decreases needed in the recent changes', 'D3.recent_decreases'); F.cfg('th_win', CONFIG['D3']['window'], 'n', 'weekly checkpoints in the window', 'D3.window'); F.cfg('th_rc', CONFIG['D3']['recent_changes'], 'n', 'recent changes examined', 'D3.recent_changes')
        return {'facts': F.f, 'title': 'Qasr Plaza · approvals waiting 31+ days are down to [[q_now]] from [[q_max]]', 'detectors': ['D3 · Sustained improvement'],
                'why': [('Sustained improvement (D3)', '[[q_now]] on ' + dlabel(t) + ' against a maximum of [[q_max]] in the last [[th_win]] weekly checkpoints ([[q_chg]]), with [[q_dec]] decreases in the last [[th_rc]] changes; D3 needs a drop of at least [[th_drop]] from a maximum of at least [[th_start]] and [[th_dec]] recent decreases.')],
                'stmts': [('Observed', 'Approvals waiting 31+ days at Qasr Plaza: [[q_now]] on ' + dlabel(t) + '.'), ('Derived', '[[q_chg]] from the maximum of [[q_max]] in the window.')],
                'series': [{'label': 'Approvals waiting 31+ days', 'facts': series_facts(F, 'q', H.WL[k - 7:k + 1], s[k - 7:k + 1], 'count', SRC_A), 'x': H.WL[k - 7:k + 1]}]}
    return b
SRC_V = 'get_trend · units.vacant.asof v1 (new) · monthly on the 20th'
def ins104_builder(t):
    def b():
        j = MIDX[t]; F = Facts(); m = 'Mirage Commons'; s = VACS[m]; r2 = d2([x / UNITS[m] for x in mser(s, t)], 'M', 'rate'); w0 = j - 5
        F.obs('v_now', s[j], 'count', 'vacant units, ' + H.MONTHS[j] + ' 20', SRC_V + ' · ' + m); F.obs('v_w0', s[w0], 'count', 'vacant units, ' + H.MONTHS[w0] + ' 20', SRC_V + ' · ' + m); F.obs('units', UNITS[m], 'count', 'units at Mirage Commons', 'get_metric · units v1 · ' + m)
        F.der('rate_now', 'ratio', ['v_now', 'units'], 'rate', 'vacancy, ' + H.MONTHS[j], 'vacant ÷ units'); F.der('rate_w0', 'ratio', ['v_w0', 'units'], 'rate', 'vacancy, ' + H.MONTHS[w0], 'vacant ÷ units')
        F.der('chg_pts', 'diff', ['rate_now', 'rate_w0'], 'pts', 'change over the window', 'latest − window start'); F.obs('m_inc', r2['inc'], 'n', 'monthly increases in the window', SRC_V); cfg_d2(F, 'M', 'rate')
        return {'facts': F.f, 'title': 'Mirage Commons · vacancy has risen every month since ' + H.MONTHS[w0], 'detectors': ['D2 · Sustained deterioration'],
                'why': [('Sustained deterioration (D2)', 'Vacant units rose in [[m_inc]] of the last [[th_changes]] monthly changes with no decrease, from [[v_w0]] to [[v_now]]: vacancy [[rate_w0]] → [[rate_now]] ([[chg_pts]]); D2 needs at least [[th_inc]] increases, no decrease, a rise of at least [[th_abs]] and [[th_rel]].')],
                'stmts': [('Observed', 'Vacancy at Mirage Commons is [[rate_now]] ([[v_now]] of [[units]] units), the highest in Central.'), ('Derived', 'Change since ' + H.MONTHS[w0] + ': [[chg_pts]].')],
                'series': [{'label': 'Vacant units (20th of the month)', 'facts': series_facts(F, 'v', H.MONTHS[:j + 1], s[:j + 1], 'count', SRC_V), 'x': H.MONTHS[:j + 1]}]}
    return b

# ---------------------------------------------------------------- the replay
def runid(kind, d, suffix=''): return f'run_{kind}_{d.isoformat()}{suffix}'
def runkey(trigger, checkpoint, scope='all'): return hashlib.sha1(f'{trigger}|{checkpoint}|{DSV}|{CFGV}|{scope}'.encode()).hexdigest()[:12]
open101 = {'p': 0}; d6_done = False
for t in H.EVAL_WEEKS:
    rid = runid('w', t); k = WIDX[t]
    # D2/D1 on Rawdah approvals (INS-101 until the D6 cluster forms)
    for m in CENTRAL:
        s = wser(AP[m], t); r2 = d2(s, 'W', 'count'); sh = AP[m][k] / CTOT[k]
        d1ok = sh >= CONFIG['D1']['share_min'] and AP[m][k] >= CONFIG['D1']['value_min'] and CTOT[k] >= CONFIG['D1']['parent_min']
        rr = d2(wser(REN[m], t), 'W', 'count')
        if m == 'Rawdah Point Mall':
            if r2['ok'] and rr['ok']:
                # D6 cluster: two metrics meet D2 on one entity at the same checkpoint
                imp = 3 if d1ok else share_impact(sh); sc, bd = band_of(imp, 3, 'High', 'risk')
                prio = {'impact': imp, 'urgency': 3, 'score': sc, 'band': bd, 'confidence': 'High', 'rule': RULE}
                meta = {'audience': 'admin', 'audiences': ['admin', 'central'], 'scope': {'level': 'mall', 'regions': ['Central'], 'malls': [m], 'leases': []}, 'type': 'Risk', 'kind': 'risk', 'detector': 'D6 · Cross-KPI co-movement', 'entity': m,
                        'metricId': 'approvals.pending_by_delay.asof+amendments.pending_by_age_band.asof', 'metrics': ['approvals.pending_by_delay.asof v1 (band 1m+)', 'amendments.pending_by_age_band.asof v1 (Renewal, 4 wk+)'], 'cards': ['approvals', 'amendments'],
                        'envelope': {'cls': 'Derived', 'scope': 'Central · Rawdah Point Mall', 'coverage': 'Coverage: complete'},
                        'hyp': ['Both backlogs may share one approval queue at Rawdah Point. The data shows them rising together; it does not show why.'],
                        'lims': ['Contracts and leases count from their last change; a change resets their age (V2 rule). Proposals count from creation.', 'Seven weekly checkpoints are evaluated (8 Sep–20 Oct). Rising together over seven weeks is not evidence of a common cause.'],
                        'notConcluded': ['No cause is concluded.', 'No revenue impact is estimated: the POC has no approved revenue-at-risk metric.'],
                        'questions': ['Why are Rawdah Point’s approval and renewal backlogs rising together?', 'Which approvals at Rawdah Point have waited longest?', 'How does Rawdah Point compare with other Central malls on all four KPIs?'],
                        'related': [{'id': 'INS-101', 'rel': 'was merged into this insight on 20 Oct'}]}
                dec = upsert('D6|' + m + '|approvals+renewals|operators', 'INS-107', rid, (t, '06:04'), AP[m][k], prio, ins107_builder(t), meta)
                cand(rid, 'D6 · Cross-KPI co-movement', m + ' · approvals + renewals', 'admin, central', 'Generated', 'Approvals and renewals both meet D2 at this checkpoint (approvals ' + str(r2['inc']) + ' of 6 increases, renewals ' + str(rr['inc']) + ' of 6, no decrease). One cluster insight for the operator audience.', 'INS-107')
                if 'INS-101' in INS and INS['INS-101']['status'] == 'open':
                    last = next(v for v in reversed(INS['INS-101']['versions']) if v['notified'])
                    close('INS-101', 'merged', rid, (t, '06:04'), 'Merged into INS-107 (cross-KPI cluster). No separate notification.')
                    cand(rid, 'D1 · Concentration + D2', m + ' · approvals', 'admin, central', 'Merged', 'Open insight INS-101 covered this signal (' + str(last['primary']) + ' → ' + str(AP[m][k]) + ', ' + fmt((AP[m][k] - last['primary']) / last['primary'], 'change') + ' since its last notified version, below 10%). Merged into INS-107; no separate notification.', 'INS-101')
                d6_done = True
            elif r2['ok'] or (d1ok and 'INS-101' in INS):
                open101['p'] += 1; p = open101['p']
                imp = share_impact(sh); urg = 3 if p >= 3 else 2
                sc, bd = band_of(imp, urg, 'High', 'risk'); prio = {'impact': imp, 'urgency': urg, 'score': sc, 'band': bd, 'confidence': 'High', 'rule': RULE}
                meta = {'audience': 'admin', 'audiences': ['admin', 'central'], 'scope': {'level': 'mall', 'regions': ['Central'], 'malls': [m], 'leases': []}, 'type': 'Risk', 'kind': 'risk', 'detector': 'D2 · Sustained deterioration', 'entity': m,
                        'metricId': 'approvals.pending_by_delay.asof', 'metrics': ['approvals.pending_by_delay.asof v1 (band 1m+)'], 'cards': ['approvals'], 'envelope': {'cls': 'Derived', 'scope': 'Central · Rawdah Point Mall', 'coverage': 'Coverage: complete'},
                        'hyp': [], 'lims': ['Contracts and leases count from their last change; a change resets their age.'], 'notConcluded': ['No cause is concluded.'], 'questions': ['Which approvals at Rawdah Point have waited longest?'], 'related': [{'id': 'INS-107', 'rel': 'is the cross-KPI cluster this insight was merged into on 20 Oct'}]}
                dec = upsert('D2|' + m + '|approvals.1m+|operators', 'INS-101', rid, (t, '06:03'), AP[m][k], prio, ins101_builder(t, d1ok), meta)
                note = ('D2 holds (' + str(r2['inc']) + ' of 6 increases, net +' + str(r2['net']) + ').' if r2['ok'] else 'D2 window not met this week; D1 holds.') + (' D1 holds (share ' + pct(sh) + ').' if d1ok else ' D1 not met (share ' + pct(sh) + ' < 50%).') + ' Persistence ' + str(p) + ' → urgency ' + str(urg) + '; impact ' + str(imp) + ' → ' + bd + '.'
                cand(rid, 'D2 · Sustained deterioration' + (' + D1' if d1ok else ''), m + ' · approvals', 'admin, central', dec, note + ' ' + cap(INS['INS-101']['versions'][-1]['why']) + '.', 'INS-101')
            if rr['eval'] and not rr['ok'] and rr['screened'] and not (r2['ok'] and rr['ok']):
                cand(rid, 'D2 · Sustained deterioration', m + ' · renewals 4 wk+', 'admin, central', 'Not generated · not yet sustained', 'Renewals ' + str(rr['w0']) + ' → ' + str(REN[m][k]) + ': ' + '; '.join(rr['fail']) + '.')
        elif m == 'Qasr Plaza':
            r3 = d3(s)
            if r2['ok']:
                prio_imp = share_impact(sh); sc, bd = band_of(prio_imp, 2, 'High', 'risk'); prio = {'impact': prio_imp, 'urgency': 2, 'score': sc, 'band': bd, 'confidence': 'High', 'rule': RULE}
                meta = {'audience': 'admin', 'audiences': ['admin', 'central'], 'scope': {'level': 'mall', 'regions': ['Central'], 'malls': [m], 'leases': []}, 'type': 'Risk', 'kind': 'risk', 'detector': 'D2 · Sustained deterioration', 'entity': m, 'metricId': 'approvals.pending_by_delay.asof', 'metrics': ['approvals.pending_by_delay.asof v1 (band 1m+)'], 'cards': [],
                        'envelope': {'cls': 'Observed', 'scope': 'Central · Qasr Plaza', 'coverage': 'Coverage: complete'}, 'hyp': [], 'lims': [], 'notConcluded': [], 'questions': [], 'related': [{'id': 'INS-103', 'rel': 'is the later improvement at the same mall'}]}
                dec = upsert('D2|' + m + '|approvals.1m+|operators', 'INS-090', rid, (t, '06:03'), AP[m][k], prio, ins090_builder(t), meta)
                cand(rid, 'D2 · Sustained deterioration', m + ' · approvals', 'admin, central', dec, 'D2 holds (' + str(r2['inc']) + ' of 6 increases, net +' + str(r2['net']) + '). Share of Central ' + pct(sh) + ' → impact ' + str(prio_imp) + ' → ' + bd + '.', 'INS-090')
            elif 'INS-090' in INS and INS['INS-090']['status'] == 'open':
                lastfire = INS['INS-090']['versions'][-1]['primary']; below = [x < lastfire for x in [AP[m][WIDX[d]] for d in H.EVAL_WEEKS if INS['INS-090']['last_checkpoint'] < d.isoformat() <= t.isoformat()]]
                if len(below) >= CONFIG['resolve']['clear_evaluations'] and all(below[-2:]):
                    lc = dt.date.fromisoformat(INS['INS-090']['last_checkpoint']); cl = [d for d in H.EVAL_WEEKS if lc < d <= t][-2:]
                    INS['INS-090'].update(ins090_builder(lc, cl)())
                    close('INS-090', 'resolved', rid, (t, '06:03'), 'Resolved automatically: below the last firing value at two consecutive evaluations (' + ', '.join(str(AP[m][WIDX[d]]) for d in cl) + ')')
                    cand(rid, 'D2 · Sustained deterioration', m + ' · approvals', 'admin, central', 'Resolved automatically', 'D2 no longer holds; ' + str(AP[m][WIDX[cl[0]]]) + ' and ' + str(AP[m][k]) + ' are below the last firing value of ' + str(lastfire) + '.', 'INS-090')
                else:
                    cand(rid, 'D2 · Sustained deterioration', m + ' · approvals', 'admin, central', 'Not generated · clearing', 'D2 no longer holds (' + '; '.join(r2['fail']) + '). INS-090 stays open until two evaluations are below ' + str(lastfire) + '.', 'INS-090')
            if r3['ok']:
                prio = {'impact': 1, 'urgency': 1, 'score': 1, 'band': 'P3', 'confidence': 'High', 'rule': RULE}
                meta = {'audience': 'admin', 'audiences': ['admin', 'central'], 'scope': {'level': 'mall', 'regions': ['Central'], 'malls': [m], 'leases': []}, 'type': 'Opportunity', 'kind': 'positive', 'detector': 'D3 · Sustained improvement', 'entity': m, 'metricId': 'approvals.pending_by_delay.asof', 'metrics': ['approvals.pending_by_delay.asof v1 (band 1m+)'], 'cards': ['approvals'],
                        'envelope': {'cls': 'Derived', 'scope': 'Central · Qasr Plaza', 'coverage': 'Coverage: complete'}, 'hyp': ['What changed at Qasr Plaza could help Rawdah Point. The data records the improvement, not its cause.'], 'lims': ['Weekly checkpoints only; changes within a week are not visible.'], 'notConcluded': ['No cause is concluded.'],
                        'questions': ['What changed in Qasr Plaza’s approval process since September?'], 'related': [{'id': 'INS-090', 'rel': 'is the earlier risk insight at the same mall, resolved automatically on 22 Sep'}]}
                dec = upsert('D3|' + m + '|approvals.1m+|operators', 'INS-103', rid, (t, '06:04'), AP[m][k], prio, ins103_builder(t), meta)
                cand(rid, 'D3 · Sustained improvement', m + ' · approvals', 'admin, central', dec, str(r3['cur']) + ' against a window maximum of ' + str(r3['max']) + ' (' + fmt(r3['drop'], 'change') + '), ' + str(r3['decs']) + ' decreases in the last 4 changes.', 'INS-103')
            elif r3['screened']:
                cand(rid, 'D3 · Sustained improvement', m + ' · approvals', 'admin, central', 'Not generated · not yet sustained', str(r3['cur']) + ' against a window maximum of ' + str(r3['max']) + ' (' + fmt(r3['drop'], 'change') + '); needs −50% and 3 recent decreases.')
        else:
            if r2['screened'] and r2['eval'] and not r2['ok'] and r2['net'] != 0:
                pass  # small mall-level wobble: below screening interest; not logged (see background property GI-12)
            rs = d3(wser(REN[m], t))
            if rs['screened'] and not rs['ok'] and t == H.EVAL_WEEKS[-1]:
                cand(rid, 'D3 · Sustained improvement', m + ' · renewals 4 wk+', 'admin, central', 'Not generated · not material', 'Renewals ' + str(rs['max']) + ' → ' + str(rs['cur']) + ' (' + fmt(rs['drop'], 'change') + '); D3 needs −50%.')
    # Central amendments all types (N2) and the cross-entity association (N5), logged on the as-of week
    if t == H.EVAL_WEEKS[-1]:
        ra = d2(AM4C[:k + 1], 'W', 'count')
        cand(rid, 'D2 · Sustained deterioration', 'Central · amendments 4 wk+ (all types)', 'admin, central', 'Not generated · not material', 'Rose from ' + str(ra['w0']) + ' to ' + str(AM4C[k]) + ' over the window; ' + '; '.join(ra['fail']) + '.')
        v = [ROWS[m]['vacant'] / ROWS[m]['units'] for m in CENTRAL]; a = [ROWS[m]['apOldTot'] for m in CENTRAL]
        def pear(x, y):
            mx, my = st.mean(x), st.mean(y); return sum((p - mx) * (q - my) for p, q in zip(x, y)) / ((sum((p - mx) ** 2 for p in x) ** .5) * (sum((q - my) ** 2 for q in y) ** .5))
        r_all = pear(v, a); i = CENTRAL.index('Rawdah Point Mall'); r_loo = pear(v[:i] + v[i + 1:], a[:i] + a[i + 1:])
        cand(rid, 'D6 · Cross-KPI association (screen)', 'Central malls · vacancy vs approvals 31+ days', 'admin, central', 'Not generated · correlation only', f'Across {len(CENTRAL)} Central malls r = {fmt(r_all, "r")} ({fmt(r_loo, "r")} without Rawdah Point). Cross-entity associations are never published as insights in {CFGV}: no shared movement over time and no mechanism in the data.')
        cand(rid, 'D7 · Lease trend', 'Lease T-31206 vs other tenants', 'tenant', 'Not evaluated · isolation', 'Tenant-audience detectors use only the tenant’s own lease. Benchmarks against other tenants are never computed for a tenant audience.')
    RUNS.append({'id': rid, 'key': runkey('weekly', t), 'trigger': 'Checkpoint · weekly (Tuesday)', 'checkpoint': t.isoformat(), 'started': stamp(t, '06:00'), 'finished': stamp(t, '06:06'), 'dataset': DSV, 'config': CFGV, 'detectors': ['D1', 'D2', 'D3', 'D6'] + (['D7', 'D8'] if t == H.EVAL_WEEKS[-1] else ['D8']), 'audiences': ['admin', 'central', 'tenant'], 'note': 'Synthetic historical replay at checkpoint ' + dlabel(t) + ' (DR-005). Same dataset version and configuration always give the same candidates and versions.'})

# ---- monthly (stock) checkpoints: vacancy D2, tenant sales D7
TS = H.tenant_sales(D)
for t in H.EVAL_MONTHS:
    rid = runid('m', t); j = MIDX[t]
    for m in CENTRAL:
        rates = [x / UNITS[m] for x in mser(VACS[m], t)]; r2 = d2(rates, 'M', 'rate')
        if r2['ok']:
            imp = 2 if (rates[-1] >= CONFIG['priority']['rate_impact'][0] or r2['net'] >= CONFIG['priority']['rate_rise_impact']) else 1
            if rates[-1] >= CONFIG['priority']['rate_impact'][1]: imp = 3
            p = 1 if 'INS-104' not in INS else len(INS['INS-104']['versions']) + 1
            urg = 3 if p >= 3 else 2; sc, bd = band_of(imp, urg, 'High', 'risk'); prio = {'impact': imp, 'urgency': urg, 'score': sc, 'band': bd, 'confidence': 'High', 'rule': RULE}
            meta = {'audience': 'admin', 'audiences': ['admin', 'central'], 'scope': {'level': 'mall', 'regions': ['Central'], 'malls': [m], 'leases': []}, 'type': 'Risk', 'kind': 'risk', 'detector': 'D2 · Sustained deterioration', 'entity': m, 'metricId': 'units.vacant.asof', 'metrics': ['units.vacant.asof v1 (rate)'], 'cards': ['vacancy'],
                    'envelope': {'cls': 'Derived', 'scope': 'Central · ' + m, 'coverage': 'Coverage: complete'},
                    'hyp': ['Leases ending without renewal could explain the rise. Lease end dates are in the dataset, so an investigation can check this; it has not been checked here.'], 'lims': ['Monthly checkpoints on the 20th; movement within a month is not visible.'], 'notConcluded': ['No cause is concluded.'],
                    'questions': ['Which Mirage Commons leases ended since April, and were any renewed?', 'How does Mirage Commons’ vacancy compare with other Central malls?'], 'related': []}
            dec = upsert('D2|' + m + '|units.vacant.rate|operators', 'INS-104', rid, (t, '06:10'), VACS[m][j], prio, ins104_builder(t), meta)
            cand(rid, 'D2 · Sustained deterioration', m + ' · vacancy', 'admin, central', dec, 'D2 holds (' + str(r2['inc']) + ' of 5 increases, ' + fmt(r2['net'], 'pts') + '). ' + cap(INS['INS-104']['versions'][-1]['why']) + '.', 'INS-104')
        elif r2['eval'] and r2['screened'] and t == H.EVAL_MONTHS[-1]:
            cand(rid, 'D2 · Sustained deterioration', m + ' · vacancy', 'admin, central', 'Not generated · no sustained change', f'Vacancy {pct(rates[-1])} is high but shows no sustained change ({r2["inc"]} increases, {r2["dec"]} decrease, {fmt(r2["net"], "pts")} in five months). A stable high level is already visible on the dashboard.')
    # D7 on the tenant's own lease, with the prior-year baseline (the dataset holds 2024–2026)
    lastm = t.month - 2   # last complete month index (Sep → 8)
    y = TS['2026'][:lastm + 1]; ch = [b - a for a, b in zip(y, y[1:])]
    declines = 0
    for x in reversed(ch):
        if x < 0: declines += 1
        else: break
    trailing = sum(y[-9:-1]) / 8; below = (y[-1] - trailing) / trailing; yoy = (y[-1] - TS['2025'][lastm]) / TS['2025'][lastm]
    if declines >= 2:
        if declines < CONFIG['D7']['declines']: dec, why = 'Not generated · not yet sustained', f'{declines} consecutive monthly declines to {fmt(y[-1], "SAR")}; D7 needs 3.'
        elif yoy > CONFIG['D7']['yoy_max']:
            d25 = (TS['2025'][lastm] - TS['2025'][lastm - 3]) / TS['2025'][lastm - 3]; d26 = (y[-1] - y[-4]) / y[-4]
            dec, why = 'Not generated · seasonal pattern', f'Three monthly declines to {fmt(y[-1], "SAR")} ({fmt(below, "change")} against the January–August average), but {fmt(yoy, "change")} against the same month last year; June→September moved {fmt(d25, "change")} in 2025 and {fmt(d26, "change")} in 2026. The prior year shows the same movement, so this is not reported.'
        else: dec, why = 'Generated', ''
        cand(rid, 'D7 · Lease trend', 'Lease T-31206 · reported sales', 'admin, central, tenant', dec, why)
    RUNS.append({'id': rid, 'key': runkey('monthly', t), 'trigger': 'Checkpoint · monthly (20th, stock metrics)', 'checkpoint': t.isoformat(), 'started': stamp(t, '06:07'), 'finished': stamp(t, '06:10'), 'dataset': DSV, 'config': CFGV, 'detectors': ['D2', 'D7'], 'audiences': ['admin', 'central', 'tenant'], 'note': 'Monthly checkpoint anchored on the as-of day of month, so the last value is the snapshot.'})

# ---- event: September discrepancy reports loaded (late-arriving data; ingested 19 Oct 18:30)
E = runid('e', dt.date(2026, 10, 19), '_ud'); te = (dt.date(2026, 10, 19), '18:32')
rates = {u['mall']: u['mm'] / u['total'] for u in D['ud']}; med = st.median(rates.values()); mad = st.median([abs(x - med) for x in rates.values()])
z = {mm: (r - med) / (1.4826 * mad) for mm, r in rates.items()}
g = H.UD_GULF; gr = [g['mm'][i] / g['units'][i] for i in range(4)]; gbase = sum(gr[:3]) / 3; gmm_base = sum(g['mm'][:3]) / 3
d4a = gr[3] >= CONFIG['D4a']['ratio_min'] * gbase and g['mm'][3] - gmm_base >= CONFIG['D4a']['abs_min'] and g['units'][3] >= CONFIG['D4a']['denominator_min']
assert d4a and z['Gulf Gate Mall'] >= 3
F = Facts(); src = 'get_trend · unit_discrepancy.units v1 · Gulf Gate Mall · latest report per month'
for i, mo in enumerate(g['months']): F.obs(f'm{i}', g['mm'][i], 'count', f'mismatched units, {mo}', src); F.obs(f'u{i}', g['units'][i], 'count', f'units checked, {mo}', src)
for i, mo in enumerate(g['months']): F.der(f'r{i}', 'ratio', [f'm{i}', f'u{i}'], 'rate', f'mismatch rate, {mo}', 'mismatched ÷ checked')
F.der('base', 'mean', ['r0', 'r1', 'r2'], 'rate', 'June–August average rate', 'mean of three months'); F.der('mm_base', 'mean', ['m0', 'm1', 'm2'], 'count', 'June–August average mismatched units', 'mean of three months')
F.der('ratio', 'times', ['r3', 'base'], 'x', 'September ÷ the June–August average', 'Sep ÷ average'); F.der('mm_gap', 'diff', ['m3', 'mm_base'], 'count', 'extra mismatched units against the average', 'Sep − average')
F.obs('z', z['Gulf Gate Mall'], 'z', 'robust z across the 18 malls that reported in September', 'get_breakdown · unit_discrepancy.units v1 · September · all reporting malls'); F.obs('peers', len(rates), 'count', 'malls that reported in September', 'get_data_coverage · unit_discrepancy.units v1 · 2026-09')
F.obs('pm', sum(u['mm'] for u in D['ud']), 'count', 'mismatched units, all reporting malls, September', 'get_metric · unit_discrepancy.units v1'); F.obs('pt', sum(u['total'] for u in D['ud']), 'count', 'units checked, all reporting malls, September', 'get_metric · unit_discrepancy.units v1')
F.der('prate', 'ratio', ['pm', 'pt'], 'rate', 'mismatch rate across reporting malls', 'mismatched ÷ checked')
F.cfg('th_ratio', CONFIG['D4a']['ratio_min'], 'x', 'temporal anomaly threshold', 'D4a.ratio_min'); F.cfg('th_abs', CONFIG['D4a']['abs_min'], 'count', 'minimum extra mismatched units', 'D4a.abs_min'); F.cfg('th_z', CONFIG['D4b']['z_min'], 'z', 'cross-sectional threshold', 'D4b.z_min'); F.obs('periods', 1, 'n', 'months above the threshold', src)
F.cfg('th_promote', CONFIG['watch']['promote_after_periods'], 'n', 'consecutive months needed to promote a Watch', 'watch.promote_after_periods')
facts106 = F.f
INS['INS-106'] = {'id': 'INS-106', 'dedupKey': 'D4|Gulf Gate Mall|unit_discrepancy.mismatch_rate|operators', 'audience': 'admin', 'audiences': ['admin'], 'scope': {'level': 'mall', 'regions': ['Eastern'], 'malls': ['Gulf Gate Mall'], 'leases': []}, 'type': 'Risk', 'kind': 'watch', 'detector': 'D4 · Anomaly', 'detectors': ['D4a · Anomaly against own baseline', 'D4b · Anomaly against peers'], 'entity': 'Gulf Gate Mall',
  'metricId': 'unit_discrepancy.units', 'metrics': ['unit_discrepancy.units v1'], 'title': 'Gulf Gate Mall · September unit mismatches jumped', 'created': stamp(*te), 'run': E, 'status': 'open', 'version': 1, 'facts': facts106,
  'prio': {'impact': 2, 'urgency': 2, 'score': 4, 'band': 'Watch', 'confidence': 'Low', 'rule': RULE},
  'why': [('Anomaly against own baseline (D4a)', 'September’s rate [[r3]] is [[ratio]] the June–August average of [[base]] ([[m3]] mismatched units against an average of [[mm_base]]); D4a fires at [[th_ratio]] with at least [[th_abs]] extra mismatched units.'), ('Anomaly against peers (D4b)', 'Across the [[peers]] malls that reported, Gulf Gate’s robust z is [[z]] (threshold [[th_z]]); the rate across those malls is [[prate]].'), ('Confidence', 'Only [[periods]] month is above the thresholds, so confidence is Low and this is a Watch, not an alert. If the October report is again at least [[th_ratio]] the baseline ([[th_promote]] months in a row), it becomes a Risk with Medium confidence and notifies; if not, it clears.')],
  'stmts': [('Observed', '[[m3]] mismatched units of [[u3]] checked in September ([[r3]]).'), ('Derived', 'June to August averaged [[base]]; across reporting malls September is [[prate]].')], 'hyp': ['A one-month jump can come from a change in how the audit was done rather than from the units themselves. The data cannot tell these apart.'],
  'lims': ['One month of evidence. The October report will confirm or clear it.', 'Seven malls had not reported September when this was generated; the peer comparison uses the 18 that did.'], 'notConcluded': ['Not treated as a trend.'],
  'questions': ['Which units at Gulf Gate were mismatched in September?', 'Did other Eastern malls change in September?'], 'series': [{'label': 'Mismatch rate', 'facts': ['r0', 'r1', 'r2', 'r3'], 'x': g['months']}], 'related': [], 'cards': ['discrepancy'],
  'envelope': {'cls': 'Derived', 'scope': 'Eastern · Gulf Gate Mall', 'coverage': 'Coverage: complete for Gulf Gate; peers 18 of 25'}, 'resurface': 'Resurfaces only if the October report is again at least twice the June–August average.',
  'versions': [{'v': 1, 'checkpoint': '2026-10-19', 'run': E, 'primary': g['mm'][3], 'band': 'Watch', 'score': 4, 'confidence': 'Low', 'notified': False, 'channel': None, 'why': 'Watch: inbox only, no badge', 'dataset': DSV, 'config': CFGV}],
  'history': [[stamp(*te), 'Generated by ' + E + ' · Watch · inbox only, no badge', 'system']]}
cand(E, 'D4 · Anomaly (D4a + D4b)', 'Gulf Gate Mall · mismatch rate', 'admin', 'Generated · Watch', f'September {pct(gr[3])} is {gr[3] / gbase:.1f}× the {pct(gbase)} June–August average (+{g["mm"][3] - gmm_base:.1f} units) and robust z {z["Gulf Gate Mall"]:.1f} across 18 reporting malls. One period only: confidence Low → Watch.', 'INS-106')
for reg in ('Central', 'Western'):
    rep = [m for m in REG[reg] if m in rates]; top = max(rep, key=lambda x: rates[x])
    cand(E, 'D4 · Anomaly (D4b)', top + ' · mismatch rate', 'admin' + (', central' if reg == 'Central' else ''), 'Not generated · within normal range', f'Highest in {reg} ({pct(rates[top])}) but within the range of the 18 reporting malls: robust z {z[top]:.1f} < 3. No temporal jump against its own baseline.')
# D5 coverage per audience scope (DXQ-13 A: regional instances generated independently within each authorized region)
def coverage_ins(iid, aud, malls_all, regions):
    F = Facts(); src = 'get_data_coverage · unit_discrepancy.units v1 · month 2026-09 · ingested by 19 Oct 18:30'
    missing = [m for m in malls_all if m in H.UD_MISSING]; rep = len(malls_all) - len(missing)
    F.obs('miss', len(missing), 'count', 'malls without a September report', src); F.obs('all', len(malls_all), 'count', 'malls in scope', src); F.obs('rep', rep, 'count', 'malls that reported', src)
    F.der('cov', 'ratio', ['rep', 'all'], 'rate', 'coverage', 'reported ÷ malls'); F.obs('oasis', 2, 'n', 'consecutive months Oasis Row has not reported', src)
    F.cfg('th_cov', CONFIG['D5']['alert_below'], 'rate', 'coverage below which a gap is raised', 'D5.alert_below'); F.cfg('th_reg', CONFIG['coverage']['min_for_regional_eval'], 'rate', 'coverage needed to evaluate a regional trend', 'coverage.min_for_regional_eval')
    cov = rep / len(malls_all); imp = 2 if cov < CONFIG['priority']['coverage_impact_below'] else 1; urg = 2
    sc, bd = band_of(imp, urg, 'High', 'data')
    INS[iid] = {'id': iid, 'dedupKey': f'D5|{"Portfolio" if len(regions) == 3 else regions[0]}|unit_discrepancy.coverage|{aud}', 'audience': aud, 'audiences': [aud], 'scope': {'level': 'portfolio' if len(regions) == 3 else 'region', 'regions': regions, 'malls': missing, 'leases': []}, 'type': 'Data quality', 'kind': 'data', 'detector': 'D5 · Coverage gap', 'detectors': ['D5 · Coverage gap'],
      'entity': ('Portfolio' if len(regions) == 3 else regions[0]) + ' · unit discrepancy reports', 'metricId': 'unit_discrepancy.units', 'metrics': ['unit_discrepancy.units v1'], 'title': ('Seven malls' if len(missing) == 7 else 'Three Central malls') + ' have not filed September unit-discrepancy reports', 'created': stamp(*te), 'run': E, 'status': 'open', 'version': 1, 'facts': F.f,
      'prio': {'impact': imp, 'urgency': urg, 'score': sc, 'band': bd, 'confidence': 'High', 'rule': RULE},
      'why': [('Coverage gap (D5)', 'Only [[rep]] of [[all]] malls reported ([[cov]]); a gap is raised below [[th_cov]], and regional trends are not evaluated below [[th_reg]]. Oasis Row has now missed [[oasis]] months in a row, which raises urgency.')],
      'stmts': [('Observed', 'Missing: ' + ', '.join(missing) + '.'), ('Derived', 'Coverage for September: [[cov]] ([[rep]] of [[all]] malls).')], 'hyp': [], 'lims': ['Totals and rates use the observed subset only and are labelled partial.', 'Reports arrived on 19 Oct; checkpoints before that date did not see them.'], 'notConcluded': ['No mismatch count is estimated for the missing malls.'],
      'questions': ['Which malls have missed discrepancy reports this year?', 'What is the mismatch rate among malls that reported?'], 'series': [], 'related': [], 'cards': ['discrepancy'],
      'envelope': {'cls': 'Observed', 'scope': ('All regions' if len(regions) == 3 else regions[0]), 'coverage': 'Coverage: partial — ' + str(rep) + ' of ' + str(len(malls_all)) + ' malls reported'},
      'versions': [{'v': 1, 'checkpoint': '2026-10-19', 'run': E, 'primary': len(missing), 'band': bd, 'score': sc, 'confidence': 'High', 'notified': True, 'channel': 'daily digest', 'why': 'new insight', 'dataset': DSV, 'config': CFGV}],
      'history': [[stamp(*te), 'Generated by ' + E + ' · ' + bd + ' · notified (daily digest)', 'system']]}
    NOTIFS.append({'key': f'{iid}|v1|{aud}|in-app', 'insight': iid, 'version': 1, 'recipient': aud, 'channel': 'daily digest', 'run': E})
    return rep, len(malls_all)
rp, ap_ = coverage_ins('INS-105', 'admin', ALL, ['Central', 'Eastern', 'Western']); rc, ac = coverage_ins('INS-105C', 'central', CENTRAL, ['Central'])
cand(E, 'D5 · Coverage gap', 'Portfolio · discrepancy reports', 'admin', 'Generated', f'{rp} of {ap_} malls reported ({pct(rp / ap_, 0)}) < 90%. Oasis Row missed two months in a row.', 'INS-105')
cand(E, 'D5 · Coverage gap', 'Central · discrepancy reports', 'central', 'Generated', f'{rc} of {ac} Central malls reported ({pct(rc / ac, 0)}). Separate instance computed within Central for the regional manager (DXQ-13 A).', 'INS-105C')
for reg in ('Central', 'Eastern', 'Western'):
    rep = sum(1 for m in REG[reg] if m in rates)
    cand(E, 'D2 · Sustained deterioration', reg + ' · mismatch rate', 'admin' + (', central' if reg == 'Central' else ''), 'Not concluded · coverage', f'Only {rep} of {len(REG[reg])} {reg} malls reported ({pct(rep / len(REG[reg]), 0)}), below the 80% needed to evaluate a regional trend. Re-evaluated when reports arrive.')
RUNS.append({'id': E, 'key': runkey('event:ud_load:batch-2026-09', '2026-10-19'), 'trigger': 'Event · September discrepancy reports loaded (batch ud-2026-09, 18 malls)', 'checkpoint': '2026-10-19', 'started': '2026-10-19 18:30', 'finished': '2026-10-19 18:32', 'dataset': DSV + ' (discrepancy partition)', 'config': CFGV, 'detectors': ['D2', 'D4', 'D5'], 'audiences': ['admin', 'central'], 'note': 'Late-arriving data: rows ingested 19 Oct 18:30 are visible from this run on, never to earlier checkpoints.', 'event': 'ud-2026-09'})

# ---- D8 tenant action required (events + weekly re-evaluation), lease T-31206 only
def ins202(t, items):
    F = Facts(); src = 'get_breakdown · tenant_action_items.open v1 · lease T-31206'
    oldest = max((t - a['since']).days for a in items)
    F.obs('n', len(items), 'count', 'items waiting for you', src); F.obs('oldest', oldest, 'days', 'days the oldest item has waited', src)
    F.cfg('th_u2', CONFIG['D8']['urgency_days'][0], 'days', 'urgency rises from', 'D8.urgency_days[0]'); F.cfg('th_u3', CONFIG['D8']['urgency_days'][1], 'days', 'highest urgency from', 'D8.urgency_days[1]')
    urg = 3 if oldest >= 14 else 2 if oldest >= 7 else 1; sc, bd = band_of(2, urg, 'High', 'action')
    return F.f, {'impact': 2, 'urgency': urg, 'score': sc, 'band': bd, 'confidence': 'High', 'rule': RULE}, [('Observed', a['what'] + ' — ' + a['kind'].lower() + ' since ' + dlabel(a['since']) + '.') for a in items]
T202_RUNS = [(dt.date(2026, 10, 12), '10:15', 'e', '_t1', 'Event · document requested (lease T-31206)', H.TENANT_ACTIONS[:1]), (dt.date(2026, 10, 13), '06:05', 'w', '', None, H.TENANT_ACTIONS[:1]),
             (dt.date(2026, 10, 17), '14:05', 'e', '_t2', 'Event · fit-out drawing returned for re-upload (lease T-31206)', H.TENANT_ACTIONS), (dt.date(2026, 10, 20), '06:05', 'w', '', None, H.TENANT_ACTIONS)]
for (d, hm, kind, suf, trig, items) in T202_RUNS:
    rid = runid(kind, d, suf); facts, prio, stm = ins202(d, items)
    meta = {'audience': 'tenant', 'audiences': ['tenant'], 'scope': {'level': 'lease', 'regions': ['Central'], 'malls': ['Sandstone Galleria'], 'leases': ['T-31206']}, 'type': 'Action needed', 'kind': 'action', 'detector': 'D8 · Tenant action required', 'entity': 'Lease T-31206 (your lease)', 'metricId': 'tenant_action_items.open', 'metrics': ['tenant_action_items.open v1 (documents to upload, requests in Action required, sales re-uploads)'], 'cards': ['documents'],
            'envelope': {'cls': 'Observed', 'scope': 'Lease T-31206', 'coverage': 'Coverage: complete'}, 'hyp': [], 'lims': ['Only your lease T-31206 is used. Other leases of your company are not included.'], 'notConcluded': [], 'questions': ['Which documents do I still need to upload, and why was the shopfront drawing returned?'], 'related': []}
    prev = INS.get('T-202', {}).get('versions', [])
    if prev and prev[-1]['primary'] == len(items) and prev[-1]['band'] == prio['band']:
        cand(rid, 'D8 · Tenant action required', 'Lease T-31206 · action items', 'tenant', 'No change', 'Same ' + str(len(items)) + ' item(s); urgency unchanged. No new version.', 'T-202'); continue
    dec = upsert('D8|T-31206|tenant_action_items|tenant', 'T-202', rid, (d, hm), len(items), prio, lambda f=facts, s_=stm, n_=len(items): {'facts': f, 'title': ('[[n]] fit-out drawings are waiting for your upload' if n_ > 1 else '[[n]] fit-out drawing is waiting for your upload'), 'detectors': ['D8 · Tenant action required'],
        'why': [('Tenant action required (D8)', '[[n]] item(s) for lease T-31206 are waiting for you; the oldest has waited [[oldest]] days. Urgency rises at [[th_u2]] and [[th_u3]] days.')], 'stmts': s_, 'series': []}, meta)
    cand(rid, 'D8 · Tenant action required', 'Lease T-31206 · action items', 'tenant', dec, str(len(items)) + ' lease-scoped item(s); oldest ' + str(max((d - a['since']).days for a in items)) + ' days → ' + prio['band'] + '. ' + cap(INS['T-202']['versions'][-1]['why']) + '. Requests in Action required for this lease: 0 (the company-wide count of 2 is never used for a lease-level audience).', 'T-202')
    if kind == 'e': RUNS.append({'id': rid, 'key': runkey('event:tenant_action:' + suf, d.isoformat(), 'lease:T-31206'), 'trigger': trig, 'checkpoint': d.isoformat(), 'started': stamp(d, hm), 'finished': stamp(d, hm), 'dataset': DSV, 'config': CFGV, 'detectors': ['D8'], 'audiences': ['tenant'], 'note': 'Status-change event scoped to one lease.', 'event': 'tenant-action' + suf})

# ---------------------------------------------------------------- post-processing for the prototype
for r in RUNS:
    cs = [c for c in CANDS if c['run'] == r['id']]
    r['counts'] = {'evaluated': len(cs), 'generated': sum(1 for c in cs if c['decision'].startswith('Generated')), 'merged': sum(1 for c in cs if c['decision'] == 'Merged'),
                   'updated': sum(1 for c in cs if c['decision'].startswith('Updated') or c['decision'].startswith('Suppressed') or c['decision'].startswith('Resolved') or c['decision'] == 'No change'), 'not': sum(1 for c in cs if c['decision'].startswith('Not'))}
RUNS.sort(key=lambda r: r['started'], reverse=True)
for i in INS.values():
    i.setdefault('series', []); i.setdefault('related', []); i.setdefault('resurface', None)
    bad = verify(i['facts']); assert not bad, (i['id'], bad)
    toks = set()
    import re
    for t_ in [i['title']] + [w[1] for w in i['why']] + [s[1] for s in i['stmts']]: toks |= set(re.findall(r'\[\[([a-zA-Z0-9_]+)\]\]', t_))
    assert toks <= set(i['facts']), (i['id'], toks - set(i['facts']))
    i['why'] = [list(w) for w in i['why']]; i['stmts'] = [list(s) for s in i['stmts']]
    if i['status'] == 'open': i['status'] = 'seen' if i['id'] in ('INS-104', 'INS-090') else 'new'
# Personal state seeded for the prototype's "now" (20 Oct 08:30)
PERSONAL = {'admin': {'INS-101': ['acknowledged', '2026-10-14 09:20'], 'INS-090': ['acknowledged', '2026-09-02 08:15'], 'INS-104': ['seen', '2026-09-22 10:41']}, 'central': {'INS-104': ['seen', '2026-09-23 08:02']}, 'tenant': {}}
for who, d_ in PERSONAL.items():
    for iid, (stt, when) in d_.items(): INS[iid]['history'].append([when, stt.capitalize(), {'admin': 'Portfolio admin', 'central': 'Regional manager · Central'}[who]])
for i in INS.values(): i['history'].sort(key=lambda h: h[0])
ORDER = ['INS-107', 'T-202', 'INS-105', 'INS-105C', 'INS-104', 'INS-106', 'INS-103', 'INS-101', 'INS-090']
INSL = [INS[k] for k in ORDER]
# dashboard cards per role
def apSum(reg): return sum(sum(D['apReg'][reg][t]) for t in D['apReg'][reg])
def apOld(reg): return sum(D['apReg'][reg][t][-1] for t in D['apReg'][reg])
def amSum(reg): return sum(sum(D['amReg'][reg][t]) for t in D['amReg'][reg])
def am4(reg): return sum(D['amReg'][reg][t][0] for t in D['amReg'][reg])
R3 = ['Central', 'Eastern', 'Western']; pu = D['pu']; ud_c = [u for u in D['ud'] if u['mall'] in CENTRAL]
CARDS = {'admin': {'ap': n0(sum(apSum(r) for r in R3)), 'apSub': n0(sum(apOld(r) for r in R3)) + ' waiting 31+ days · all regions', 'am': n0(sum(amSum(r) for r in R3)), 'amSub': n0(sum(am4(r) for r in R3)) + ' waiting 4 weeks or more', 'ud': n0(sum(u['mm'] for u in D['ud'])), 'udSub': 'mismatched units · ' + str(len(D['ud'])) + ' of 25 malls reported (observed subset)', 'vac': pct(sum(pu[r][2] for r in R3) / sum(pu[r][0] for r in R3)), 'vacSub': n0(sum(pu[r][2] for r in R3)) + ' of ' + n0(sum(pu[r][0] for r in R3)) + ' units vacant'},
         'central': {'ap': n0(apSum('Central')), 'apSub': n0(apOld('Central')) + ' waiting 31+ days · Central', 'am': n0(amSum('Central')), 'amSub': n0(am4('Central')) + ' waiting 4 weeks or more', 'ud': n0(sum(u['mm'] for u in ud_c)), 'udSub': 'mismatched units · ' + str(len(ud_c)) + ' of 10 Central malls reported', 'vac': pct(pu['Central'][2] / pu['Central'][0]), 'vacSub': n0(pu['Central'][2]) + ' of ' + n0(pu['Central'][0]) + ' units vacant'},
         'tenant': {'tenantSales': 'SAR ' + n0(sum(TS['2026'])), 'tenantDocs': n0(len(H.TENANT_ACTIONS))}}
assert sum(apSum(r) for r in R3) == 232 and apOld('Central') == 62
# Facts for the K10 summary example: a portfolio-wide statement that is outside INS-107's scope and must be blocked
TF = Facts(); TF.obs('p_all', sum(apOld(r) for r in R3), 'count', 'approvals waiting 31+ days, all regions, 20 Oct', 'get_metric · approvals.pending_by_delay v1 (parity) · all regions')
TF.obs('a_now', AP['Rawdah Point Mall'][-1], 'count', 'approvals waiting 31+ days, Rawdah Point, 20 Oct', SRC_A + ' · Rawdah Point Mall'); TF.der('p_share', 'ratio', ['a_now', 'p_all'], 'rate', 'Rawdah share of all regions', 'Rawdah ÷ all regions')
THREAD_EXTRA = {'INS-107': [{'k': 'p0', 'kind': 'Observed', 'text': 'Across all regions [[p_all]] approvals have waited 31+ days; Rawdah Point holds [[p_share]] of them.', 'scope': {'level': 'portfolio', 'regions': R3, 'malls': [], 'leases': []}, 'scopeLbl': 'All regions', 'facts': TF.f}]}
assert not verify(TF.f)
blob = json.dumps({'insights': INSL, 'cands': CANDS, 'runs': RUNS}, sort_keys=True, default=str)
out = {'dsv': DSV, 'config': CONFIG, 'cards': CARDS, 'insights': INSL, 'cands': CANDS, 'runs': RUNS, 'notifications': NOTIFS, 'personal': PERSONAL, 'weeks': H.WL, 'months': H.MONTHS,
       'replay_hash': hashlib.sha256(blob.encode()).hexdigest()[:16], 'tenantSales': TS, 'threadExtra': THREAD_EXTRA}
json.dump(out, open(S + '/dx6/insights.json', 'w'), ensure_ascii=False, indent=1, default=str)
print('insights', len(INSL), 'candidates', len(CANDS), 'runs', len(RUNS), 'notifications', len(NOTIFS), 'hash', out['replay_hash'])
for i in INSL: print(' ', i['id'], i['status'], i['prio']['band'], 'v' + str(i['version']), i['created'], '|', ' ; '.join(v['checkpoint'][5:] + ':' + v['band'] + (':N' if v['notified'] else '') for v in i['versions']))

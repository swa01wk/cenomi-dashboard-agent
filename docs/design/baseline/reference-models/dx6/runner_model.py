"""DX6 refinement 3 — executable model of the evaluation runner protocol (design verification, not app code).

Models the lightweight local-POC protocol: run identity, trigger deduplication, single-worker queue with claim
leases, staged candidates, one-transaction publication with optimistic version checks, an idempotent notification
outbox, restart after crashes, bitemporal reads for late data, dataset-version corrections and deterministic replay.
The evaluation function is the replay oracle (dx6/insights.json) plus small toy detectors for the correction cases.
Writes dx6/runner_results.json.
"""
import json, sys, copy, hashlib, random, subprocess, datetime as dt
S = sys.argv[1]
ORACLE = json.load(open(S + '/dx6/insights.json'))
CFG = ORACLE['config']['version']; DSV = ORACLE['dsv']

def h(obj): return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]
class Crash(Exception): pass
class Conflict(Exception): pass

class Store:
    """Tables with unique keys. tx() gives all-or-nothing commits (copy-on-commit)."""
    def __init__(self):
        self.t = {'runs': {}, 'events': {}, 'staging': {}, 'candidates': {}, 'insights': {}, 'versions': {}, 'outbox': {}, 'delivered': {}}
    def tx(self): return Tx(self)
class Tx:
    def __init__(self, s): self.s = s; self.w = copy.deepcopy(s.t)
    def insert(self, table, key, row):
        if key in self.w[table]: raise KeyError((table, key))
        self.w[table][key] = row
    def commit(self): self.s.t = self.w

def run_key(trigger, checkpoint, dataset, config, partition='all'):
    return h([trigger, checkpoint, dataset, config, partition])

# ---------------------------------------------------------------- evaluation function (deterministic, read-only)
BY_RUN = {}
for c in ORACLE['cands']: BY_RUN.setdefault(c['run'], {'cands': [], 'versions': []})['cands'].append(c)
for i in ORACLE['insights']:
    for v in i['versions']: BY_RUN.setdefault(v['run'], {'cands': [], 'versions': []})['versions'].append({'insight': i['id'], 'dedup': i['dedupKey'], 'v': v, 'audiences': i['audiences']})
RUN_META = {r['id']: r for r in ORACLE['runs']}
def evaluate(run_id, dataset):
    """Pure function of (run, dataset version, config): returns candidates and version proposals."""
    out = copy.deepcopy(BY_RUN.get(run_id, {'cands': [], 'versions': []}))
    if dataset != DSV:   # toy correction: version -02 corrects Mirage Commons' October vacancy 58 → 57
        for p in out['versions']:
            if p['insight'] == 'INS-104' and p['v']['checkpoint'] == '2026-10-20': p['v'] = dict(p['v'], primary=57, dataset=dataset, why='data corrected (58 → 57)')
    return out

# ---------------------------------------------------------------- runner
class Runner:
    def __init__(self, store, worker='w1'): self.s = store; self.worker = worker; self.log = []
    def trigger(self, kind, ref, checkpoint, dataset=DSV, event_id=None, partition='all'):
        """Returns 'queued', 'duplicate' (already completed), or 'coalesced' (already queued or running)."""
        if event_id:
            if event_id in self.s.t['events']: self.log.append(('trigger', event_id, 'duplicate event')); return 'duplicate'
            tx = self.s.tx(); tx.insert('events', event_id, {'kind': kind, 'checkpoint': checkpoint}); tx.commit()
        key = run_key(kind, checkpoint, dataset, CFG, partition)
        r = self.s.t['runs'].get(key)
        if r:
            st = 'duplicate' if r['status'] == 'completed' else 'coalesced'; self.log.append(('trigger', key, st)); return st
        tx = self.s.tx(); tx.insert('runs', key, {'key': key, 'ref': ref, 'kind': kind, 'checkpoint': checkpoint, 'dataset': dataset, 'config': CFG, 'status': 'queued', 'attempt': 0, 'lease': None}); tx.commit()
        return 'queued'
    def claim(self, key, now, lease_s=300):
        r = self.s.t['runs'][key]
        if r['status'] == 'completed': return False
        if r['status'] == 'running' and r['lease'] and r['lease'][1] > now and r['lease'][0] != self.worker: return False
        tx = self.s.tx(); w = tx.w['runs'][key]; w['status'] = 'running'; w['attempt'] += 1; w['lease'] = (self.worker, now + lease_s); tx.commit(); return True
    def execute(self, key, now=0, crash=None):
        if not self.claim(key, now): return 'skipped'
        r = self.s.t['runs'][key]
        # stage (a restart first discards any staging left by an earlier attempt)
        tx = self.s.tx(); tx.w['staging'] = {k: v for k, v in tx.w['staging'].items() if v['run'] != key}; tx.commit()
        res = evaluate(r['ref'], r['dataset'])
        tx = self.s.tx()
        for n, c in enumerate(res['cands']): tx.insert('staging', (key, n), dict(c, run=key, attempt=r['attempt']))
        tx.commit()
        if crash == 'after_staging': raise Crash('after staging')
        # publish: one transaction; optimistic check on each insight's current version
        tx = self.s.tx()
        for n, c in enumerate(res['cands']): tx.insert('candidates', (key, n), dict(c, run=key))
        for p in res['versions']:
            iid = p['insight']; cur = tx.w['insights'].get(iid)
            expected = (cur['version'] if cur else 0)
            if (iid, key) in [(x[0], x[2]) for x in tx.w['versions'].values()]: continue     # already published by this run
            if cur and cur['checkpoint'] > p['v']['checkpoint']: continue                     # never overwrite a later checkpoint
            nv = expected + 1
            tx.w['insights'][iid] = {'version': nv, 'checkpoint': p['v']['checkpoint'], 'dedup': p['dedup'], 'dataset': p['v']['dataset']}
            tx.insert('versions', (iid, nv), (iid, nv, key, p['v']['primary'], p['v']['band'], p['v']['dataset'], p['v']['why']))
            if p['v']['notified']:
                for a in p['audiences']:
                    nk = f'{iid}|v{nv}|{a}|in-app'
                    if nk not in tx.w['outbox']: tx.insert('outbox', nk, {'insight': iid, 'version': nv, 'recipient': a, 'channel': p['v']['channel']})
        if crash == 'inside_publish': raise Crash('inside publish (transaction not committed)')
        tx.w['runs'][key]['status'] = 'completed'; tx.w['runs'][key]['outcome'] = h(res); tx.w['staging'] = {k: v for k, v in tx.w['staging'].items() if v['run'] != key}
        tx.commit()
        if crash == 'after_commit': raise Crash('after commit, before acknowledgement')
        return 'completed'
    def deliver(self, crash_after=None):
        n = 0
        for k, row in sorted(self.s.t['outbox'].items()):
            if k in self.s.t['delivered']: continue
            tx = self.s.tx(); tx.insert('delivered', k, row); tx.commit(); n += 1
            if crash_after is not None and n == crash_after: raise Crash('delivery interrupted')
        return n
    def drain(self, now=0):
        q = sorted((r for r in self.s.t['runs'].values() if r['status'] != 'completed'), key=lambda r: (r['checkpoint'], r['kind'], r['key']))
        return [self.execute(r['key'], now) for r in q]

CAL = sorted(ORACLE['runs'], key=lambda r: (r['checkpoint'], r['started']))
def kind_of(r): return 'weekly' if r['id'].startswith('run_w') else 'monthly' if r['id'].startswith('run_m') else 'event'
def enqueue_all(rn, order=None, dataset=DSV):
    for r in (order or CAL): rn.trigger(kind_of(r), r['id'], r['checkpoint'], dataset, event_id=r.get('event'))
def snapshot(s):
    return h({'versions': sorted(s.t['versions'].values()), 'candidates': sorted((k[1], json.dumps(v, sort_keys=True)) for k, v in s.t['candidates'].items()), 'outbox': sorted(s.t['outbox'])})
def reference():
    s = Store(); rn = Runner(s); enqueue_all(rn); rn.drain(); rn.deliver(); return s
REF = reference(); REFH = snapshot(REF)
T = []; CASES = {}
def test(tid, name, ok, detail): T.append({'id': tid, 'name': name, 'ok': bool(ok), 'detail': detail})

# R1 duplicate event delivery
s = Store(); rn = Runner(s); enqueue_all(rn); rn.drain(); rn.deliver(); before = (len(s.t['versions']), len(s.t['outbox']), len(s.t['candidates']))
res = rn.trigger('event', 'run_e_2026-10-19_ud', '2026-10-19', event_id='ud-2026-09'); rn.drain(); n = rn.deliver()
test('R1', 'Duplicate event delivery is ignored', res == 'duplicate' and before == (len(s.t['versions']), len(s.t['outbox']), len(s.t['candidates'])) and n == 0, {'result': res, 'new_versions': len(s.t['versions']) - before[0], 'new_notifications': n})
CASES['duplicate_event'] = {'title': 'Event ud-2026-09 delivered again', 'result': 'Ignored: event id already recorded', 'lines': ['Trigger result: duplicate (event id ud-2026-09 already recorded)', f'New candidates: {len(s.t["candidates"]) - before[2]} · new insight versions: {len(s.t["versions"]) - before[0]} · new notifications: {n}']}
# R2 two schedulers fire the same checkpoint
s = Store(); rn = Runner(s); a = rn.trigger('weekly', 'run_w_2026-10-20', '2026-10-20'); b = rn.trigger('weekly', 'run_w_2026-10-20', '2026-10-20'); rn.drain(); c = rn.trigger('weekly', 'run_w_2026-10-20', '2026-10-20')
test('R2', 'The same checkpoint triggered twice runs once (run key = trigger · checkpoint · dataset · config)', (a, b, c) == ('queued', 'coalesced', 'duplicate') and len(s.t['runs']) == 1, {'first': a, 'second_while_queued': b, 'after_completion': c})
CASES['rerun_checkpoint'] = {'title': 'Checkpoint 20 Oct triggered again', 'result': 'No-op: run key already completed', 'lines': [f'Run key {run_key("weekly", "2026-10-20", DSV, CFG)} · status completed', 'Trigger result: duplicate · 0 new candidates · 0 new versions · 0 notifications', 'A new dataset or configuration version would produce a different key and a new run.']}
# R3 concurrent workers claim the same run
s = Store(); w1 = Runner(s, 'w1'); w2 = Runner(s, 'w2'); w1.trigger('weekly', 'run_w_2026-10-20', '2026-10-20'); key = run_key('weekly', '2026-10-20', DSV, CFG)
c1 = w1.claim(key, now=0); c2 = w2.claim(key, now=10); c3 = w2.claim(key, now=400)    # lease 300 s expired → takeover
test('R3', 'Concurrent claims: one worker holds the lease; another can take over only after it expires', c1 and not c2 and c3 and s.t['runs'][key]['attempt'] == 2, {'w1': c1, 'w2_during_lease': c2, 'w2_after_expiry': c3})
# R4 optimistic version check: a publish never overwrites a later checkpoint
s = Store(); rn = Runner(s); enqueue_all(rn); rn.drain()
v_before = s.t['insights']['T-202']['version']
st4 = rn.trigger('event-redelivery', 'run_e_2026-10-17_t2', '2026-10-17', event_id='tenant-action_t2#redelivered'); rn.drain()   # a different key that replays an older checkpoint
test('R4', 'An older checkpoint replayed late never overwrites a later version', st4 == 'queued' and s.t['insights']['T-202']['version'] == v_before and s.t['insights']['T-202']['checkpoint'] == '2026-10-20', {'version': s.t['insights']['T-202']['version'], 'checkpoint': s.t['insights']['T-202']['checkpoint']})
# R5 crash after staging, restart
s = Store(); rn = Runner(s); enqueue_all(rn)
first = sorted((r for r in s.t['runs'].values()), key=lambda r: (r['checkpoint'], r['kind'], r['key']))
crashed = None
for r in first:
    if r['ref'] == 'run_w_2026-10-20':
        try: rn.execute(r['key'], now=0, crash='after_staging')
        except Crash: crashed = r['key']
        break
    rn.execute(r['key'], now=0)
staged = sum(1 for v in s.t['staging'].values() if v['run'] == crashed); visible_mid = sum(1 for x in s.t['versions'].values() if x[2] == crashed)
rn2 = Runner(s, 'w2'); rn2.drain(now=1000); rn2.deliver()
test('R5', 'Crash after staging: nothing is visible; the restart discards staging and publishes once', staged > 0 and visible_mid == 0 and snapshot(s) == REFH and s.t['runs'][crashed]['attempt'] == 2, {'staged_rows_at_crash': staged, 'visible_versions_at_crash': visible_mid, 'equal_to_clean_run': snapshot(s) == REFH})
CASES['crash_before_publish'] = {'title': 'Crash after staging, before publish', 'result': 'Restarted: identical to a clean run', 'lines': [f'At the crash: {staged} staged candidate rows, 0 published versions, 0 notifications', 'Lease expired → attempt 2 discards staging and re-evaluates (detectors are read-only and deterministic)', f'Result hash equal to a clean run: {snapshot(s) == REFH}']}
# R6 crash inside the publish transaction
s = Store(); rn = Runner(s); enqueue_all(rn); pre = None
for r in sorted(s.t['runs'].values(), key=lambda r: (r['checkpoint'], r['kind'], r['key'])):
    if r['ref'] == 'run_w_2026-10-20':
        pre = (len(s.t['versions']), len(s.t['outbox']))
        try: rn.execute(r['key'], 0, crash='inside_publish')
        except Crash: pass
        mid = (len(s.t['versions']), len(s.t['outbox'])); break
    rn.execute(r['key'], 0)
Runner(s, 'w2').drain(now=1000); Runner(s, 'w2').deliver()
test('R6', 'Crash inside publish: the transaction rolls back; no partial insight or notification', pre == mid and snapshot(s) == REFH, {'before': pre, 'after_crash': mid})
# R7 crash after commit (before acknowledgement) and during delivery
s = Store(); rn = Runner(s); enqueue_all(rn)
for r in sorted(s.t['runs'].values(), key=lambda r: (r['checkpoint'], r['kind'], r['key'])):
    try: rn.execute(r['key'], 0, crash='after_commit' if r['ref'] == 'run_w_2026-10-20' else None)
    except Crash: pass
again = rn.trigger('weekly', 'run_w_2026-10-20', '2026-10-20')
try: rn.deliver(crash_after=3)
except Crash: pass
n2 = rn.deliver(); n3 = rn.deliver()
test('R7', 'Crash after commit or during delivery: re-trigger is a no-op and each notification is delivered exactly once', again == 'duplicate' and len(s.t['delivered']) == len(s.t['outbox']) == len(REF.t['outbox']) and n3 == 0, {'retrigger': again, 'outbox': len(s.t['outbox']), 'delivered': len(s.t['delivered'])})
# R8 shuffled trigger order gives the same result (worker orders by checkpoint)
rnd = random.Random(7); order = CAL[:]; rnd.shuffle(order)
s = Store(); rn = Runner(s); enqueue_all(rn, order); rn.drain(); rn.deliver()
test('R8', 'Triggers arriving in any order give the same versions, candidates and notifications', snapshot(s) == REFH, {'hash': snapshot(s), 'reference': REFH})
# R9 deterministic replay: two runs of the replay oracle and two runner replays agree
h1 = subprocess.run([sys.executable, S + '/dx6/replay.py', S], capture_output=True, text=True).stdout.split('hash ')[1].split()[0]
h2 = subprocess.run([sys.executable, S + '/dx6/replay.py', S], capture_output=True, text=True).stdout.split('hash ')[1].split()[0]
test('R9', 'Deterministic replay: the detector replay and the runner replay are byte-identical across runs', h1 == h2 == ORACLE['replay_hash'] and snapshot(reference()) == REFH, {'replay_hash': h1, 'runner_hash': REFH})
CASES['full_replay'] = {'title': 'Full replay of the checkpoint calendar', 'result': 'Identical result', 'lines': [f'{len(CAL)} runs replayed on {DSV} with {CFG}', f'Detector replay hash {h1} (twice) · runner snapshot {REFH} (twice)', f'{len(REF.t["versions"])} insight versions · {len(REF.t["candidates"])} candidates · {len(REF.t["outbox"])} notifications']}
# R10 notification suppression: re-runs and silent updates add no outbox rows
silent = sum(1 for x in REF.t['versions'].values() if 'silent' in x[6] or x[4] == 'Watch'); notified = len({(o['insight'], o['version']) for o in REF.t['outbox'].values()})
test('R10', 'Only notified versions create outbox rows (silent updates, Watch and merges do not)', notified == sum(1 for i in ORACLE['insights'] for v in i['versions'] if v['notified']) and silent > 0, {'notified_versions': notified, 'silent_or_watch_versions': silent})
# R11 late-arriving data: bitemporal reads
SEP_INGEST = dt.datetime(2026, 10, 19, 18, 30)
rows = [{'mall': 'Gulf Gate Mall', 'month': '2026-09', 'mm': 11, 'ingested_at': SEP_INGEST}, {'mall': 'Gulf Gate Mall', 'month': '2026-08', 'mm': 3, 'ingested_at': dt.datetime(2026, 9, 18, 9, 0)}]
def visible(cp): return [r for r in rows if r['ingested_at'] <= cp]
v13 = visible(dt.datetime(2026, 10, 13, 6, 0)); v19 = visible(dt.datetime(2026, 10, 19, 18, 31))
test('R11', 'Late-arriving rows are invisible to earlier checkpoints and visible from their ingestion run on', [r['month'] for r in v13] == ['2026-08'] and len(v19) == 2, {'13 Oct sees': [r['month'] for r in v13], '19 Oct sees': [r['month'] for r in v19]})
# R12 corrected data: a new dataset version re-evaluates the latest checkpoint; history keeps the old version
s = copy.deepcopy(REF); rn = Runner(s); st = rn.trigger('monthly', 'run_m_2026-10-20', '2026-10-20', dataset='sd-2026.10.20-02', partition='all'); rn.drain(); rn.deliver()
vs = sorted(x for x in s.t['versions'].values() if x[0] == 'INS-104')
test('R12', 'A corrected dataset version gets a new run key; the insight gains a version marked “data corrected”, earlier versions keep their dataset, no notification without a band rise', st == 'queued' and vs[-1][5] == 'sd-2026.10.20-02' and vs[-2][5] == DSV and vs[-1][3] == 57 and len(s.t['outbox']) == len(REF.t['outbox']), {'versions': [[x[1], x[3], x[4], x[5]] for x in vs]})
# R13 stale evidence flag between publication of a new dataset and its re-evaluation
def stale(store, iid, latest): return store.t['insights'][iid]['dataset'] != latest
test('R13', 'Insights whose evidence predates the latest dataset version are flagged stale until re-evaluated', stale(REF, 'INS-104', 'sd-2026.10.20-02') and not stale(s, 'INS-104', 'sd-2026.10.20-02'), {'before_correction_run': stale(REF, 'INS-104', 'sd-2026.10.20-02'), 'after': stale(s, 'INS-104', 'sd-2026.10.20-02')})
f = [x for x in T if not x['ok']]
json.dump({'tests': T, 'passed': len(T) - len(f), 'total': len(T), 'cases': CASES, 'reference_hash': REFH, 'replay_hash': ORACLE['replay_hash']}, open(S + '/dx6/runner_results.json', 'w'), indent=1, default=str)
print('runner model', len(T) - len(f), '/', len(T)); [print('FAIL', x['id'], x['name'], x['detail']) for x in f]

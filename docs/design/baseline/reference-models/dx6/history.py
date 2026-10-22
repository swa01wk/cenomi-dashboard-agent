"""Canonical scenario history for DX6 (v2) — design-verification data, not application code.

Single source for every series the detectors read. Snapshot values on the as-of date come from the shared
DX2/DX4 dataset (sd-2026.10.20-01); the earlier checkpoints are the declared history extension (DXD-73),
now required to be reconstructible from record lifecycles (see recon.py).
"""
import json, datetime as dt

AS_OF = dt.date(2026, 10, 20)          # DR-003/DR-004: frozen as_of, a Tuesday
DSV = 'sd-2026.10.20-01'

def load(S):
    D = json.load(open(S + '/dx4/raw.json'))
    D3 = json.load(open(S + '/dx3/data.json'))
    return D, D3

# Weekly checkpoints (Tuesday, Asia/Riyadh), 14 values: 21 Jul … 20 Oct. Detector windows need 7 checkpoints,
# so the first weekly evaluation in the replay is 1 Sep (DXD-81 minimum history).
WEEKS = [AS_OF - dt.timedelta(days=7 * k) for k in range(13, -1, -1)]
WL = [f'{d.day} {d.strftime("%b")}' for d in WEEKS]
EVAL_WEEKS = [d for d in WEEKS if d >= dt.date(2026, 9, 1)]
# Monthly checkpoints for stock metrics, anchored on the as-of day of month (20th) so the last value is the snapshot.
MONTHS = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
MDATES = [dt.date(2026, m, 20) for m in range(4, 11)]
EVAL_MONTHS = [dt.date(2026, 9, 20), dt.date(2026, 10, 20)]

def ext(prefix, base):
    return prefix + base

# Approvals waiting 31+ days (band "1 month plus"), all three types, per Central mall.
AP1M = {
    'Rawdah Point Mall': ext([15, 16, 17], [18, 20, 21, 22, 24, 27, 29, 32, 35, 39, 41]),
    'Qasr Plaza': ext([3, 4, 5], [6, 7, 8, 9, 9, 8, 7, 5, 4, 3, 2]),
    'Sandstone Galleria': ext([4, 4, 4], [4, 4, 4, 4, 5, 4, 4, 5, 4, 4, 4]),
    'Najd Gate Mall': ext([3, 3, 3], [3, 3, 4, 3, 4, 4, 3, 4, 4, 4, 4]),
    'Wadi Crescent Centre': ext([3, 3, 3], [3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3]),
    'Falcon Square': [2] * 14, 'Oasis Row': [2] * 14, 'Cedar Park Mall': ext([2, 2, 2], [2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2]),
    'Amber Heights': [1] * 14, 'Mirage Commons': [1] * 14}
# v2 adds three earlier weekly checkpoints (21 Jul, 28 Jul, 4 Aug); the v1 values from 11 Aug are unchanged.
# Renewal amendments in the 4 wk+ band (28+ days since creation), per Central mall that has any.
REN4 = {'Rawdah Point Mall': [4, 4, 4, 4, 4, 4, 4, 4, 5, 6, 7, 7, 8, 9],
        'Sandstone Galleria': [8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 6, 6, 6, 6],
        'Qasr Plaza': [4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3]}
OTHER4_CENTRAL = 7   # Expansion 1 + HoldOver 2 + Termination 4 in 4 wk+, constant across the window
# Vacant units on the 20th of each month (stock), Central malls with movement; others flat at the snapshot.
VAC = {'Mirage Commons': [47, 48, 50, 51, 53, 56, 58], 'Sandstone Galleria': [54, 53, 54, 54, 55, 54, 54],
       'Oasis Row': [41, 41, 40, 41, 41, 41, 41], 'Wadi Crescent Centre': [49, 49, 48, 49, 49, 49, 49]}
# Unit discrepancy, latest report per mall per calendar month (Asia/Riyadh, DR-006). Gulf Gate history.
UD_GULF = {'months': ['Jun', 'Jul', 'Aug', 'Sep'], 'mm': [3, 4, 3, 11], 'units': [140, 141, 142, 142]}
UD_MISSING = {'Oasis Row': ['Aug', 'Sep'], 'Amber Heights': ['Sep'], 'Mirage Commons': ['Sep'], 'Lantern Quay': ['Sep'],
              'Mangrove Mall': ['Sep'], 'Marina Square West': ['Sep'], 'Hijaz Crossing': ['Sep']}
SEP_REPORTS_INGESTED = dt.datetime(2026, 10, 19, 18, 30)   # late-arriving: September reports loaded on 19 Oct
# Tenant T-31206 (Lumen Home, Sandstone Galleria). 2026 from DX2/DX4; 2025 and 2024 from the DX2 tenant board's
# generator (y25 = 2026 × 0.93 rounded to 100; y24 = y25 × 0.9, January 2024 × 0.55 because the lease started 15 Jan).
def r100(x): return int(round(x / 100.0)) * 100
def tenant_sales(D):
    y26 = [c['v'] for c in D['tenant']['cols']]
    y25 = [r100(x * 0.93) for x in y26] + [r100(y26[7] * 1.02 * 0.93), r100(y26[7] * 1.08 * 0.93), r100(y26[7] * 1.21 * 0.93)]
    y24 = [r100(x * 0.9 * (0.55 if i == 0 else 1)) for i, x in enumerate(y25)]
    return {'2024': y24, '2025': y25, '2026': y26}
# Lease-scoped action items for T-31206 (DX2 tenant board: documents to upload; no SR in Action required at Sandstone).
TENANT_ACTIONS = [
    {'id': 'DOC-T31206-LL', 'what': 'Lighting layout', 'kind': 'Fit-out drawing to upload', 'since': dt.date(2026, 10, 12)},
    {'id': 'DOC-T31206-SF', 'what': 'Shopfront details — re-upload', 'kind': 'Fit-out drawing returned for re-upload', 'since': dt.date(2026, 10, 17)}]
TENANT_SR_ACTION_REQUIRED = {'Rawdah Point Mall': 1, 'Sandstone Galleria': 0, 'Gulf Gate Mall': 1}   # company view = 2

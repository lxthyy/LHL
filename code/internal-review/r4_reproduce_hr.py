# -*- coding: utf-8 -*-
"""
审校 4：定向复现加权 HR 与死因别 HR（不跑全流程，只跑 20 个 Cox 模型）
与 结果表\weighted_hr.csv、cause_specific.csv 逐格比对
"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from scipy import stats as st

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
DATA = os.path.join(P, '数据', 'analysis_dataset_extc.csv')
OUT = os.path.join(P, '代码', '_审校')

d = pd.read_csv(DATA, encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al',
       'Dispersion': 'disp', 'PC1': 'pc1'}
d = d.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d = d[d.months > 0].reset_index(drop=True)
D = pd.get_dummies(d[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True,
                   dtype=float)
for c in D.columns:
    d[c] = D[c].values
RA = [c for c in D.columns if c.startswith('race_')]
CY = [c for c in D.columns if c.startswith('cycle_')]
COV = NUM + RA + CY
d['w'] = d.WTMEC2YR / 8.0
d['psu'] = pd.factorize(d.cycle.astype(str) + '_' +
                        d.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                        d.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
for k in IDX.values():
    d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)
print('n=%d deaths=%d' % (len(d), int(d.dead.sum())))


def wcox(cols, event='dead', df=None):
    df = d if df is None else df
    data = df[['months', event, 'w'] + cols]
    f = CoxPHFitter().fit(data, 'months', event, weights_col='w')
    sr = np.asarray(f.compute_residuals(data, 'score'), dtype=float)
    if sr.shape[1] == len(cols) + 1:
        sr = sr[:, 1:]
    G = pd.DataFrame(sr, columns=cols).assign(psu=df.psu.values).groupby('psu').sum().values
    bread = f.variance_matrix_.values
    V = bread @ (G.T @ G) @ bread
    b = float(f.params_[cols[0]])
    return b, float(np.sqrt(V[0, 0]))


rows = []
for name, v in IDX.items():
    b, se = wcox(['z_' + v] + COV)
    rows.append(dict(index=name, HR=np.exp(b), lo=np.exp(b - 1.96 * se),
                     hi=np.exp(b + 1.96 * se)))
new = pd.DataFrame(rows)
old = pd.read_csv(os.path.join(P, '结果表', 'weighted_hr.csv'), encoding='utf-8-sig')
old.columns = ['index', 'HR', 'lo', 'hi', 'p']
print('\n=== 加权 HR：重跑 vs 冻结 ===')
for i in range(len(new)):
    a, b = new.iloc[i], old.iloc[i]
    print('%-10s new %.4f (%.4f-%.4f)  frozen %.4f (%.4f-%.4f)  %s' % (
        a['index'], a.HR, a.lo, a.hi, b.HR, b.lo, b.hi,
        'OK' if abs(a.HR - b.HR) < 1e-9 else 'DIFF'))

# 死因别
C6 = ['1999-00', '2001-02', '2003-04', '2005-06', '2007-08', '2009-10']
d6 = d[d.cycle.isin(C6)].reset_index(drop=True)
D6 = pd.get_dummies(d6[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True,
                    dtype=float)
for c in D6.columns:
    d6[c] = D6[c].values
COV6 = NUM + [c for c in D6.columns if c.startswith('race_')] + \
       [c for c in D6.columns if c.startswith('cycle_')]
cs = []
for ev, cn in [('evt_cvd', '心血管'), ('evt_can', '肿瘤'), ('evt_resp', '呼吸')]:
    for name, v in IDX.items():
        b, se = wcox(['z_' + v] + COV6, event=ev, df=d6)
        cs.append(dict(outcome=cn, index=name, HR=np.exp(b),
                       lo=np.exp(b - 1.96 * se), hi=np.exp(b + 1.96 * se),
                       p=2 * (1 - st.norm.cdf(abs(b / se)))))
new6 = pd.DataFrame(cs)
old6 = pd.read_csv(os.path.join(P, '结果表', 'cause_specific.csv'), encoding='utf-8-sig')
print('\n=== 死因别 HR：重跑 vs 冻结 ===')
bad = 0
for i in range(len(new6)):
    a, b = new6.iloc[i], old6.iloc[i]
    ok = abs(a.HR - b.HR) < 1e-9
    if not ok:
        bad += 1
    print('%-4s %-10s new %.4f (%.4f-%.4f) frozen %.4f (%.4f-%.4f) %s' % (
        a.outcome, a['index'], a.HR, a.lo, a.hi, b.HR, b.lo, b.hi,
        'OK' if ok else 'DIFF'))
print('\n死因别不一致:', bad)

# ---- 落盘：供十次一致性比对（并行时用 R4_TAG 区分） ----
import hashlib
TAG = os.environ.get('R4_TAG', '')
new.to_csv(os.path.join(OUT, 'r4_hr%s.csv' % TAG), index=False, encoding='utf-8-sig')
new6.to_csv(os.path.join(OUT, 'r4_cause%s.csv' % TAG), index=False, encoding='utf-8-sig')
for f in ['r4_hr%s.csv' % TAG, 'r4_cause%s.csv' % TAG]:
    h = hashlib.sha256(open(os.path.join(OUT, f), 'rb').read()).hexdigest()[:16].upper()
    print('HASH %s %s' % (h, f))

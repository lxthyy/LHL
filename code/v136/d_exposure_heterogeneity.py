# -*- coding: utf-8 -*-
"""v1.36 D: 重建体力活动变量 -> 复现暴露谱 -> 跨指数异质性检验（Wald, PSU bootstrap）"""
import os
import numpy as np
import pandas as pd
from scipy import stats as st

P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
OUT = os.path.join(P, '结果表', '_v136')
PAQ = os.path.join(os.environ['TEMP'], 'paq')
os.makedirs(OUT, exist_ok=True)

CYC = {'D': '2005-06', 'E': '2007-08', 'F': '2009-10', 'I': '2015-16', 'J': '2017-18'}
pa = []
for k, lab in CYC.items():
    x = pd.read_sas(os.path.join(PAQ, 'PAQ_%s.XPT' % k), format='xport')
    cols = [v for v in ['PAQ650', 'PAQ665'] if v in x.columns]
    if not cols:
        print('  skip %s (%s): PAQ650/665 not fielded' % (k, lab))
        continue
    y = x[['SEQN'] + cols].copy()
    val = pd.Series(False, index=y.index)
    for c in cols:
        val = val | (y[c] == 1)
    y['active'] = val.astype(float)
    y.loc[y[cols].isna().all(axis=1), 'active'] = np.nan
    y['cycle'] = lab
    pa.append(y[['SEQN', 'cycle', 'active']])
pa = pd.concat(pa, ignore_index=True)
pa['SEQN'] = pa.SEQN.astype('int64')
pa.to_csv(os.path.join(P, '数据', 'paq_active.csv'), index=False, encoding='utf-8-sig')
print('paq_active rows:', len(pa), 'cycles:', sorted(pa.cycle.unique()))

d = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX9 = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al9', 'Dispersion': 'disp', 'PC1': 'pc1'}
d = d.dropna(subset=['months', 'dead'] + NUM + list(IDX9.values()) + ['race'])
d = d[d.months > 0].reset_index(drop=True)
Dm = pd.get_dummies(d[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True, dtype=float)
for c in Dm.columns:
    d[c] = Dm[c].values
RA = [c for c in Dm.columns if c.startswith('race_')]
CY = [c for c in Dm.columns if c.startswith('cycle_')]
COV = NUM + RA + CY
d['psu'] = pd.factorize(d.cycle.astype(str) + '_' +
                        d.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                        d.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
d = d.merge(pa, on=['SEQN', 'cycle'], how='left')
print('active non-missing in analytic sample:', int(d.active.notna().sum()),
      '| cycles with PA:', sorted(d.loc[d.active.notna(), 'cycle'].unique()))

EXPO = {'BMI': 'bmi', 'Current smoking': 'smoke', 'Physical activity': 'active',
        'Education': 'edu', 'Income-to-poverty ratio': 'pir'}
names = list(IDX9)

def design(dd, expo):
    covs = [c for c in COV if c != expo]
    X = np.column_stack([np.ones(len(dd)), dd[expo].astype(float).values,
                         dd[covs].astype(float).values])
    Y = np.column_stack([((dd[v].astype(float) - dd[v].astype(float).mean()) /
                          dd[v].astype(float).std()).values for v in IDX9.values()])
    ok = np.isfinite(X).all(1) & np.isfinite(Y).all(1)
    return X[ok], Y[ok], ok

def coef(X, Y):
    b, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return b[1]

rep, res = [], []
rng = np.random.default_rng(20261105)
B = 400
Rc = np.zeros((4, 5))
for i in range(4):
    Rc[i, 0] = 1
    Rc[i, i + 1] = -1

for lab, v in EXPO.items():
    sub = d.dropna(subset=[v]).reset_index(drop=True)
    X, Y, ok = design(sub, v)
    b0 = coef(X, Y)
    rep.append(dict(exposure=lab, n=len(X), **{k: round(float(x), 4) for k, x in zip(names, b0)}))
    psu_arr = sub.psu.values[ok]
    pr, ids = {}, []
    for p in np.unique(psu_arr):
        pr[p] = np.where(psu_arr == p)[0]
        ids.append(p)
    ids = np.array(ids)
    draws = []
    for _ in range(B):
        pick = rng.choice(ids, size=len(ids), replace=True)
        rows = np.concatenate([pr[p] for p in pick])
        draws.append(coef(X[rows], Y[rows]))
    draws = np.array(draws)
    V = np.cov(draws.T)
    Rb = Rc @ b0
    W = float(Rb @ np.linalg.solve(Rc @ V @ Rc.T, Rb))
    p = float(st.chi2.sf(W, df=4))
    res.append(dict(exposure=lab, n=len(X), beta_min=float(b0.min()), beta_max=float(b0.max()),
                    spread=float(b0.max() - b0.min()), wald=W, df=4, p=p,
                    n_boot=B))
    print('%-26s n=%6d spread=%.4f  Wald=%.2f  p=%.3g' % (lab, len(X), res[-1]['spread'], W, p),
          flush=True)

rep = pd.DataFrame(rep)
rep.to_csv(os.path.join(OUT, 'exposure_reproduce.csv'), index=False, encoding='utf-8-sig')
print(rep.to_string(index=False))
res = pd.DataFrame(res)
res.to_csv(os.path.join(OUT, 'exposure_heterogeneity.csv'), index=False, encoding='utf-8-sig')
print(res.to_string(index=False))

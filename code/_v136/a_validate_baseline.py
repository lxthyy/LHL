# -*- coding: utf-8 -*-
"""v1.36 A: 复现校验 + 基线模型（无指数）"""
import os, sys, json, time
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
OUT = os.path.join(P, '结果表', '_v136')
os.makedirs(OUT, exist_ok=True)

d = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al', 'Dispersion': 'disp', 'PC1': 'pc1'}
d = d.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d = d[d.months > 0].reset_index(drop=True)
Dm = pd.get_dummies(d[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True, dtype=float)
for c in Dm.columns:
    d[c] = Dm[c].values
RA = [c for c in Dm.columns if c.startswith('race_')]
CY = [c for c in Dm.columns if c.startswith('cycle_')]
COV = NUM + RA + CY
d['w'] = d.WTMEC2YR / 8.0
d['psu'] = pd.factorize(d.cycle.astype(str) + '_' +
                        d.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                        d.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
for k in IDX.values():
    d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)

print('n=%d deaths=%d cov=%d cycles=%d psus=%d'
      % (len(d), d.dead.sum(), len(COV), len(CY), d.psu.nunique()))

res = []
risk = {}
t0 = time.time()
for name, v in IDX.items():
    f = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_' + v]], 'months', 'dead')
    res.append(dict(index=name, C=f.concordance_index_))
    risk[name] = f.predict_partial_hazard(d[COV + ['z_' + v]]).values
    print('  %-11s C=%.6f  (%.0fs)' % (name, f.concordance_index_, time.time() - t0))

base = CoxPHFitter().fit(d[['months', 'dead'] + COV], 'months', 'dead')
print('  %-11s C=%.6f' % ('Covariates', base.concordance_index_))

out = pd.DataFrame(res)
out['delta_vs_base'] = out.C - base.concordance_index_
out.to_csv(os.path.join(OUT, 'cindex_with_baseline.csv'), index=False, encoding='utf-8-sig')
np.save(os.path.join(OUT, 'risk_scores.npy'), risk, allow_pickle=True)
d[['SEQN', 'cycle', 'psu', 'w', 'months', 'dead']].to_csv(
    os.path.join(OUT, 'sample_key.csv'), index=False, encoding='utf-8-sig')
print(out.to_string(index=False))
print('baseline C = %.6f' % base.concordance_index_)

# -*- coding: utf-8 -*-
"""v1.36 B: 设计基础（PSU within stratum）cluster bootstrap，1000 次"""
import os, time
import numpy as np
import pandas as pd
from lifelines.utils import concordance_index

P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
OUT = os.path.join(P, '结果表', '_v136')
risk = np.load(os.path.join(OUT, 'risk_scores.npy'), allow_pickle=True).item()
key = pd.read_csv(os.path.join(OUT, 'sample_key.csv'), encoding='utf-8-sig')
d = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d = d[d.months > 0].dropna(subset=['months', 'dead', 'age', 'male', 'edu', 'pir', 'bmi',
                                   'smoke', 'race', 'hd', 'al', 'disp', 'pc1', 'phenoage'])
d = d.reset_index(drop=True)
assert len(d) == len(key), (len(d), len(key))

# 与 a_ 脚本完全相同的行序：重跑同一套清洗
d2 = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d2['hd_log'] = np.log(d2.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al', 'Dispersion': 'disp', 'PC1': 'pc1'}
d2 = d2.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d2 = d2[d2.months > 0].reset_index(drop=True)
d2['psu'] = pd.factorize(d2.cycle.astype(str) + '_' +
                         d2.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                         d2.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
d2['stratum'] = pd.factorize(d2.cycle.astype(str) + '_' +
                             d2.SDMVSTRA.fillna(-1).astype(int).astype(str))[0]
assert len(d2) == len(key) and (d2.psu.values == key.psu.values).all()

T = d2.months.values
E = d2.dead.values.astype(int)
R = {k: v for k, v in risk.items()}
names = list(IDX)
psu = d2.psu.values
strata = d2.stratum.values

# PSU -> rows
psu_rows = {}
for i, p in enumerate(psu):
    psu_rows.setdefault(p, []).append(i)
psu_rows = {p: np.array(v) for p, v in psu_rows.items()}
psu_str = pd.Series(psu).groupby(strata).apply(lambda s: np.array(sorted(s.unique()))).to_dict()

obs = {k: concordance_index(T, -R[k], E) for k in names}
pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
print('observed:', {k: round(v, 6) for k, v in obs.items()})

B = 1000
rng = np.random.default_rng(20261105)
rec = {p: [] for p in pairs}
t0 = time.time()
for b in range(B):
    idx = []
    for s, plist in psu_str.items():
        draw = rng.choice(plist, size=len(plist), replace=True)
        for p in draw:
            idx.append(psu_rows[p])
    idx = np.concatenate(idx)
    tt, ee = T[idx], E[idx]
    cc = {k: concordance_index(tt, -R[k][idx], ee) for k in names}
    for p in pairs:
        rec[p].append(cc[p[0]] - cc[p[1]])
    if (b + 1) % 100 == 0:
        print('  %d/%d  %.0fs' % (b + 1, B, time.time() - t0), flush=True)

rows = []
for p in pairs:
    v = np.array(rec[p])
    rows.append(dict(pair='%s − %s' % p, dC=float(np.mean(v)),
                     lo=float(np.percentile(v, 2.5)), hi=float(np.percentile(v, 97.5)),
                     se=float(np.std(v, ddof=1)), n_boot=B,
                     equiv=bool(np.percentile(v, 2.5) > -0.01 and np.percentile(v, 97.5) < 0.01)))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, 'equivalence_cluster_boot1000.csv'), index=False, encoding='utf-8-sig')
print(df.to_string(index=False))
print('等价对:', int(df.equiv.sum()))

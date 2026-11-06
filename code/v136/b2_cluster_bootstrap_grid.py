# -*- coding: utf-8 -*-
"""v1.36 B2: 设计基础 cluster bootstrap（保存全部抽样，供界敏感性与同时带复用）"""
import os, time
import numpy as np
import pandas as pd
from lifelines.utils import concordance_index

P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
OUT = os.path.join(P, '结果表', '_v136')
risk = np.load(os.path.join(OUT, 'risk_scores.npy'), allow_pickle=True).item()
key = pd.read_csv(os.path.join(OUT, 'sample_key.csv'), encoding='utf-8-sig')
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
assert (d2.psu.values == key.psu.values).all()

T, E = d2.months.values, d2.dead.values.astype(int)
R = {k: np.asarray(v) for k, v in risk.items()}
names = list(IDX)
psu, strata = d2.psu.values, d2.stratum.values
psu_rows = {p: np.where(psu == p)[0] for p in np.unique(psu)}
psu_str = {s: np.unique(psu[strata == s]) for s in np.unique(strata)}
pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]

obs = {k: concordance_index(T, -R[k], E) for k in names}
B = 1000
rng = np.random.default_rng(20261105)
D = np.zeros((B, len(pairs)))
t0 = time.time()
for b in range(B):
    rows = np.concatenate([psu_rows[p] for s, pl in psu_str.items()
                           for p in rng.choice(pl, size=len(pl), replace=True)])
    tt, ee = T[rows], E[rows]
    cc = {k: concordance_index(tt, -R[k][rows], ee) for k in names}
    D[b] = [cc[a] - cc[c] for a, c in pairs]
    if (b + 1) % 100 == 0:
        print('  %d/%d %.0fs' % (b + 1, B, time.time() - t0), flush=True)

np.save(os.path.join(OUT, 'cluster_boot_draws.npy'), D)
pd.DataFrame([dict(pair='%s − %s' % p, dC=float(D[:, i].mean()),
                   lo=float(np.percentile(D[:, i], 2.5)), hi=float(np.percentile(D[:, i], 97.5)),
                   se=float(D[:, i].std(ddof=1))) for i, p in enumerate(pairs)]
             ).to_csv(os.path.join(OUT, 'equivalence_cluster_boot1000.csv'),
                      index=False, encoding='utf-8-sig')

rows = []
for m in (0.0025, 0.005, 0.01, 0.015, 0.02, 0.03):
    ok = [(np.percentile(D[:, i], 2.5) > -m) and (np.percentile(D[:, i], 97.5) < m)
          for i in range(len(pairs))]
    rows.append(dict(margin=m, n_eq=int(sum(ok)),
                     pairs='; '.join('%s − %s' % pairs[i] for i in range(len(pairs)) if ok[i])))
grid = pd.DataFrame(rows)
grid.to_csv(os.path.join(OUT, 'margin_grid_cluster.csv'), index=False, encoding='utf-8-sig')
print(grid.to_string(index=False))

centered = D - D.mean(0)
band = float(np.percentile(np.abs(centered).max(1), 95))
print('simultaneous band half-width:', round(band, 4))
pd.DataFrame([dict(band_halfwidth=band, n_boot=B)]).to_csv(
    os.path.join(OUT, 'simultaneous_band_cluster.csv'), index=False, encoding='utf-8-sig')

# -*- coding: utf-8 -*-
"""v1.36 C: 分辨极限的经验验证（子抽样到给定死亡数，重算 C 与排序）"""
import os, time
import numpy as np
import pandas as pd
from lifelines.utils import concordance_index

P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
OUT = os.path.join(P, '结果表', '_v136')
risk = np.load(os.path.join(OUT, 'risk_scores.npy'), allow_pickle=True).item()
key = pd.read_csv(os.path.join(OUT, 'sample_key.csv'), encoding='utf-8-sig')
T = key.months.values
E = key.dead.values.astype(int)
names = list(risk)
R = {k: np.asarray(v) for k, v in risk.items()}
N = len(T)
Dtot = int(E.sum())
best = 'PhenoAge'
print('N=%d deaths=%d' % (N, Dtot))

rng = np.random.default_rng(20261105)
targets = [50, 100, 200, 500, 1000, 2000, 5636]
REPS = 400
rows = []
t0 = time.time()
for D in targets:
    f = D / Dtot
    n = int(round(f * N))
    hits, maxdiff, sd_dc, se_pair = 0, [], [], []
    for b in range(REPS):
        i = rng.choice(N, size=n, replace=False)
        tt, ee = T[i], E[i]
        cc = {k: concordance_index(tt, -R[k][i], ee) for k in names}
        if max(cc, key=cc.get) == best:
            hits += 1
        vals = np.array(list(cc.values()))
        maxdiff.append(vals.max() - vals.min())
        se_pair.append(cc['PhenoAge'] - cc['PC1'])
    se_pair = np.array(se_pair)
    rows.append(dict(deaths_target=D, n=n, reps=REPS,
                     p_naming_phenoage=hits / REPS,
                     median_max_minus_min=float(np.median(maxdiff)),
                     sd_deltaC_phenoage_pc1=float(np.std(se_pair, ddof=1)),
                     mdd80_empirical=float(2.80 * np.std(se_pair, ddof=1)),
                     deaths_realised=float(Dtot * n / N)))
    print('  D=%5d n=%6d  P(best)=%.3f  med(max-min)=%.4f  SD(ΔC)=%.4f  %.0fs'
          % (D, n, hits / REPS, np.median(maxdiff), np.std(se_pair, ddof=1), time.time() - t0),
          flush=True)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, 'resolution_floor_empirical.csv'), index=False, encoding='utf-8-sig')
print(df.to_string(index=False))

# -*- coding: utf-8 -*-
"""
按检测年代切分，检验等价性是否跨检测体系成立
1999-2010：五个指标（含 CRP 旧法）    2011-2018：三个无 CRP 指标
配对 bootstrap 直接重采样个体（线性预测子固定），不重拟合 Cox
"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
OUT = os.path.join(P, '结果表', '加强')
rng = np.random.default_rng(20261105)

d = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al',
       'Dispersion': 'disp', 'PC1': 'pc1'}
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
d = d.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race', 'cycle'])
d = d[d.months > 0].reset_index(drop=True)
d['yr'] = d.cycle.astype(str).str.extract(r'(\d{4})')[0].astype(float)
d = d.dropna(subset=['yr']).reset_index(drop=True)

d2 = pd.get_dummies(d, columns=['race'], drop_first=True, dtype=float)
COV = NUM + [c for c in d2.columns if c.startswith('race_')]

ERAS = [('1999–2010', d2[d2.yr <= 2010], list(IDX)),
        ('2011–2018', d2[d2.yr >= 2011], ['AL', 'Dispersion', 'PC1'])]
NB = 200
rows = []
for ename, e, use in ERAS:
    e = e.reset_index(drop=True)
    lp = {}
    for k in use:
        x = (e[IDX[k]] - e[IDX[k]].mean()) / e[IDX[k]].std()
        f = CoxPHFitter().fit(pd.concat([e[['months', 'dead'] + COV], x.rename('z')], axis=1),
                              'months', 'dead')
        lp[k] = f.predict_partial_hazard(
            pd.concat([e[COV], x.rename('z')], axis=1)).values
    t, ev = e.months.values, e.dead.values
    base = {k: concordance_index(t, -lp[k], ev) for k in use}
    n = len(e)
    boot = {k: [] for k in use}
    for _ in range(NB):
        i = rng.integers(0, n, n)
        for k in use:
            boot[k].append(concordance_index(t[i], -lp[k][i], ev[i]))
    for a, b in [(x, y) for i, x in enumerate(use) for y in use[i + 1:]]:
        diff = base[a] - base[b]
        bd = np.array(boot[a]) - np.array(boot[b])
        lo, hi = np.percentile(bd, [2.5, 97.5])
        rows.append(dict(era=ename, n=n, deaths=int(ev.sum()), pair=f'{a}−{b}',
                         c_a=round(base[a], 4), c_b=round(base[b], 4),
                         diff=round(diff, 4), lo=round(lo, 4), hi=round(hi, 4)))
    print('%s  n=%d  死亡=%d  已完成' % (ename, n, int(ev.sum())))

R = pd.DataFrame(rows)
R['eq_0.01'] = (R.lo > -0.01) & (R.hi < 0.01)
R['eq_0.005'] = (R.lo > -0.005) & (R.hi < 0.005)
R['eq_0.015'] = (R.lo > -0.015) & (R.hi < 0.015)
R.to_csv(os.path.join(OUT, 'era_split_equivalence.csv'), index=False, encoding='utf-8-sig')
print()
print(R.to_string(index=False))
print()
for ename in R.era.unique():
    s = R[R.era == ename]
    print('%s：±0.005 下 %d/%d 对等价，±0.01 下 %d/%d，±0.015 下 %d/%d' % (
        ename, s['eq_0.005'].sum(), len(s), s['eq_0.01'].sum(), len(s),
        s['eq_0.015'].sum(), len(s)))

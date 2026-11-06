# -*- coding: utf-8 -*-
"""run_x10：十周期（含 2011-14）三指数面板
指数：离散度 / AL9c（去 BMI、去 CRP）/ PC1；权重 /10；死因别限 1999-2014
"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
from scipy import stats as st

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
EXT = os.path.join(OUT, 'ext10')
os.makedirs(EXT, exist_ok=True)
rng = np.random.default_rng(20261031)

d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_extc10.csv'), encoding='utf-8-sig')
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'Dispersion': 'disp', 'AL9c': 'al9c', 'PC1': 'pc1'}
d = d.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d = d[d.months > 0].reset_index(drop=True)
DD = pd.get_dummies(d[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True,
                    dtype=float)
for c in DD.columns:
    d[c] = DD[c].values
COV = NUM + [c for c in DD.columns if c.startswith('race_')] + \
      [c for c in DD.columns if c.startswith('cycle_')]
d['w'] = d.WTMEC2YR / 10.0
d['psu'] = pd.factorize(d.cycle.astype(str) + '_' +
                        d.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                        d.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
for k in IDX.values():
    d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)
print('n=%d 死亡=%d 心血管=%d 肿瘤=%d 呼吸=%d 协变量=%d'
      % (len(d), int(d.dead.sum()), int(d.evt_cvd.sum()), int(d.evt_can.sum()),
         int(d.evt_resp.sum()), len(COV)))


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
    return b, float(np.sqrt(V[0, 0])), f


main, wt, risk = [], [], {}
for name, v in IDX.items():
    f = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_' + v]], 'months', 'dead')
    b, se = f.params_['z_' + v], f.standard_errors_['z_' + v]
    main.append(dict(指数=name, C指数=f.concordance_index_, HR=np.exp(b),
                     lo=np.exp(b - 1.96 * se), hi=np.exp(b + 1.96 * se),
                     p=f.summary.loc['z_' + v, 'p']))
    b2, s2, _ = wcox(['z_' + v] + COV)
    wt.append(dict(指数=name, HR_w=np.exp(b2), lo=np.exp(b2 - 1.96 * s2),
                   hi=np.exp(b2 + 1.96 * s2), p=2 * (1 - st.norm.cdf(abs(b2 / s2)))))
    risk[name] = f.predict_partial_hazard(d[COV + ['z_' + v]]).values
print('\n=== C 指数 / 加权 HR（十周期）===')
print(pd.DataFrame(main).round(4).to_string(index=False))
print(pd.DataFrame(wt).round(4).to_string(index=False))
pd.DataFrame(main).to_csv(os.path.join(EXT, 'cindex_hr.csv'), index=False, encoding='utf-8-sig')
pd.DataFrame(wt).to_csv(os.path.join(EXT, 'weighted_hr.csv'), index=False, encoding='utf-8-sig')

# ---- 三对等价性 bootstrap ----
names = list(IDX)
T, E = d.months.values, d.dead.values.astype(int)
B, n = 300, len(d)
dc = {'%s − %s' % (a, b): [] for i, a in enumerate(names) for b in names[i + 1:]}
for _ in range(B):
    idx = rng.integers(0, n, n)
    cc = {k: concordance_index(T[idx], -v[idx], E[idx]) for k, v in risk.items()}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            dc['%s − %s' % (a, b)].append(cc[a] - cc[b])
eq = pd.DataFrame([dict(比较=k, dC=float(np.mean(v)), lo=float(np.percentile(v, 2.5)),
                        hi=float(np.percentile(v, 97.5)),
                        等价='是' if (np.percentile(v, 2.5) > -0.01
                                   and np.percentile(v, 97.5) < 0.01) else '否')
                   for k, v in dc.items()])
print('\n=== 等价性（±0.01）===')
print(eq.round(4).to_string(index=False))
eq.to_csv(os.path.join(EXT, 'equivalence.csv'), index=False, encoding='utf-8-sig')

# ---- 死因别 1999-2014（八周期）----
C8 = ['1999-00', '2001-02', '2003-04', '2005-06', '2007-08', '2009-10',
      '2011-12', '2013-14']
d8 = d[d.cycle.isin(C8)].reset_index(drop=True)
D8 = pd.get_dummies(d8[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True,
                    dtype=float)
for c in D8.columns:
    d8[c] = D8[c].values
COV8 = NUM + [c for c in D8.columns if c.startswith('race_')] + \
       [c for c in D8.columns if c.startswith('cycle_')]
print('\n死因别窗口 1999-2014：n=%d 死亡=%d（心血管 %d 肿瘤 %d 呼吸 %d）'
      % (len(d8), int(d8.dead.sum()), int(d8.evt_cvd.sum()), int(d8.evt_can.sum()),
         int(d8.evt_resp.sum())))
cs = []
for ev, nn in [('evt_cvd', '心血管'), ('evt_can', '肿瘤'), ('evt_resp', '呼吸')]:
    for name, v in IDX.items():
        b, se, _ = wcox(['z_' + v] + COV8, event=ev, df=d8)
        cs.append(dict(结局=nn, 指数=name, HR=np.exp(b), lo=np.exp(b - 1.96 * se),
                       hi=np.exp(b + 1.96 * se), p=2 * (1 - st.norm.cdf(abs(b / se))),
                       事件=int(d8[ev].sum())))
cs = pd.DataFrame(cs)
print(cs.pivot(index='指数', columns='结局', values='HR').round(3).to_string())
print(cs.pivot(index='指数', columns='结局', values='p').round(4).to_string())
cs.to_csv(os.path.join(EXT, 'cause_specific.csv'), index=False, encoding='utf-8-sig')
print('\n完成 →', EXT)

# -*- coding: utf-8 -*-
"""selbias2：CRP 选择偏倚的三套对照（稳健版）
(1) 全八周期完整病例（现稿口径）
(2) IPW 加权（纳入概率）
(3) 只用 2005-2018（这六个周期 CRP 全员检测，不含子样本缺失）
(4) 只用 1999-2010（含 CRP 子样本）
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from lifelines import CoxPHFitter

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
EXT = os.path.join(OUT, 'ext_selbias')
os.makedirs(EXT, exist_ok=True)

d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al',
       'Dispersion': 'disp', 'PC1': 'pc1'}
need = ['months', 'dead'] + NUM + list(IDX.values()) + ['race']
d = d[d.months > 0].reset_index(drop=True)
inc = d[need].notna().all(axis=1)
print('候选 %d；完整病例 %d（%.1f%%）；未纳入 %d（其中死亡 %d）'
      % (len(d), inc.sum(), 100 * inc.mean(), (~inc).sum(),
         int(d.loc[~inc, 'dead'].sum())))

C = d[inc].reset_index(drop=True)
print('完整病例中 1999-2004 占 %.1f%%，死亡 %d'
      % (100 * C.cycle.isin(['1999-00', '2001-02', '2003-04']).mean(),
         int(C.dead.sum())))


def prep(df):
    DD = pd.get_dummies(df[['race', 'cycle']], columns=['race', 'cycle'],
                        drop_first=True, dtype=float)
    out = pd.concat([df.reset_index(drop=True), DD.reset_index(drop=True)], axis=1)
    cov = NUM + [c for c in DD.columns if c.startswith('race_')] + \
          [c for c in DD.columns if c.startswith('cycle_')]
    out['w'] = out.WTMEC2YR / 8.0
    out['psu'] = pd.factorize(out.cycle.astype(str) + '_' +
                              out.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                              out.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
    return out, cov


def fit(df, cov, v, wt='w'):
    df = df.copy()
    df['z'] = ((df[v] - df[v].mean()) / df[v].std()).clip(-5, 5)
    cols = ['months', 'dead', wt, 'z', 'psu'] + cov
    dat = df[cols].dropna()
    if dat[wt].sum() <= 0:
        return np.nan, np.nan, np.nan, np.nan
    fitdf = dat.drop(columns='psu')          # psu 只用于聚类，不入模
    f = CoxPHFitter().fit(fitdf, 'months', 'dead', weights_col=wt)
    sr = np.asarray(f.compute_residuals(fitdf, 'score'), dtype=float)
    pnames = list(f.params_.index)
    G = pd.DataFrame(sr, columns=pnames).assign(
        psu=dat.psu.values).groupby('psu').sum().values
    bread = f.variance_matrix_.values
    V = bread @ (G.T @ G) @ bread
    j = pnames.index('z')
    b = float(f.params_['z'])
    se = float(np.sqrt(V[j, j]))
    return f.concordance_index_, np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se)


rows = []
# (1) 完整病例
D1, cov1 = prep(C)
for k, v in IDX.items():
    c, hr, lo, hi = fit(D1, cov1, v)
    rows.append(dict(指数=k, 分析='全八周期（现稿）', n=len(D1), 死亡=int(D1.dead.sum()),
                     C指数=c, HR=hr, lo=lo, hi=hi))

# (2) IPW
Z = C[NUM + ['cycle', 'race']].copy()
ZC = pd.get_dummies(Z[['race', 'cycle']], columns=['race', 'cycle'],
                    drop_first=True, dtype=float)
ZZ = pd.concat([Z[NUM].reset_index(drop=True), ZC.reset_index(drop=True)], axis=1)
for c in ZZ.columns:
    if ZZ[c].isna().any():
        ZZ[c] = ZZ[c].fillna(ZZ[c].median())
X = sm.add_constant(ZZ.astype(float))
# 纳入概率在全候选样本上估计
Zall = d[NUM + ['race', 'cycle']].copy()
ZAC = pd.get_dummies(Zall[['race', 'cycle']], columns=['race', 'cycle'],
                     drop_first=True, dtype=float)
ZA = pd.concat([Zall[NUM].reset_index(drop=True), ZAC.reset_index(drop=True)], axis=1)
for c in ZA.columns:
    if c not in X.columns:
        ZA[c] = 0.0
    if ZA[c].isna().any():
        ZA[c] = ZA[c].fillna(ZA[c].median())
ps_all = sm.GLM(inc.astype(int), sm.add_constant(ZA[X.columns[1:]].astype(float)),
                family=sm.families.Binomial()).fit().predict()
D2 = D1.copy()
D2['w_ipw'] = D1.w.values / np.clip(np.asarray(ps_all)[inc.values], 0.05, 0.99)
for k, v in IDX.items():
    c, hr, lo, hi = fit(D2, cov1, v, wt='w_ipw')
    rows.append(dict(指数=k, 分析='IPW', n=len(D2), 死亡=int(D2.dead.sum()),
                     C指数=c, HR=hr, lo=lo, hi=hi))

# (3)(4) 分周期段
for lab, keep in [('仅 2005-2018（CRP 全测）',
                   ['2005-06', '2007-08', '2009-10', '2015-16', '2017-18']),
                  ('仅 1999-2010（含 CRP 子样本）',
                   ['1999-00', '2001-02', '2003-04', '2005-06', '2007-08', '2009-10'])]:
    sub = C[C.cycle.isin(keep)].reset_index(drop=True)
    Ds, covs = prep(sub)
    for k, v in IDX.items():
        c, hr, lo, hi = fit(Ds, covs, v)
        rows.append(dict(指数=k, 分析=lab, n=len(Ds), 死亡=int(Ds.dead.sum()),
                         C指数=c, HR=hr, lo=lo, hi=hi))

R = pd.DataFrame(rows)
print('\n' + R.round(4).to_string(index=False))
R.to_csv(os.path.join(EXT, 'selbias2.csv'), index=False, encoding='utf-8-sig')
print('\n已写出', os.path.join(EXT, 'selbias2.csv'))

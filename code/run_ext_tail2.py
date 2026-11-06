# -*- coding: utf-8 -*-
"""run_ext_tail2：补跑 5-8 段（AL9 / 未周期校正 / 五指数校准 / Table 1）"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from scipy import stats as st

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
EXT = os.path.join(OUT, 'ext')
T10 = 120.0
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al', 'Dispersion': 'disp', 'PC1': 'pc1'}


def wcox(d, cols, event='dead'):
    data = d[['months', event, 'w', 'psu'] + cols].dropna()
    fitdf = data.drop(columns='psu')          # psu 只用于聚类，不能当协变量入模
    f = CoxPHFitter().fit(fitdf, 'months', event, weights_col='w')
    sr = np.asarray(f.compute_residuals(fitdf, 'score'), dtype=float)
    if sr.shape[1] == len(cols) + 1:
        sr = sr[:, 1:]
    G = pd.DataFrame(sr, columns=cols).assign(psu=data.psu.values).groupby('psu').sum().values
    bread = f.variance_matrix_.values
    V = bread @ (G.T @ G) @ bread
    b = float(f.params_[cols[0]])
    return b, float(np.sqrt(V[0, 0])), f


def prep(path):
    r = pd.read_csv(path, encoding='utf-8-sig')
    r['hd_log'] = np.log(r.hd.clip(lower=1e-6))
    r = r.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
    r = r[r.months > 0].reset_index(drop=True)
    DD = pd.get_dummies(r[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True,
                        dtype=float)
    r = pd.concat([r, DD], axis=1)
    cov = NUM + [c for c in DD.columns if c.startswith('race_')] + \
          [c for c in DD.columns if c.startswith('cycle_')]
    r['w'] = r.WTMEC2YR / 8.0
    r['psu'] = pd.factorize(r.cycle.astype(str) + '_' +
                            r.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                            r.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
    return r, cov


d, COV = prep(os.path.join(OUT, 'analysis_dataset_extc.csv'))
for k in IDX.values():
    d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)
d['z_al9'] = ((d.al9 - d.al9.mean()) / d.al9.std()).clip(-5, 5)
print('n=%d 死亡=%d' % (len(d), int(d.dead.sum())))

print('\n=== 5 敏感性：AL 10 项 vs 9 项 ===')
res = []
for nm, v in [('AL10', 'al'), ('AL9', 'al9')]:
    b, se, _ = wcox(d, ['z_' + v] + COV)
    res.append(dict(版本=nm, n=int(d[v].notna().sum()), HR=np.exp(b),
                    lo=np.exp(b - 1.96 * se), hi=np.exp(b + 1.96 * se),
                    p=2 * (1 - st.norm.cdf(abs(b / se)))))
al = pd.DataFrame(res)
al.to_csv(os.path.join(EXT, 'sens_al9.csv'), index=False, encoding='utf-8-sig')
print(al.round(3).to_string(index=False))

print('\n=== 6 敏感性：指数不做周期标准化 ===')
d3, COV3 = prep(os.path.join(OUT, 'analysis_dataset_ext.csv'))
for k in IDX.values():
    d3['z_' + k] = ((d3[k] - d3[k].mean()) / d3[k].std()).clip(-5, 5)
res = []
for name, v in IDX.items():
    b, se, _ = wcox(d3, ['z_' + v] + COV3)
    res.append(dict(指数=name, n=len(d3), HR=np.exp(b), lo=np.exp(b - 1.96 * se),
                    hi=np.exp(b + 1.96 * se), p=2 * (1 - st.norm.cdf(abs(b / se)))))
nc = pd.DataFrame(res)
nc.to_csv(os.path.join(EXT, 'sens_no_cycle_standardisation.csv'), index=False,
          encoding='utf-8-sig')
print(nc.round(3).to_string(index=False))

print('\n=== 7 五指数 10 年校准 ===')
km_c = KaplanMeierFitter().fit(d.months, 1 - d.dead, weights=d.w)
G = np.clip(km_c.predict(np.clip(d.months.values - 1e-6, 1e-6, None)).values, 1e-4, 1.0)
O = (d.w.values * ((d.dead.values == 1) & (d.months.values <= T10)) / G).sum() / d.w.sum()
cal = []
for name, v in IDX.items():
    cols = ['z_' + v] + COV
    b, se, f = wcox(d, cols)
    lp = f.predict_log_partial_hazard(d[cols]).values
    rk = np.clip(1 - f.predict_survival_function(d[cols], times=[T10]).values[0], 1e-8, 1 - 1e-8)
    Em = float((d.w.values * rk).sum() / d.w.sum())
    dd = pd.DataFrame({'months': d.months.values, 'dead': d.dead.values,
                       'w': d.w.values, 'lp': lp})
    fs = CoxPHFitter().fit(dd, 'months', 'dead', weights_col='w')
    sr = np.asarray(fs.compute_residuals(dd, 'score'), dtype=float)
    if sr.shape[1] == 2:
        sr = sr[:, 1]
    Gs = pd.DataFrame(sr.reshape(-1, 1), columns=['lp']).assign(
        psu=d.psu.values).groupby('psu').sum().values
    bread = fs.variance_matrix_.values
    sl = float(fs.params_['lp'])
    sle = float(np.sqrt((bread @ (Gs.T @ Gs) @ bread)[0, 0]))
    dec = np.asarray(pd.qcut(rk, 10, labels=False, duplicates='drop')) + 1
    dev = 0.0
    for k in range(1, int(dec.max()) + 1):
        m = dec == k
        g = d[m]
        obs = 1 - float(KaplanMeierFitter().fit(g.months, g.dead, weights=g.w).predict(T10))
        pv = float((d.w.values[m] * rk[m]).sum() / d.w.values[m].sum())
        dev += float(d.w.values[m].sum() / d.w.sum()) * abs(obs - pv)
    cal.append(dict(指数=name, 观测10年=O, 预测均值=Em, OE=O / Em, 斜率=sl,
                    斜率lo=sl - 1.96 * sle, 斜率hi=sl + 1.96 * sle,
                    十分位加权绝对偏差=dev))
cal = pd.DataFrame(cal)
cal.to_csv(os.path.join(EXT, 'calibration_all_indices.csv'), index=False, encoding='utf-8-sig')
print(cal.round(3).to_string(index=False))

print('\n=== 8 Table 1：按 PhenoAge 加速五分位 ===')
d['pa_q'] = pd.qcut(d.pa_accel, 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
rows = []
for k, g in d.groupby('pa_q', observed=True):
    rows.append(dict(组=k, n=len(g), 年龄=g.age.mean(), 男性=100 * g.male.mean(),
                     BMI=g.bmi.mean(), 现吸烟=100 * g.smoke.mean(),
                     教育=g.edu.mean(), PIR=g.pir.mean(),
                     PhenoAge=g.phenoage.mean(), 离散度=g.disp.mean(), HD=g.hd.mean(),
                     AL=g.al.mean(), PC1=g.pc1.mean(), 死亡=100 * g.dead.mean()))
t1 = pd.DataFrame(rows)
t1.to_csv(os.path.join(EXT, 'table1_by_phenoage_quintile.csv'), index=False,
          encoding='utf-8-sig')
print(t1.round(2).to_string(index=False))

print('\n=== 9 敏感性：年龄 ≤79（规避 1999-2006 顶码85 / 2007-2018 顶码80 不一致）===')
d79 = d[d.age <= 79].reset_index(drop=True)
for k in IDX.values():
    d79['z_' + k] = ((d79[k] - d79[k].mean()) / d79[k].std()).clip(-5, 5)
res = []
for name, v in IDX.items():
    b, se, f = wcox(d79, ['z_' + v] + COV)
    res.append(dict(指数=name, n=len(d79), 死亡=int(d79.dead.sum()),
                    C指数=f.concordance_index_, HR=np.exp(b),
                    lo=np.exp(b - 1.96 * se), hi=np.exp(b + 1.96 * se),
                    p=2 * (1 - st.norm.cdf(abs(b / se)))))
a79 = pd.DataFrame(res)
a79.to_csv(os.path.join(EXT, 'sens_age79.csv'), index=False, encoding='utf-8-sig')
print(a79.round(4).to_string(index=False))
print('Δ C 指数（vs PhenoAge）：')
for _, r in a79.iterrows():
    print('  %-11s %+.4f' % (r.指数, r.C指数 - a79.loc[0, 'C指数']))
print('\n完成')

# -*- coding: utf-8 -*-
"""
run_ext_extra：补齐 + 新增有意义分析
1 结构复现（五域 PCA / Tucker φ）
2 暴露谱
3 比例风险假设（Schoenfeld 残差 vs 时间的相关）
4 landmark：排除前 24 个月死亡（反向因果）
5 AL9 敏感性（去掉 BMI 项，保住全部样本）
6 未做周期标准化的对照
7 五个指数全部校准
8 Table 1（按 PhenoAge 加速五分位）
"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from scipy import stats as st

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
EXT = os.path.join(OUT, 'ext')
CACHE = r'D:\最新智研\trae工作文件夹\SJK\nhanes_cache'
os.makedirs(EXT, exist_ok=True)
T10 = 120.0
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al', 'Dispersion': 'disp', 'PC1': 'pc1'}


def prep(df, idxmap=IDX):
    d = df.copy()
    if 'hd_log' not in d.columns:
        d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
    d = d.dropna(subset=['months', 'dead'] + NUM + list(idxmap.values()) + ['race'])
    d = d[d.months > 0].reset_index(drop=True)
    dd = pd.get_dummies(d[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True,
                        dtype=float)
    d = pd.concat([d.drop(columns=['race', 'cycle']), dd], axis=1)
    COV = NUM + [c for c in dd.columns if c.startswith('race_')] + \
          [c for c in dd.columns if c.startswith('cycle_')]
    d['w'] = d.WTMEC2YR / 8.0
    d['psu'] = pd.factorize(d.cycle_c.astype(str) if 'cycle_c' in d.columns else
                            d.index.astype(str))[0]
    d['psu'] = pd.factorize(d['_cyc'] .astype(str) if '_cyc' in d.columns else
                            d.index.astype(str))[0]
    for k in idxmap.values():
        d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)
    return d, COV


def load_psu(d, raw):
    key = raw['cycle'].astype(str) + '_' + raw['SDMVSTRA'].fillna(-1).astype(int).astype(str) \
          + '_' + raw['SDMVPSU'].fillna(-1).astype(int).astype(str)
    return pd.factorize(key.values)[0]


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


raw = pd.read_csv(os.path.join(OUT, 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
raw['hd_log'] = np.log(raw.hd.clip(lower=1e-6))
d = raw.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d = d[d.months > 0].reset_index(drop=True)
DD = pd.get_dummies(d[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True, dtype=float)
d = pd.concat([d.reset_index(drop=True), DD.reset_index(drop=True)], axis=1)
RA = [c for c in DD.columns if c.startswith('race_')]
CY = [c for c in DD.columns if c.startswith('cycle_')]
COV = NUM + RA + CY
d['w'] = d.WTMEC2YR / 8.0
d['psu'] = pd.factorize(d.cycle.astype(str) + '_' +
                        d.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                        d.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
for k in IDX.values():
    d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)
print('分析样本 n=%d 死亡=%d' % (len(d), int(d.dead.sum())))

# ---------- 1 结构 ----------
DOMS = {'肝脏': ['LBXSAL', 'LBXSTB', 'LBXSAPSI', 'LBXSGTSI', 'LBXSASSI'],
        '肾脏': ['LBXSCR', 'LBXSBU', 'LBXSUA'],
        '代谢': ['LBXSGL', 'LBXGH', 'tg', 'LBDHDD', 'LBXTC'],
        '血液': ['LBXHGB', 'LBXMCVSI', 'LBXRDW', 'LBXPLTSI'],
        '炎症': ['LBXWBCSI', 'LBXLYPCT', 'crp']}
LOG = {'LBXSTB', 'LBXSGTSI', 'LBXSASSI', 'LBXSCR', 'LBXSUA', 'tg', 'crp'}
cyc_d = pd.get_dummies(d.cycle, prefix='cy', drop_first=True, dtype=float)
z = {}
for cs in DOMS.values():
    for c in cs:
        v = d[c].astype(float)
        if c in LOG:
            v = np.log(v.where(v > 0))
        ok = v.notna()
        X = np.column_stack([np.ones(ok.sum()), d.loc[ok, 'age'], d.loc[ok, 'age'] ** 2,
                             d.loc[ok, 'male'], cyc_d.loc[ok].values])
        y = v[ok].values
        bt, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = pd.Series(np.nan, index=d.index)
        r.loc[ok] = (y - X @ bt) / (y - X @ bt).std()
        z[c] = r.clip(-4, 4)
Z = pd.DataFrame(z)
F = pd.DataFrame(index=d.index)
for dm, cs in DOMS.items():
    M = Z[cs]
    F[dm] = M.mean(axis=1).where(M.notna().sum(axis=1) >= max(2, len(cs) // 2))

grp = {'男性': d.male == 1, '女性': d.male == 0,
       '1999-2004': d.cycle.isin(['1999-00', '2001-02', '2003-04']),
       '2005-2010': d.cycle.isin(['2005-06', '2007-08', '2009-10']),
       '2015-2018': d.cycle.isin(['2015-16', '2017-18'])}
Ls, rows = {}, []
for k, m in grp.items():
    Mx = F[m].dropna()
    Zs = ((Mx - Mx.mean()) / Mx.std()).values
    u, s, vt = np.linalg.svd(Zs - Zs.mean(0), full_matrices=False)
    L = pd.Series(vt[0] * s[0], index=list(DOMS))
    if L.sum() < 0:
        L = -L
    Ls[k] = L
    for dm in L.index:
        rows.append(dict(分组=k, 域=dm, 载荷=float(L[dm]),
                         PC1解释率=float(s[0] ** 2 / (s ** 2).sum()), n=len(Mx)))
    print('  %-10s n=%5d PC1 %.1f%% %s' % (k, len(Mx), 100 * s[0] ** 2 / (s ** 2).sum(),
                                           L.round(2).to_dict()))
tk = lambda a, b: float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
print()
for a, b in [('男性', '女性'), ('1999-2004', '2005-2010'), ('2005-2010', '2015-2018'),
             ('1999-2004', '2015-2018')]:
    v = tk(Ls[a].values, Ls[b].values)
    rows.append(dict(分组='%s vs %s' % (a, b), 域='Tucker φ', 载荷=v, PC1解释率=np.nan, n=np.nan))
    print('  Tucker φ（%s vs %s）= %.3f' % (a, b, v))
pd.DataFrame(rows).to_csv(os.path.join(EXT, 'tucker.csv'), index=False, encoding='utf-8-sig')

# ---------- 2 暴露谱 ----------
pa = []
for c, lab in {'D': '2005-06', 'E': '2007-08', 'F': '2009-10', 'I': '2015-16',
               'J': '2017-18'}.items():
    p = os.path.join(CACHE, 'PAQ_%s.xpt' % c)
    if not os.path.exists(p):
        continue
    x = pd.read_sas(p, format='xport')
    cols = [v for v in ['PAQ650', 'PAQ665'] if v in x.columns]
    if not cols:
        continue
    y = x[['SEQN'] + cols].copy()
    y['active'] = ((y.get('PAQ650') == 1) | (y.get('PAQ665') == 1)).astype(float)
    y.loc[y[cols].isna().all(axis=1), 'active'] = np.nan
    y['cycle'] = lab
    pa.append(y[['SEQN', 'cycle', 'active']])
d2 = d.merge(pd.concat(pa, ignore_index=True), on=['SEQN', 'cycle'], how='left')

EXPO = {'BMI': 'bmi', 'Current smoking': 'smoke', 'Physical activity': 'active',
        'Education': 'edu', 'Income-to-poverty ratio': 'pir'}
IDX9 = dict(IDX, AL='al9')
sp = []
for lab, v in EXPO.items():
    dd = d2.dropna(subset=[v]).copy()
    covs = [c for c in COV if c != v]
    X0 = dd[covs].values.astype(float)
    for nm, iv in IDX9.items():
        y = dd[iv].astype(float)
        y = ((y - y.mean()) / y.std()).values
        Xa = np.column_stack([dd[v].values.astype(float), X0])
        ok = np.isfinite(y) & np.isfinite(Xa).all(1)
        Xa, yy = Xa[ok], y[ok]
        A = np.column_stack([np.ones(len(Xa)), Xa])
        beta, *_ = np.linalg.lstsq(A, yy, rcond=None)
        r = yy - A @ beta
        df_ = len(yy) - A.shape[1]
        se = np.sqrt((r @ r / df_) * np.linalg.pinv(A.T @ A)[1, 1])
        r2f = 1 - r @ r / ((yy - yy.mean()) ** 2).sum()
        Ar = np.column_stack([np.ones(len(Xa)), Xa[:, 1:]])
        b0, *_ = np.linalg.lstsq(Ar, yy, rcond=None)
        r0 = yy - Ar @ b0
        r2r = 1 - r0 @ r0 / ((yy - yy.mean()) ** 2).sum()
        sp.append(dict(exposure=lab, index=nm, beta=beta[1], lo=beta[1] - 1.96 * se,
                       hi=beta[1] + 1.96 * se, p=2 * (1 - st.t.cdf(abs(beta[1] / se), df_)),
                       partial_R2=max(r2f - r2r, 0), n=len(yy)))
sp = pd.DataFrame(sp)
sp.to_csv(os.path.join(EXT, 'response_spectrum.csv'), index=False, encoding='utf-8-sig')
print('\n=== 响应谱 β ===')
print(sp.pivot(index='exposure', columns='index', values='beta').round(3).to_string())

# ---------- 3 比例风险假设 ----------
print('\n=== 比例风险假设（Schoenfeld 残差与 log 时间的相关）===')
ph = []
for name, v in IDX.items():
    cols = COV + ['z_' + v]
    f = CoxPHFitter().fit(d[['months', 'dead'] + cols], 'months', 'dead')
    sch = f.compute_residuals(d[['months', 'dead'] + cols], 'scaled_schoenfeld')
    lt = np.log(d.months.values[d.dead.values == 1])   # Schoenfeld 只在事件行有定义
    for c in cols:
        r, p = st.pearsonr(sch[c].values, lt)
        ph.append(dict(指数=name, 变量=c, r=r, p=p))
ph = pd.DataFrame(ph)
ph.to_csv(os.path.join(EXT, 'ph_assumption.csv'), index=False, encoding='utf-8-sig')
key = ph[ph.变量.str.startswith('z_')]
print(key.round(3).to_string(index=False))
print('全部协变量中 |r|>0.10 且 p<0.05 的比例：%.1f%%'
      % (100 * ((ph.r.abs() > 0.10) & (ph.p < 0.05)).mean()))

# ---------- 4 landmark ----------
print('\n=== landmark：排除前 24 个月死亡 ===')
lm = d[d.months > 24].copy()
lm['months'] = lm.months - 24
lm = lm.reset_index(drop=True)
for k in IDX.values():
    lm['z_' + k] = ((lm[k] - lm[k].mean()) / lm[k].std()).clip(-5, 5)
lm['psu'] = pd.factorize(lm.cycle.astype(str) + '_' +
                         lm.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                         lm.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
res = []
for name, v in IDX.items():
    b, se, f = wcox(lm, ['z_' + v] + COV)
    res.append(dict(指数=name, n=len(lm), 事件=int(lm.dead.sum()), HR=np.exp(b),
                    lo=np.exp(b - 1.96 * se), hi=np.exp(b + 1.96 * se),
                    p=2 * (1 - st.norm.cdf(abs(b / se)))))
lm_res = pd.DataFrame(res)
lm_res.to_csv(os.path.join(EXT, 'landmark24.csv'), index=False, encoding='utf-8-sig')
print(lm_res.round(3).to_string(index=False))

# ---------- 5 AL9 ----------
print('\n=== 敏感性：AL 用 9 项（去 BMI）===')
res = []
for nm, v in [('AL10', 'al'), ('AL9', 'al9')]:
    d['z_' + v] = ((d[v] - d[v].mean()) / d[v].std()).clip(-5, 5)
    b, se, _ = wcox(d, ['z_' + v] + COV)
    res.append(dict(版本=nm, HR=np.exp(b), lo=np.exp(b - 1.96 * se),
                    hi=np.exp(b + 1.96 * se), p=2 * (1 - st.norm.cdf(abs(b / se)))))
al_res = pd.DataFrame(res)
al_res.to_csv(os.path.join(EXT, 'sens_al9.csv'), index=False, encoding='utf-8-sig')
print(al_res.round(3).to_string(index=False))

# ---------- 6 未做周期标准化 ----------
print('\n=== 敏感性：指数不做周期标准化（仅年龄+性别）===')
raw2 = pd.read_csv(os.path.join(OUT, 'analysis_dataset_ext.csv'), encoding='utf-8-sig')
raw2['hd_log'] = np.log(raw2.hd.clip(lower=1e-6))
d3 = raw2.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d3 = d3[d3.months > 0].reset_index(drop=True)
DD3 = pd.get_dummies(d3[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True,
                     dtype=float)
d3 = pd.concat([d3.reset_index(drop=True), DD3.reset_index(drop=True)], axis=1)
COV3 = NUM + [c for c in DD3.columns if c.startswith('race_')] + \
       [c for c in DD3.columns if c.startswith('cycle_')]
d3['w'] = d3.WTMEC2YR / 8.0
d3['psu'] = pd.factorize(d3.cycle.astype(str) + '_' +
                         d3.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                         d3.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
for k in IDX.values():
    d3['z_' + k] = ((d3[k] - d3[k].mean()) / d3[k].std()).clip(-5, 5)
res = []
for name, v in IDX.items():
    b, se, _ = wcox(d3, ['z_' + v] + COV3)
    res.append(dict(指数=name, n=len(d3), HR=np.exp(b), lo=np.exp(b - 1.96 * se),
                    hi=np.exp(b + 1.96 * se), p=2 * (1 - st.norm.cdf(abs(b / se)))))
nocyc = pd.DataFrame(res)
nocyc.to_csv(os.path.join(EXT, 'sens_no_cycle_standardisation.csv'), index=False,
             encoding='utf-8-sig')
print(nocyc.round(3).to_string(index=False))

# ---------- 7 五指数校准 ----------
print('\n=== 五个指数的 10 年校准 ===')
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
        dev += float(d.w.values[m].sum() / d.w.sum()) * abs(obs - float(
            (d.w.values[m] * rk[m]).sum() / d.w.values[m].sum()))
    cal.append(dict(指数=name, 观测10年=O, 预测均值=Em, OE=O / Em, 斜率=sl,
                    斜率lo=sl - 1.96 * sle, 斜率hi=sl + 1.96 * sle,
                    十分位加权绝对偏差=dev))
cal = pd.DataFrame(cal)
cal.to_csv(os.path.join(EXT, 'calibration_all_indices.csv'), index=False, encoding='utf-8-sig')
print(cal.round(3).to_string(index=False))

# ---------- 8 Table 1 ----------
print('\n=== Table 1：按 PhenoAge 加速五分位 ===')
d['pa_q'] = pd.qcut(d.pa_accel, 5, labels=['Q1(最年轻)', 'Q2', 'Q3', 'Q4', 'Q5(最老)'])
rows = []
for k, g in d.groupby('pa_q', observed=True):
    rows.append(dict(组=k, n=len(g),
                     年龄=g.age.mean(), 男性=100 * g.male.mean(),
                     BMI=g.bmi.mean(), 现吸烟=100 * g.smoke.mean(),
                     教育=g.edu.mean(), PIR=g.pir.mean(),
                     PhenoAge=g.phenoage.mean(), 离散度=g.disp.mean(),
                     HD=g.hd.mean(), AL=g.al.mean(), PC1=g.pc1.mean(),
                     死亡=100 * g.dead.mean()))
t1 = pd.DataFrame(rows)
t1.to_csv(os.path.join(EXT, 'table1_by_phenoage_quintile.csv'), index=False,
          encoding='utf-8-sig')
print(t1.round(2).to_string(index=False))
print('\n全部完成 →', EXT)

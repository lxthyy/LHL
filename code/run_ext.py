# -*- coding: utf-8 -*-
"""run_ext：八周期（1999-2018）主分析"""
import os
import json
import hashlib
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.utils import concordance_index
from scipy import stats as st

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
EXT = os.path.join(OUT, 'ext')
CACHE = r'D:\最新智研\trae工作文件夹\SJK\nhanes_cache'
os.makedirs(EXT, exist_ok=True)
rng = np.random.default_rng(20261028)
T10 = 120.0

d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al', 'Dispersion': 'disp', 'PC1': 'pc1'}
d = d.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d = d[d.months > 0].reset_index(drop=True)
d['cycle_c'] = d.cycle
D = pd.get_dummies(d[['race', 'cycle_c']], columns=['race', 'cycle_c'], drop_first=True,
                   dtype=float)
for c in D.columns:
    d[c] = D[c].values
RA = [c for c in D.columns if c.startswith('race_')]
CY = [c for c in D.columns if c.startswith('cycle_c_')]
COV = NUM + RA + CY
d['w'] = d.WTMEC2YR / 8.0
d['psu'] = pd.factorize(d.cycle.astype(str) + '_' +
                        d.SDMVSTRA.fillna(-1).astype(int).astype(str) + '_' +
                        d.SDMVPSU.fillna(-1).astype(int).astype(str))[0]
for k in IDX.values():
    d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)
T, E, W = d.months.values, d.dead.values.astype(int), d.w.values
print('n=%d 死亡=%d 心血管=%d 肿瘤=%d 呼吸=%d 协变量=%d（周期 %d）'
      % (len(d), E.sum(), d.evt_cvd.sum(), d.evt_can.sum(), d.evt_resp.sum(), len(COV), len(CY)))


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


main, wt = [], []
for name, v in IDX.items():
    f = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_' + v]], 'months', 'dead')
    b, se = f.params_['z_' + v], f.standard_errors_['z_' + v]
    main.append(dict(指数=name, C指数=f.concordance_index_, HR=np.exp(b),
                     lo=np.exp(b - 1.96 * se), hi=np.exp(b + 1.96 * se),
                     p=f.summary.loc['z_' + v, 'p']))
    b2, s2, _ = wcox(['z_' + v] + COV)
    wt.append(dict(指数=name, HR_w=np.exp(b2), lo=np.exp(b2 - 1.96 * s2),
                   hi=np.exp(b2 + 1.96 * s2), p=2 * (1 - st.norm.cdf(abs(b2 / s2)))))
pd.DataFrame(main).to_csv(os.path.join(EXT, 'cindex_hr.csv'), index=False, encoding='utf-8-sig')
pd.DataFrame(wt).to_csv(os.path.join(EXT, 'weighted_hr.csv'), index=False, encoding='utf-8-sig')
print('\n=== C 指数（未加权）===')
print(pd.DataFrame(main).round(4).to_string(index=False))
print('\n=== 加权 + PSU 聚类 ===')
print(pd.DataFrame(wt).round(4).to_string(index=False))

cs = []
# 2015-2018 周期官方仅公开心脏病与肿瘤两类死因（NCHS 2019 公共版 LMF 文件说明），
# 呼吸死因在该两周期结构性缺失、心血管口径不含卒中 → 死因别分析限定 1999-2014
C6 = ['1999-00', '2001-02', '2003-04', '2005-06', '2007-08', '2009-10']
d6 = d[d.cycle.isin(C6)].reset_index(drop=True)
DD6 = pd.get_dummies(d6[['race', 'cycle']], columns=['race', 'cycle'], drop_first=True,
                     dtype=float)
for c in DD6.columns:
    d6[c] = DD6[c].values
COV6 = NUM + [c for c in DD6.columns if c.startswith('race_')] + \
       [c for c in DD6.columns if c.startswith('cycle_')]
print('\n死因别分析窗口 1999-2014：n=%d 死亡=%d（协变量 %d）'
      % (len(d6), int(d6.dead.sum()), len(COV6)))
for ev, nn in [('evt_cvd', '心血管'), ('evt_can', '肿瘤'), ('evt_resp', '呼吸')]:
    for name, v in IDX.items():
        b, se, _ = wcox(['z_' + v] + COV6, event=ev, df=d6)
        cs.append(dict(结局=nn, 指数=name, HR=np.exp(b), lo=np.exp(b - 1.96 * se),
                       hi=np.exp(b + 1.96 * se), p=2 * (1 - st.norm.cdf(abs(b / se))),
                       事件=int(d6[ev].sum()), n=len(d6), 窗口='1999-2014'))
cs = pd.DataFrame(cs)
cs.to_csv(os.path.join(EXT, 'cause_specific.csv'), index=False, encoding='utf-8-sig')
print('\n=== 死因别 HR（加权）===')
print(cs.pivot(index='指数', columns='结局', values='HR').round(3).to_string())
print('\np：')
print(cs.pivot(index='指数', columns='结局', values='p').round(4).to_string())

risk = {}
for name, v in IDX.items():
    f = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_' + v]], 'months', 'dead')
    risk[name] = f.predict_partial_hazard(d[COV + ['z_' + v]]).values
names = list(IDX)
DCF = os.path.join(EXT, '_dc.npy')
if os.path.exists(DCF):
    dc = np.load(DCF, allow_pickle=True).item()
    print('\n(复用 bootstrap)')
else:
    B, n = 300, len(d)
    dc = {'%s − %s' % (a, b): [] for i, a in enumerate(names) for b in names[i + 1:]}
    for _ in range(B):
        idx = rng.integers(0, n, n)
        cc = {k: concordance_index(T[idx], -v[idx], E[idx]) for k, v in risk.items()}
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                dc['%s − %s' % (a, b)].append(cc[a] - cc[b])
    np.save(DCF, np.array(dc, dtype=object), allow_pickle=True)
M = 0.01
eq = pd.DataFrame([dict(比较=k, dC=float(np.mean(v)), lo=float(np.percentile(v, 2.5)),
                        hi=float(np.percentile(v, 97.5)),
                        等价='是' if (np.percentile(v, 2.5) > -M and np.percentile(v, 97.5) < M) else '否')
                   for k, v in dc.items()])
eq.to_csv(os.path.join(EXT, 'equivalence.csv'), index=False, encoding='utf-8-sig')
print('\n=== 等价性（±0.01）===')
print(eq.round(4).to_string(index=False))

f_pa = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_pa_accel']], 'months', 'dead')
f_pd = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_pa_accel', 'z_disp']], 'months', 'dead')
f_pp = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_pa_accel', 'z_pc1']], 'months', 'dead')
sv = lambda f, df: f.predict_survival_function(df, times=[T10]).iloc[0].values
r_pa, r_pd = 1 - sv(f_pa, d), 1 - sv(f_pd, d)
ev10 = (d.dead.values == 1) & (d.months.values <= T10)
ne10 = (d.dead.values == 0) & (d.months.values > T10)
up, dn = r_pd > r_pa, r_pd < r_pa
nri = (up[ev10].mean() - dn[ev10].mean()) + (dn[ne10].mean() - up[ne10].mean())
idi = (r_pd[ev10].mean() - r_pd[~ev10].mean()) - (r_pa[ev10].mean() - r_pa[~ev10].mean())
inc = pd.DataFrame([dict(模型='PhenoAge', C=f_pa.concordance_index_),
                    dict(模型='PhenoAge+离散度', C=f_pd.concordance_index_),
                    dict(模型='PhenoAge+PC1', C=f_pp.concordance_index_),
                    dict(模型='ΔC(+离散度)', C=f_pd.concordance_index_ - f_pa.concordance_index_),
                    dict(模型='NRI(+离散度)', C=nri), dict(模型='IDI(+离散度)', C=idi)])
inc.to_csv(os.path.join(EXT, 'incremental.csv'), index=False, encoding='utf-8-sig')
print('\n=== 增量（10 年：事件 %d / 非事件 %d）===' % (ev10.sum(), ne10.sum()))
print(inc.round(4).to_string(index=False))
print('联合模型 离散度 HR=%.3f (%.3f–%.3f) p=%.3g'
      % (np.exp(f_pd.params_['z_disp']),
         np.exp(f_pd.params_['z_disp'] - 1.96 * f_pd.standard_errors_['z_disp']),
         np.exp(f_pd.params_['z_disp'] + 1.96 * f_pd.standard_errors_['z_disp']),
         f_pd.summary.loc['z_disp', 'p']))

P4 = ['PhenoAge', 'HD', 'AL', 'PC1']
rr = []
for i, a in enumerate(P4):
    for b in P4[i + 1:]:
        qa = np.asarray(pd.qcut(risk[a], 5, labels=False, duplicates='drop'))
        qb = np.asarray(pd.qcut(risk[b], 5, labels=False, duplicates='drop'))
        rr.append(dict(对比='%s vs %s' % (a, b), 换档比例=100 * float((qa != qb).mean()),
                       相差2档以上=100 * float((np.abs(qa - qb) >= 2).mean())))
cap = []
for name, v in risk.items():
    top = np.asarray(pd.Series(v) >= np.quantile(v, 0.9))
    cap.append(dict(指数=name, 标记人数=int(top.sum()),
                    捕获率=100 * float(((d.dead == 1).values & top).sum() / (d.dead == 1).sum()),
                    标记内死亡率=100 * float(d.dead.values[top].mean())))
pd.DataFrame(rr).to_csv(os.path.join(EXT, 'reclass.csv'), index=False, encoding='utf-8-sig')
pd.DataFrame(cap).to_csv(os.path.join(EXT, 'capture10.csv'), index=False, encoding='utf-8-sig')
print('\n=== 五分位重分类 ===')
print(pd.DataFrame(rr).round(2).to_string(index=False))
print('\n=== top10% 捕获 ===')
print(pd.DataFrame(cap).round(2).to_string(index=False))

O_km = 1 - float(KaplanMeierFitter().fit(T, E, weights=W).predict(T10))
km_c = KaplanMeierFitter().fit(T, 1 - E, weights=W)
G = np.clip(km_c.predict(np.clip(T - 1e-6, 1e-6, None)).values, 1e-4, 1.0)
O_ip = (W * ((E == 1) & (T <= T10)) / G).sum() / W.sum()


def slope_cox(lp):
    dd = pd.DataFrame({'months': T, 'dead': E, 'w': W, 'lp': lp})
    f = CoxPHFitter().fit(dd, 'months', 'dead', weights_col='w')
    sr = np.asarray(f.compute_residuals(dd, 'score'), dtype=float)
    if sr.shape[1] == 2:
        sr = sr[:, 1]
    Gs = pd.DataFrame(sr.reshape(-1, 1), columns=['lp']).assign(
        psu=d.psu.values).groupby('psu').sum().values
    bread = f.variance_matrix_.values
    return float(f.params_['lp']), float(np.sqrt((bread @ (Gs.T @ Gs) @ bread)[0, 0]))


cal, decs = [], []
for lab, cols in [('PhenoAge', ['z_pa_accel']), ('PhenoAge+disp', ['z_pa_accel', 'z_disp'])]:
    _, _, f = wcox(cols + COV)
    lp = f.predict_log_partial_hazard(d[cols + COV]).values
    rk = np.clip(1 - f.predict_survival_function(d[cols + COV], times=[T10]).values[0],
                 1e-8, 1 - 1e-8)
    Em = float((W * rk).sum() / W.sum())
    s, sse = slope_cox(lp)
    dec = np.asarray(pd.qcut(rk, 10, labels=False, duplicates='drop')) + 1
    for k in range(1, int(dec.max()) + 1):
        m = dec == k
        g = d[m]
        pv = float((W[m] * rk[m]).sum() / W[m].sum())
        obs = 1 - float(KaplanMeierFitter().fit(g.months, g.dead, weights=g.w).predict(T10))
        decs.append(dict(模型=lab, 十分位=k, n=int(m.sum()),
                         加权占比=float(W[m].sum() / W.sum()), 预测=pv, 观察=obs, 差值=obs - pv))
    cal.append(dict(模型=lab, 观测_KM=O_km, 观测_IPCW=O_ip, 预测均值=Em, OE_KM=O_km / Em,
                    OE_IPCW=O_ip / Em, 斜率=s, 斜率SE=sse, 斜率lo=s - 1.96 * sse,
                    斜率hi=s + 1.96 * sse))
pd.DataFrame(cal).to_csv(os.path.join(EXT, 'calibration.csv'), index=False, encoding='utf-8-sig')
pd.DataFrame(decs).to_csv(os.path.join(EXT, 'calibration_deciles.csv'), index=False,
                          encoding='utf-8-sig')
print('\n=== 校准 ===')
print(pd.DataFrame(cal).round(3).T.to_string())

nb = []
we = np.where(T <= T10, 1 / G, 0.0)
wc = np.where(T > T10, 1 / max(float(km_c.predict(T10)), 0.01), 0.0)
for pt in [0.05, 0.10, 0.15, 0.20, 0.30]:
    for lab, cols in [('PhenoAge', ['z_pa_accel']), ('PhenoAge+disp', ['z_pa_accel', 'z_disp'])]:
        f = CoxPHFitter().fit(d[['months', 'dead', 'w'] + cols + COV], 'months', 'dead',
                              weights_col='w')
        rk = 1 - f.predict_survival_function(d[cols + COV], times=[T10]).values[0]
        flag = rk >= pt
        tp = (we * ((E == 1) & (T <= T10) & flag)).sum()
        fp = (wc * ((T > T10) & flag)).sum()
        nb.append(dict(阈值=pt, 模型=lab, 净收益=(tp - fp * pt / (1 - pt)) / len(d) * 1000))
    tp = (we * ((E == 1) & (T <= T10))).sum()
    fp = (wc * (T > T10)).sum()
    nb.append(dict(阈值=pt, 模型='全部干预', 净收益=(tp - fp * pt / (1 - pt)) / len(d) * 1000))
nb = pd.DataFrame(nb)
nb.to_csv(os.path.join(EXT, 'dca.csv'), index=False, encoding='utf-8-sig')
print('\n=== 净收益/1000 人/10 年 ===')
print(nb.pivot(index='阈值', columns='模型', values='净收益').round(2).to_string())

# 五域 PCA / Tucker φ 与暴露谱已由 run_ext_extra.py 统一计算（写入 tucker.csv、
# response_spectrum.csv）。此处原有副本依赖 dom_* 列，而 build_ext_cyc 后不再保留该列，
# 会抛 KeyError，故移除，避免重复且失效的计算。

man = {'generated': pd.Timestamp.now().isoformat(), 'n': int(len(d)), 'deaths': int(E.sum()),
       'cvd': int(d.evt_cvd.sum()), 'cancer': int(d.evt_can.sum()),
       'resp': int(d.evt_resp.sum()), 'cycles': sorted(d.cycle.unique().tolist()),
       'covariates': COV, 'weight': 'WTMEC2YR/8（1999-2002 已折算为2年等价）',
       'cluster': 'factorize(cycle, SDMVSTRA, SDMVPSU)',
       'index_standardisation': '周期内残差化（1+年龄+年龄²+男性+周期哑变量），缩尾±4SD',
       'phenoage': 'albumin g/L; creatinine umol/L; glucose mmol/L; CRP mg/dL; t=120, gamma=0.0076927',
       'files': {}}
for f in sorted(os.listdir(EXT)):
    if f.endswith('.csv'):
        man['files'][f] = hashlib.sha256(open(os.path.join(EXT, f), 'rb').read()).hexdigest()[:16]
json.dump(man, open(os.path.join(EXT, 'run_manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('\n完成 →', EXT)

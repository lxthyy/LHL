# -*- coding: utf-8 -*-
"""
加强分析 3（重写）：时间依赖判别 + 竞争风险累计发生率
------------------------------------------------------------------
(1) 时间依赖 C 指数：随访在第 5 年、第 10 年行政截尾，给出各指数的 C 与两两 ΔC。
(2) 竞争风险：自行实现 Aalen–Johansen（支持设计权重、天然处理时间并列），
    给出 10 年累计发生率，五个指数 Q5 vs Q1，三种死因，其余死因为竞争事件。

输出到 结果表\\加强\\，不改动任何既有结果表。
"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
OUTD = os.path.join(P, '结果表', '加强')
os.makedirs(OUTD, exist_ok=True)

d = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'),
                encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al',
       'Dispersion': 'disp', 'PC1': 'pc1'}
d = d.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d = d[d.months > 0].reset_index(drop=True)
Dm = pd.get_dummies(d[['race', 'cycle']], columns=['race', 'cycle'],
                    drop_first=True, dtype=float)
for c in Dm.columns:
    d[c] = Dm[c].values
COV = NUM + [c for c in Dm.columns if c.startswith(('race_', 'cycle_'))]
for k in IDX.values():
    d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)
print('分析集 n=%d 死亡=%d' % (len(d), int(d.dead.sum())))

risk = {}
for nm, v in IDX.items():
    f = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_' + v]], 'months', 'dead')
    risk[nm] = f.predict_partial_hazard(d[COV + ['z_' + v]]).values

t_all, e_all = d.months.values, d.dead.values.astype(int)
names = list(IDX)
pairs = ['%s − %s' % (a, b) for i, a in enumerate(names) for b in names[i + 1:]]

# ---------- (1) 时间依赖 C 与 ΔC ----------
rows_c, rows_d = [], []
for horizon in (60.0, 120.0, None):
    if horizon is None:
        t, e, label = t_all, e_all, '全程'
    else:
        e = np.where(t_all <= horizon, e_all, 0)
        t = np.minimum(t_all, horizon)
        label = '%d 年' % (horizon / 12)
    cc = {nm: concordance_index(t, -risk[nm], e) for nm in names}
    for nm in names:
        rows_c.append(dict(horizon=label, index=nm, C=cc[nm]))
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            rows_d.append(dict(horizon=label, pair='%s − %s' % (a, b),
                               dC=cc[a] - cc[b]))
C = pd.DataFrame(rows_c).pivot(index='index', columns='horizon', values='C')
C = C[['5 年', '10 年', '全程']].round(4)
C.to_csv(os.path.join(OUTD, 'time_dependent_cindex.csv'), encoding='utf-8-sig')
print('\n=== 时间依赖 C 指数 ===')
print(C.to_string())
print('\nC 指数极差：5 年 %.4f  10 年 %.4f  全程 %.4f'
      % (C['5 年'].max() - C['5 年'].min(),
         C['10 年'].max() - C['10 年'].min(),
         C['全程'].max() - C['全程'].min()))

DC = pd.DataFrame(rows_d).pivot(index='pair', columns='horizon', values='dC')
DC = DC[['5 年', '10 年', '全程']].round(4)
DC['超过0.01_5年'] = DC['5 年'].abs() >= 0.01
DC['超过0.01_全程'] = DC['全程'].abs() >= 0.01
DC.to_csv(os.path.join(OUTD, 'time_dependent_dC.csv'), encoding='utf-8-sig')
print('\n=== 两两 ΔC（点估计）与是否超出 ±0.01 ===')
print(DC.to_string())


# ---------- (2) Aalen–Johansen（自实现，支持权重） ----------
def aj_cif(t, code, w, tau=120.0):
    """Aalen–Johansen 累计发生率（向量化）。code: 0 删失, 1 目标, 2 竞争。"""
    o = np.argsort(t, kind='mergesort')
    t, code, w = t[o], code[o], w[o]
    uniq, start = np.unique(t, return_index=True)
    keep = uniq <= tau
    if not keep.any():
        return 0.0
    start, uniq = start[keep], uniq[keep]
    w1 = w * (code == 1)
    w2 = w * (code == 2)
    seg_all = np.add.reduceat(w, start)
    seg_d1 = np.add.reduceat(w1, start)
    seg_d2 = np.add.reduceat(w2, start)
    seg_d = seg_d1 + seg_d2
    before = np.concatenate([[0.0], np.cumsum(seg_all)[:-1]])
    at_risk = seg_all.sum() - before
    ok = at_risk > 0
    if not ok.any():
        return 0.0
    at_risk, seg_d, seg_d1 = at_risk[ok], seg_d[ok], seg_d1[ok]
    S_prev = np.concatenate([[1.0], np.cumprod(1 - seg_d / at_risk)[:-1]])
    return float(np.sum(S_prev * seg_d1 / at_risk))


causes = {'cardiovascular': 'evt_cvd', 'cancer': 'evt_can', 'respiratory': 'evt_resp'}
d['w'] = d.WTMEC2YR / 8.0
quint = {nm: pd.qcut(d[v], 5, labels=False, duplicates='drop').values
         for nm, v in IDX.items()}
rng = np.random.default_rng(20261104)
out = []
for nm in names:
    hi = quint[nm] == quint[nm].max()
    lo = quint[nm] == 0
    for cause, flag in causes.items():
        for lab, mask in [('Q5 (highest)', hi), ('Q1 (lowest)', lo)]:
            sub = d[mask]
            code = np.where(sub[flag].values == 1, 1,
                            np.where(sub.dead.values == 1, 2, 0))
            t = sub.months.values
            w = sub.w.values
            cif = aj_cif(t, code, w)
            bs = []
            for _ in range(200):
                idx = rng.integers(0, len(sub), len(sub))
                bs.append(aj_cif(t[idx], code[idx], w[idx]))
            lo_ci, hi_ci = np.percentile(bs, [2.5, 97.5])
            out.append(dict(index=nm, cause=cause, group=lab, n=int(mask.sum()),
                            cif_10y=cif, lo=float(lo_ci), hi=float(hi_ci)))
            print('  %-11s %-15s %-14s n=%5d  10y CIF=%.3f (%.3f–%.3f)'
                  % (nm, cause, lab, mask.sum(), cif, lo_ci, hi_ci))

cr = pd.DataFrame(out)
cr.to_csv(os.path.join(OUTD, 'competing_risk_cif.csv'),
          index=False, encoding='utf-8-sig')
piv = cr.pivot_table(index=['cause', 'index'], columns='group', values='cif_10y')
piv['差值(Q5−Q1)'] = piv['Q5 (highest)'] - piv['Q1 (lowest)']
print('\n=== 10 年累计发生率（Q5 − Q1 差值）===')
print(piv.round(3).to_string())
print('\n输出 →', OUTD)

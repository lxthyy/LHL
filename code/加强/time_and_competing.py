# -*- coding: utf-8 -*-
"""
加强分析 3：时间依赖判别 + 竞争风险累计发生率
------------------------------------------------------------------
(1) 时间依赖 C 指数：把随访在第 5 年、第 10 年做行政截尾，重算 C 指数，
    看“各指数判别力相同”这一结论是否只在全程随访下成立。
(2) 竞争风险：Aalen–Johansen 累计发生率（10 年），每个指数最高与最低五分位，
    死因别（心血管 / 肿瘤 / 呼吸），其余死因为竞争事件，采用设计权重。

输出到 结果表\\加强\\，不改动任何既有结果表。
"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines import AalenJohansenFitter

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
D = pd.get_dummies(d[['race', 'cycle']], columns=['race', 'cycle'],
                   drop_first=True, dtype=float)
for c in D.columns:
    d[c] = D[c].values
COV = NUM + [c for c in D.columns if c.startswith(('race_', 'cycle_'))]
for k in IDX.values():
    d['z_' + k] = ((d[k] - d[k].mean()) / d[k].std()).clip(-5, 5)
print('分析集 n=%d 死亡=%d' % (len(d), int(d.dead.sum())))

risk = {}
for nm, v in IDX.items():
    f = CoxPHFitter().fit(d[['months', 'dead'] + COV + ['z_' + v]], 'months', 'dead')
    risk[nm] = f.predict_partial_hazard(d[COV + ['z_' + v]]).values


def fast_cindex(t, r, e):
    t = np.asarray(t, float); r = np.asarray(r, float); e = np.asarray(e, int)
    uniq, inv = np.unique(r, return_inverse=True)
    k = len(uniq)
    tree = np.zeros(k + 1)

    def add(i):
        i += 1
        while i <= k:
            tree[i] += 1
            i += i & -i

    def qs(i):
        if i < 0:
            return 0
        s, i = 0, i + 1
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    order = np.argsort(-t, kind='mergesort')
    ts = t[order]
    n = len(t)
    conc, comp, total_less, start = 0.0, 0, 0, 0
    while start < n:
        end = start
        while end < n and ts[end] == ts[start]:
            end += 1
        grp = order[start:end]
        for i in grp:
            if e[i] == 1:
                less = qs(inv[i] - 1)
                le = qs(inv[i])
                conc += less + 0.5 * (le - less)
                comp += total_less
        for i in grp:
            add(inv[i])
            total_less += 1
        start = end
    return conc / comp if comp else np.nan


# ---------- (1) 时间依赖 C 指数 ----------
rows = []
t_all, e_all = d.months.values, d.dead.values.astype(int)
for horizon in (60.0, 120.0, None):
    if horizon is None:
        t, e = t_all, e_all
        label = '全程'
    else:
        e = np.where(t_all <= horizon, e_all, 0)     # 超过时限的按删失处理
        t = np.minimum(t_all, horizon)
        label = '%d 年' % (horizon / 12)
    for nm in IDX:
        from lifelines.utils import concordance_index as _ci
        rows.append(dict(horizon=label, index=nm,
                         C=_ci(t, -risk[nm], e)))
hc = pd.DataFrame(rows).pivot(index='index', columns='horizon', values='C')
hc = hc[['5 年', '10 年', '全程']].round(4)
hc.to_csv(os.path.join(OUTD, 'time_dependent_cindex.csv'), encoding='utf-8-sig')
print('\n=== 时间依赖 C 指数（行政截尾）===')
print(hc.to_string())

# ---------- (2) 竞争风险累计发生率 ----------
causes = {'cardiovascular': 'evt_cvd', 'cancer': 'evt_can', 'respiratory': 'evt_resp'}
d['w'] = d.WTMEC2YR / 8.0
out = []
rng = np.random.default_rng(20261104)
quint = {}
for nm, v in IDX.items():
    q = pd.qcut(d[v], 5, labels=False, duplicates='drop')
    # 保持方向一致：高分位 = 高指数
    quint[nm] = q.values

def cif10(months, ev, w):
    """10 年 Aalen–Johansen 累计发生率；优先用设计权重，失败则退回未加权。"""
    try:
        aj = AalenJohansenFitter().fit(months, ev, event_of_interest=1,
                                       weights_col=w)
        return float(np.nan_to_num(
            aj.cumulative_density_at_times([120.0]).values[0])[0]), True
    except Exception:
        aj = AalenJohansenFitter().fit(months, ev, event_of_interest=1)
        return float(np.nan_to_num(
            aj.cumulative_density_at_times([120.0]).values[0])[0]), False


for nm in IDX:
    hi = quint[nm] == quint[nm].max()
    lo = quint[nm] == 0
    for cause, flag in causes.items():
        for lab, mask in [('Q5 (highest)', hi), ('Q1 (lowest)', lo)]:
            sub = d[mask]
            ev = np.where(sub[flag].values == 1, 1,
                          np.where(sub.dead.values == 1, 2, 0))
            cif, wtd = cif10(sub.months.values, ev, sub.w.values)
            bs = []
            for _ in range(200):
                idx = rng.integers(0, len(sub), len(sub))
                try:
                    v, _ = cif10(sub.months.values[idx], ev[idx],
                                 sub.w.values[idx])
                    bs.append(v)
                except Exception:
                    continue
            lo_ci = float(np.percentile(bs, 2.5)) if bs else np.nan
            hi_ci = float(np.percentile(bs, 97.5)) if bs else np.nan
            out.append(dict(index=nm, cause=cause, group=lab, n=int(mask.sum()),
                            weighted=wtd, cif_10y=cif, lo=lo_ci, hi=hi_ci))
            print('  %-11s %-15s %-14s n=%5d  10y CIF=%.3f (%.3f–%.3f)%s'
                  % (nm, cause, lab, mask.sum(), cif, lo_ci, hi_ci,
                     '' if wtd else '  [未加权]'))

cr = pd.DataFrame(out)
cr.to_csv(os.path.join(OUTD, 'competing_risk_cif.csv'),
          index=False, encoding='utf-8-sig')
print('\n输出 →', OUTD)

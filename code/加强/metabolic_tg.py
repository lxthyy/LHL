# -*- coding: utf-8 -*-
"""
加强分析 2：代谢域去 TG 的敏感性分析（按 build_ext_cyc.py 原样复刻）
------------------------------------------------------------------
第一步必须“复刻成功”：重建的五域 → disp / pc1 与已存值相关必须 ≈1.00，
否则中止，不产出任何结论。

复刻口径（逐行照抄 build_ext_cyc.py）：
  log 变换 = np.log(v.where(v > 0))
  残差化 = age, age², male, cycle 虚拟变量；残差 / 残差 SD；缩尾 ±CAP
  域分  = 可得项的均值，要求 项数 >= max(2, len(items)//2)
  disp  = F.std(axis=1, ddof=0)
  pc1   = 仅用五域齐全的行，标准化后 SVD，L = vt[0]*sv[0]，按 L.sum() 定向

输出到 结果表\\加强\\，不改动任何既有结果表。
"""
import os
import sys
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
OUTD = os.path.join(P, '结果表', '加强')
os.makedirs(OUTD, exist_ok=True)
CAP = 4

d = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'),
                encoding='utf-8-sig')
print('读入 %d 行 × %d 列' % (len(d), d.shape[1]))

DOMS = {'hepatic': ['LBXSAL', 'LBXSTB', 'LBXSAPSI', 'LBXSGTSI', 'LBXSASSI'],
        'renal': ['LBXSCR', 'LBXSBU', 'LBXSUA'],
        'metabolic': ['LBXSGL', 'LBXGH', 'tg', 'LBDHDD', 'LBXTC'],
        'haem': ['LBXHGB', 'LBXMCVSI', 'LBXRDW', 'LBXPLTSI'],
        'inflam': ['LBXWBCSI', 'LBXLYPCT', 'crp']}
LOG = {'LBXSTB', 'LBXSGTSI', 'LBXSASSI', 'LBXSCR', 'LBXSUA', 'tg', 'crp'}


def build(dom_spec):
    cyc = pd.get_dummies(d.cycle, prefix='cy', drop_first=True, dtype=float)
    z = {}
    for cs in dom_spec.values():
        for c in cs:
            v = d[c].astype(float)
            if c in LOG:
                v = np.log(v.where(v > 0))
            ok = v.notna() & d.age.notna()
            X = np.column_stack([np.ones(ok.sum()), d.loc[ok, 'age'],
                                 d.loc[ok, 'age'] ** 2, d.loc[ok, 'male'],
                                 cyc.loc[ok].values])
            y = v[ok].values
            bt, *_ = np.linalg.lstsq(X, y, rcond=None)
            r = pd.Series(np.nan, index=d.index)
            rr = y - X @ bt
            r.loc[ok] = rr / rr.std()
            z[c] = r.clip(-CAP, CAP)
    Z = pd.DataFrame(z)
    F = pd.DataFrame(index=d.index)
    for dm, cs in dom_spec.items():
        M = Z[cs]
        F[dm] = M.mean(axis=1).where(M.notna().sum(axis=1) >= max(2, len(cs) // 2))
    disp = F.std(axis=1, ddof=0)
    Fs = F.dropna()
    Zz = (Fs - Fs.mean()) / Fs.std()
    u, sv, vt = np.linalg.svd(Zz.values - Zz.values.mean(0), full_matrices=False)
    L = vt[0] * sv[0]
    if L.sum() < 0:
        L = -L
    pc = pd.Series(np.nan, index=d.index)
    pc.loc[Fs.index] = Zz.values @ L
    return F, disp, pc, float(sv[0] ** 2 / (sv ** 2).sum())


F_tg, disp_tg, pc_tg, evr_tg = build(DOMS)
DOMS_NT = dict(DOMS)
DOMS_NT['metabolic'] = [c for c in DOMS['metabolic'] if c != 'tg']
F_nt, disp_nt, pc_nt, evr_nt = build(DOMS_NT)

chk = {
    'corr(disp 复刻, disp 已存)': disp_tg.corr(d.disp),
    'max|disp 复刻 − disp 已存|': float((disp_tg - d.disp).abs().max()),
    'corr(pc1 复刻, pc1 已存)': pc_tg.corr(d.pc1),
    'max|pc1 复刻 − pc1 已存|': float((pc_tg - d.pc1).abs().max()),
    'PC1 解释率 含TG': evr_tg,
    'corr(disp 含TG, disp 去TG)': disp_tg.corr(disp_nt),
    'corr(pc1 含TG, pc1 去TG)': pc_tg.corr(pc_nt),
    'n disp 含TG': int(disp_tg.notna().sum()),
    'n disp 去TG': int(disp_nt.notna().sum()),
}
print('\n=== 复刻对拍 ===')
for k, v in chk.items():
    print('  %-28s %s' % (k, round(v, 6) if isinstance(v, float) else v))
pd.Series(chk).to_csv(os.path.join(OUTD, 'tg_rebuild_check.csv'),
                      encoding='utf-8-sig')

ok = (chk['corr(disp 复刻, disp 已存)'] > 0.999 and
      chk['corr(pc1 复刻, pc1 已存)'] > 0.999)
if not ok:
    print('\n中止：复刻未达到 0.999，不能据此做敏感性分析。')
    sys.exit(2)
print('\n复刻成功（相关 > 0.999），继续敏感性分析。')


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


d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
names = ['PhenoAge', 'HD', 'AL', 'Dispersion', 'PC1']
pairs = ['%s − %s' % (a, b) for i, a in enumerate(names) for b in names[i + 1:]]


def prep(disp_col, pc_col):
    x = d.dropna(subset=['months', 'dead'] + NUM +
                 ['pa_accel', 'hd_log', 'al', disp_col, pc_col, 'race']).copy()
    x = x[x.months > 0].reset_index(drop=True)
    Dm = pd.get_dummies(x[['race', 'cycle']], columns=['race', 'cycle'],
                        drop_first=True, dtype=float)
    for c in Dm.columns:
        x[c] = Dm[c].values
    cov = NUM + [c for c in Dm.columns if c.startswith(('race_', 'cycle_'))]
    cols = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al',
            'Dispersion': disp_col, 'PC1': pc_col}
    risk = {}
    for nm, col in cols.items():
        z = ((x[col] - x[col].mean()) / x[col].std()).clip(-5, 5)
        y = x[['months', 'dead'] + cov].assign(v=z.values)
        f = CoxPHFitter().fit(y, 'months', 'dead')
        risk[nm] = f.predict_partial_hazard(y).values
    return x, risk


def boot(x, risk, B=200, seed=20261104):
    rng = np.random.default_rng(seed)
    t, e = x.months.values, x.dead.values.astype(int)
    n = len(x)
    out = {k: [] for k in pairs}
    for _ in range(B):
        idx = rng.integers(0, n, n)
        cc = {k: concordance_index(t[idx], -risk[k][idx], e[idx]) for k in names}
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                out['%s − %s' % (a, b)].append(cc[a] - cc[b])
    return out


d['disp_tg'], d['disp_nt'] = disp_tg, disp_nt
d['pc1_tg'], d['pc1_nt'] = pc_tg, pc_nt

res = {}
for tag, dc_, pc_ in [('withTG', 'disp_tg', 'pc1_tg'), ('noTG', 'disp_nt', 'pc1_nt')]:
    x, risk = prep(dc_, pc_)
    t, e = x.months.values, x.dead.values.astype(int)
    print('\n[%s] n=%d  PhenoAge C=%.6f（lifelines）'
          % (tag, len(x), concordance_index(t, -risk['PhenoAge'], e)))
    res[tag] = boot(x, risk)
    print('[%s] bootstrap 200 次完成' % tag)

rows = []
for k in pairs:
    v, w = res['withTG'][k], res['noTG'][k]
    rows.append(dict(
        pair=k,
        dC_withTG=float(np.mean(v)), lo_withTG=float(np.percentile(v, 2.5)),
        hi_withTG=float(np.percentile(v, 97.5)),
        dC_noTG=float(np.mean(w)), lo_noTG=float(np.percentile(w, 2.5)),
        hi_noTG=float(np.percentile(w, 97.5)),
        eq_withTG=bool(np.percentile(v, 2.5) > -0.01 and np.percentile(v, 97.5) < 0.01),
        eq_noTG=bool(np.percentile(w, 2.5) > -0.01 and np.percentile(w, 97.5) < 0.01)))
cmpdf = pd.DataFrame(rows)
cmpdf.to_csv(os.path.join(OUTD, 'tg_sensitivity_equivalence.csv'),
             index=False, encoding='utf-8-sig')
print('\n=== 代谢域去 TG 前后的十个配对（±0.01）===')
print(cmpdf.round(4).to_string(index=False))
print('\n等价对数：含 TG %d / 去 TG %d'
      % (cmpdf.eq_withTG.sum(), cmpdf.eq_noTG.sum()))
print('输出 →', OUTD)

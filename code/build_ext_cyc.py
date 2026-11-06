# -*- coding: utf-8 -*-
"""
build_ext_cyc：八周期主口径 —— 指数在“周期内”构建，剔除检测平台换代的位移
- 各指标残差化：1 + 年龄 + 年龄² + 男性 + 周期哑变量
- HD：每个周期内以本周期 20-39 岁为参照
- AL：4 个分位项用当周期分位，其余用临床固定阈值
- PhenoAge：按 Levine 原式（不校正，公式本身就是固定标尺）
输出 analysis_dataset_extc.csv
"""
import os
import numpy as np
import pandas as pd

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
CAP = 4.0

d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_ext.csv'), encoding='utf-8-sig')
print('读入 %d 行 × %d 列，周期 %d 个' % (len(d), d.shape[1], d.cycle.nunique()))

DOMS = {'肝脏': ['LBXSAL', 'LBXSTB', 'LBXSAPSI', 'LBXSGTSI', 'LBXSASSI'],
        '肾脏': ['LBXSCR', 'LBXSBU', 'LBXSUA'],
        '代谢': ['LBXSGL', 'LBXGH', 'tg', 'LBDHDD', 'LBXTC'],
        '血液': ['LBXHGB', 'LBXMCVSI', 'LBXRDW', 'LBXPLTSI'],
        '炎症': ['LBXWBCSI', 'LBXLYPCT', 'crp']}
LOG = {'LBXSTB', 'LBXSGTSI', 'LBXSASSI', 'LBXSCR', 'LBXSUA', 'tg', 'crp'}

cyc = pd.get_dummies(d.cycle, prefix='cy', drop_first=True, dtype=float)
nclip = 0
z = {}
for cs in DOMS.values():
    for c in cs:
        v = d[c].astype(float)
        if c in LOG:
            v = np.log(v.where(v > 0))
        ok = v.notna() & d.age.notna()
        X = np.column_stack([np.ones(ok.sum()), d.loc[ok, 'age'], d.loc[ok, 'age'] ** 2,
                             d.loc[ok, 'male'], cyc.loc[ok].values])
        y = v[ok].values
        bt, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = pd.Series(np.nan, index=d.index)
        r.loc[ok] = (y - X @ bt) / (y - X @ bt).std()
        nclip += int((r.abs() > CAP).sum())
        z[c] = r.clip(-CAP, CAP)
Z = pd.DataFrame(z)
print('缩尾 ±%.0f SD：%d 个（%.3f%%）' % (CAP, nclip, 100 * nclip / (len(d) * Z.shape[1])))

drift = Z.groupby(d.cycle).mean()
rngs = (drift.max() - drift.min()).sort_values(ascending=False)
print('\n=== 周期校正后剩余周期效应（残差 SD 极差）===')
print(rngs.round(4).head(6).to_string())

F = pd.DataFrame(index=d.index)
for dm, cs in DOMS.items():
    M = Z[cs]
    F[dm] = M.mean(axis=1).where(M.notna().sum(axis=1) >= max(2, len(cs) // 2))
d['disp'] = F.std(axis=1, ddof=0)
Fs = F.dropna()
Zz = (Fs - Fs.mean()) / Fs.std()
u, sv, vt = np.linalg.svd(Zz.values - Zz.values.mean(0), full_matrices=False)
L = vt[0] * sv[0]
if L.sum() < 0:
    L = -L
pc = pd.Series(np.nan, index=d.index)
pc.loc[Fs.index] = Zz.values @ L
d['pc1'] = pc
print('PC1 解释率 %.1f%%' % (100 * sv[0] ** 2 / (sv ** 2).sum()))

# HD：周期内参照
HDV = ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSUA', 'LBXHGB',
       'LBXMCVSI', 'LBXRDW', 'LBXWBCSI', 'LBXLYPCT', 'LBXPLTSI', 'crp']
H = pd.DataFrame(index=d.index)
for c in HDV:
    v = d[c].astype(float)
    if c in LOG or c == 'crp':
        v = np.log(v.where(v > 0))
    H[c] = v.clip(v.quantile(0.01), v.quantile(0.99))
hd = pd.Series(np.nan, index=d.index)
for lab, idx in d.groupby('cycle').groups.items():
    sub = H.loc[idx]
    ok = sub.notna().all(axis=1)
    ref = ok & (d.loc[idx, 'age'] <= 39)
    if ref.sum() < 200:
        continue
    mu = sub[ref].mean()
    icov = np.linalg.pinv(np.cov(sub[ref].values, rowvar=False))
    Dv = sub[ok].values - mu.values
    hd.loc[sub[ok].index] = np.einsum('ij,jk,ik->i', Dv, icov, Dv)
d['hd'] = hd

# AL：分位项按周期
it = pd.DataFrame(index=d.index)
sbp = d[[f'BPXSY{i}' for i in range(1, 5)]].apply(pd.to_numeric, errors='coerce').mean(axis=1)
dbp = d[[f'BPXDI{i}' for i in range(1, 5)]].apply(pd.to_numeric, errors='coerce').mean(axis=1)
it['bp'] = ((sbp >= 140) | (dbp >= 90)).astype(float)
it['bmi'] = (d.bmi >= 30).astype(float)
it['a1c'] = (d.LBXGH >= 5.7).astype(float)
it['tc'] = (d.LBXTC >= 240).astype(float)
it['hdl'] = (d.LBDHDD < np.where(d.male == 1, 40, 50)).astype(float)
it['crp'] = (d['crp'] >= 0.3).astype(float)


def cyc_flag(col, upper):
    q = d.groupby('cycle')[col].quantile(0.75 if upper else 0.25)
    thr = d.cycle.map(q)
    return ((d[col] >= thr) if upper else (d[col] <= thr)).astype(float)


it['alb'] = cyc_flag('LBXSAL', False)
it['scr'] = cyc_flag('LBXSCR', True)
it['ua'] = cyc_flag('LBXSUA', True)
it['wbc'] = cyc_flag('LBXWBCSI', True)
# 修正（2026-10-30 审计）：缺失不得被当作“未处于高危”——NaN 与阈值比较返回 False
_bpna = d[[f'BPXSY{i}' for i in range(1, 5)] + [f'BPXDI{i}' for i in range(1, 5)]] \
    .apply(pd.to_numeric, errors='coerce').isna().all(axis=1)
_MASK = {'bp': _bpna, 'bmi': d.bmi.isna(), 'a1c': d.LBXGH.isna(),
         'tc': d.LBXTC.isna(), 'hdl': d.LBDHDD.isna(), 'crp': d['crp'].isna(),
         'alb': d.LBXSAL.isna(), 'scr': d.LBXSCR.isna(),
         'ua': d.LBXSUA.isna(), 'wbc': d.LBXWBCSI.isna()}
for _k, _m in _MASK.items():
    it.loc[_m, _k] = np.nan
d['al'] = it.sum(axis=1, min_count=8)
d['al9'] = it.drop(columns=['bmi']).sum(axis=1, min_count=8)

print('\n各周期：n / 死亡 / 指数中位数')
print(d.groupby('cycle').agg(n=('SEQN', 'size'), 死亡=('dead', 'sum'),
                              phenoage=('phenoage', 'median'), disp=('disp', 'median'),
                              hd=('hd', 'median'), al=('al', 'median'),
                              pc1=('pc1', 'median')).round(2).to_string())

d.to_csv(os.path.join(OUT, 'analysis_dataset_extc.csv'), index=False, encoding='utf-8-sig')
print('\n已写出 analysis_dataset_extc.csv（周期内标准化，主口径）%d 行' % len(d))

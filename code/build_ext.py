# -*- coding: utf-8 -*-
"""
build_ext：1999-2018 八周期合并 → 指数构建（含修正 PhenoAge）
输入：out\analysis_dataset.csv（2005-2018 原始列）+ out\dataset_9904.csv（1999-2004）
输出：out\analysis_dataset_ext.csv
"""
import os
import numpy as np
import pandas as pd

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
CACHE = r'D:\最新智研\trae工作文件夹\SJK\nhanes_cache'
CAP = 4.0
GAMMA, T_MONTHS = 0.0076927, 120.0

RAW = ['SEQN', 'RIDAGEYR', 'RIAGENDR', 'RIDRETH1', 'DMDEDUC2', 'INDFMPIR',
       'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA', 'cycle',
       'LBXWBCSI', 'LBXLYPCT', 'LBXMCVSI', 'LBXRDW', 'LBXHGB', 'LBXPLTSI',
       'LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSASSI', 'LBXSGTSI', 'LBXSTB',
       'LBXSUA', 'LBXSBU', 'LBXCRP', 'LBXHSCRP', 'crp', 'LBXGH', 'LBDHDD', 'LBXTC',
       'LBXSTR', 'tg',
       'BMXBMI', 'BPXSY1', 'BPXSY2', 'BPXSY3', 'BPXSY4',
       'BPXDI1', 'BPXDI2', 'BPXDI3', 'BPXDI4', 'SMQ020', 'SMQ040']

a = pd.read_csv(os.path.join(OUT, 'analysis_dataset.csv'), encoding='utf-8-sig')
b = pd.read_csv(os.path.join(OUT, 'dataset_9904.csv'), encoding='utf-8-sig')
for c in RAW:
    if c not in b.columns:
        b[c] = np.nan
d = pd.concat([b[RAW], a[[c for c in RAW if c in a.columns]]], ignore_index=True)
print('拼合后 %d 行，周期：%s' % (len(d), sorted(d.cycle.unique())))

# 统一派生列
s = lambda x: pd.to_numeric(x, errors='coerce')
d['age'] = s(d.RIDAGEYR)
d['male'] = (s(d.RIAGENDR) == 1).astype(int)
d['race'] = s(d.RIDRETH1)
d['edu'] = s(d.DMDEDUC2).where(lambda v: v.isin([1, 2, 3, 4, 5]))   # 7=拒答 9=不知道 → 缺失
d['pir'] = s(d.INDFMPIR)
d['bmi'] = s(d.BMXBMI)
d['smoke'] = np.where(s(d.SMQ020) != 1, 0, np.where(s(d.SMQ040) == 3, 0, 1))
d.loc[s(d.SMQ020).isna(), 'smoke'] = np.nan
d['crp'] = s(d.LBXCRP).fillna(s(d.LBXHSCRP) / 10.0)   # mg/dL；HSCRP 为 mg/L
d['tg'] = s(d.LBXSTR).fillna(s(d.get('tg')))
for c in ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSASSI', 'LBXSGTSI',
          'LBXSTB', 'LBXSUA', 'LBXSBU', 'LBXGH', 'LBDHDD', 'LBXTC',
          'LBXWBCSI', 'LBXLYPCT', 'LBXMCVSI', 'LBXRDW', 'LBXHGB', 'LBXPLTSI']:
    d[c] = s(d[c])

# 死亡
MORT = {'1999-00': 'NHANES_1999_2000_MORT_2019_PUBLIC.dat',
        '2001-02': 'NHANES_2001_2002_MORT_2019_PUBLIC.dat',
        '2003-04': 'NHANES_2003_2004_MORT_2019_PUBLIC.dat',
        '2005-06': 'NHANES_2005_2006_MORT_2019_PUBLIC.dat',
        '2007-08': 'NHANES_2007_2008_MORT_2019_PUBLIC.dat',
        '2009-10': 'NHANES_2009_2010_MORT_2019_PUBLIC.dat',
        '2015-16': 'NHANES_2015_2016_MORT_2019_PUBLIC.dat',
        '2017-18': 'NHANES_2017_2018_MORT_2019_PUBLIC.dat'}
rows = []
for lab, f in MORT.items():
    p = os.path.join(CACHE, f)
    if not os.path.exists(p):
        print('  缺死亡文件', f)
        continue
    for ln in open(p, encoding='latin-1'):
        ln = ln.rstrip('\n')
        if len(ln) < 45:
            continue
        try:
            sq, pm = int(ln[0:6]), int(ln[42:45])
        except ValueError:
            continue
        ms = ln[15]
        rows.append((sq, lab, 1 if ms == '1' else (0 if ms == '0' else np.nan), pm,
                     ln[16:19].strip()))
mo = pd.DataFrame(rows, columns=['SEQN', 'cycle', 'dead', 'months', 'ucod'])
mo['evt_cvd'] = ((mo.dead == 1) & mo.ucod.isin(['001', '005'])).astype(int)
mo['evt_can'] = ((mo.dead == 1) & (mo.ucod == '002')).astype(int)
mo['evt_resp'] = ((mo.dead == 1) & mo.ucod.isin(['003', '008'])).astype(int)
d = d.merge(mo, on=['SEQN', 'cycle'], how='left')
print('死亡链接：%d 有人匹配，死亡 %d，心血管 %d 肿瘤 %d 呼吸 %d'
      % (d.dead.notna().sum(), int(d.dead.sum()), int(d.evt_cvd.sum()),
         int(d.evt_can.sum()), int(d.evt_resp.sum())))

d = d[(d.age >= 20) & (d.age <= 85)].reset_index(drop=True)
print('20-85 岁：%d 行' % len(d))

# ---------- 五域 ----------
DOMS = {'肝脏': ['LBXSAL', 'LBXSTB', 'LBXSAPSI', 'LBXSGTSI', 'LBXSASSI'],
        '肾脏': ['LBXSCR', 'LBXSBU', 'LBXSUA'],
        '代谢': ['LBXSGL', 'LBXGH', 'tg', 'LBDHDD', 'LBXTC'],
        '血液': ['LBXHGB', 'LBXMCVSI', 'LBXRDW', 'LBXPLTSI'],
        '炎症': ['LBXWBCSI', 'LBXLYPCT', 'crp']}
LOG = {'LBXSTB', 'LBXSGTSI', 'LBXSASSI', 'LBXSCR', 'LBXSUA', 'tg', 'crp'}

nclip = 0
z = {}
for cs in DOMS.values():
    for c in cs:
        v = d[c].astype(float)
        if c in LOG:
            v = np.log(v.where(v > 0))
        ok = v.notna() & d.age.notna() & d.RIAGENDR.notna()
        X = np.column_stack([np.ones(ok.sum()), d.loc[ok, 'age'],
                             d.loc[ok, 'age'] ** 2, d.loc[ok, 'male']])
        y = v[ok].values
        bt, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = pd.Series(np.nan, index=d.index)
        r.loc[ok] = (y - X @ bt) / (y - X @ bt).std()
        nclip += int((r.abs() > CAP).sum())
        z[c] = r.clip(-CAP, CAP)
Z = pd.DataFrame(z)
print('缩尾 ±%.0f SD：%d 个（%.3f%%）' % (CAP, nclip, 100 * nclip / (len(d) * Z.shape[1])))

drift = Z.groupby(d.cycle).mean()
rng = (drift.max() - drift.min()).sort_values(ascending=False)
print('\n=== 各指标“周期效应”幅度（残差 SD 单位，跨周期极差）===')
print(rng.round(3).head(10).to_string())
print('（>0.2 说明仪器换代造成的位移不可忽略）')

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

HDV = ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSUA', 'LBXHGB',
       'LBXMCVSI', 'LBXRDW', 'LBXWBCSI', 'LBXLYPCT', 'LBXPLTSI', 'crp']
H = pd.DataFrame(index=d.index)
for c in HDV:
    v = d[c].astype(float)
    if c in LOG or c == 'crp':
        v = np.log(v.where(v > 0))
    H[c] = v.clip(v.quantile(0.01), v.quantile(0.99))
okh = H.notna().all(axis=1)
ref = okh & (d.age <= 39)
mu = H[ref].mean()
icov = np.linalg.pinv(np.cov(H[ref].values, rowvar=False))
D = H[okh].values - mu.values
hd = pd.Series(np.nan, index=d.index)
hd.loc[okh] = np.einsum('ij,jk,ik->i', D, icov, D)
d['hd'] = hd

sbp = d[[f'BPXSY{i}' for i in range(1, 5)]].apply(pd.to_numeric, errors='coerce').mean(axis=1)
dbp = d[[f'BPXDI{i}' for i in range(1, 5)]].apply(pd.to_numeric, errors='coerce').mean(axis=1)
it = pd.DataFrame(index=d.index)
it['bp'] = ((sbp >= 140) | (dbp >= 90)).astype(float)
it['bmi'] = (d.bmi >= 30).astype(float)
it['a1c'] = (d.LBXGH >= 5.7).astype(float)
it['tc'] = (d.LBXTC >= 240).astype(float)
it['hdl'] = (d.LBDHDD < np.where(d.male == 1, 40, 50)).astype(float)
it['crp'] = (d['crp'] >= 0.3).astype(float)
it['alb'] = (d.LBXSAL <= d.LBXSAL.quantile(0.25)).astype(float)
it['scr'] = (d.LBXSCR >= d.LBXSCR.quantile(0.75)).astype(float)
it['ua'] = (d.LBXSUA >= d.LBXSUA.quantile(0.75)).astype(float)
it['wbc'] = (d.LBXWBCSI >= d.LBXWBCSI.quantile(0.75)).astype(float)
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

# PhenoAge（修正版）
xb = (-19.9067 - 0.0336 * (d.LBXSAL * 10) + 0.0095 * (d.LBXSCR * 88.4)
      + 0.1953 * (d.LBXGL if 'LBXGL' in d.columns else d.LBXSGL / 18.0)
      + 0.0954 * np.log(d['crp'].where(d['crp'] > 0))
      - 0.0120 * d.LBXLYPCT + 0.0268 * d.LBXMCVSI + 0.3306 * d.LBXRDW
      + 0.00188 * d.LBXSAPSI + 0.0554 * d.LBXWBCSI + 0.0804 * d.age)
ms = 1 - np.exp(-np.exp(xb) * (np.exp(T_MONTHS * GAMMA) - 1) / GAMMA)
ms = ms.clip(1e-12, 1 - 1e-9)
d['phenoage'] = 141.50225 + np.log(-0.00553 * np.log(1 - ms)) / 0.090165
d['pa_accel'] = (d.phenoage - d.age).replace([np.inf, -np.inf], np.nan)

print('\n=== 各周期关键指标中位数（单位一致性 + 年代趋势）===')
cols = ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSGTSI', 'LBXTC', 'LBDHDD',
        'LBXCRP', 'LBXWBCSI', 'LBXRDW', 'LBXHGB', 'LBXGH', 'phenoage', 'disp', 'hd', 'al', 'pc1']
print(d.groupby('cycle')[cols].median().round(2).T.to_string())
print('\n各周期样本与死亡：')
print(d.groupby('cycle').agg(n=('SEQN', 'size'), 死亡=('dead', 'sum'),
                             随访中位=('months', 'median')).to_string())

d.to_csv(os.path.join(OUT, 'analysis_dataset_ext.csv'), index=False, encoding='utf-8-sig')
print('\n已写出 analysis_dataset_ext.csv  %d 行 × %d 列' % d.shape)

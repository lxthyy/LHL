# -*- coding: utf-8 -*-
"""
衰老指数头对头比较 · 预实验 v0.1
目的：判断"不同衰老指数是否测同一件事"这个题是否成立
样本：NHANES 2005-06 / 2007-08 / 2009-10 / 2015-16 / 2017-18 成人 20-85，死亡随访至 2019
指数：
  A. PhenoAge 加速（Levine 2018，Table 1 单位：白蛋白 g/L、肌酐 umol/L、血糖 mmol/L）
  B. HD 稳态失调（Mahalanobis 距离，参照 20-39 岁）
  C. AL 稳态负荷（10 项高危计数）
  D. 五域离散度（域内年龄+性别残差 z 的标准差）
  E. 五域 PC1（一般衰老因子）
输出：相关矩阵 / Cox C-index / 增量判别（NRI、IDI）
"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

C = r'D:\最新智研\trae工作文件夹\SJK\nhanes_cache'
OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261027)

CYC = {'D': ('2005-06', 'NHANES_2005_2006_MORT_2019_PUBLIC.dat'),
       'E': ('2007-08', 'NHANES_2007_2008_MORT_2019_PUBLIC.dat'),
       'F': ('2009-10', 'NHANES_2009_2010_MORT_2019_PUBLIC.dat'),
       'I': ('2015-16', 'NHANES_2015_2016_MORT_2019_PUBLIC.dat'),
       'J': ('2017-18', 'NHANES_2017_2018_MORT_2019_PUBLIC.dat')}


def rd(mod, c, cols):
    p = os.path.join(C, f'{mod}_{c}.xpt')
    if not os.path.exists(p):
        return None
    d = pd.read_sas(p, format='xport')
    return d[['SEQN'] + [x for x in cols if x in d.columns]]


def s(v):
    return pd.to_numeric(v, errors='coerce')


frames = []
for c, (lab, _) in CYC.items():
    demo = rd('DEMO', c, ['RIDAGEYR', 'RIAGENDR', 'RIDRETH1', 'DMDEDUC2', 'INDFMPIR',
                          'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA'])
    cbc = rd('CBC', c, ['LBXWBCSI', 'LBXLYPCT', 'LBXMCVSI', 'LBXRDW', 'LBXHGB', 'LBXPLTSI'])
    bio = rd('BIOPRO', c, ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSASSI',
                           'LBXSGTSI', 'LBXSTB', 'LBXSUA', 'LBXSBU'])
    crp = rd('CRP', c, ['LBXCRP'])
    hscrp = rd('HSCRP', c, ['LBXHSCRP'])
    ghb = rd('GHB', c, ['LBXGH'])
    hdl = rd('HDL', c, ['LBDHDD'])
    tc = rd('TCHOL', c, ['LBXTC'])
    tr = rd('TRIGLY', c, ['LBXTR', 'LBDTRSI'])
    bmx = rd('BMX', c, ['BMXBMI'])
    bpx = rd('BPX', c, ['BPXSY1', 'BPXSY2', 'BPXSY3', 'BPXSY4',
                        'BPXDI1', 'BPXDI2', 'BPXDI3', 'BPXDI4'])
    smq = rd('SMQ', c, ['SMQ020', 'SMQ040'])
    if any(x is None for x in [demo, cbc, bio]):
        print('跳过周期', c)
        continue
    m = demo.merge(cbc, on='SEQN', how='left').merge(bio, on='SEQN', how='left')
    for e in [crp, hscrp, ghb, hdl, tc, tr, bmx, bpx, smq]:
        if e is not None:
            m = m.merge(e, on='SEQN', how='left')
    m['cycle'] = lab
    frames.append(m)

d = pd.concat(frames, ignore_index=True)
d['crp'] = s(d.get('LBXCRP')).fillna(s(d.get('LBXHSCRP')) / 10.0)   # mg/dL
d['tg'] = s(d.get('LBXTR')).fillna(s(d.get('LBDTRSI')))
d = d[(d.RIDAGEYR >= 20) & (d.RIDAGEYR <= 85)].reset_index(drop=True)
print('成人 20-85：%d 行' % len(d))

# ---------- 五域（沿用原项目口径） ----------
DOM = {'肝脏': ['LBXSAL', 'LBXSTB', 'LBXSAPSI', 'LBXSGTSI', 'LBXSASSI'],
       '肾脏': ['LBXSCR', 'LBXSBU', 'LBXSUA'],
       '代谢': ['LBXSGL', 'LBXGH', 'tg', 'LBDHDD', 'LBXTC'],
       '血液': ['LBXHGB', 'LBXMCVSI', 'LBXRDW', 'LBXPLTSI'],
       '炎症': ['LBXWBCSI', 'LBXLYPCT', 'crp']}
LOG = {'LBXSTB', 'LBXSGTSI', 'LBXSASSI', 'LBXSCR', 'LBXSUA', 'tg', 'crp'}


def az(col):
    v = s(d[col])
    if col in LOG:
        v = np.log(v.where(v > 0))
    ok = v.notna() & d.RIDAGEYR.notna() & d.RIAGENDR.notna()
    if ok.sum() < 200:
        return pd.Series(np.nan, index=d.index)
    X = np.column_stack([np.ones(ok.sum()), d.loc[ok, 'RIDAGEYR'],
                         d.loc[ok, 'RIDAGEYR'] ** 2, (d.loc[ok, 'RIAGENDR'] == 1).astype(float)])
    y = v[ok].values
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = pd.Series(np.nan, index=d.index)
    r.loc[ok] = (y - X @ b) / (y - X @ b).std()
    return r


z = pd.DataFrame(index=d.index)
for dom, cs in DOM.items():
    parts = [az(x) for x in cs if x in d.columns]
    parts = [p for p in parts if p.notna().sum() > 200]
    M = pd.concat(parts, axis=1)
    z[dom] = M.mean(axis=1).where(M.notna().sum(axis=1) >= max(2, len(parts) // 2))

d['disp'] = z.std(axis=1)
zfull = z.dropna()
pca_vals = np.linalg.svd(zfull.values - zfull.values.mean(0), full_matrices=False)
pc1 = pd.Series(np.nan, index=d.index)
pc1.loc[zfull.index] = pca_vals[0][:, 0]
if np.corrcoef(pc1.dropna(), zfull.mean(axis=1))[0, 1] < 0:
    pc1 = -pc1
d['pc1'] = pc1
expl = pca_vals[1][0] ** 2 / (pca_vals[1] ** 2).sum()
print('五域 PCA 第一主成分解释率 %.1f%%' % (100 * expl))

# ---------- PhenoAge ----------
def phenoage(row_alb, row_cre_umol, row_glu_mmol, row_crp, row_lym, row_mcv,
             row_rdw, row_alp, row_wbc, row_age):
    xb = (-19.9067 - 0.0336 * row_alb + 0.0095 * row_cre_umol + 0.1953 * row_glu_mmol
          + 0.0954 * np.log(row_crp) - 0.0120 * row_lym + 0.0268 * row_mcv
          + 0.3306 * row_rdw + 0.00188 * row_alp + 0.0554 * row_wbc + 0.0804 * row_age)
    mm = 1 - np.exp(-np.exp(xb) * (np.exp(0.0076927 * 9) - 1) / 0.0076927)
    mm = np.clip(mm, 1e-12, 1 - 1e-9)
    return 141.50225 + np.log(-0.00553 * np.log(1 - mm)) / 0.090165


ph = phenoage(s(d.LBXSAL), s(d.LBXSCR) * 88.4, s(d.LBXSGL) / 18.0, d['crp'],
              s(d.LBXLYPCT), s(d.LBXMCVSI), s(d.LBXRDW), s(d.LBXSAPSI),
              s(d.LBXWBCSI), d.RIDAGEYR)
d['phenoage'] = ph
d['pa_accel'] = (d.phenoage - d.RIDAGEYR).replace([np.inf, -np.inf], np.nan)
d.loc[d.phenoage.abs() > 200, 'pa_accel'] = np.nan
ok = d.pa_accel.notna()
print('PhenoAge 可算 %d（%.1f%%）；与年龄 r=%.3f；均值差 %+.1f 岁；加速 SD=%.1f'
      % (ok.sum(), 100 * ok.mean(), np.corrcoef(d.phenoage[ok], d.RIDAGEYR[ok])[0, 1],
         d.pa_accel[ok].mean(), d.pa_accel[ok].std()))

# ---------- HD：Mahalanobis ----------
HDV = ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSUA', 'LBXHGB',
       'LBXMCVSI', 'LBXRDW', 'LBXWBCSI', 'LBXLYPCT', 'LBXPLTSI', 'crp']
hd = pd.DataFrame(index=d.index)
for v in HDV:
    x = s(d[v]) if v != 'crp' else d['crp']
    if v in LOG or v == 'crp':
        x = np.log(x.where(x > 0))
    hd[v] = x
ref = (d.RIDAGEYR <= 39)
mu = hd[ref].mean()
sd_ = hd[ref].std()
cov = np.cov(hd[ref].dropna().values.T)
cov += np.eye(cov.shape[0]) * 1e-6
inv = np.linalg.pinv(cov)
Z = (hd - mu) / sd_
Zd = Z.dropna()
dist = np.sqrt(np.einsum('ij,jk,ik->i', Zd.values, inv, Zd.values))
d['hd'] = np.nan
d.loc[Zd.index, 'hd'] = dist
print('HD 可算 %d；参照组(20-39) n=%d' % (d.hd.notna().sum(), ref.sum()))

# ---------- AL：10 项稳态负荷 ----------
sbp = pd.concat([s(d[c]) for c in ['BPXSY1', 'BPXSY2', 'BPXSY3', 'BPXSY4']], axis=1).mean(axis=1)
dbp = pd.concat([s(d[c]) for c in ['BPXDI1', 'BPXDI2', 'BPXDI3', 'BPXDI4']], axis=1).mean(axis=1)
male = (d.RIAGENDR == 1)
items = pd.DataFrame(index=d.index)
items['bp'] = ((sbp >= 140) | (dbp >= 90)).astype(float)
items['bmi'] = (s(d.BMXBMI) >= 30).astype(float)
items['a1c'] = (s(d.LBXGH) >= 5.7).astype(float)
items['tc'] = (s(d.LBXTC) >= 240).astype(float)
items['hdl'] = (s(d.LBDHDD) < np.where(male, 40, 50)).astype(float)
items['crp'] = (d['crp'] >= 0.3).astype(float)
items['alb'] = (s(d.LBXSAL) <= s(d.LBXSAL).quantile(0.25)).astype(float)
items['scr'] = (s(d.LBXSCR) >= s(d.LBXSCR).quantile(0.75)).astype(float)
items['ua'] = (s(d.LBXSUA) >= s(d.LBXSUA).quantile(0.75)).astype(float)
items['wbc'] = (s(d.LBXWBCSI) >= s(d.LBXWBCSI).quantile(0.75)).astype(float)
d['al'] = items.sum(axis=1, min_count=8)
print('AL 可算 %d；均值 %.1f' % (d.al.notna().sum(), d.al.mean()))

# ---------- 死亡随访 ----------
rows = []
for c, (lab, f) in CYC.items():
    p = os.path.join(C, f)
    if not f or not os.path.exists(p):
        continue
    for ln in open(p, encoding='latin-1'):
        ln = ln.rstrip('\n')
        if len(ln) < 45:
            continue
        try:
            seqn = int(ln[0:6])
            pm = int(ln[42:45])
        except ValueError:
            continue
        ms = ln[15]
        rows.append((seqn, lab, 1 if ms == '1' else (0 if ms == '0' else np.nan), pm))
mf = pd.DataFrame(rows, columns=['SEQN', 'cycle', 'dead', 'months'])
d = d.merge(mf, on=['SEQN', 'cycle'], how='left')
print('有死亡随访 %d，死亡 %d（%.1f%%），中位随访 %.0f 月'
      % (d.dead.notna().sum(), int(d.dead.fillna(0).sum()),
         100 * d.dead.mean(), d.months.median()))

# ---------- 协变量 ----------
d['male'] = male.astype(int)
d['age'] = s(d.RIDAGEYR)
d['smoke'] = np.where(s(d.get('SMQ020')) != 1, 0,
                      np.where(s(d.get('SMQ040')) == 3, 0, 1))  # 0 从不/已戒, 1 现吸
d['bmi'] = s(d.BMXBMI)
d['edu'] = s(d.get('DMDEDUC2'))
d['pir'] = s(d.get('INDFMPIR'))
d['race'] = s(d.get('RIDRETH1'))
d['cyc'] = d.cycle

COV = ['age', 'male', 'race', 'edu', 'pir', 'bmi', 'smoke']
IDX = {'PhenoAge 加速': 'pa_accel', 'HD 稳态失调': 'hd', 'AL 稳态负荷': 'al',
       '五域离散度': 'disp', '五域 PC1': 'pc1'}

base = d.dropna(subset=['dead', 'months'] + COV + list(IDX.values())).copy()
base = base[base.months > 0]
print('\n共同完整样本 n=%d，死亡 %d（%.1f%%）' % (len(base), int(base.dead.sum()), 100 * base.dead.mean()))

# 标准化
for k in IDX.values():
    base['z_' + k] = (base[k] - base[k].mean()) / base[k].std()

# ---------- 相关矩阵 ----------
corr = base[[*IDX.values(), 'age']].corr(method='spearman')
corr.to_csv(os.path.join(OUT, 'corr_indices.csv'), encoding='utf-8-sig')
print('\n=== Spearman 相关 ===')
print(corr.round(2).to_string())

# ---------- Cox ----------
def fit(df, cols, label):
    f = CoxPHFitter()
    f.fit(df[['months', 'dead'] + cols], duration_col='months', event_col='dead')
    c = f.concordance_index_
    return f, c


res = []
for name, v in IDX.items():
    f, c = fit(base, COV + ['z_' + v], name)
    b = f.params_['z_' + v]
    se = f.standard_errors_['z_' + v]
    res.append(dict(指数=name, n=len(base), C指数=c, HR每SD=np.exp(b),
                    lo=np.exp(b - 1.96 * se), hi=np.exp(b + 1.96 * se),
                    p=f.summary.loc['z_' + v, 'p']))
res = pd.DataFrame(res)

# 仅年龄性别
f0, c0 = fit(base, ['age', 'male'], 'age+sex')
# PhenoAge + 离散度
f2, c2 = fit(base, COV + ['z_pa_accel', 'z_disp'], 'PA+disp')
f3, c3 = fit(base, COV + ['z_pa_accel', 'z_pc1'], 'PA+PC1')
res = pd.concat([res, pd.DataFrame([
    dict(指数='（参照：年龄+性别）', n=len(base), C指数=c0, HR每SD=np.nan, lo=np.nan, hi=np.nan, p=np.nan),
    dict(指数='PhenoAge + 五域离散度', n=len(base), C指数=c2, HR每SD=np.exp(f2.params_['z_disp']),
         lo=np.exp(f2.params_['z_disp'] - 1.96 * f2.standard_errors_['z_disp']),
         hi=np.exp(f2.params_['z_disp'] + 1.96 * f2.standard_errors_['z_disp']),
         p=f2.summary.loc['z_disp', 'p']),
    dict(指数='PhenoAge + 五域PC1', n=len(base), C指数=c3, HR每SD=np.exp(f3.params_['z_pc1']),
         lo=np.exp(f3.params_['z_pc1'] - 1.96 * f3.standard_errors_['z_pc1']),
         hi=np.exp(f3.params_['z_pc1'] + 1.96 * f3.standard_errors_['z_pc1']),
         p=f3.summary.loc['z_pc1', 'p'])])], ignore_index=True)
res.to_csv(os.path.join(OUT, 'cox_cindex.csv'), index=False, encoding='utf-8-sig')
print('\n=== Cox 模型（全因死亡）===')
print(res.round(3).to_string(index=False))

# ---------- 增量判别：ΔC / NRI / IDI（10 年） ----------
T = 120.0


def pred_surv(f, df):
    return f.predict_survival_function(df, times=[T]).iloc[0].values


p1 = pred_surv(f, base)          # PhenoAge 模型（f 是最后一个含 pa_accel 的，重建）
f_pa, _ = fit(base, COV + ['z_pa_accel'], 'pa')
p1 = pred_surv(f_pa, base)
p2 = pred_surv(f2, base)
risk1, risk2 = 1 - p1, 1 - p2

ev = (base.dead.values == 1) & (base.months.values <= T)
ne = (base.dead.values == 0) & (base.months.values > T)


def nri_idi(r_old, r_new, ev, ne):
    up = r_new > r_old
    dn = r_new < r_old
    nri_e = up[ev].mean() - dn[ev].mean()
    nri_n = dn[ne].mean() - up[ne].mean()
    nri = nri_e + nri_n
    def slope(r, y):
        return r[y].mean() - r[~y].mean()
    idi = (slope(r_new, ev) - slope(r_old, ev)) - (slope(r_new, ne) - slope(r_old, ne))
    return nri, nri_e, nri_n, idi


nri, nri_e, nri_n, idi = nri_idi(risk1, risk2, ev, ne)
print('\n=== 增量（PhenoAge -> +离散度，10 年）===')
print('ΔC = %+.4f' % (c2 - f_pa.concordance_index_))
print('连续 NRI = %+.3f（事件 %+.3f / 非事件 %+.3f）' % (nri, nri_e, nri_n))
print('IDI = %+.4f' % idi)
print('10 年事件 %d / 非事件 %d' % (ev.sum(), ne.sum()))

pd.DataFrame([dict(指标='ΔC', 值=c2 - f_pa.concordance_index_),
              dict(指标='NRI', 值=nri), dict(指标='IDI', 值=idi),
              dict(指标='10年事件', 值=int(ev.sum()))]).to_csv(
    os.path.join(OUT, 'incremental.csv'), index=False, encoding='utf-8-sig')

base.to_csv(os.path.join(OUT, 'analysis_dataset.csv'), index=False, encoding='utf-8-sig')
print('\n结果已写入', OUT)

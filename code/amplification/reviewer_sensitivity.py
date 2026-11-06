# -*- coding: utf-8 -*-
"""
审稿意见 1、2 的定量回答
A. 分辨极限对"指标相关结构"的敏感性：SE 是否随 sqrt(1-rho) 走，换成别的 rho 时极限变多少
B. leave-one-cycle-out：去掉任一周期，五个指标的排名翻不翻
"""
import os
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
from scipy.stats import spearmanr

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
NPY = (r'c:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理'
       r'\age_compare\out\ext\_dc.npy')
OUTD = os.path.join(P, '结果表', '加强')

d = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
IDX = {'PhenoAge': 'pa_accel', 'HD': 'hd_log', 'AL': 'al',
       'Dispersion': 'disp', 'PC1': 'pc1'}
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
d = d.dropna(subset=['months', 'dead'] + NUM + list(IDX.values()) + ['race'])
d = d[d.months > 0].reset_index(drop=True)

# ---------- A ----------
names = list(IDX)
M = pd.DataFrame({k: d[v] for k, v in IDX.items()})
rho = M.corr(method='spearman')

dc = np.load(NPY, allow_pickle=True).item()
rowsA = []
for k in dc:
    a, b = [x.strip() for x in k.replace('−', '-').split('-')]
    se = float(np.std(dc[k], ddof=1))
    r = float(rho.loc[a, b])
    rowsA.append(dict(pair=k, rho=r, se=se, se_over_sqrt=se / np.sqrt(1 - r)))
A = pd.DataFrame(rowsA).sort_values('rho')
print('=== A. 每对的 rho 与 SE ===')
print(A.round(4).to_string(index=False))
print('SE/sqrt(1-rho) 中位 %.6f，范围 %.6f–%.6f（若近似常数，说明该标度成立）'
      % (A.se_over_sqrt.median(), A.se_over_sqrt.min(), A.se_over_sqrt.max()))

K = A.se_over_sqrt.median()
print('\n在 100 例死亡下，不同 rho 对应的分辨极限（MDD80 = 2.8016 x SE x sqrt(5636/100)）：')
for r in [0.16, 0.36, 0.56]:
    se = K * np.sqrt(1 - r)
    print('  rho=%.2f  SE=%.5f  极限=%.4f' % (r, se, 2.8016 * se * np.sqrt(5636 / 100)))
print('对照：五个指标之间的最大真实差异 = 0.0109')

# ---------- B ----------
print('\n=== B. leave-one-cycle-out 排名 ===')
d['z'] = 1.0
COV = NUM + ['race']
d2 = pd.get_dummies(d, columns=['race'], drop_first=True, dtype=float)
COV = NUM + [c for c in d2.columns if c.startswith('race_')]
for k, v in IDX.items():
    d2['z_' + k] = ((d2[v] - d2[v].mean()) / d2[v].std()).clip(-5, 5)
cycles = sorted(d2.cycle.unique())
base = {}
for k in IDX:
    f = CoxPHFitter().fit(d2[['months', 'dead', 'z_' + k] + COV],
                          'months', 'dead')
    base[k] = f.concordance_index_
order0 = sorted(base, key=lambda x: -base[x])
print('全样本：', ' > '.join('%s %.4f' % (k, base[k]) for k in order0))

flips = 0
rowsB = []
for cy in cycles:
    sub = d2[d2.cycle != cy].reset_index(drop=True)
    cur = {}
    for k in IDX:
        f = CoxPHFitter().fit(sub[['months', 'dead', 'z_' + k] + COV],
                              'months', 'dead')
        cur[k] = f.concordance_index_
    o = sorted(cur, key=lambda x: -cur[x])
    same = (o == order0)
    flips += (0 if same else 1)
    rowsB.append(dict(dropped=cy, order=' > '.join(o), same_as_full=same,
                      **{k: round(cur[k], 4) for k in IDX}))
    print('去掉 %-9s -> %s  %s' % (cy, ' > '.join(o), '同' if same else '★翻转'))
B = pd.DataFrame(rowsB)
A.to_csv(os.path.join(OUTD, 'rho_vs_se.csv'), index=False, encoding='utf-8-sig')
B.to_csv(os.path.join(OUTD, 'leave_one_cycle_out.csv'), index=False, encoding='utf-8-sig')
print('\n排名翻转的周期数: %d / %d' % (flips, len(cycles)))

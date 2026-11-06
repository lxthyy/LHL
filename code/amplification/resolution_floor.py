# -*- coding: utf-8 -*-
"""
加强分析 4：分辨极限（resolution floor）
------------------------------------------------
问题：已发表的头对头比较，其样本量能不能分辨它们自己报告出来的差异？

输入（均为已发表结果的同源产物，不重跑 Cox）：
  结果表\\加强\\equivalence_B1000.csv   10 对的 1000 次配对 bootstrap 区间
  结果表\\cindex_hr.csv                 五个指数的全样本 C 指数
  结果表\\加强\\ 下的 _dc 抽样矩阵经 equivalence_B1000 反推（只用区间宽度取 SE）

方法：
  1. 每对 SE = (hi - lo) / (2 × 1.96)。
  2. SE 随事件数按 1/sqrt(D) 缩放（C 指数差的标准误尺度性质），
     以全样本 D=5,636 为基准外推到小样本。
  3. 分辨极限 MDD80 = (1.96 + 0.8416) × SE。
  4. 排名识别率：把每次 bootstrap 的中心化偏差向量（由 10 个差值重构，
     加零均值约束使其唯一）按 sqrt(D_full/D) 放大后叠加到全样本 C 指数，
     统计「模拟研究中排名第一的指数是否就是真实第一」的概率。

输出：结果表\\加强\\resolution_floor.csv、resolution_rank.csv
"""
import os
import numpy as np
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
NPY = (r'c:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理'
       r'\age_compare\out\ext\_dc.npy')
OUTD = os.path.join(P, '结果表', '加强')

D_FULL = 5636.0                      # 全样本死亡数
N_FULL = 34393.0
EVT = D_FULL / N_FULL

# ---------- 1. 每对 SE ----------
eq = pd.read_csv(os.path.join(OUTD, 'equivalence_B1000.csv'))
eq['se'] = (eq.hi_pointwise - eq.lo_pointwise) / (2 * 1.96)
print('=== 全样本每对 SE（D=%d）===' % D_FULL)
print(eq[['pair', 'dC', 'se']].round(5).to_string(index=False))

# ---------- 2. 真实 C 指数 ----------
ci = pd.read_csv(os.path.join(P, '结果表', 'cindex_hr.csv'))
ci.columns = ['index', 'C', 'HR', 'lo', 'hi', 'p']
ci = ci.sort_values('C', ascending=False).reset_index(drop=True)
print('\n=== 全样本 C 指数 ===')
print(ci[['index', 'C']].round(4).to_string(index=False))
true_best = ci['index'][0]

# ---------- 3. 由 bootstrap 差值重构偏差向量 ----------
dc = np.load(NPY, allow_pickle=True).item()
pairs = list(dc.keys())
M = np.column_stack([np.asarray(dc[k], dtype=float) for k in pairs])   # 抽样 × 对
M = M - M.mean(axis=0, keepdims=True)                                   # 中心化

# 以 PhenoAge 为参照重构（差值 -> 绝对偏差，差一个常数，用零均值约束定住）
ref = 'PhenoAge'
names = ['PhenoAge', 'HD', 'AL', 'Dispersion', 'PC1']
idx = {n: i for i, n in enumerate(names)}


def diffs_of(a, b):
    """取 a-b 这一对的抽样列（自动匹配方向）"""
    for k in pairs:
        kk = k.replace('−', '-').replace('–', '-')
        if kk == '%s - %s' % (a, b):
            return M[:, pairs.index(k)]
        if kk == '%s - %s' % (b, a):
            return -M[:, pairs.index(k)]
    raise KeyError((a, b))


X = np.zeros((M.shape[0], len(names)))
for n in names:
    if n == ref:
        continue
    X[:, idx[n]] = -diffs_of(ref, n)      # x_n - x_ref
X = X - X.mean(axis=1, keepdims=True)     # 每次抽样内零均值约束（消除参照系自由度）
print('\n重构偏差矩阵: %d 抽样 × %d 指数；各指数 SD = %s'
      % (X.shape[0], X.shape[1], np.round(X.std(axis=0), 5)))

# ---------- 4. 分辨极限表 ----------
C_obs = ci.set_index('index').loc[names, 'C'].values
rows, rank_rows = [], []
for D in [50, 75, 100, 150, 200, 300, 500, 750, 1000, 2000, 5000, int(D_FULL)]:
    k = np.sqrt(D_FULL / D)
    se_med = float(eq.se.median()) * k
    se_min = float(eq.se.min()) * k
    se_max = float(eq.se.max()) * k
    # 排名识别
    Csim = C_obs[None, :] + k * X
    best = np.array(names)[Csim.argmax(axis=1)]
    p_top1 = float((best == true_best).mean())
    # 真实前二（PhenoAge > HD）的顺序是否被复现
    p_top2 = float((Csim[:, idx['PhenoAge']] > Csim[:, idx['HD']]).mean())
    rows.append(dict(deaths=int(D), n_approx=int(round(D / EVT)),
                     se_median=se_med, ci_halfwidth_95=1.96 * se_med,
                     mdd80=2.8016 * se_med,
                     se_min=se_min, se_max=se_max,
                     mdd80_tightest=2.8016 * se_min,
                     p_identify_true_best=p_top1,
                     p_correct_top2_order=p_top2))
    for n in names:
        rank_rows.append(dict(deaths=int(D), index=n,
                              p_rank1=float((best == n).mean())))

rf = pd.DataFrame(rows)
rk = pd.DataFrame(rank_rows)
rf.to_csv(os.path.join(OUTD, 'resolution_floor.csv'), index=False, encoding='utf-8-sig')
rk.to_csv(os.path.join(OUTD, 'resolution_rank.csv'), index=False, encoding='utf-8-sig')

print('\n=== 分辨极限 ===')
print(rf[['deaths', 'n_approx', 'se_median', 'ci_halfwidth_95', 'mdd80',
          'p_identify_true_best', 'p_correct_top2_order']].round(4).to_string(index=False))
print('\n=== 各死数下「被选为第一」的概率 ===')
print(rk.pivot(index='deaths', columns='index', values='p_rank1')
      .round(3).to_string())

print('\n输出 →', OUTD)

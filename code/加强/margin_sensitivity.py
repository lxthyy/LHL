# -*- coding: utf-8 -*-
"""
加强分析 1：等价边界的敏感性 + 10 对比较的多重性（同时置信带）
------------------------------------------------------------------
数据来源：直接复用已保存的配对 bootstrap 抽样
  _临时_可随意清理\\age_compare\\out\\ext\\_dc.npy（2026-10-28，300 次，与已发表结果同源）
因此本脚本不重跑 Cox、不重抽，只做两件已发表结果里没有的事：
  (1) 边界敏感性：±0.0025 / 0.005 / 0.01 / 0.015 / 0.02 / 0.03 六档，各档几对等价
  (2) 多重性控制：由同一批抽样构造 family-wise 同时置信带（10 对的最大偏差）
输出到 结果表\\加强\\，不改动任何既有结果表。
"""
import os
import numpy as np
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
NPY = (r'c:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理'
       r'\age_compare\out\ext\_dc.npy')
OUTD = os.path.join(P, '结果表', '加强')
os.makedirs(OUTD, exist_ok=True)

dc = np.load(NPY, allow_pickle=True).item()
pairs = list(dc.keys())
M = np.column_stack([np.asarray(dc[k], dtype=float) for k in pairs])
print('抽样矩阵: %d 对 × %d 次' % M.shape)
print('说明：所用抽样与已发表 equivalence.csv 同源（2026-10-28 保存）')

point = M.mean(axis=0)
print('\n=== 复现核对（应与已发表 Table 2 一致）===')
chk = pd.DataFrame({
    'pair': pairs, 'dC': point,
    'lo': np.percentile(M, 2.5, axis=0),
    'hi': np.percentile(M, 97.5, axis=0)})
print(chk.round(4).to_string(index=False))
chk.to_csv(os.path.join(OUTD, 'check_reproduce.csv'), index=False, encoding='utf-8-sig')

# ---- 同时置信带：每次抽样取 10 对中心化偏差的绝对值最大者 ----
centered = M - point
fw_half = float(np.percentile(np.abs(centered).max(axis=1), 95))
print('\nfamily-wise 95%% 半宽（同时置信带）= %.5f' % fw_half)

eq = pd.DataFrame({
    'pair': pairs, 'dC': point,
    'lo_pointwise': np.percentile(M, 2.5, axis=0),
    'hi_pointwise': np.percentile(M, 97.5, axis=0)})
eq['lo_simultaneous'] = eq.dC - fw_half
eq['hi_simultaneous'] = eq.dC + fw_half
eq['n_boot'] = M.shape[0]
eq.to_csv(os.path.join(OUTD, 'equivalence_simultaneous.csv'),
          index=False, encoding='utf-8-sig')

# ---- 边界敏感性 ----
MARGINS = [0.0025, 0.005, 0.01, 0.015, 0.02, 0.03]
grid, summ = [], []
for m in MARGINS:
    pw = (eq.lo_pointwise > -m) & (eq.hi_pointwise < m)
    sim = (eq.lo_simultaneous > -m) & (eq.hi_simultaneous < m)
    for i, r in eq.iterrows():
        grid.append(dict(margin=m, pair=r.pair, dC=r.dC,
                         eq_pointwise=bool(pw[i]), eq_simultaneous=bool(sim[i])))
    summ.append(dict(margin=m,
                     n_eq_pointwise=int(pw.sum()),
                     n_eq_simultaneous=int(sim.sum()),
                     pairs_pointwise='; '.join(eq.pair[pw].tolist())))
gs = pd.DataFrame(grid)
sm = pd.DataFrame(summ)
gs.to_csv(os.path.join(OUTD, 'margin_grid.csv'), index=False, encoding='utf-8-sig')
sm.to_csv(os.path.join(OUTD, 'margin_summary.csv'), index=False, encoding='utf-8-sig')

print('\n=== 边界敏感性：十对中几对等价 ===')
print(sm[['margin', 'n_eq_pointwise', 'n_eq_simultaneous']].to_string(index=False))
print('\n各档点态等价的对：')
for _, r in sm.iterrows():
    print('  ±%-6s %d 对  %s' % (r.margin, r.n_eq_pointwise, r.pairs_pointwise))

# ---- 顺带：暴露谱实际样本量 ----
rs = os.path.join(P, '结果表', 'response_spectrum.csv')
if os.path.exists(rs):
    sp = pd.read_csv(rs)
    ns = sp.groupby('exposure')['n'].agg(['min', 'max']).reset_index()
    ns.to_csv(os.path.join(OUTD, 'exposure_sample_sizes.csv'),
              index=False, encoding='utf-8-sig')
    print('\n=== 暴露谱实际样本量 ===')
    print(ns.to_string(index=False))

print('\n全部输出 →', OUTD)

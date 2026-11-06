# -*- coding: utf-8 -*-
"""
Figure 4：分辨极限（resolution floor）
--------------------------------------
横轴：死亡数（对数）
纵轴：C 指数差
实线：80% 把握可检出的最小差异（2.80 × SE）
虚线：95% 区间半宽（1.96 × SE）
横带：本文五个指标之间的真实差异全距（0.0008–0.0109）
灰底：高于全距的区域——任何研究在此区域都分辨不出真实差异
圆点：同时报告了死亡数与可比判别力差的审计研究
底部刻度：报告了死亡数的审计研究位置
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
OUT = os.path.join(P, '图表')
os.makedirs(OUT, exist_ok=True)

D_FULL = 5636.0
SE_MED = 0.00058

d = np.arange(50, 7000, 10)
se = SE_MED * np.sqrt(D_FULL / d)
mdd = 2.8016 * se
half = 1.96 * se

fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=300)

ax.axhspan(0.0109, 0.020, color='0.90', zorder=0)
ax.axhspan(0.0008, 0.0109, color='#dfe9f3', zorder=0)
ax.plot(d, mdd, color='#1f3b73', lw=2, label='Smallest detectable difference (80% power)')
ax.plot(d, half, color='#1f3b73', lw=1.2, ls='--', label='95% interval half-width')

ax.set_xscale('log')
ax.set_xlim(50, 7000)
ax.set_ylim(0, 0.020)
ax.set_xlabel('Number of deaths')
ax.set_ylabel('Difference in C-index')
ax.set_xticks([50, 100, 200, 500, 1000, 2000, 5000])
ax.set_xticklabels(['50', '100', '200', '500', '1000', '2000', '5000'])

# 审计研究：报告了死亡数的
stud = [('Provost 2025', 31658), ('Kuiper 2023', 132), ('Levine 2014', 1076),
        ('Li 2020', 389), ('Jiang 2024', 8508), ('Guida 2024', 167),
        ('Fohr 2023', 187), ('Vetter 2026', 90)]
for name, deaths in stud:
    if 50 <= deaths <= 7000:
        ax.plot([deaths], [0.0004], marker='|', ms=9, color='0.35', mew=1.4)

# 同时有死亡数与可比判别力差的三项
pts = [('Kuiper 2023', 132, 0.020), ('Levine 2014', 1076, 0.196),
       ('Jiang 2024', 8508, 0.020)]
for name, deaths, delta in pts:
    if deaths <= 7000 and delta <= 0.020:
        ax.plot([deaths], [delta], 'o', ms=5, color='#c0392b', zorder=5)
ax.annotate('Kuiper 2023', (132, 0.020), textcoords='offset points', xytext=(6, -3),
            fontsize=7, color='#c0392b')
ax.annotate('Jiang 2024', (7000, 0.020), textcoords='offset points', xytext=(-4, 5),
            fontsize=7, color='#c0392b', ha='right')

ax.text(60, 0.0013, 'Range of true differences\namong the five indices\n(0.0008–0.0109)',
        fontsize=7, color='#1f3b73', va='bottom')
ax.text(60, 0.0192, 'Differences no study of this size can resolve',
        fontsize=7, color='0.35', va='top')

ax.legend(loc='lower left', fontsize=7, frameon=False)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
fig.tight_layout()
for ext in ['png', 'pdf']:
    fig.savefig(os.path.join(OUT, 'Figure4_resolution_floor.' + ext))
print('saved ->', os.path.join(OUT, 'Figure4_resolution_floor.png'))

# -*- coding: utf-8 -*-
"""
Figure 4 v2：分辨极限（resolution floor）
--------------------------------------
v2 修复：
  - 移除重叠的底部刻度线（原 8 个挤成一团 → 保留 3 个代表）
  - x 轴扩大到 12000，让 Jiang 8508 能显示
  - 红点标注位置合理化
  - 新增 SVG 输出
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
OUT = os.path.join(P, '图表')
os.makedirs(OUT, exist_ok=True)

D_FULL = 5636.0
SE_MED = 0.00058

d = np.arange(50, 13000, 10)
se = SE_MED * np.sqrt(D_FULL / d)
mdd = 2.8016 * se
half = 1.96 * se

fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=300)

ax.axhspan(0.0109, 0.020, color='0.90', zorder=0)
ax.axhspan(0.0008, 0.0109, color='#dfe9f3', zorder=0)
ax.plot(d, mdd, color='#1f3b73', lw=2, label='Smallest detectable difference (80% power)')
ax.plot(d, half, color='#1f3b73', lw=1.2, ls='--', label='95% interval half-width')

ax.set_xscale('log')
ax.set_xlim(50, 12000)
ax.set_ylim(0, 0.020)
ax.set_xlabel('Number of deaths')
ax.set_ylabel('Difference in C-index')
ax.set_xticks([50, 100, 200, 500, 1000, 2000, 5000, 10000])
ax.set_xticklabels(['50', '100', '200', '500', '1000', '2000', '5000', '10000'])

# v2 修复：只保留 3 个代表研究（小样本/中样本/大样本），其余刻度线移除
stud_repr = [('Kuiper 2023', 132), ('Levine 2014', 1076), ('Jiang 2024', 8508)]
for name, deaths in stud_repr:
    ax.plot([deaths], [0.0004], marker='|', ms=10, color='0.35', mew=1.4)

# 三个红点（同时有死亡数和可比 C 指数差的审计研究）
pts = [('Kuiper 2023', 132, 0.020), ('Levine 2014', 1076, 0.013),
       ('Jiang 2024', 8508, 0.020)]
for name, deaths, delta in pts:
    ax.plot([deaths], [delta], 'o', ms=5, color='#c0392b', zorder=5)

# Kuiper 贴顶灰带里，右上标注
ax.annotate('Kuiper 2023', (132, 0.020), textcoords='offset points',
            xytext=(8, 5), fontsize=7, color='#c0392b')
# Levine 居中，下移到曲线下方 0.013 位置（图中真实 C-index delta）
ax.annotate('Levine 2014', (1076, 0.013), textcoords='offset points',
            xytext=(8, 5), fontsize=7, color='#c0392b')
# Jiang 贴顶灰带里，左对齐避免出图右边界
ax.annotate('Jiang 2024', (8508, 0.020), textcoords='offset points',
            xytext=(-4, 5), fontsize=7, color='#c0392b', ha='right')

ax.text(60, 0.0013, 'Range of true differences\namong the five indices\n(0.0008–0.0109)',
        fontsize=7, color='#1f3b73', va='bottom')
ax.text(60, 0.0192, 'Differences no study of this size can resolve',
        fontsize=7, color='0.35', va='top')

ax.legend(loc='lower left', fontsize=7, frameon=False)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
fig.tight_layout()

base = 'Figure4_resolution_floor_v2'
for ext in ['png', 'pdf', 'svg']:
    fig.savefig(os.path.join(OUT, base + '.' + ext))
print('saved ->', os.path.join(OUT, base + '.{png,pdf,svg}'))

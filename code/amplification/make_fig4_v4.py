# -*- coding: utf-8 -*-
"""
Figure 4 v4：分辨极限（resolution floor）
--------------------------------------
v4 相对 v3 的改动：
  · 图例增加两条标记说明，让"底部刻度线(ticks)"与"实心圆(filled circles)"
    的区分在图内可见，与图注一致：
       |  Audited comparison reporting a death count
       ●  … and a comparable discrimination difference
  · 输出 Figure4_resolution_floor_v4.{png,pdf,svg}
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

matplotlib.rcParams['svg.fonttype'] = 'none'
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
OUT = os.path.join(P, '图表')
os.makedirs(OUT, exist_ok=True)

D_FULL = 5636.0
SE_MED = 0.00058
POWER = 2.8016
Z = 1.96

d = np.arange(50, 15000, 10)
se = SE_MED * np.sqrt(D_FULL / d)
mdd = POWER * se
half = Z * se

Y_MAX = 0.028
Y_SPLIT = 0.0109
Y_FLOOR = 0.0008

fig, ax = plt.subplots(figsize=(7.0, 5.0), dpi=300)
fig.subplots_adjust(left=0.105, right=0.975, top=0.965, bottom=0.275)

ax.axhspan(Y_SPLIT, Y_MAX, color='0.91', zorder=0)
ax.axhspan(Y_FLOOR, Y_SPLIT, color='#dfe9f3', zorder=0)

l_mdd, = ax.plot(d, mdd, color='#1f3b73', lw=2.0, zorder=3,
                 label='Smallest detectable difference (80% power)')
l_half, = ax.plot(d, half, color='#1f3b73', lw=1.2, ls=(0, (5, 3)), zorder=3,
                  label='95% interval half-width')

ax.set_xscale('log')
ax.set_xlim(50, 15000)
ax.set_ylim(0, Y_MAX)
ax.set_xlabel('Number of deaths', fontsize=9)
ax.set_ylabel('Difference in C-index', fontsize=9)
ax.set_xticks([50, 100, 200, 500, 1000, 2000, 5000, 10000])
ax.set_xticklabels(['50', '100', '200', '500', '1000', '2000', '5000', '10000'])
ax.tick_params(axis='both', labelsize=8)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.spines['left'].set_color('0.35')
ax.spines['bottom'].set_color('0.35')

TICK_Y = 0.0003
studies = [
    ('Kuiper 2023', 132, 0.020, (300, 0.0242), 'left'),
    ('Levine 2014', 1076, 0.013, (1550, 0.0163), 'left'),
    ('Jiang 2024', 8508, 0.020, (2300, 0.0212), 'left'),
]

for name, deaths, delta, xytext, ha in studies:
    ax.plot([deaths], [TICK_Y], marker='|', ms=9, mew=1.5,
            color='0.35', zorder=4, clip_on=False)

for name, deaths, delta, xytext, ha in studies:
    ax.plot([deaths], [delta], 'o', ms=5.2, mfc='#c0392b', mec='white',
            mew=0.8, zorder=6)
    ax.annotate(name, xy=(deaths, delta), xytext=xytext,
                textcoords='data', ha=ha, va='bottom',
                fontsize=7.5, color='#a93226', zorder=7,
                arrowprops=dict(arrowstyle='-', lw=0.6, color='#a93226',
                                shrinkA=1, shrinkB=4,
                                connectionstyle='arc3,rad=0'))

ax.text(56, 0.0021,
        'Range of true differences among\nthe five indices (0.0008–0.0109)',
        fontsize=7.5, color='#1f3b73', va='bottom', ha='left', zorder=5)

ax.text(56, 0.0273,
        'Above this band no study of the given size can resolve any '
        'difference that exists',
        fontsize=7.5, color='0.32', va='top', ha='left', zorder=5)

# 标记图例（让 ticks 与 circles 的区分可见）
p_tick = Line2D([], [], marker='|', ls='none', ms=9, mew=1.5, color='0.35',
                label='Audited comparison reporting a death count')
p_circ = Line2D([], [], marker='o', ls='none', ms=5.2, mfc='#c0392b',
                mec='white', mew=0.8,
                label='… also reporting a comparable discrimination difference')

leg = ax.legend(handles=[l_mdd, l_half, p_tick, p_circ],
                loc='upper center', bbox_to_anchor=(0.5, -0.135),
                ncol=1, fontsize=7.8, frameon=False,
                handlelength=2.2, borderaxespad=0)

fig.savefig(os.path.join(OUT, 'Figure4_resolution_floor_v4.png'), dpi=600)
fig.savefig(os.path.join(OUT, 'Figure4_resolution_floor_v4.pdf'))
fig.savefig(os.path.join(OUT, 'Figure4_resolution_floor_v4.svg'))
print('saved ->', os.path.join(OUT, 'Figure4_resolution_floor_v4.{png,pdf,svg}'))

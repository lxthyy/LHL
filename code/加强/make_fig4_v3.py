# -*- coding: utf-8 -*-
"""
Figure 4 v3：分辨极限（resolution floor）
--------------------------------------
v3 修复（针对 v2 仍存在的重叠）：
  1. y 轴上限 0.020 → 0.028：Kuiper / Jiang 两个点原本贴在绘图区顶边上，
     标记与标注文字互相压、且被边框切掉
  2. 三处研究标签改为「数据坐标定位 + 引线」，各自落在空白区，不再叠在点上
  3. 顶部说明文字上移，与标签分离
  4. 图例移到图外底部（两列），不再压住左下角的说明文字与刻度线
  5. 底部刻度线上移到 0.0003，避免与 x 轴线重合
  6. SVG 用 svg.fonttype='none' 输出：文字仍是 <text> 元素，可在
     Illustrator / Inkscape 里直接改字，不会被转成路径

输出：Figure4_resolution_floor_v3.{svg,pdf,png}
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# SVG 文字保留为可编辑文本
matplotlib.rcParams['svg.fonttype'] = 'none'
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
OUT = os.path.join(P, '图表')
os.makedirs(OUT, exist_ok=True)

D_FULL = 5636.0          # 分析样本死亡数
SE_MED = 0.00058         # 十对 ΔC 的中位标准误（见 resolution_floor.csv）
POWER = 2.8016           # 双侧 α=0.05、80% power 的倍数
Z = 1.96

d = np.arange(50, 15000, 10)
se = SE_MED * np.sqrt(D_FULL / d)
mdd = POWER * se
half = Z * se

Y_MAX = 0.028
Y_SPLIT = 0.0109          # 五指数之间最大真实差异
Y_FLOOR = 0.0008          # 最小真实差异

fig, ax = plt.subplots(figsize=(7.0, 5.0), dpi=300)
fig.subplots_adjust(left=0.105, right=0.975, top=0.965, bottom=0.235)

# 两条背景带
ax.axhspan(Y_SPLIT, Y_MAX, color='0.91', zorder=0)
ax.axhspan(Y_FLOOR, Y_SPLIT, color='#dfe9f3', zorder=0)

ax.plot(d, mdd, color='#1f3b73', lw=2.0, zorder=3,
        label='Smallest detectable difference (80% power)')
ax.plot(d, half, color='#1f3b73', lw=1.2, ls=(0, (5, 3)), zorder=3,
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

# ---- 三个代表研究：底部刻度线（表示该研究报告的死亡数） ----
TICK_Y = 0.0003
studies = [
    # (标签, 死亡数, 该研究的 ΔC 或 None, 标签落点, 对齐)
    ('Kuiper 2023', 132, 0.020, (300, 0.0242), 'left'),
    ('Levine 2014', 1076, 0.013, (1550, 0.0163), 'left'),
    ('Jiang 2024', 8508, 0.020, (2300, 0.0212), 'left'),
]

for name, deaths, delta, xytext, ha in studies:
    ax.plot([deaths], [TICK_Y], marker='|', ms=9, mew=1.5,
            color='0.35', zorder=4, clip_on=False)

# 填充圆点：既报了死亡数、又报了可比 C 指数差的三项
for name, deaths, delta, xytext, ha in studies:
    ax.plot([deaths], [delta], 'o', ms=5.2, mfc='#c0392b', mec='white',
            mew=0.8, zorder=6)
    ax.annotate(name, xy=(deaths, delta), xytext=xytext,
                textcoords='data', ha=ha, va='bottom',
                fontsize=7.5, color='#a93226', zorder=7,
                arrowprops=dict(arrowstyle='-', lw=0.6, color='#a93226',
                                shrinkA=1, shrinkB=4,
                                connectionstyle='arc3,rad=0'))

# ---- 图内说明文字（放在空白处，互不重叠） ----
ax.text(56, 0.0021,
        'Range of true differences among\nthe five indices (0.0008–0.0109)',
        fontsize=7.5, color='#1f3b73', va='bottom', ha='left', zorder=5)

ax.text(56, 0.0273,
        'Above this band no study of the given size can resolve any '
        'difference that exists',
        fontsize=7.5, color='0.32', va='top', ha='left', zorder=5)

# 图例挪到图外底部，两列
leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.155),
                ncol=1, fontsize=7.8, frameon=False,
                handlelength=2.2, borderaxespad=0)

fig.savefig(os.path.join(OUT, 'Figure4_resolution_floor_v3.png'), dpi=600)
fig.savefig(os.path.join(OUT, 'Figure4_resolution_floor_v3.pdf'))
fig.savefig(os.path.join(OUT, 'Figure4_resolution_floor_v3.svg'))
print('saved ->', os.path.join(OUT, 'Figure4_resolution_floor_v3.{png,pdf,svg}'))

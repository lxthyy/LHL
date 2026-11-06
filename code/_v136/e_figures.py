# -*- coding: utf-8 -*-
"""v1.36: 重绘 Figure 1（cluster-bootstrap 区间）与 Figure 4（解析 + 经验）"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
OUT = os.path.join(P, '结果表', '_v136')
FIG = os.path.join(P, '图表')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'axes.linewidth': 0.8, 'pdf.fonttype': 42})

# ---------------- Figure 1 ----------------
eq = pd.read_csv(os.path.join(OUT, 'equivalence_cluster_boot1000.csv'), encoding='utf-8-sig')
eq['equiv'] = (eq.lo > -0.01) & (eq.hi < 0.01)
eq = eq.iloc[::-1].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.axvspan(-0.01, 0.01, color='0.9', zorder=0)
for x in (-0.01, 0.01):
    ax.axvline(x, color='0.45', ls='--', lw=0.8, zorder=1)
ax.axvline(0, color='0.2', lw=0.8, zorder=1)
y = np.arange(len(eq))
for i, r in eq.iterrows():
    col = '#2c6fbb' if r.equiv else '#b03a2e'
    ax.plot([r.lo, r.hi], [y[i], y[i]], color=col, lw=1.2, zorder=3)
    ax.plot(r.dC, y[i], 'o', color=col, ms=4.5, zorder=4)
    ax.text(0.0165, y[i], '%.4f' % r.dC, va='center', ha='left', fontsize=7.5, color=col)
ax.set_yticks(y)
ax.set_yticklabels(eq.pair, fontsize=8)
ax.set_xlim(-0.016, 0.0205)
ax.set_xlabel('Difference in C-index (95% cluster-bootstrap CI)')
ax.text(0.0, len(eq) - 0.2, 'equivalence margin ±0.01', ha='center', va='bottom',
        fontsize=7.5, color='0.35')
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], color='#2c6fbb', marker='o', ls='-', ms=4, label='equivalent'),
                   Line2D([], [], color='#b03a2e', marker='o', ls='-', ms=4, label='not equivalent')],
          loc='lower right', frameon=False, fontsize=7.5)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
for ext in ('pdf', 'png', 'svg'):
    fig.savefig(os.path.join(FIG, 'Figure1_equivalence_forest_v1.36.' + ext), dpi=600)
plt.close(fig)

# ---------------- Figure 4 ----------------
rf = pd.read_csv(os.path.join(P, '结果表', '加强', 'resolution_floor.csv'), encoding='utf-8-sig')
emp = pd.read_csv(os.path.join(OUT, 'resolution_floor_empirical.csv'), encoding='utf-8-sig')
emp = emp[emp.deaths_target < 5636]   # 全集点无抽样变异，不画
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.axhspan(0.0008, 0.0108, color='0.9', zorder=0)
ax.text(60, 0.0062, 'range of true differences among\nthe five indices (0.0008–0.0108)',
        fontsize=7, color='0.35', va='center')
ax.plot(rf.deaths, rf.mdd80, '-', color='#1f4e79', lw=1.6, label='Smallest detectable difference (80% power)')
ax.plot(rf.deaths, rf.ci_halfwidth_95, '--', color='#7f7f7f', lw=1.1, label='95% interval half-width')
ax.plot(emp.deaths_target, emp.mdd80_empirical, 'o', color='#b03a2e', ms=4.5,
        label='Empirical (subsampling)')
for d, lab in [(132, 'Kuiper 2023'), (1076, 'Levine 2014'), (8508, 'Jiang 2024')]:
    ax.axvline(d, color='0.55', lw=0.7, ls=':', ymax=0.12)
    ax.text(d, 0.0006, lab, rotation=90, fontsize=6.5, color='0.4', ha='right', va='bottom')
ax.set_xscale('log')
ax.set_xlim(45, 12000)
ax.set_ylim(0, 0.021)
ax.set_xlabel('Number of deaths')
ax.set_ylabel('Difference in C-index')
ax.legend(frameon=False, fontsize=7, loc='upper right')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
for ext in ('pdf', 'png', 'svg'):
    fig.savefig(os.path.join(FIG, 'Figure4_resolution_floor_v1.36.' + ext), dpi=600)
plt.close(fig)
print('figures written')

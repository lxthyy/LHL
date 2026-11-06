# -*- coding: utf-8 -*-
"""v1.37 Figure 1：区间换 jackknife，并把图例移到左上以消除标签重叠"""
import os, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
FIG = os.path.join(P, '图表')
UP = os.path.join(P, '待上传')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'axes.linewidth': 0.8, 'pdf.fonttype': 42})

eq = pd.read_csv(os.path.join(P, '结果表', '_v136', 'jackknife_equivalence.csv'))
eq = eq.rename(columns={'se_jack': 'se'})
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
ax.set_xlim(-0.016, 0.0215)
ax.set_ylim(-0.8, len(eq) - 0.2)
ax.set_xlabel('Difference in C-index (95% jackknife CI; shaded band = ±0.01 margin)')
ax.legend(handles=[Line2D([], [], color='#2c6fbb', marker='o', ls='-', ms=4, label='equivalent'),
                   Line2D([], [], color='#b03a2e', marker='o', ls='-', ms=4, label='not equivalent')],
          loc='lower center', bbox_to_anchor=(0.5, 1.005), ncol=2, frameon=False, fontsize=7.5)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
for ext in ('pdf', 'png', 'svg'):
    fig.savefig(os.path.join(FIG, 'Figure1_equivalence_forest_v1.37.' + ext), dpi=600)
plt.close(fig)

# 备份旧上传件并替换
old = os.path.join(UP, 'Figure1_equivalence_forest.pdf')
bak = os.path.join(P, '_历史版本', 'v1.36_上传件', 'Figure1_equivalence_forest.pdf')
os.makedirs(os.path.dirname(bak), exist_ok=True)
if os.path.exists(old) and not os.path.exists(bak):
    shutil.copy2(old, bak)
shutil.copy2(os.path.join(FIG, 'Figure1_equivalence_forest_v1.37.pdf'), old)
print('Figure1 v1.37 written and swapped')

# 即时几何复核
import fitz
pg = fitz.open(old)[0]
spans = [(s['bbox'], s['text'].strip(), s['size']) for b in pg.get_text('dict')['blocks']
         for l in b.get('lines', []) for s in l['spans'] if s['text'].strip()]
ov = []
for i in range(len(spans)):
    for j in range(i + 1, len(spans)):
        a, b = spans[i][0], spans[j][0]
        x0, y0 = max(a[0], b[0]), max(a[1], b[1])
        x1, y1 = min(a[2], b[2]), min(a[3], b[3])
        ia = max(0, x1 - x0) * max(0, y1 - y0)
        ar = lambda z: max(0, z[2] - z[0]) * max(0, z[3] - z[1])
        if ia > 1 and ia / max(min(ar(a), ar(b)), 1e-6) > 0.10:
            ov.append((spans[i][1][:18], spans[j][1][:18], round(ia, 1)))
print('text-text overlaps:', len(ov), ov[:3])
print('min font size:', min(s[2] for s in spans), 'spans:', len(spans))

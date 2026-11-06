# -*- coding: utf-8 -*-
"""v1.05 图 1/图 2：用 5 次复现的 r1 结果重绘，输出到投稿包图表目录（另存 v1.01）"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SRC = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\rep\r1\out\ext'
FIG = (r'C:\Users\lxddz\Desktop\科研稿件总库\C_初稿与算法_2篇\28_衰老指数对比_未定刊'
       r'\Age and Ageing\图表')
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 7.5,
    'axes.linewidth': 0.6, 'axes.edgecolor': '#333333',
    'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
    'xtick.major.size': 3, 'ytick.major.size': 3,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'savefig.bbox': 'tight',
})
C_RED, C_GREEN = '#C0392B', '#2E8B57'


def save(fig, name):
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(FIG, '%s.%s' % (name, ext)),
                    dpi=400 if ext == 'png' else None)
    plt.close(fig)
    print('  ->', os.path.join(FIG, name))


# ================= Figure 1 等价性森林图 =================
eq = pd.read_csv(os.path.join(SRC, 'equivalence.csv'), encoding='utf-8-sig')
eq = eq.iloc[::-1].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(3.5, 3.2))
ax.add_patch(Rectangle((-0.01, -0.6), 0.02, len(eq) - 0.4, color='#E8EEF4', zorder=0))
ax.axvline(0, color='#555555', lw=0.7, zorder=1)
for i, r in eq.iterrows():
    c = C_GREEN if r['等价'] == '是' else C_RED
    ax.plot([r.lo, r.hi], [i, i], color=c, lw=1.2, solid_capstyle='round', zorder=2)
    ax.plot(r.dC, i, 'o', color=c, ms=4.2, zorder=3)
ax.set_yticks(range(len(eq)))
ax.set_yticklabels(eq['比较'], fontsize=7)
ax.set_xlim(-0.011, 0.019)
ax.set_xlabel('Difference in C-index (95% CI)')
ax.text(0.0, len(eq) - 0.30, 'equivalence margin ±0.01', ha='center', va='bottom',
        fontsize=6.3, color='#4A6572')
ax.plot([], [], 'o', color=C_GREEN, ms=4, label='equivalent')
ax.plot([], [], 'o', color=C_RED, ms=4, label='not equivalent')
ax.legend(frameon=False, fontsize=6.2, loc='lower right', handletextpad=0.3)
ax.spines[['top', 'right']].set_visible(False)
ax.tick_params(axis='y', length=0)
for i, r in eq.iterrows():
    ax.text(0.0187, i, '%.4f' % r.dC, ha='right', va='center', fontsize=6.2, color='#333333')
save(fig, 'Figure1_equivalence_forest_v1.01')

# ================= Figure 2 死因别（1999–2014） =================
cs = pd.read_csv(os.path.join(SRC, 'cause_specific.csv'), encoding='utf-8-sig')
order = ['PhenoAge', 'HD', 'Dispersion', 'AL', 'PC1']
causes = ['心血管', '肿瘤', '呼吸']
cen = {'心血管': 'Cardiovascular', '肿瘤': 'Cancer', '呼吸': 'Respiratory'}
H = cs.pivot(index='指数', columns='结局', values='HR').loc[order, causes]
P = cs.pivot(index='指数', columns='结局', values='p').loc[order, causes]
Lo = cs.pivot(index='指数', columns='结局', values='lo').loc[order, causes]
Hi = cs.pivot(index='指数', columns='结局', values='hi').loc[order, causes]

fig, ax = plt.subplots(figsize=(2.9, 3.3))
im = ax.imshow(H.values, cmap='RdYlBu_r', vmin=1.0, vmax=1.8, aspect='auto')
for i in range(H.shape[0]):
    for j in range(H.shape[1]):
        v, p = H.values[i, j], P.values[i, j]
        star = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
        col = 'white' if v > 1.45 else '#111111'
        ax.text(j, i - 0.16, '%.2f' % v, ha='center', va='center', fontsize=7.6,
                color=col, fontweight='bold')
        ax.text(j, i + 0.06, '%.2f–%.2f' % (Lo.values[i, j], Hi.values[i, j]),
                ha='center', va='center', fontsize=5.4, color=col)
        ax.text(j, i + 0.26, star, ha='center', va='center', fontsize=6.2, color=col)
ax.set_xticks(range(3))
ax.set_xticklabels([cen[c] for c in causes], fontsize=7)
ax.set_yticks(range(5))
ax.set_yticklabels(order, fontsize=7.5)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
cb.set_label('HR per 1 SD', fontsize=6.8)
cb.ax.tick_params(labelsize=6)
cb.outline.set_linewidth(0.4)
ax.set_title('Cause-specific mortality, 1999–2014\n(n=25,680; 5,360 deaths)',
             fontsize=6.8, pad=5)
save(fig, 'Figure2_cause_specific_v1.01')
print('\n完成')

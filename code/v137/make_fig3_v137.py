# -*- coding: utf-8 -*-
"""v1.05 配套：重绘 Figure 3 / S1 / S2（数据取 5 次复现的 r1），另存 v1.01"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SRC = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\rep\r1\out\ext'
PKG = r'c:\Users\lxddz\Desktop\LHL_投稿包_v1.36\图表'

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 7.8,
                     'axes.linewidth': 0.6, 'axes.edgecolor': '#333333',
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
                     'pdf.fonttype': 42, 'savefig.bbox': 'tight'})
C_BLUE, C_RED, C_GREY = '#2C6FAC', '#C0392B', '#9AA0A6'
order = ['PhenoAge', 'HD', 'Dispersion', 'AL', 'PC1']


def save(fig, name):
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(PKG, '%s.%s' % (name, ext)),
                    dpi=400 if ext == 'png' else None)
    plt.close(fig)
    print('  ->', name)


# ---------------- Figure 3：两暴露对比点图 ----------------
sp = pd.read_csv(os.path.join(SRC, 'response_spectrum.csv'), encoding='utf-8-sig')
SER = [('Current smoking', C_RED, 'o', 'Current smoking'),
       ('Physical activity', C_BLUE, 's', 'Physical activity')]
fig, ax = plt.subplots(figsize=(4.75, 3.43))
x = np.arange(len(order))
for k, (exp, col, mk, lab) in enumerate(SER):
    g = sp[sp.exposure == exp].set_index('index').loc[order]
    off = -0.12 if k == 0 else 0.12
    ax.errorbar(x + off, g.beta, yerr=[g.beta - g.lo, g.hi - g.beta], fmt=mk,
                ms=4, lw=0, elinewidth=1.0, capsize=2, color=col, label=lab)
    for xi, v in zip(x + off, g.beta):
        ax.annotate('%.2f' % v, (xi, v), textcoords='offset points',
                    xytext=(0, 6 if k == 0 else -11), ha='center', fontsize=6.03,
                    color=col)
ax.axhline(0, color='#777777', lw=0.6, ls=':')
ax.set_xticks(x)
ax.set_xticklabels(order, fontsize=7.80)
ax.set_ylabel('Standardised β per unit exposure')
ax.set_xlim(-0.6, len(order) - 0.4)
ax.legend(frameon=False, fontsize=6.76, loc='upper right', ncol=1)
ax.spines[['top', 'right']].set_visible(False)
save(fig, 'Figure3_exposure_profile_v1.37')

# ---------------- Figure S1：校准 + 决策曲线 ----------------
cd = pd.read_csv(os.path.join(SRC, 'calibration_deciles.csv'), encoding='utf-8-sig')
dc = pd.read_csv(os.path.join(SRC, 'dca.csv'), encoding='utf-8-sig')
fig, axes = plt.subplots(1, 2, figsize=(9.24, 3.83))
ax = axes[0]
ax.plot([0, 0.7], [0, 0.7], ls='--', lw=0.7, color=C_GREY, label='Perfect calibration')
for m, (mk, col, lab) in {'PhenoAge': ('o', C_BLUE, 'PhenoAge'),
                          'PhenoAge+disp': ('s', C_RED, 'PhenoAge + dispersion')}.items():
    g = cd[cd['模型'] == m].sort_values('预测')
    ax.plot(g['预测'], g['观察'], marker=mk, ms=3.4, lw=1.0, color=col, label=lab)
ax.set_xlabel('Predicted 10-year mortality')
ax.set_ylabel('Observed 10-year mortality (weighted KM)')
ax.set_xlim(0, 0.7)
ax.set_ylim(0, 0.7)
ax.legend(frameon=False, fontsize=6.55, loc='upper left')
ax.set_title('A   Calibration', loc='left', fontsize=8.32, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)
ax = axes[1]
for m, col, lab in [('PhenoAge', C_BLUE, 'PhenoAge'),
                    ('PhenoAge+disp', C_RED, 'PhenoAge + dispersion'),
                    ('全部干预', C_GREY, 'Treat all')]:
    g = dc[dc['模型'] == m].sort_values('阈值')
    ax.plot(g['阈值'], g['净收益'], marker='o', ms=3.2, lw=1.0, color=col, label=lab)
ax.axhline(0, color='#999999', lw=0.6, ls=':')
ax.set_xlabel('Threshold probability')
ax.set_ylabel('Net benefit per 1,000 (10 y)')
ax.legend(frameon=False, fontsize=6.55, loc='lower left')
ax.set_title('B   Decision curve', loc='left', fontsize=8.32, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)
save(fig, 'FigureS1_calibration_dca_v1.37')

# ---------------- Figure S2：全暴露谱热图 ----------------
sp2 = pd.read_csv(os.path.join(SRC, 'response_spectrum.csv'), encoding='utf-8-sig')
expo = ['Current smoking', 'Physical activity', 'BMI',
        'Income-to-poverty ratio', 'Education']
expo_lbl = ['Current smoking', 'Physical activity', 'BMI', 'Income-to-poverty', 'Education']
cols = ['PhenoAge', 'HD', 'Dispersion', 'AL', 'PC1']
B = sp2.pivot(index='exposure', columns='index', values='beta').loc[expo, cols]
Pp = sp2.pivot(index='exposure', columns='index', values='p').loc[expo, cols]
fig, ax = plt.subplots(figsize=(4.49, 3.70))
vmax = float(np.nanmax(np.abs(B.values)))
im = ax.imshow(B.values, cmap='RdBu_r', vmin=-vmax, vmax=vmax, aspect='auto')
for i in range(B.shape[0]):
    for j in range(B.shape[1]):
        v, p = B.values[i, j], Pp.values[i, j]
        star = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        txt = '%.2f' % v + ('\n' + star if star else '\nn.s.')
        col = 'white' if abs(v) > 0.55 * vmax else '#111111'
        ax.text(j, i, txt, ha='center', va='center', fontsize=6.66, color=col)
ax.set_xticks(range(len(cols)))
ax.set_xticklabels(cols, fontsize=7.28, rotation=30, ha='right')
ax.set_yticks(range(len(expo)))
ax.set_yticklabels(expo_lbl, fontsize=7.28)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
cb.set_label('Standardised β per unit exposure', fontsize=6.55)
cb.ax.tick_params(labelsize=6)
cb.outline.set_linewidth(0.4)
save(fig, 'FigureS2_full_exposure_spectrum_v1.37')
print('完成 ->', PKG)

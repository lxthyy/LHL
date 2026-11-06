# -*- coding: utf-8 -*-
"""Figure 3 重绘：字号 ≥6 pt，图例移到图外，避免与数值标签相撞"""
import os, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import fitz

P = r'c:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
FIG = os.path.join(P, '图表')
UP = os.path.join(P, '待上传')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.2,
                     'axes.linewidth': 0.7, 'pdf.fonttype': 42, 'savefig.bbox': 'tight'})
C_BLUE, C_RED = '#2C6FAC', '#C0392B'
order = ['PhenoAge', 'HD', 'Dispersion', 'AL', 'PC1']

sp = pd.read_csv(os.path.join(P, '结果表', 'response_spectrum.csv'), encoding='utf-8-sig')
SER = [('Current smoking', C_RED, 'o'), ('Physical activity', C_BLUE, 's')]

fig, ax = plt.subplots(figsize=(4.2, 2.9))
x = np.arange(len(order))
for k, (exp, col, mk) in enumerate(SER):
    g = sp[sp.exposure == exp].set_index('index').loc[order]
    off = -0.12 if k == 0 else 0.12
    ax.errorbar(x + off, g.beta, yerr=[g.beta - g.lo, g.hi - g.beta], fmt=mk,
                ms=4, lw=0, elinewidth=1.0, capsize=2, color=col, label=exp)
    for xi, v in zip(x + off, g.beta):
        ax.annotate('%.2f' % v, (xi, v), textcoords='offset points',
                    xytext=(0, 7 if k == 0 else -12), ha='center',
                    fontsize=6.4, color=col)
ax.axhline(0, color='#777777', lw=0.6, ls=':')
ax.set_xticks(x)
ax.set_xticklabels(order, fontsize=8.0)
ax.set_ylabel('Standardised β per unit exposure', fontsize=8.4)
ax.set_xlim(-0.6, len(order) - 0.4)
ax.legend(frameon=False, fontsize=7.6, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=2)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
for ext in ('pdf', 'png', 'svg'):
    fig.savefig(os.path.join(FIG, 'Figure3_exposure_profile_v1.37.' + ext), dpi=600)
plt.close(fig)

pg = fitz.open(os.path.join(FIG, 'Figure3_exposure_profile_v1.37.pdf'))[0]
spn = [(s['bbox'], s['text'].strip(), s['size']) for b in pg.get_text('dict')['blocks']
       for l in b.get('lines', []) for s in l['spans'] if s['text'].strip()]
mn = min(x[2] for x in spn)
ov = []
for i in range(len(spn)):
    for j in range(i + 1, len(spn)):
        a, b = spn[i][0], spn[j][0]
        x0, y0 = max(a[0], b[0]), max(a[1], b[1])
        x1, y1 = min(a[2], b[2]), min(a[3], b[3])
        ia = max(0, x1 - x0) * max(0, y1 - y0)
        ar = lambda z: max(0, z[2] - z[0]) * max(0, z[3] - z[1])
        if ia > 1 and ia / max(min(ar(a), ar(b)), 1e-6) > 0.10:
            ov.append((spn[i][1][:16], spn[j][1][:16], round(ia, 1)))
print('min pt = %.2f | overlaps = %d | w_cm = %.2f' % (mn, len(ov), pg.rect.width / 28.35))
if ov:
    print('  ', ov[:3])
if mn >= 6.0 and not ov:
    shutil.copy2(os.path.join(FIG, 'Figure3_exposure_profile_v1.37.pdf'),
                 os.path.join(UP, 'Figure3_exposure_profile.pdf'))
    print('SWAPPED')
else:
    print('NOT swapped')

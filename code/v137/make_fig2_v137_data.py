# -*- coding: utf-8 -*-
"""Figure 2 用冻结的 cause_specific.csv 重画（与表 2 Panel C 逐位一致）"""
import os, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import fitz

P = r'c:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
FIG = os.path.join(P, '图表')
UP = os.path.join(P, '待上传')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'axes.linewidth': 0.7, 'pdf.fonttype': 42, 'savefig.bbox': 'tight'})

d = pd.read_csv(os.path.join(P, '结果表', 'cause_specific.csv'))
rows = ['PhenoAge', 'HD', 'Dispersion', 'AL', 'PC1']
label = {'PhenoAge': 'PhenoAge', 'HD': 'Homeostatic\ndysregulation',
         'Dispersion': 'Inter-organ\ndispersion', 'AL': 'Allostatic load', 'PC1': 'PC1'}
cols = ['心血管', '肿瘤', '呼吸']
cname = {'心血管': 'Cardiovascular\n(1,685 deaths)', '肿瘤': 'Cancer\n(1,194 deaths)',
         '呼吸': 'Respiratory\n(428 deaths)'}

def star(p):
    if p < 0.001: return '***'
    if p < 0.01: return '**'
    if p < 0.05: return '*'
    return 'n.s.'

M = np.zeros((len(rows), len(cols)))
for i, r in enumerate(rows):
    for j, c in enumerate(cols):
        M[i, j] = d[(d['指数'] == r) & (d['结局'] == c)].HR.iloc[0]

fig, ax = plt.subplots(figsize=(5.6, 4.3))
im = ax.imshow(M, cmap='Reds', vmin=1.0, vmax=1.8, aspect='auto')
for i, r in enumerate(rows):
    for j, c in enumerate(cols):
        row = d[(d['指数'] == r) & (d['结局'] == c)].iloc[0]
        txt = 'white' if row.HR > 1.55 else '#222222'
        ax.text(j, i - 0.16, '%.2f' % row.HR, ha='center', va='center',
                fontsize=9.0, color=txt, fontweight='bold')
        ax.text(j, i + 0.10, '%.2f–%.2f' % (row.lo, row.hi), ha='center', va='center',
                fontsize=7.6, color=txt)
        ax.text(j, i + 0.32, star(row.p), ha='center', va='center',
                fontsize=7.6, color=txt)
ax.set_xticks(range(len(cols)))
ax.set_xticklabels([cname[c] for c in cols], fontsize=8.2)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([label[r] for r in rows], fontsize=8.2)
ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True)
ax.set_yticks(np.arange(-.5, len(rows), 1), minor=True)
ax.grid(which='minor', color='white', lw=1.2)
ax.tick_params(which='minor', length=0)
cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cb.set_label('HR per 1 SD', fontsize=8.0)
ax.set_title('Cause-specific mortality, 1999–2014\n(n = 25,678; 5,360 deaths)',
             fontsize=8.6, pad=8)
fig.tight_layout()
for ext in ('pdf', 'png', 'svg'):
    fig.savefig(os.path.join(FIG, 'Figure2_cause_specific_v1.37.' + ext), dpi=600)
plt.close(fig)

pg = fitz.open(os.path.join(FIG, 'Figure2_cause_specific_v1.37.pdf'))[0]
sp = [(s['bbox'], s['text'].strip(), s['size']) for b in pg.get_text('dict')['blocks']
      for l in b.get('lines', []) for s in l['spans'] if s['text'].strip()]
mn = min(x[2] for x in sp)
ov = 0
for i in range(len(sp)):
    for j in range(i + 1, len(sp)):
        a, b = sp[i][0], sp[j][0]
        x0, y0 = max(a[0], b[0]), max(a[1], b[1])
        x1, y1 = min(a[2], b[2]), min(a[3], b[3])
        ia = max(0, x1 - x0) * max(0, y1 - y0)
        ar = lambda z: max(0, z[2] - z[0]) * max(0, z[3] - z[1])
        if ia > 1 and ia / max(min(ar(a), ar(b)), 1e-6) > 0.10:
            ov += 1
print('min pt = %.2f | overlaps = %d | w_cm = %.2f' % (mn, ov, pg.rect.width / 28.35))
print('n=25,678 in text:', '25,678' in pg.get_text('text'))
if mn >= 6.0 and ov == 0:
    up = os.path.join(UP, 'Figure2_cause_specific.pdf')
    shutil.copy2(os.path.join(FIG, 'Figure2_cause_specific_v1.37.pdf'), up)
    print('SWAPPED')
else:
    print('NOT swapped')

# -*- coding: utf-8 -*-
"""用冻结表重建 Table 2（v1.06）：Panel A/B/C 全部按 CSV 生成，Panel D 原样保留"""
import os
import re
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
T = os.path.join(P, '表格')
R = os.path.join(P, '结果表')

ci = pd.read_csv(os.path.join(R, 'cindex_hr.csv'), encoding='utf-8-sig')
wh = pd.read_csv(os.path.join(R, 'weighted_hr.csv'), encoding='utf-8-sig')
eq = pd.read_csv(os.path.join(R, 'equivalence.csv'), encoding='utf-8-sig')
cs = pd.read_csv(os.path.join(R, 'cause_specific.csv'), encoding='utf-8-sig')

NAME = {'PhenoAge': 'PhenoAge', 'HD': 'Homeostatic dysregulation',
        'Dispersion': 'Inter-organ dispersion', 'AL': 'Allostatic load', 'PC1': 'PC1'}
ORDER = ['PhenoAge', 'HD', 'Dispersion', 'AL', 'PC1']

old = open(os.path.join(T, 'Table2_v1.05.md'), encoding='utf-8').read()
panelD = old[old.index('## Panel D'):]

L = []
L.append('# Table 2 (v1.06)\n')
L.append('**Table 2.** Discrimination, equivalence and cause-specific estimates for '
         'laboratory ageing indices (NHANES 1999–2018). Panels A–C are generated directly '
         'from the frozen result tables (`cindex_hr.csv`, `weighted_hr.csv`, '
         '`equivalence.csv`, `cause_specific.csv`); v1.06 corrects every interval that had '
         'drifted from those files.\n')

L.append('## Panel A. All-cause discrimination and hazard ratios (n = 34,393; 5,636 deaths)\n')
L.append('| Index | C-index | Weighted HR per 1 SD (95% CI) |')
L.append('|---|---|---|')
for k in ORDER:
    a = ci[ci['指数'] == k].iloc[0]
    b = wh[wh['指数'] == k].iloc[0]
    L.append('| %s | %.3f | %.2f (%.2f–%.2f) |' % (
        NAME[k], a['C指数'], b['HR_w'], b['lo'], b['hi']))
L.append('')

L.append('## Panel B. Pairwise equivalence (paired bootstrap, 300 resamples; margin ±0.01)\n')
L.append('| Comparison | ΔC-index (95% CI) | Equivalent |')
L.append('|---|---|---|')
for _, r in eq.iterrows():
    yn = 'Yes' if str(r['等价']).strip() == '是' else 'No'
    fmt = lambda v: ('%.4f' % v).replace('-', '\u2212')
    L.append('| %s | %s (%s to %s) | %s |' % (
        r['比较'], fmt(r['dC']), fmt(r['lo']), fmt(r['hi']), yn))
L.append('')

L.append('## Panel C. Cause-specific hazard ratios (1999–2014; n = 25,678; 5,360 deaths)\n')
L.append('| Index | Cardiovascular (1,685) | Cancer (1,194) | Respiratory (428) |')
L.append('|---|---|---|---|')
for k in ORDER:
    cells = []
    for oc in ['心血管', '肿瘤', '呼吸']:
        r = cs[(cs['结局'] == oc) & (cs['指数'] == k)].iloc[0]
        cells.append('%.2f (%.2f–%.2f)' % (r['HR'], r['lo'], r['hi']))
    L.append('| %s | %s | %s | %s |' % (NAME[k], cells[0], cells[1], cells[2]))
L.append('')

note = old[old.index('Notes. All estimates are weighted'):old.index('## Panel D')]
L.append(note.rstrip())
L.append('')
L.append(panelD)

out = '\n'.join(L)
open(os.path.join(T, 'Table2_v1.06.md'), 'w', encoding='utf-8').write(out)
print('Table2_v1.06.md written')
print(out[:1200])

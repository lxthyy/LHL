# -*- coding: utf-8 -*-
"""v1.25 → v1.26：加年代切分结果；补充表升 v1.14（含 S13）"""
import os
import re
import shutil

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
SRC = os.path.join(P, '正文', 'Manuscript_v1.25.md')
DST = os.path.join(P, '正文', 'Manuscript_v1.26.md')
s = open(SRC, encoding='utf-8').read()

s = s.replace('# Manuscript v1.25 — target', '# Manuscript v1.26 — target', 1)
s = s.replace('**Changes from v1.24 —',
              '**Changes from v1.25 — era-split sensitivity added (Results, Table S13).** '
              'Repeating the equivalence analysis within assay eras reproduced the pattern '
              'where deaths were sufficient and could not decide where they were not.\n\n'
              '**Changes from v1.24 —', 1)

INS = ('Repeating the analysis within assay eras gave the same picture: in 1999–2010 '
       '(25,678 participants, 5,360 deaths) 8 of 10 pairs were equivalent at ±0.01 and '
       'all 10 at ±0.015; in 2011–2018 (8,715 participants, 276 deaths) the intervals '
       'were too wide to decide, as the floor predicts (Table S13).\n\n')

REP = [
    ('with a rank correlation of 1.000000.\n\n',
     'with a rank correlation of 1.000000.\n\n' + INS),
    ('Calibration was assessed at ten years by the ratio of observed to expected events, by\n'
     'a calibration slope, and by the absolute deviation in deciles.',
     'Calibration at ten years used observed-to-expected ratios, a slope and decile\n'
     'deviations.'),
    ('Our cohort spans eight survey cycles and two decades, which is what made the\n'
     'cross-cycle standardisation possible.',
     'Eight cycles over two decades made the cross-cycle standardisation possible.'),
]
miss = []
for a, b in REP:
    if a in s:
        s = s.replace(a, b, 1)
    else:
        miss.append(a[:50])
open(DST, 'w', encoding='utf-8').write(s)
print('未命中:', miss)


def wc(t):
    t = re.sub(r'[#*_\[\]\(\)>]', ' ', t)
    return len([w for w in t.split() if re.search(r'[A-Za-z0-9]', w)])


print('正文:', wc(s[s.index('## Introduction'):s.index('## Figure legends')]))

# --- Table S13 ---
import pandas as pd
R = pd.read_csv(os.path.join(P, '结果表', '加强', 'era_split_equivalence.csv'),
                encoding='utf-8-sig')
L = ['**Table S13.** Equivalence of the five ageing indices within assay eras.\n',
     'Paired differences in C-index with 95% bootstrap intervals (200 resamples of '
     'individuals, linear predictors fixed). Equivalence is declared when the interval '
     'lies wholly inside the stated margin.\n',
     '| Era | n | Deaths | Pair | C-index (A) | C-index (B) | Difference | 95% CI | '
     '±0.01 | ±0.015 |',
     '|---|---|---|---|---|---|---|---|---|---|']
for _, r in R.iterrows():
    L.append('| %s | %d | %d | %s | %.4f | %.4f | %.4f | %.4f to %.4f | %s | %s |' % (
        r.era, r.n, r.deaths, r['pair'], r.c_a, r.c_b, r['diff'], r.lo, r.hi,
        'yes' if r['eq_0.01'] else 'no', 'yes' if r['eq_0.015'] else 'no'))
L.append('')
L.append('1999–2010: 3, 8 and 10 of 10 pairs equivalent at margins of ±0.005, ±0.01 and '
         '±0.015. 2011–2018 contains three indices only (PhenoAge and HD require CRP, not '
         'measured after 2010) and 276 deaths, giving a resolution floor of about 0.0074, '
         'so a ±0.01 decision is not informative in that era.')
L.append('')
L.append('These are subsamples of the same survey, not an independent cohort: they test '
         'transfer across assay platforms and population composition, not across countries.')
L.append('')
L.append('Source: `代码\\加强\\era_split.py`; `结果表\\加强\\era_split_equivalence.csv`.')
open(os.path.join(P, '表格', 'TableS13_era_split.md'), 'w', encoding='utf-8').write('\n'.join(L))

sup = os.path.join(P, '补充材料')
src = os.path.join(sup, 'Supplementary_Tables_v1.13.md')
dst = os.path.join(sup, 'Supplementary_Tables_v1.14.md')
t = open(src, encoding='utf-8').read()
t = t.replace('# Supplementary Tables v1.13 (S1–S12)',
              '# Supplementary Tables v1.14 (S1–S13)', 1)
t = t.replace('Companion to Manuscript v1.24', 'Companion to Manuscript v1.26')
t = t.rstrip() + '\n\n---\n\n## Table S13. Equivalence within assay eras\n\n' + '\n'.join(L) + '\n'
open(dst, 'w', encoding='utf-8').write(t)
print('补充表 -> v1.14（S1–S13）')

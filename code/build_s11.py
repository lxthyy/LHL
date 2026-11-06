# -*- coding: utf-8 -*-
"""生成补充材料 v1.10（在 v1.09 基础上加 S11：22 篇审计全表 + 原文句子）"""
import os
import re
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
MR = os.path.join(P, 'meta_research')
SUP = os.path.join(P, '补充材料')

cand = pd.read_csv(os.path.join(MR, 'candidates.csv'), encoding='utf-8-sig')
old = open(os.path.join(SUP, 'Supplementary_Tables_v1.09.md'), encoding='utf-8').read()

head = ('# Supplementary Tables v1.10 (S1–S11)\n\n'
        'Companion to Manuscript v1.21. All values are reproducible from the frozen\n'
        'tables in `results/`; see the number-provenance table supplied with this\n'
        'submission. **v1.10 adds Table S11** (the full audit of 22 head-to-head\n'
        'comparisons, with the source sentence for every extracted value) and does not\n'
        'alter any earlier table.\n')
body = old.split('\n', 1)[1]

# ---- S11a：结构表 ----
lines = []
lines.append('---\n')
lines.append('## Table S11. Head-to-head comparisons of biological age indices with a mortality outcome (n = 22)\n')
lines.append('### S11a. Study-level summary\n')
lines.append('| Study | Cohort (country) | Participants | Deaths | Indices compared | Largest difference | Margin stated | Difference tested |')
lines.append('|---|---|---|---|---|---|---|---|')
for _, r in cand.iterrows():
    name = '%s %s' % (str(r.first_author).split()[0], r.year)
    diff = 'NR' if str(r.delta).strip() == 'NR' else '%s %s' % (r.delta, r.delta_units)
    lines.append('| %s | %s (%s) | %s | %s | %s | %s | %s | %s |' % (
        name, r.cohort, r.country, r.n_analysed, r.n_deaths,
        str(r.indices_compared).replace('|', '/'), diff,
        r.equivalence_margin, r.formal_difference_test))
lines.append('')
lines.append('NR = not reported numerically in the source; such values were recorded as not '
             'reported rather than estimated. "Largest difference" is the largest within-study '
             'gap between the best and worst index on the scale the study used; hazard-ratio '
             'differences are not comparable across studies with different instruments and '
             'adjustment sets. No study stated an equivalence or non-inferiority margin.')
lines.append('')

# ---- S11b：原文句子 ----
lines.append('### S11b. Source sentence for every extracted value\n')
lines.append('| Study | Source sentence (verbatim) |')
lines.append('|---|---|')
for _, r in cand.iterrows():
    name = '%s %s' % (str(r.first_author).split()[0], r.year)
    note = str(r.extraction_note).replace('|', '/').replace('\n', ' ')
    lines.append('| %s | %s |' % (name, note))
lines.append('')
lines.append('Source: `meta_research/candidates.csv`; extraction by a single reviewer, each '
             'value checked against the sentence above. The search was structured, not a '
             'PRISMA-compliant systematic review.')
lines.append('')

out = head + '\n' + body.rstrip() + '\n\n' + '\n'.join(lines)
path = os.path.join(SUP, 'Supplementary_Tables_v1.10.md')
open(path, 'w', encoding='utf-8').write(out)
print('written:', path, len(out), 'chars')

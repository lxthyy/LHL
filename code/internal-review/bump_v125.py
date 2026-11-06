# -*- coding: utf-8 -*-
"""v1.24 → v1.25：按审稿人意见降级标题、加 rho 敏感性与留一周期结果"""
import os
import re

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
SRC = os.path.join(P, '正文', 'Manuscript_v1.24.md')
DST = os.path.join(P, '正文', 'Manuscript_v1.25.md')
s = open(SRC, encoding='utf-8').read()

s = s.replace('# Manuscript v1.24 — target', '# Manuscript v1.25 — target', 1)
s = s.replace('**Changes from v1.23 —',
              '**Changes from v1.24 — two analyses requested by an adversarial review. '
              'Both change what the paper is entitled to claim:**\n'
              '1. The resolution floor is not fixed: it depends on how strongly the two '
              'scores correlate. At 100 deaths it falls from 0.0138 (ρ 0.16) to 0.0100 '
              '(ρ 0.56), so the earlier claim that it exceeds every real difference holds '
              'only below ρ ≈ 0.45. **The title is downgraded accordingly.**\n'
              '2. Leaving out any one of the eight cycles left the ranking unchanged in all '
              'eight analyses. The ranking is therefore stable *within* one survey system; '
              'what fails to replicate is its transport across cohorts, not its estimation.\n\n'
              '**Changes from v1.23 —', 1)

REP = [
    # 标题
    ('**Below the resolution of the studies that report it: equivalence analysis of five\n'
     'biological age indices in 34,393 US adults and audit of 22 head-to-head comparisons**',
     '**The resolution of a comparison depends on how correlated the two scores are:\n'
     'equivalence analysis of five biological age indices in 34,393 US adults and audit of\n'
     '22 head-to-head comparisons**'),
    # 摘要
    ('The resolution floor was 0.0124\nat 100 deaths — larger than every difference among the\n'
     'five indices — and 0.0017 at 5,636 deaths.',
     'The resolution floor at 100 deaths was 0.0124 for scores correlating at the median of\n'
     'this set, 0.0100 for the most correlated pair and 0.0138 for the least, and 0.0017 at\n'
     '5,636 deaths.'),
    # 结果：rho 敏感性
    ('At 100 deaths the floor is **0.0124 C-index units** — larger than the largest difference\n'
     'that exists among these five indices (0.0109).',
     'At 100 deaths the floor is **0.0124 C-index units** for scores correlating at the median\n'
     'of this set (ρ 0.36); it falls to 0.0100 for the most correlated pair (ρ 0.56) — below\n'
     'the largest difference that exists among these five indices (0.0109) — and rises to\n'
     '0.0138 at ρ 0.16.'),
    # 讨论：留一周期
    ('A ranking is therefore not a stable property of the\n'
     'indices; it is a property of the cohort.',
     'Within one survey system the ranking is in fact stable: dropping any one of the eight\n'
     'cycles left the order unchanged in all eight analyses. A ranking is therefore not a\n'
     'property of the indices in general, but of the cohort in which they are measured.'),
    # 压缩
    ('This is, to our knowledge, the first head-to-head comparison of these five constructions\n'
     'under one design. ', ''),
    ('usually\nin one cohort and with superiority testing [13,14]', 'with superiority testing [13,14]'),
    ('(O:E 0.974–0.978; slope 1.00, 95% CI\n0.88–1.12; decile deviation 0.004–0.005)',
     '(O:E 0.974–0.978; slope 1.00; decile deviation 0.004–0.005)'),
    ('across four selection specifications C-indices\nstayed within 0.003 (Table S7); hazard ratios were more sensitive to era than to\n'
     'selection — HD was 1.53 in 1999–2010 and 1.67 in 2005–2018.',
     'across four selection specifications C-indices\nstayed within 0.003 (Table S7); HD\'s hazard ratio was 1.53 in 1999–2010 and 1.67 in\n'
     '2005–2018.'),
    ('NHANES is a public, de-identified dataset;\nthe study was exempt from ethics review, and the analysis follows STROBE [20].',
     'NHANES is public and de-identified;\nthe study was exempt from ethics review and follows STROBE [20].'),
    ('In 34,393 adults followed for up to twenty years, five laboratory-derived ageing indices\n'
     'were interchangeable for all-cause mortality:',
     'In 34,393 adults followed for up to twenty years, the five indices were interchangeable\n'
     'for all-cause mortality:'),
]
miss = []
for a, b in REP:
    if a in s:
        s = s.replace(a, b, 1)
    else:
        miss.append(a[:60])
open(DST, 'w', encoding='utf-8').write(s)
print('未命中替换:', len(miss))
for m in miss:
    print('  !', m)


def wc(t):
    t = re.sub(r'[#*_\[\]\(\)>]', ' ', t)
    return len([w for w in t.split() if re.search(r'[A-Za-z0-9]', w)])


print('正文:', wc(s[s.index('## Introduction'):s.index('## Figure legends')]))
print('摘要:', wc(s[s.index('## Abstract'):s.index('**Research in context**')]))

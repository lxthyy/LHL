# -*- coding: utf-8 -*-
"""STROBE 清单 v1.01 → v1.02：只换稿件标题，条目内容不动"""
import os

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
src = os.path.join(P, 'STROBE清单_v1.01.md')
dst = os.path.join(P, 'STROBE清单_v1.02.md')
s = open(src, encoding='utf-8').read()

old_titles = [
    'Equivalence, not superiority: a comparison framework for candidate\nbiomarkers, applied to five laboratory ageing indices in 34,393 US adults',
    'Equivalence, not superiority: a comparison framework for candidate biomarkers, applied to five laboratory ageing indices in 34,393 US adults',
]
new_title = ('Below the resolution of the studies that report it: equivalence analysis of\n'
             'five biological age indices in 34,393 US adults and audit of 22 head-to-head\n'
             'comparisons')
hit = False
for t in old_titles:
    if t in s:
        s = s.replace(t, new_title)
        hit = True
s = s.replace('# STROBE 清单 v1.01', '# STROBE 清单 v1.02', 1)
s = s.replace('# STROBE Checklist (v1.01, English)', '# STROBE Checklist (v1.02, English)', 1)
s = s.replace('(Manuscript v1.15)', '(Manuscript v1.21)', 1)
s = s.replace(
    'Design: repeated cross-sectional surveys (NHANES 1999–2018) with linked\n'
    'mortality follow-up',
    'Design: repeated cross-sectional surveys (NHANES 1999–2018) with linked\n'
    'mortality follow-up\n'
    'Note: the literature audit (Methods, "Literature audit") is a review of published\n'
    'studies and is not covered by STROBE items; its conduct is described in Methods and\n'
    'its extraction table is Supplementary Table S11.', 1)
open(dst, 'w', encoding='utf-8').write(s)
print('title replaced:', hit)
print('written:', dst)
print(s[:400])

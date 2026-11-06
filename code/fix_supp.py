# -*- coding: utf-8 -*-
"""补充方法 v1.01 → v1.02（换题、去 JCE、升版本）；补充表 v1.10 去掉重复的 v1.20 行"""
import os

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
SUP = os.path.join(P, '补充材料')

# ---- 1) 补充方法 ----
src = os.path.join(SUP, 'Supplementary_Methods_v1.01.md')
dst = os.path.join(SUP, 'Supplementary_Methods_v1.02.md')
s = open(src, encoding='utf-8').read()
old_head = """# Supplementary Methods v1.01

Companion to: *Equivalence, not superiority: a comparison framework for candidate
biomarkers, applied to five laboratory ageing indices in 34,393 US adults*
(Manuscript v1.18, JCE)

Changes from v1.00: the manuscript reference is updated to v1.18, and the handling
of education codes 7 and 9 is now stated here (S1) instead of in the main Methods,
where it was moved out to meet the 3,000-word limit. No analysis changed.
"""
new_head = """# Supplementary Methods v1.02

Companion to: *Below the resolution of the studies that report it: equivalence analysis
of five biological age indices in 34,393 US adults and audit of 22 head-to-head
comparisons* (Manuscript v1.21, The Lancet Healthy Longevity)

Changes from v1.01: manuscript reference updated to v1.21 and the target journal
changed. The handling of education codes 7 and 9 remains stated here (S1). **No
analysis, formula or number changed.**
"""
if old_head in s:
    s = s.replace(old_head, new_head)
    print('methods head replaced')
else:
    print('!! methods head NOT matched')
open(dst, 'w', encoding='utf-8').write(s)

# ---- 2) 补充表 v1.10 去掉重复的 Companion 行 ----
t = os.path.join(SUP, 'Supplementary_Tables_v1.10.md')
x = open(t, encoding='utf-8').read()
dup = 'Companion to Manuscript v1.20. All values are reproducible from the frozen\n'
if dup in x:
    x = x.replace(dup, '', 1)
    open(t, 'w', encoding='utf-8').write(x)
    print('tables dup line removed')
else:
    print('!! tables dup line NOT found')
print(repr(x[:260]))

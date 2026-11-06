# -*- coding: utf-8 -*-
"""v1.26：插入年代段（正确锚点）+ 自动压到 3500 以内"""
import os
import re

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
F = os.path.join(P, '正文', 'Manuscript_v1.26.md')
s = open(F, encoding='utf-8').read()


def wc(t):
    t = re.sub(r'[#*_\[\]\(\)>]', ' ', t)
    return len([w for w in t.split() if re.search(r'[A-Za-z0-9]', w)])


def body(x):
    return wc(x[x.index('## Introduction'):x.index('## Figure legends')])


INS = ('Within assay eras the pattern held: 1999\u20132010 (25,678; 5,360 deaths) gave 8 of '
       '10 equivalent pairs at \u00b10.01; 2011\u20132018 was too sparse to decide (Table S13).')

if 'Within assay eras' not in s:
    s, n = re.subn(r'(stayed within\s+0\.003 \(Table S7\));',
                   r'\1.\n\n' + INS + '\n', s, count=1)
    print('插入:', n)
open(F, 'w', encoding='utf-8').write(s)
print('插入后正文:', body(s))

TRIM = [
    (r'less than any margin discussed here', 'below any margin here'),
    (r' the five indices were interchangeable for all-cause mortality',
     ' the five indices were interchangeable'),
    (r'followed for up to twenty years', 'followed up to twenty years'),
    (r'All five indices were well calibrated at ten years',
     'All five were well calibrated at ten years'),
    (r'The principal component reproduced across cycles \(Table S4\); proportional hazards held',
     'The principal component reproduced across cycles (Table S4); hazards held'),
]
for a, b in TRIM:
    if body(s) <= 3499:
        break
    s, k = re.subn(a, b, s, count=1)
    print('trim %s -> %d' % (k, body(s)))

open(F, 'w', encoding='utf-8').write(s)
print('最终正文:', body(s), '摘要:', wc(s[s.index('## Abstract'):s.index('**Research in context**')]))

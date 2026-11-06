# -*- coding: utf-8 -*-
"""补充表 v1.10 → v1.11（仅把 Companion 版本号改为 v1.22），并生成清单 v1.04"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from md2docx import md_to_docx

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
SUP = os.path.join(P, '补充材料')
UP = os.path.join(P, '待上传')

src = os.path.join(SUP, 'Supplementary_Tables_v1.10.md')
dst = os.path.join(SUP, 'Supplementary_Tables_v1.11.md')
s = open(src, encoding='utf-8').read()
s = s.replace('# Supplementary Tables v1.10 (S1–S11)',
              '# Supplementary Tables v1.11 (S1–S11)', 1)
s = s.replace('Companion to Manuscript v1.21.', 'Companion to Manuscript v1.22.', 1)
open(dst, 'w', encoding='utf-8').write(s)
print('md v1.11 written')

md_to_docx(dst, os.path.join(UP, 'Supplementary_Tables_v1.11.docx'))

# 清单 v1.03 → v1.04
c3 = os.path.join(P, '投稿包清单_v1.03.md')
c4 = os.path.join(P, '投稿包清单_v1.04.md')
t = open(c3, encoding='utf-8').read()
t = t.replace('# 投稿包清单 v1.03', '# 投稿包清单 v1.04', 1)
t = t.replace('Supplementary_Tables_v1.10.docx', 'Supplementary_Tables_v1.11.docx')
t = t.replace('补充材料\\Supplementary_Tables_v1.10.md',
              '补充材料\\Supplementary_Tables_v1.11.md')
t = t.replace('| 9 | `Supplementary_Tables_v1.11.docx` | 补充表 S1–S11 |',
              '| 9 | `Supplementary_Tables_v1.11.docx` | 补充表 S1–S11（仅版本号随正文 v1.22 同步） |')
open(c4, 'w', encoding='utf-8').write(t)
print('checklist v1.04 written')

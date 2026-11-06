# -*- coding: utf-8 -*-
"""投稿包清单 v1.02 → v1.03"""
import os

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
src = os.path.join(P, '投稿包清单_v1.02.md')
dst = os.path.join(P, '投稿包清单_v1.03.md')
s = open(src, encoding='utf-8').read()

rep = [
    ('# 投稿包清单 v1.02', '# 投稿包清单 v1.03'),
    ('正文版本：Manuscript v1.21　　包内最新 docx：Manuscript_v1.21.docx',
     '正文版本：Manuscript v1.22　　包内最新 docx：Manuscript_v1.22.docx'),
    ('Manuscript_v1.21.docx', 'Manuscript_v1.22.docx'),
    ('正文\\Manuscript_v1.21.md', '正文\\Manuscript_v1.22.md'),
    ('Title_Page_v1.06.docx', 'Title_Page_v1.07.docx'),
    ('正文\\标题页_v1.06.md', '正文\\标题页_v1.07.md'),
    ('| **v1.02** | **2026-11-04** |',
     '| v1.02 | 2026-11-04 |'),
]
for a, b in rep:
    s = s.replace(a, b)

row = ('| **v1.03** | **2026-11-04** | 正文 v1.22：新增 Box（五项最小报告集）、'
       'Results 增加「4/8 篇不足 200 例死亡」段、摘要 Interpretation 重写；标题页 v1.07 |')
if 'v1.03' not in s.split('## 四、版本记录')[-1]:
    s = s.rstrip() + '\n' + row + '\n'

open(dst, 'w', encoding='utf-8').write(s)
print('written:', dst)
print('leftover v1.21:', 'Manuscript_v1.21' in s, '| leftover v1.06:', 'Title_Page_v1.06' in s)

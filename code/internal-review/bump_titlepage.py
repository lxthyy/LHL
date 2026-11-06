# -*- coding: utf-8 -*-
"""终检前的收尾：标题页升 v1.09，归档旧件"""
import os
import re
import shutil

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
H = os.path.join(P, '_历史版本', 'JCE时期_20261030')

src = os.path.join(P, '正文', '标题页_v1.08.md')
dst = os.path.join(P, '正文', '标题页_v1.09.md')
s = open(src, encoding='utf-8').read()
s = s.replace('v1.08', 'v1.09')
open(dst, 'w', encoding='utf-8').write(s)
print('标题页 -> v1.09')

q = os.path.join(P, '代码', 'build_docx.py')
t = open(q, encoding='utf-8').read()
t = t.replace('标题页_v1.08.md', '标题页_v1.09.md').replace(
    'Title_Page_v1.08.docx', 'Title_Page_v1.09.docx')
open(q, 'w', encoding='utf-8').write(t)

for rel in [r'正文\标题页_v1.08.md', r'待上传\Title_Page_v1.08.docx']:
    f = os.path.join(P, rel)
    if os.path.exists(f):
        shutil.move(f, os.path.join(H, os.path.basename(f)))
        print('archived', os.path.basename(f))

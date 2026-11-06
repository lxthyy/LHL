# -*- coding: utf-8 -*-
"""归档 v1.22 时期的旧件到 _历史版本"""
import os
import shutil

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
H = os.path.join(P, '_历史版本', 'JCE时期_20261030')
os.makedirs(H, exist_ok=True)

items = [
    r'待上传\Manuscript_v1.22.docx', r'待上传\Title_Page_v1.07.docx',
    r'待上传\Supplementary_Tables_v1.11.docx', r'待上传\Cover_Letter_LHL_v1.00.docx',
    r'正文\Manuscript_v1.22.md', r'正文\标题页_v1.07.md',
    r'补充材料\Supplementary_Tables_v1.11.md', r'投稿信\Cover_Letter_LHL_v1.00.md',
    r'表格\Table2_v1.05.md', r'表格\Table4_resolution_floor.md',
]
for it in items:
    s = os.path.join(P, it)
    if os.path.exists(s):
        shutil.move(s, os.path.join(H, os.path.basename(s)))
        print('archived', it)
    else:
        print('skip(not found)', it)

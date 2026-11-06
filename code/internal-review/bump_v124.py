# -*- coding: utf-8 -*-
"""v1.23 → v1.24（年龄 SD 18.2→18.1），并重建 docx"""
import os
import shutil

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
H = os.path.join(P, '_历史版本', 'JCE时期_20261030')
SRC = os.path.join(P, '正文', 'Manuscript_v1.23.md')
DST = os.path.join(P, '正文', 'Manuscript_v1.24.md')

s = open(SRC, encoding='utf-8').read()
s = s.replace('# Manuscript v1.23 — target', '# Manuscript v1.24 — target', 1)
s = s.replace('**Changes from v1.22 — numerical audit corrections.',
              '**Changes from v1.23 — one correction found while documenting derived numbers: '
              'the standard deviation of age is 18.1 years (unweighted), not 18.2. '
              'Weighted SD is 16.7; the manuscript reports unweighted descriptives, '
              'consistent with Table 1.**\n\n'
              '**Changes from v1.22 — numerical audit corrections.', 1)
open(DST, 'w', encoding='utf-8').write(s)
print('written', DST)

# 旧 v1.23 归档
shutil.move(SRC, os.path.join(H, 'Manuscript_v1.23.md'))
docx_old = os.path.join(P, '待上传', 'Manuscript_v1.23.docx')
if os.path.exists(docx_old):
    shutil.move(docx_old, os.path.join(H, 'Manuscript_v1.23.docx'))
print('archived v1.23')

# 更新 build_docx 与 build_manifest
for f, a, b in [
    ('build_docx.py', 'Manuscript_v1.23.md', 'Manuscript_v1.24.md'),
    ('build_docx.py', 'Manuscript_v1.23.docx', 'Manuscript_v1.24.docx'),
    ('build_manifest.py', 'Manuscript_v1.23.docx', 'Manuscript_v1.24.docx'),
    ('build_manifest.py', r'正文\Manuscript_v1.23.md', r'正文\Manuscript_v1.24.md'),
]:
    p = os.path.join(P, '代码', f)
    t = open(p, encoding='utf-8').read()
    t = t.replace(a, b)
    open(p, 'w', encoding='utf-8').write(t)
print('build scripts updated')

# -*- coding: utf-8 -*-
"""v1.35 -> v1.36 全包改名 + 重建 docx"""
import os, sys, shutil
sys.path.insert(0, r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36\代码')
from md2docx_v2 import md_to_docx

P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
H = os.path.join(P, '_历史版本')
UP = os.path.join(P, '待上传')

def mv(a, b):
    if os.path.exists(a):
        os.makedirs(os.path.dirname(b), exist_ok=True)
        if os.path.exists(b):
            os.remove(b)
        os.rename(a, b)
        print('  ', os.path.relpath(a, P), '->', os.path.relpath(b, P))

for sub, names in {
    '正文': ['Manuscript', '标题页'],
    '表格': ['Table1', 'Table2', 'Table3', 'Table4'],
    '补充材料': ['Supplementary_Methods', 'Supplementary_Tables'],
    '投稿信': ['Cover_Letter_LHL'],
}.items():
    for n in names:
        mv(os.path.join(P, sub, f'{n}_v1.35.md'), os.path.join(P, sub, f'{n}_v1.36.md'))

for n in ['STROBE清单', '利益冲突声明', '00_目标刊格式要求_LancetHealthyLongevity',
          '返修接手说明', '复现说明', '投稿包清单', '数字溯源对照']:
    mv(os.path.join(P, f'{n}_v1.35.md'), os.path.join(P, f'{n}_v1.36.md'))
mv(os.path.join(P, '环境清单_v1.35.txt'), os.path.join(P, '环境清单_v1.36.txt'))

parts = []
for f in ['Table1_v1.36.md', 'Table2_v1.36.md', 'Table3_v1.36.md', 'Table4_v1.36.md']:
    parts.append(open(os.path.join(P, '表格', f), encoding='utf-8').read().strip())
tmp = os.path.join(P, '_临时', 'Tables_v1.36.md')
os.makedirs(os.path.dirname(tmp), exist_ok=True)
open(tmp, 'w', encoding='utf-8').write('\n\n'.join(parts))

jobs = [
    ('正文\\Manuscript_v1.36.md', 'Manuscript_v1.36.docx',
     dict(start_marker='**The resolution of a comparison depends on')),
    (tmp, 'Tables_v1.36.docx', {}),
    ('补充材料\\Supplementary_Tables_v1.36.md', 'Supplementary_Tables_v1.36.docx', {}),
    ('补充材料\\Supplementary_Methods_v1.36.md', 'Supplementary_Methods_v1.36.docx', {}),
    ('投稿信\\Cover_Letter_LHL_v1.36.md', 'Cover_Letter_LHL_v1.36.docx', {}),
    ('正文\\标题页_v1.36.md', 'Title_Page_v1.36.docx', {}),
    ('STROBE清单_v1.36.md', 'STROBE_checklist_v1.36.docx', {}),
]
for src, name, kw in jobs:
    md_to_docx(os.path.join(P, src), os.path.join(UP, name), **kw)

mv(os.path.join(UP, 'Declaration_of_Interest_v1.35.docx'),
   os.path.join(UP, 'Declaration_of_Interest_v1.36.docx'))
for old in ['Manuscript_v1.35.docx', 'Title_Page_v1.35.docx', 'Tables_v1.35.docx',
            'Supplementary_Methods_v1.35.docx', 'Supplementary_Tables_v1.35.docx',
            'STROBE_checklist_v1.35.docx', 'Cover_Letter_LHL_v1.35.docx']:
    p = os.path.join(UP, old)
    if os.path.exists(p):
        os.remove(p)
        print('   remove', old)

print('\n待上传：')
for f in sorted(os.listdir(UP)):
    print('  ', f)

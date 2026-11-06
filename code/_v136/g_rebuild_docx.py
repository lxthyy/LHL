# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36\代码')
from md2docx_v2 import md_to_docx
P = r'C:\Users\lxddz\Desktop\LHL_投稿包_v1.36'
UP = os.path.join(P, '待上传')
parts = []
for f in ['Table1_v1.36.md', 'Table2_v1.36.md', 'Table3_v1.36.md', 'Table4_v1.36.md']:
    parts.append(open(os.path.join(P, '表格', f), encoding='utf-8').read().strip())
tmp = os.path.join(P, '_临时', 'Tables_v1.36.md')
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
print('done')

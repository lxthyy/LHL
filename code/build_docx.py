# -*- coding: utf-8 -*-
"""把 v1.21 正文、表 1–4、补充表 v1.10、投稿信转成 DOCX（上标文献编号）"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from md2docx import md_to_docx

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
UP = os.path.join(P, '待上传')
TMP = os.path.join(P, '_临时')
os.makedirs(UP, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# 1) 正文
md_to_docx(os.path.join(P, '正文', 'Manuscript_v1.26.md'),
           os.path.join(UP, 'Manuscript_v1.26.docx'),
           start_marker='**Below the resolution of the studies that')

# 2) 表 1–4 合成一份
parts = []
for f, tag in [('Table1_v1.01.md', None), ('Table2_v1.06.md', None),
               ('Table3_literature_audit.md', None), ('Table4_v1.01.md', None)]:
    txt = open(os.path.join(P, '表格', f), encoding='utf-8').read().strip()
    parts.append(txt)
combined = '\n\n'.join(parts)
tmp_md = os.path.join(TMP, 'Tables_v1.21.md')
open(tmp_md, 'w', encoding='utf-8').write(combined)
md_to_docx(tmp_md, os.path.join(UP, 'Tables_v1.21.docx'))

# 3) 补充表
md_to_docx(os.path.join(P, '补充材料', 'Supplementary_Tables_v1.14.md'),
           os.path.join(UP, 'Supplementary_Tables_v1.14.docx'))

# 4) 补充方法
md_to_docx(os.path.join(P, '补充材料', 'Supplementary_Methods_v1.02.md'),
           os.path.join(UP, 'Supplementary_Methods_v1.02.docx'))

# 5) 投稿信
md_to_docx(os.path.join(P, '投稿信', 'Cover_Letter_LHL_v1.01.md'),
           os.path.join(UP, 'Cover_Letter_LHL_v1.01.docx'))

# 6) 标题页
md_to_docx(os.path.join(P, '正文', '标题页_v1.08.md'),
           os.path.join(UP, 'Title_Page_v1.08.docx'))

# 7) 利益冲突声明
md_to_docx(os.path.join(P, '利益冲突声明_v1.03.md'),
           os.path.join(UP, 'Declaration_of_Interest_v1.03.docx'))

# 8) STROBE 清单
md_to_docx(os.path.join(P, 'STROBE清单_v1.02.md'),
           os.path.join(UP, 'STROBE_checklist_v1.02.docx'))

print('done')

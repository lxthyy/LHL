# -*- coding: utf-8 -*-
"""build_docx_v2.py —— Lancet Healthy Longevity 专用
------------------------------------------------
  - 正文 start_marker 跳到 Abstract 前，跳过 changelog
  - 所有文件用 md2docx_v2（三线表 + 自动跳过 changelog/Source/版本号标题）
  - 输出统一放 待上传\，文件名按 Elsevier 英文命名

v2.01（2026-11-05）：源文件版本升级
  Manuscript v1.26->v1.27 / 标题页 v1.08->v1.09 / Table1 v1.01->v1.02
  Table2 v1.06->v1.07 / Table3 ->v1.01 / STROBE v1.02->v1.03
  Supplementary_Tables v1.14->v1.15
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from md2docx_v2 import md_to_docx

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
UP = os.path.join(P, '待上传')
TMP = os.path.join(P, '_临时')
os.makedirs(UP, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

print('=== build_docx_v2.py: Lancet-ready DOCX generation ===')
print(f'Package: {P}')
print(f'Output:  {UP}\n')

# 1) 正文 — 跳过 changelog
md_to_docx(
    os.path.join(P, '正文', 'Manuscript_v1.33.md'),
    os.path.join(UP, 'Manuscript_v1.33.docx'),
    start_marker='**The resolution of a comparison depends on')

# 2) 表 1–4 合成一份 Tables 文件（三线表）
parts = []
for f in ['Table1_v1.02.md', 'Table2_v1.07.md',
          'Table3_v1.03.md', 'Table4_v1.02.md']:
    txt = open(os.path.join(P, '表格', f), encoding='utf-8').read().strip()
    parts.append(txt)
combined = '\n\n'.join(parts)
tmp_md = os.path.join(TMP, 'Tables_v2.05.md')
open(tmp_md, 'w', encoding='utf-8').write(combined)
md_to_docx(tmp_md, os.path.join(UP, 'Tables_v2.05.docx'))

# 3) 补充表（S1-S13）
md_to_docx(
    os.path.join(P, '补充材料', 'Supplementary_Tables_v1.18.md'),
    os.path.join(UP, 'Supplementary_Tables_v1.18.docx'))

# 4) 补充方法
md_to_docx(
    os.path.join(P, '补充材料', 'Supplementary_Methods_v1.04.md'),
    os.path.join(UP, 'Supplementary_Methods_v1.04.docx'))

# 5) 投稿信
md_to_docx(
    os.path.join(P, '投稿信', 'Cover_Letter_LHL_v1.05.md'),
    os.path.join(UP, 'Cover_Letter_LHL_v1.05.docx'))

# 6) 标题页
md_to_docx(
    os.path.join(P, '正文', '标题页_v1.13.md'),
    os.path.join(UP, 'Title_Page_v1.13.docx'))

# 7) COI —— 【禁止自动生成】
#    2026-11-05 起，待上传层的 Declaration_of_Interest_v1.03.docx 已由作者手签
#    （签名图 + 日期图内嵌在表格单元格里）。从 md 重建会把签名覆盖掉，故此处停用。
#    若确需重建，请先备份已签名版本到 _历史版本\，再手工取消下面的注释。
# md_to_docx(
#     os.path.join(P, '利益冲突声明_v1.03.md'),
#     os.path.join(UP, 'Declaration_of_Interest_v1.03.docx'))
print('  -- Declaration_of_Interest_v1.06.docx 保留手签版，跳过重建')

# 8) STROBE
md_to_docx(
    os.path.join(P, 'STROBE清单_v1.04.md'),
    os.path.join(UP, 'STROBE_checklist_v1.04.docx'))

print('\n=== DONE ===')

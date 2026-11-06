# -*- coding: utf-8 -*-
"""生成 _待上传对应表.txt（TAB 分隔）与 哈希清单_v1.01.txt（HASH 两空格 路径）"""
import os
import hashlib

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')

MAP = [
    ('Manuscript_v1.33.docx', r'正文\Manuscript_v1.33.md'),
    ('Title_Page_v1.13.docx', r'正文\标题页_v1.13.md'),
    ('Tables_v2.05.docx', r'表格\Table1_v1.02.md'),
    ('Supplementary_Methods_v1.04.docx', r'补充材料\Supplementary_Methods_v1.04.md'),
    ('Supplementary_Tables_v1.18.docx', r'补充材料\Supplementary_Tables_v1.18.md'),
    ('STROBE_checklist_v1.04.docx', r'STROBE清单_v1.04.md'),
    ('Declaration_of_Interest_v1.06.docx', r'利益冲突声明_v1.03.md'),
    ('Cover_Letter_LHL_v1.05.docx', r'投稿信\Cover_Letter_LHL_v1.05.md'),
]

lines = ['# docx 上传件 <TAB> 源 md 相对路径（v1.05，2026-11-05）']
for k, v in MAP:
    lines.append('%s\t%s' % (k, v))
open(os.path.join(P, '_待上传对应表.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('对应表已写（TAB 分隔）')

rows = []
for root, dirs, fs in os.walk(P):
    for f in fs:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, P)
        if os.path.basename(rel).startswith('哈希清单_v'):
            continue
        h = hashlib.sha256(open(fp, 'rb').read()).hexdigest().upper()
        rows.append((h, rel))
rows.sort(key=lambda x: x[1])

out = ['# SHA-256 manifest · 2026-11-05 · %d files' % len(rows)]
out += ['%s  %s' % (h, r) for h, r in rows]
open(os.path.join(P, '哈希清单_v1.01.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('哈希清单已写：%d 个文件' % len(rows))

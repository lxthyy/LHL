# -*- coding: utf-8 -*-
"""打包数据与代码存档（供随稿提交 / Zenodo 上传）"""
import os
import zipfile

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
OUT = os.path.join(P, '数据代码存档_v1.00.zip')

INC_DIRS = ['数据', os.path.join('结果表'), os.path.join('结果表', '加强'),
            '代码', os.path.join('代码', '加强'), os.path.join('代码', '_审校')]
INC_FILES = [r'meta_research\audit_table_v1.00.csv',
             r'meta_research\candidates.csv',
             r'数字溯源对照_v1.02.md',
             r'哈希清单_v1.01.txt',
             r'补充材料\Supplementary_Methods_v1.02.md']

n = 0
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for d in INC_DIRS:
        full = os.path.join(P, d)
        if not os.path.isdir(full):
            continue
        for f in sorted(os.listdir(full)):
            q = os.path.join(full, f)
            if os.path.isfile(q) and f.lower().endswith(('.csv', '.py', '.md', '.txt')):
                z.write(q, os.path.join(d, f))
                n += 1
    for rel in INC_FILES:
        q = os.path.join(P, rel)
        if os.path.exists(q):
            z.write(q, rel)
            n += 1
print('文件数', n, '大小 %.1f MB' % (os.path.getsize(OUT) / 1e6))

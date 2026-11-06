# -*- coding: utf-8 -*-
"""审校 5：表 3/表 4 行数与数值、补充材料交叉引用、图表引用完整性"""
import os
import re
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
T = os.path.join(P, '表格')
MS = os.path.join(P, '正文', 'Manuscript_v1.22.md')
s = open(MS, encoding='utf-8').read()

print('=== Table 3 ===')
t3 = open(os.path.join(T, 'Table3_literature_audit.md'), encoding='utf-8').read()
rows = [l for l in t3.split('\n') if l.startswith('|') and '---' not in l][1:]
print('数据行:', len(rows), '(应为 22)')

print('\n=== Table 4 vs resolution_floor.csv ===')
t4 = open(os.path.join(T, 'Table4_resolution_floor.md'), encoding='utf-8').read()
rf = pd.read_csv(os.path.join(P, '结果表', '加强', 'resolution_floor.csv'))
pairs = [(50, 0.0175), (100, 0.0124), (200, 0.0088), (500, 0.0055),
         (1000, 0.0039), (2000, 0.0028), (5636, 0.0017)]
for dth, mdd in pairs:
    got = float(rf.loc[rf.deaths == dth, 'mdd80'].iloc[0])
    inT = ('%.4f' % got) in t4
    print('  deaths %5d  mdd80 %.4f  表内出现: %s  %s' % (
        dth, got, inT, 'OK' if abs(got - mdd) < 5e-5 and inT else 'CHECK'))

print('\n=== 补充材料交叉引用 ===')
refs = sorted(set(re.findall(r'Table S(\d+)', s)), key=int)
figs = sorted(set(re.findall(r'Figure S(\d+)', s)))
print('正文引用 Table S:', refs)
print('正文引用 Figure S:', figs)
sup = open(os.path.join(P, '补充材料', 'Supplementary_Tables_v1.11.md'), encoding='utf-8').read()
have = sorted(set(re.findall(r'Table S(\d+)', sup)), key=int)
print('补充材料实际含 Table S:', have)
missing = [x for x in refs if x not in have]
print('正文引用了但补充材料没有:', missing if missing else '无')

print('\n=== 主图引用 ===')
for f in ['Figure 1', 'Figure 2', 'Figure 3', 'Figure 4']:
    print('  %s 在正文出现 %d 次' % (f, s.count(f)))
for f in ['Table 1', 'Table 2', 'Table 3', 'Table 4']:
    print('  %s 在正文出现 %d 次' % (f, s.count(f)))

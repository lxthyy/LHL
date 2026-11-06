# -*- coding: utf-8 -*-
"""audit_data：权重、指数分布、时间单位、缺失结构"""
import os
import numpy as np
import pandas as pd

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
print('行数 %d，列数 %d' % d.shape)

print('\n=== 1. 权重检查（WTMEC2YR 原始列）===')
print(d.groupby('cycle').WTMEC2YR.agg(['mean', 'median', 'min']).round(0).to_string())

print('\n=== 2. 随访时间 ===')
print('months：min %.1f  max %.1f  中位 %.1f' % (d.months.min(), d.months.max(),
                                                d.months.median()))
print('死亡者 months<=0：%d' % int(((d.dead == 1) & (d.months <= 0)).sum()))

print('\n=== 3. 指数分布 ===')
for c in ['phenoage', 'pa_accel', 'hd', 'al', 'al9', 'disp', 'pc1']:
    if c in d:
        s = d[c].dropna()
        print('%-9s n=%5d  min %9.2f  中位 %8.2f  max %9.2f' %
              (c, len(s), s.min(), s.median(), s.max()))

print('\n=== 4. AL 取值分布 ===')
print(d.al.value_counts().sort_index().to_string())

print('\n=== 5. 缺失结构（关键列）===')
for c in ['LBXCRP', 'crp', 'LBXCRP', 'phenoage', 'hd', 'al', 'disp', 'pc1', 'bmi', 'edu', 'pir']:
    if c in d:
        print('%-10s 缺失 %5d (%.1f%%)' % (c, d[c].isna().sum(), 100 * d[c].isna().mean()))

print('\n=== 6. CRP 缺失是否集中在 1999-2004 ===')
if 'crp' in d:
    print(pd.crosstab(d.cycle, d.crp.isna(), normalize='index').mul(100).round(1).to_string())

print('\n=== 7. 极端值检查 ===')
for c in ['age', 'bmi', 'LBXSAL', 'LBXSCR', 'LBXWBCSI', 'LBXHGB']:
    if c in d:
        print('%-10s min %8.2f  p1 %8.2f  p99 %8.2f  max %8.2f' %
              (c, d[c].min(), d[c].quantile(.01), d[c].quantile(.99), d[c].max()))

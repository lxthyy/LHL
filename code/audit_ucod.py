# -*- coding: utf-8 -*-
"""audit_ucod：核查 NHANES 死亡文件字段位置与死因编码映射"""
import os
import pandas as pd

CACHE = r'D:\最新智研\trae工作文件夹\SJK\nhanes_cache'
FILES = ['NHANES_1999_2000_MORT_2019_PUBLIC.dat',
         'NHANES_2005_2006_MORT_2019_PUBLIC.dat',
         'NHANES_2011_2012_MORT_2019_PUBLIC.dat',
         'NHANES_2015_2016_MORT_2019_PUBLIC.dat',
         'NHANES_2017_2018_MORT_2019_PUBLIC.dat']

p = os.path.join(CACHE, FILES[0])
lines = open(p, encoding='latin-1').read().splitlines()
print('样本行（前 3 条，| 分隔每 10 字符）：')
for ln in lines[:3]:
    print(repr(ln), ' len=', len(ln))

rows = []
for f in FILES:
    p = os.path.join(CACHE, f)
    for ln in open(p, encoding='latin-1'):
        ln = ln.rstrip('\n')
        if len(ln) < 45:
            continue
        try:
            sq = int(ln[0:6])
        except ValueError:
            continue
        rows.append(dict(cycle=f.split('_')[1] + '-' + f.split('_')[2],
                         elig=ln[14], stat=ln[15], ucod=ln[16:19].strip(),
                         pm_int=ln[42:45].strip(),
                         pm_exm=ln[45:48].strip() if len(ln) >= 48 else ''))
d = pd.DataFrame(rows)
print('\n总记录 %d；ELIGSTAT 取值 %s' % (len(d), d.elig.value_counts().to_dict()))
print('MORTSTAT 取值 %s' % d.stat.value_counts().to_dict())

dd = d[d.stat == '1']
print('\n死亡者中 UCOD_LEADING 分布：')
t = dd.ucod.value_counts().sort_index()
share = (100 * t / t.sum()).round(1)
out = pd.DataFrame({'死亡数': t, '占比%': share})
print(out.to_string())

print('\n按周期 × 编码（仅 001/002/003/004/005/007/008）：')
sub = dd[dd.ucod.isin(['001', '002', '003', '004', '005', '007', '008'])]
print(pd.crosstab(sub.cycle, sub.ucod).to_string())

print('\nPERMTH_INT（43-45）缺失或非数字：%d' % (~dd.pm_int.str.isdigit()).sum())
print('PERMTH_INT 中位 %s，最大 %s' % (dd.pm_int[dd.pm_int.str.isdigit()].astype(int).median(),
                                        dd.pm_int[dd.pm_int.str.isdigit()].astype(int).max()))

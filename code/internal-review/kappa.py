# -*- coding: utf-8 -*-
"""
第二人复核一致率与 Cohen's kappa
用法：把两位复核者的判定填进 _补强\复核数据.csv（列：item,rater1,rater2，取值 有/无/未提）
      python kappa.py
无数据时只打印填写说明。
"""
import os
import itertools

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
F = os.path.join(P, '_补强', '复核数据.csv')

if not os.path.exists(F):
    print('尚未填写复核数据。')
    print('请创建 %s，格式：' % F)
    print('item,rater1,rater2')
    print('S01_margin,无,无')
    print('S01_test,否,否')
    print('...（5 篇 × 4 项 = 20 行）')
    raise SystemExit(0)

import pandas as pd

d = pd.read_csv(F, encoding='utf-8-sig')
n = len(d)
agree = int((d.rater1 == d.rater2).sum())
po = agree / n
cats = sorted(set(d.rater1) | set(d.rater2))
pe = sum((d.rater1.eq(c).mean() * d.rater2.eq(c).mean()) for c in cats)
kappa = (po - pe) / (1 - pe) if pe < 1 else float('nan')

print('条目数 %d，一致 %d（%.1f%%），Cohen kappa = %.2f' % (n, agree, po * 100, kappa))
print('\n可直接写进 Methods：')
print('A second reviewer, blinded to the first extraction, independently extracted the '
      'same items from a random 20%% sample (5 of 22 studies; seed 20261105). '
      'Agreement was %d/%d items (%.1f%%; Cohen kappa %.2f).' % (agree, n, po * 100, kappa))

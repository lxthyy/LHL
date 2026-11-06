# -*- coding: utf-8 -*-
"""第二人复核 20% 抽样（固定种子，可复现）"""
import os
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
SEED = 20261105

c = pd.read_csv(os.path.join(P, 'meta_research', 'candidates.csv'), encoding='utf-8-sig')
s = c.sample(n=5, random_state=SEED)[
    ['study_id', 'first_author', 'year', 'journal', 'cohort', 'n_analysed',
     'n_deaths', 'indices_compared', 'doi_or_url']]

lines = ['# 第二人复核 · 抽样结果（seed %d）\n' % SEED,
         '从 22 篇中随机抽取 5 篇（20%）。复核者只看全文，不看本文的提取结果。\n',
         '| study_id | 作者 | 年 | 期刊 | 队列 | n | 死亡 | DOI |',
         '|---|---|---|---|---|---|---|---|']
for _, r in s.iterrows():
    lines.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
        r.study_id, r.first_author, r.year, r.journal, r.cohort,
        r.n_analysed, r.n_deaths, r.doi_or_url))
lines.append('')
lines.append('复核表与一致率记录见同目录 `第二人复核_抽样包.md`；'
             '算 κ 用 `代码\\_审校\\kappa.py`。')
open(os.path.join(P, '_补强', '抽样结果.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[3:]))

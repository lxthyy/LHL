# -*- coding: utf-8 -*-
"""
报告质量评分卡：对 22 篇头对头比较按本文提出的五项标准逐篇打分（0/1）
输出：表格\Table5_reporting_scorecard.md 与 汇总统计
"""
import os
import re
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
c = pd.read_csv(os.path.join(P, 'meta_research', 'candidates.csv'), encoding='utf-8-sig')

EXPO = re.compile(r'exposure|smoking|BMI|physical activity|lifestyle|education|'
                  r'income|behaviou?r', re.I)
POWER = re.compile(r'detectable|power|smallest|precision', re.I)
PC = 'published_conclusion(max 15 words, verbatim quote)'


def f1(r):
    """(i) 配对差异 + 区间：以"是否正式检验差异"为代理"""
    return 1 if str(r.formal_difference_test).strip().lower() == 'yes' else 0


def f2(r):
    """(ii) 预设等价/非劣界"""
    return 0 if 'none' in str(r.equivalence_margin).lower() else 1


def f3(r):
    """(iii) 报告可检出最小差异"""
    txt = ' '.join(str(x) for x in [r.extraction_note, r[PC]])
    return 1 if POWER.search(txt) else 0


def f4(r):
    """(iv) 报告事件数"""
    return 1 if re.match(r'^\d', str(r.n_deaths).strip()) else 0


def f5(r):
    """(v) 构念/暴露对比（按摘要关键词，保守判定）"""
    txt = ' '.join(str(x) for x in [r.extraction_note, r[PC], r.indices_compared])
    return 1 if EXPO.search(txt) else 0


rows = []
for _, r in c.iterrows():
    sc = [f1(r), f2(r), f3(r), f4(r), f5(r)]
    rows.append(dict(study_id=r.study_id, study='%s %s' % (str(r.first_author).split()[0], r.year),
                     配对差异=f1(r), 预设界=f2(r), 可检出差异=f3(r),
                     事件数=f4(r), 构念对比=f5(r), 合计=sum(sc)))
d = pd.DataFrame(rows).sort_values(['合计', 'study'], ascending=[False, True])

n = len(d)
summary = pd.DataFrame([
    dict(条目='(i) 配对差异 + 区间（以正式检验为代理）', 达成='%d/%d' % (d['配对差异'].sum(), n)),
    dict(条目='(ii) 预设等价/非劣界', 达成='%d/%d' % (d['预设界'].sum(), n)),
    dict(条目='(iii) 报告可检出最小差异', 达成='%d/%d' % (d['可检出差异'].sum(), n)),
    dict(条目='(iv) 报告事件数', 达成='%d/%d' % (d['事件数'].sum(), n)),
    dict(条目='(v) 构念/暴露对比', 达成='%d/%d' % (d['构念对比'].sum(), n)),
])
print(summary.to_string(index=False))
print('\n总分：均值 %.2f/5，中位 %d，范围 %d–%d' % (
    d['合计'].mean(), d['合计'].median(), d['合计'].min(), d['合计'].max()))
print('达成 ≤1 项的篇数:', int((d['合计'] <= 1).sum()))

L = ['**Table 5.** Reporting scorecard for the 22 audited head-to-head comparisons.\n',
     'Each study scored 1 if the item was reported and 0 if not. Items follow the box in '
     'the Discussion.\n',
     '| Study | (i) Paired difference with interval | (ii) Pre-specified margin | '
     '(iii) Smallest detectable difference | (iv) Events reported | '
     '(v) Construct/exposure contrast | Total |',
     '|---|---|---|---|---|---|---|']
for _, r in d.iterrows():
    L.append('| %s | %d | %d | %d | %d | %d | **%d** |' % (
        r.study, r['配对差异'], r['预设界'], r['可检出差异'], r['事件数'],
        r['构念对比'], r['合计']))
L.append('')
L.append('Item (i) is scored from whether the study formally tested the difference between '
         'indices; item (iii) from whether any statement of detectable difference or '
         'precision was made; item (v) from whether exposure or construct contrasts were '
         'reported, judged from the abstract and extraction note and therefore '
         'conservative.')
L.append('')
L.append('Summary: item (i) %d/22, (ii) %d/22, (iii) %d/22, (iv) %d/22, (v) %d/22; '
         'mean total %.2f of 5 (range %d–%d); %d of 22 studies scored 1 or less.' % (
             d['配对差异'].sum(), d['预设界'].sum(), d['可检出差异'].sum(),
             d['事件数'].sum(), d['构念对比'].sum(), d['合计'].mean(),
             d['合计'].min(), d['合计'].max(), int((d['合计'] <= 1).sum())))
L.append('')
L.append('Source: `meta_research\\candidates.csv`; script `代码\\_审校\\scorecard.py`.')
open(os.path.join(P, '表格', 'Table5_reporting_scorecard.md'), 'w',
     encoding='utf-8').write('\n'.join(L))
print('\nwritten Table5_reporting_scorecard.md')

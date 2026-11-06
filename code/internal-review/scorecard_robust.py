# -*- coding: utf-8 -*-
"""
评分卡稳健性：三种编码下分数怎么变
A 严格（现行五项）  B 宽松（区间重叠也算、剔除第 v 项）  C 只留两条客观项
输出：表格\TableS12_reporting_scorecard.md
"""
import os
import re
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
c = pd.read_csv(os.path.join(P, 'meta_research', 'candidates.csv'), encoding='utf-8-sig')
PC = 'published_conclusion(max 15 words, verbatim quote)'
POWER = re.compile(r'detectable|power|smallest|precision', re.I)
EXPO = re.compile(r'exposure|smoking|BMI|physical activity|lifestyle|education|'
                  r'income|behaviou?r', re.I)

rows = []
for _, r in c.iterrows():
    formal = str(r.formal_difference_test).strip().lower() == 'yes'
    ci = str(r.ci_reported).strip().lower() == 'yes'
    margin = 'none' not in str(r.equivalence_margin).lower()
    power = bool(POWER.search(' '.join(str(x) for x in [r.extraction_note, r[PC]])))
    deaths = bool(re.match(r'^\d', str(r.n_deaths).strip()))
    expo = bool(EXPO.search(' '.join(str(x) for x in
                                     [r.extraction_note, r[PC], r.indices_compared])))
    A = formal + margin + power + deaths + expo
    B = (formal or ci) + margin + power + deaths          # 4 项
    C = margin + deaths                                   # 2 项
    rows.append(dict(study='%s %s' % (str(r.first_author).split()[0], r.year),
                     A=A, Amean=A / 5, B=B, Bmean=B / 4, C=C, Cmean=C / 2,
                     i_formal=formal, i_any_ci=(formal or ci), ii=margin,
                     iii=power, iv=deaths, v=expo))
d = pd.DataFrame(rows)

print('编码   均值   中位  范围   ≤1 的篇数')
for k, n in [('A', 5), ('B', 4), ('C', 2)]:
    print('%s     %.2f   %.1f   %d–%d   %d' % (
        k, d[k].mean(), d[k].median(), d[k].min(), d[k].max(),
        int((d[k] <= 1).sum()) if k != 'C' else int((d[k] == 0).sum())))

print('\n逐项：')
for lab, col in [('(i) 正式检验差异', 'i_formal'), ('(i) 任何区间比较', 'i_any_ci'),
                 ('(ii) 预设等价界', 'ii'), ('(iii) 可检出差异', 'iii'),
                 ('(iv) 事件数', 'iv'), ('(v) 暴露对比(摘要判定)', 'v')]:
    print('  %-22s %d/22' % (lab, int(d[col].sum())))

L = ['**Table S12.** Conformity of the 22 audited comparisons to the proposed reporting '
     'items, under three codings.\n',
     'This table measures **how far the literature sits from a standard we propose**; it is '
     'not a quality score. A well-conducted study can legitimately score zero: superiority '
     'testing is a valid design, equivalence margins are not yet a convention in this '
     'literature, and items judged from abstracts alone are marked at their most '
     'conservative value.\n',
     '| Coding | Items counted | Mean | Median | Range | Studies scoring ≤1 |',
     '|---|---|---|---|---|---|']
L.append('| A (strict) | all five | %.2f | %.1f | %d–%d | %d |' % (
    d.A.mean(), d.A.median(), d.A.min(), d.A.max(), int((d.A <= 1).sum())))
L.append('| B (lenient) | four: overlap-based comparison counted, item (v) dropped | %.2f | %.1f | %d–%d | %d |' % (
    d.B.mean(), d.B.median(), d.B.min(), d.B.max(), int((d.B <= 1).sum())))
L.append('| C (objective only) | two: pre-specified margin and event count | %.2f | %.1f | %d–%d | %d |' % (
    d.C.mean(), d.C.median(), d.C.min(), d.C.max(), int((d.C == 0).sum())))
L.append('')
L.append('Item-by-item counts: formal test of the difference %d/22; any interval-based '
         'comparison %d/22; pre-specified equivalence margin %d/22; a statement of the '
         'smallest detectable difference %d/22; event count reported %d/22; exposure or '
         'construct contrast visible in the abstract %d/22.' % (
             d.i_formal.sum(), d.i_any_ci.sum(), d.ii.sum(), d.iii.sum(),
             d.iv.sum(), d.v.sum()))
L.append('')
L.append('**Interpretation.** Only two things are claimed in the main text: that no study '
         'pre-specified a margin, and that two formally tested the difference. The score '
         'itself is not used as a headline because it moves from %.2f to %.2f of the '
         'maximum depending on coding.' % (d.A.mean() / 5, d.B.mean() / 4))
L.append('')
L.append('Source: `meta_research\\candidates.csv`; script `代码\\_审校\\scorecard_robust.py`.')
open(os.path.join(P, '表格', 'TableS12_reporting_scorecard.md'), 'w',
     encoding='utf-8').write('\n'.join(L))
print('\nwritten TableS12_reporting_scorecard.md')

# -*- coding: utf-8 -*-
"""v1.23 收尾：表 4、补充表、投稿信、图 4、标题页 与正文版本同步"""
import os
import re

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')


def patch(src, dst, reps, title_from=None, title_to=None):
    s = open(src, encoding='utf-8').read()
    if title_from:
        s = s.replace(title_from, title_to, 1)
    for a, b in reps:
        s = s.replace(a, b)
    open(dst, 'w', encoding='utf-8').write(s)
    print('written', os.path.basename(dst))


# 表 4
patch(os.path.join(P, '表格', 'Table4_resolution_floor.md'),
      os.path.join(P, '表格', 'Table4_v1.01.md'),
      [('0.0008–0.0108', '0.0008–0.0109'),
       ('0.0008–0.0108', '0.0008–0.0109'),
       ('0.0108', '0.0109')])

# 补充表 → v1.12
patch(os.path.join(P, '补充材料', 'Supplementary_Tables_v1.11.md'),
      os.path.join(P, '补充材料', 'Supplementary_Tables_v1.12.md'),
      [('Companion to Manuscript v1.22', 'Companion to Manuscript v1.23'),
       ('0.0008–0.0108', '0.0008–0.0109'),
       ('0.0108', '0.0109')],
      title_from='# Supplementary Tables v1.11 (S1–S11)',
      title_to='# Supplementary Tables v1.12 (S1–S11)')

# 投稿信
patch(os.path.join(P, '投稿信', 'Cover_Letter_LHL_v1.00.md'),
      os.path.join(P, '投稿信', 'Cover_Letter_LHL_v1.01.md'),
      [('0.0008 and 0.0108', '0.0008 and 0.0109'),
       ('0.0108', '0.0109'),
       ('Manuscript v1.22', 'Manuscript v1.23')],
      title_from='# Cover Letter — The Lancet Healthy Longevity',
      title_to='# Cover Letter — The Lancet Healthy Longevity')

# 标题页 → v1.08
tp = open(os.path.join(P, '正文', '标题页_v1.07.md'), encoding='utf-8').read()
tp = tp.replace('# Title Page v1.07', '# Title Page v1.08', 1)
tp = tp.replace('Main text 3,497 words; abstract 249 words.',
                'Main text 3,499 words; abstract 249 words.', 1)
open(os.path.join(P, '正文', '标题页_v1.08.md'), 'w', encoding='utf-8').write(tp)
print('written 标题页_v1.08.md')

# 图 4 脚本带宽
fp = os.path.join(P, '代码', '加强', 'make_fig4.py')
g = open(fp, encoding='utf-8').read()
g = g.replace('0.0108', '0.0109')
open(fp, 'w', encoding='utf-8').write(g)
print('figure script updated')

# 正文中的表 2 引用说明
ms = os.path.join(P, '正文', 'Manuscript_v1.23.md')
t = open(ms, encoding='utf-8').read()
t = t.replace('**Table 2.** Discrimination, equivalence and cause-specific estimates, including the\nten-cycle extension for the three indices that do not require CRP.',
              '**Table 2.** Discrimination, equivalence and cause-specific estimates, including the\nten-cycle extension for the three indices that do not require CRP (v1.06).')
open(ms, 'w', encoding='utf-8').write(t)
print('manuscript table-2 pointer updated')

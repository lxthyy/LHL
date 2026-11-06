# -*- coding: utf-8 -*-
"""v1.26：插入年代分析段（用 ASCII 锚点正则，避开特殊连字符差异）"""
import os
import re

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
F = os.path.join(P, '正文', 'Manuscript_v1.26.md')
s = open(F, encoding='utf-8').read()

INS = ('Repeating the analysis within assay eras reproduced this: 1999-2010 (25,678 '
       'participants, 5,360 deaths) gave 8 of 10 pairs equivalent at +-0.01 and all 10 at '
       '+-0.015; 2011-2018 (8,715 participants, 276 deaths) was too sparse to decide '
       '(Table S13).')

s2, n1 = re.subn(
    r'Structural\s+reproducibility of the principal component is in Table S4\. '
    r'Proportional hazards held\s+\(largest \|r\| 0\.055\), and neither the landmark, '
    r'9-item AL nor no-standardisation analysis\s+changed the ordering \(Table S2\)\.',
    'The principal component reproduced across cycles (Table S4); proportional hazards held '
    'and no sensitivity analysis changed the ordering (Table S2).', s, count=1, flags=re.S)

# 删掉与本段重复的年代 HR 句
s2, n2 = re.subn(r"\s*HD's hazard ratio was 1\.53 in [^.]*\.", '', s2, count=1, flags=re.S)
# 插入新段
s2, n3 = re.subn(r'(stayed within 0\.003 \(Table S7\)\.)\s*\n',
                 r'\1\n\n' + INS + '\n', s2, count=1)

# 还原排版用字符
s2 = s2.replace('+-0.01', '±0.01').replace('+-0.015', '±0.015')
s2 = s2.replace('1999-2010 (25,678', '1999–2010 (25,678').replace('2011-2018 (8,715', '2011–2018 (8,715')
open(F, 'w', encoding='utf-8').write(s2)
print('替换命中:', n1, n2, n3)


def wc(t):
    t = re.sub(r'[#*_\[\]\(\)>]', ' ', t)
    return len([w for w in t.split() if re.search(r'[A-Za-z0-9]', w)])


print('正文:', wc(s2[s2.index('## Introduction'):s2.index('## Figure legends')]))
print('摘要:', wc(s2[s2.index('## Abstract'):s2.index('**Research in context**')]))

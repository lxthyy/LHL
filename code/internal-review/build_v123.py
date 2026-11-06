# -*- coding: utf-8 -*-
"""
生成 v1.23：按 04_审校报告 修正 7 处缺陷
方案 B：全包以 300 次抽样的 equivalence.csv 为准（图 1、表 2 都由它生成）
  0.0108 → 0.0109；0.0090–0.0108 → 0.0091–0.0109；≤0.0054 → ≤0.0055
另修：5 处 HR 区间、54.7→54.6、26.7–27.5→26.7–27.7、文献重编号并补引 [27]
"""
import os
import re
import shutil

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
SRC = os.path.join(P, '正文', 'Manuscript_v1.22.md')
DST = os.path.join(P, '正文', 'Manuscript_v1.23.md')
s = open(SRC, encoding='utf-8').read()

# ---------- 0) 版本头 ----------
s = s.replace('# Manuscript v1.22 — target', '# Manuscript v1.23 — target', 1)
s = s.replace(
    '**Changes from v1.21 — the paper now states a reporting standard, not only a critique.',
    '**Changes from v1.22 — numerical audit corrections. Seven defects found by回源比对; '
    'every value now traces to a frozen result table:**\n'
    '1. The equivalence bootstrap is stated and used consistently at 300 resamples '
    '(the run behind Figure 1 and Table 2). The maximum pairwise difference is therefore '
    '0.0109, not 0.0108; the four largest pairs span 0.0091–0.0109; the largest equivalent '
    'pair is 0.0055.\n'
    '2. Five confidence intervals corrected to the frozen tables: PhenoAge 1.36–1.79, '
    'dispersion 1.15–1.58 and PC1 1.08–1.36 (weighted); cardiovascular PhenoAge 1.37–1.84; '
    'cancer PhenoAge 1.17–1.62 and cancer dispersion 1.09–1.50.\n'
    '3. Quintile-5 mean age corrected to 54.6 years.\n'
    '4. Variance explained by PC1 corrected to 26.7–27.7%.\n'
    '5. References renumbered into first-appearance order; reference 27 is now cited.\n\n'
    '**Changes from v1.21 — the paper now states a reporting standard, not only a critique.', 1)

# ---------- 1) 数值替换 ----------
rep = [
    ('0.0090–0.0108', '0.0091–0.0109'),
    ('0.0008 and 0.0108', '0.0008 and 0.0109'),
    ('0.0008–0.0108', '0.0008–0.0109'),
    ('between 0.0008 and 0.0108', 'between 0.0008 and 0.0109'),
    ('at most 0.011', 'at most 0.011'),
    ('≤ 0.0054', '≤ 0.0055'),
    ('54.7 years', '54.6 years'),
    ('26.7–27.5%', '26.7–27.7%'),
    ('1.56 (95% CI 1.38–1.77)', '1.56 (95% CI 1.36–1.79)'),
    ('1.35 (1.14–1.59)', '1.35 (1.15–1.58)'),
    ('1.21 (1.07–1.37)', '1.21 (1.08–1.36)'),
    ('1.59 (1.38–1.83)', '1.59 (1.37–1.84)'),
    ('1.37 (1.16–1.63)', '1.37 (1.17–1.62)'),
    ('1.28 (1.09–1.52)', '1.28 (1.09–1.50)'),
    ('(300 resamples;\n1,000 for the intervals reported) [16,17]',
     '(300 resamples) [16,17]'),
]
for a, b in rep:
    s = s.replace(a, b)

# 其余 0.0108（摘要、讨论、结论等）
s = s.replace('0.0108', '0.0109')

# ---------- 2) 补引 [27] ----------
old27 = ('the same pair of indices produced 0.004 and 0.048 in two cohorts analysed by the '
         'same investigators [26];')
new27 = ('the same pair of indices produced 0.004 and 0.048 in two cohorts analysed by the '
         'same investigators [26], and three allostatic-load formulations matched '
         'biological-age measures in the same cohort [27];')
if old27 in s:
    s = s.replace(old27, new27, 1)
    print('cited 27')
else:
    print('!! 27 anchor not found')

# ---------- 3) 文献重编号（正文） ----------
MAP = {i: i for i in range(1, 16)}
MAP.update({21: 16, 22: 17, 23: 18, 24: 19,
            16: 20, 17: 21, 18: 22, 19: 23, 20: 24,
            25: 25, 26: 26, 27: 27})

head, refs = s.split('## References', 1)
CITE = re.compile(r'\[([0-9][0-9,\s\u2013\-]*)\]')


def remap(m):
    nums = []
    for part in re.split(r'[,]\s*', m.group(1)):
        part = part.strip()
        if '\u2013' in part or '-' in part:
            a, b = re.split(r'[\u2013\-]', part)
            nums += list(range(int(a), int(b) + 1))
        elif part:
            nums.append(int(part))
    new = [MAP[n] for n in nums]
    # 压缩连续段
    out, i = [], 0
    while i < len(new):
        j = i
        while j + 1 < len(new) and new[j + 1] == new[j] + 1:
            j += 1
        if j - i >= 2:
            out.append('%d\u2013%d' % (new[i], new[j]))
        else:
            out += [str(x) for x in new[i:j + 1]]
        i = j + 1
    return '[' + ','.join(out) + ']'


head = CITE.sub(remap, head)

# 重排文献列表
ents = re.findall(r'^(\d+)\.\s+(.*?)(?=^\d+\.\s|\Z)', refs, flags=re.S | re.M)
bynum = {int(n): t.strip() for n, t in ents}
inv = {v: k for k, v in MAP.items()}
new_refs = ['\n']
for newn in range(1, len(bynum) + 1):
    oldn = inv[newn]
    new_refs.append('%d. %s\n' % (newn, bynum[oldn]))
s = head + '## References\n' + '\n'.join(new_refs)

open(DST, 'w', encoding='utf-8').write(s)
print('written', DST)
print('残留 0.0108:', s.count('0.0108'), '| 0.0109:', s.count('0.0109'))

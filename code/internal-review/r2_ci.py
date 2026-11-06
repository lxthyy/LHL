# -*- coding: utf-8 -*-
"""
审校 2：正文里每一个 "HR (lo–hi)" 与冻结结果表逐条比对
输出：不一致清单（含正确值）
"""
import os
import re
import glob
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
MS = os.path.join(P, '正文', 'Manuscript_v1.22.md')

# 收集所有 (HR, lo, hi) 来源
src = []
for f in glob.glob(os.path.join(P, '结果表', '**', '*.csv'), recursive=True):
    try:
        df = pd.read_csv(f, encoding='utf-8-sig')
    except Exception:
        continue
    cols = {c.lower(): c for c in df.columns}
    hr = next((c for c in df.columns if c.lower() in ('hr', 'hr_w', 'or')), None)
    lo = next((c for c in df.columns if c.lower() in ('lo', 'lo_w')), None)
    hi = next((c for c in df.columns if c.lower() in ('hi', 'hi_w')), None)
    if not (hr and lo and hi):
        continue
    name = os.path.relpath(f, P).replace('结果表\\', '')
    for i, r in df.iterrows():
        try:
            key = str(r.get('指数', r.get('结局', ''))) + ' ' + str(r.get('指数', ''))
            src.append((round(float(r[hr]), 2), round(float(r[lo]), 2),
                        round(float(r[hi]), 2), name + '[' + str(i) + ']' + ' ' + key.strip()))
        except Exception:
            pass

s = open(MS, encoding='utf-8').read()
body = s[s.index('## Results'):s.index('## References')]
pat = re.compile(r'(\d\.\d{2})\s*\((?:95% CI\s*)?(\d\.\d{2})\s*[–\-]\s*(\d\.\d{2})\)')

print('=== "HR (lo–hi)" 逐条比对 ===')
bad = 0
for m in pat.finditer(body):
    a, b, c = [float(x) for x in m.groups()]
    hits = [x for x in src if x[0] == a]
    if not hits:
        continue
    exact = [x for x in hits if x[1] == b and x[2] == c]
    if exact:
        continue
    bad += 1
    ctx = body[max(0, m.start() - 60):m.end() + 10].replace('\n', ' ')
    print('稿件 %s (%s–%s)  ← 源表无此区间' % (m.group(1), m.group(2), m.group(3)))
    print('   上下文:', ctx[-90:])
    for x in hits[:3]:
        print('   候选: %s (%s–%s)  %s' % x)
    print()

print('不一致条数:', bad)

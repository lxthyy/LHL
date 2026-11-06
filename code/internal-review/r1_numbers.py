# -*- coding: utf-8 -*-
"""
审校 1：数字回源（正文/摘要/表/图注 的每个数字都要能在冻结结果表里找到）
------------------------------------------------------------------
输出：每个数字 → 命中的 CSV 文件（或 UNMATCHED）
"""
import os
import re
import glob
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
MS = os.path.join(P, '正文', 'Manuscript_v1.22.md')

# ---- 收集所有 CSV 的数值池 ----
pool = {}
for f in glob.glob(os.path.join(P, '结果表', '**', '*.csv'), recursive=True):
    try:
        df = pd.read_csv(f, encoding='utf-8-sig')
    except Exception:
        try:
            df = pd.read_csv(f, encoding='utf-8')
        except Exception:
            continue
    for c in df.columns:
        for v in pd.to_numeric(df[c], errors='coerce').dropna():
            pool.setdefault(round(float(v), 6), set()).add(
                os.path.relpath(f, P) + ':' + c)

# 审计表
aud = pd.read_csv(os.path.join(P, 'meta_research', 'audit_table_v1.00.csv'),
                 encoding='utf-8-sig')
for c in aud.columns:
    for v in pd.to_numeric(aud[c], errors='coerce').dropna():
        pool.setdefault(round(float(v), 6), set()).add('audit_table:' + c)

# ---- 正文数字 ----
s = open(MS, encoding='utf-8').read()
body = s[s.index('## Abstract'):s.index('## References')]

# 统计类：整千/百分比/年份/编号等，不参与回源
SKIP = re.compile(r'^(19|20)\d\d$|^\d{1,2}$|^\d+$')

tok = re.findall(r'\d[\d,]*\.?\d*', body)
seen, unmatched, matched = [], [], 0
for t in tok:
    raw = t.replace(',', '')
    try:
        v = float(raw)
    except ValueError:
        continue
    if v in pool:
        matched += 1
    elif SKIP.match(raw):
        continue
    else:
        # 允许 ±1% 容差（四舍五入差异）
        hit = None
        for k in pool:
            if k != 0 and abs(v - k) / abs(k) < 0.01:
                hit = k
                break
        if hit is None:
            unmatched.append(t)

print('=== 数字回源 ===')
print('正文（摘要→文献前）数字 token: %d' % len(tok))
print('直接命中冻结表: %d' % matched)
print('未命中（需人工判断是否为年份/倍数/换算）: %d' % len(unmatched))
print('未命中清单:')
uniq = sorted(set(unmatched), key=lambda x: (-len(x), x))
print(', '.join(uniq))

# -*- coding: utf-8 -*-
"""
审校 3：Vancouver 编号顺序 + 文献条目规范
"""
import os
import re

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
MS = os.path.join(P, '正文', 'Manuscript_v1.22.md')
s = open(MS, encoding='utf-8').read()

body = s[s.index('## Introduction'):s.index('## References')]
refs_txt = s[s.index('## References'):]

# ---- 引用顺序 ----
cites = []
for m in re.finditer(r'\[([0-9][0-9,\s\u2013\-]*)\]', body):
    for part in re.split(r'[,\s]+', m.group(1)):
        part = part.strip()
        if not part:
            continue
        if '\u2013' in part or '-' in part:
            a, b = re.split(r'[\u2013\-]', part)
            cites += list(range(int(a), int(b) + 1))
        else:
            cites.append(int(part))

first = []
for c in cites:
    if c not in first:
        first.append(c)
print('=== 引用编号 ===')
print('首次出现顺序:', first)
print('是否为 1..N 递增:', first == list(range(1, len(first) + 1)))
print('正文共引用:', len(set(cites)), '个编号；最大:', max(cites))

# ---- 文献条目 ----
entries = re.findall(r'^(\d+)\.\s+(.*?)(?=^\d+\.\s|\Z)', refs_txt, flags=re.S | re.M)
print('\n=== 文献条目 %d 条 ===' % len(entries))
problems = []
for num, txt in entries:
    one = ' '.join(txt.split())
    if 'doi:10.' not in one:
        problems.append('%s 无 DOI' % num)
    # 作者段：到第一个句号+空格+大写字母+期刊（简化：取到第一个 ". " 之前的作者列表）
    head = one.split('. ')[0]
    authors = head.split(', ')
    n_et_al = 'et al' in one
    if n_et_al and len(authors) != 3:
        problems.append('%s 用 et al 但列出 %d 位作者（应为 3）: %s' % (num, len(authors), head[:70]))
    if not n_et_al and len(authors) > 6:
        problems.append('%s 未用 et al 但列了 %d 位（>6 应缩写）: %s' % (num, len(authors), head[:70]))
if problems:
    for p in problems:
        print('  !', p)
else:
    print('  作者数规则与 DOI 均通过')

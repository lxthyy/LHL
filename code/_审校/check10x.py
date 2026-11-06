# -*- coding: utf-8 -*-
"""两个检查器各跑 10 次，验证结论与输出完全一致"""
import hashlib
import subprocess
import sys
import os

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
TOOL = r'c:\Users\lxddz\Desktop\__完整工作区打包\_工具'
CASES = [
    ('结构层', [sys.executable, os.path.join(TOOL, '投稿包检查.py'), P]),
    ('数值层', [sys.executable, os.path.join(TOOL, '投稿包深度检查.py'), P,
                '--limits', '3500,250,30']),
]
for name, cmd in CASES:
    hs, verdicts = [], []
    for i in range(10):
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        out = r.stdout or ''
        h = hashlib.sha256(out.encode('utf-8')).hexdigest()[:16].upper()
        hs.append(h)
        v = [l for l in out.split('\n') if l.startswith('结论')]
        verdicts.append(v[0].strip() if v else '?')
    print('%-6s 10 次：唯一输出哈希 %d 种；结论 %s' % (
        name, len(set(hs)), '一致' if len(set(verdicts)) == 1 else '不一致'))
    print('        ', verdicts[0])
    for i, (h, v) in enumerate(zip(hs, verdicts), 1):
        print('   第%2d次 %s  %s' % (i, h, v))

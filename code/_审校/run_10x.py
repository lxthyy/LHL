# -*- coding: utf-8 -*-
"""
十次一致性跑：对指定脚本连续跑 N 次，逐次记录输出文件哈希
用法： python run_10x.py <脚本路径> <输出文件1> [<输出文件2> ...] [--n 10]
"""
import os
import sys
import time
import hashlib
import subprocess

args = [a for a in sys.argv[1:] if not a.startswith('--')]
n = 10
for a in sys.argv[1:]:
    if a.startswith('--n'):
        n = int(a.split('=')[1]) if '=' in a else 10

script, outs = args[0], args[1:]
log = os.path.join(os.path.dirname(script), 'run_%dx_%s.txt' % (
    n, os.path.basename(script).replace('.py', '')))

with open(log, 'a', encoding='utf-8') as L:
    L.write('\n===== %s  %d 次  开始 %s =====\n' % (
        os.path.basename(script), n, time.strftime('%H:%M:%S')))
    hashes = []
    for i in range(1, n + 1):
        t0 = time.time()
        r = subprocess.run([sys.executable, script], capture_output=True)
        row = []
        for f in outs:
            if os.path.exists(f):
                h = hashlib.sha256(open(f, 'rb').read()).hexdigest()[:16].upper()
                row.append(h)
            else:
                row.append('MISSING')
        hashes.append(tuple(row))
        L.write('第%2d次  %6.1fs  rc=%d  %s\n' % (i, time.time() - t0, r.returncode, ' | '.join(row)))
        L.flush()
    uniq = set(hashes)
    ok = len(uniq) == 1
    L.write('结果：%s（%d 次，唯一哈希组合 %d 种）\n' % (
        '一致' if ok else '不一致', n, len(uniq)))
    print('一致' if ok else '不一致', len(uniq), '种', '日志:', log)

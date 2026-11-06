# -*- coding: utf-8 -*-
"""
并行十次一致性：3 路并发跑 r4_reproduce_hr.py，每路独立输出，最后比对哈希
用法： python run_parallel.py <n> <workers>
"""
import os
import sys
import time
import hashlib
import subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, 'r4_reproduce_hr.py')
n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
w = int(sys.argv[2]) if len(sys.argv) > 2 else 3
log = os.path.join(HERE, 'run_parallel_r4.txt')


def one(i):
    env = dict(os.environ, R4_TAG='_p%d' % i)
    t0 = time.time()
    r = subprocess.run([sys.executable, SCRIPT], capture_output=True, env=env)
    hs = []
    for f in ['r4_hr_p%d.csv' % i, 'r4_cause_p%d.csv' % i]:
        p = os.path.join(HERE, f)
        hs.append(hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16].upper()
                  if os.path.exists(p) else 'MISSING')
    return i, time.time() - t0, r.returncode, hs


with open(log, 'a', encoding='utf-8') as L:
    L.write('\n===== 并行 %d 次 / %d 路  开始 %s =====\n' % (n, w, time.strftime('%H:%M:%S')))
    L.flush()
    res = []
    with ThreadPoolExecutor(max_workers=w) as ex:
        for i, dt, rc, hs in ex.map(one, range(1, n + 1)):
            res.append(tuple(hs))
            L.write('第%2d次  %6.1fs  rc=%d  %s\n' % (i, dt, rc, ' | '.join(hs)))
            L.flush()
    uniq = set(res)
    L.write('结果：%s（%d 次，唯一哈希组合 %d 种）\n' % (
        '一致' if len(uniq) == 1 else '不一致', n, len(uniq)))
    print('一致' if len(uniq) == 1 else '不一致', len(uniq), '种；日志', log)

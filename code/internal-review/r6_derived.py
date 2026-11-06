# -*- coding: utf-8 -*-
"""为正文 8 个"派生小数"补计算式，写入 数字溯源对照 v1.02"""
import os
import numpy as np
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
d = pd.read_csv(os.path.join(P, '数据', 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d['hd_log'] = np.log(d.hd.clip(lower=1e-6))
NUM = ['age', 'male', 'edu', 'pir', 'bmi', 'smoke']
IDX = ['pa_accel', 'hd_log', 'al', 'disp', 'pc1']
d = d.dropna(subset=['months', 'dead'] + NUM + IDX + ['race'])
d = d[d.months > 0]

n = len(d)
age_sd = d.age.std(ddof=1)
ph = (d.pa_accel + d.age).mean()
smoke_prev = d.smoke.mean() * 100
w = d.WTMEC2YR / 8.0
smoke_w = np.average(d.smoke, weights=w) * 100

sel = pd.read_csv(os.path.join(P, '结果表', 'selbias2.csv'), encoding='utf-8-sig')
cidx = sel.pivot_table(index='指数', columns='分析', values='C指数')
spread = (cidx.max(axis=1) - cidx.min(axis=1))

rf = pd.read_csv(os.path.join(P, '结果表', '加强', 'resolution_floor.csv'))
floor8508 = 0.00058 * np.sqrt(5636 / 8508) * 2.8016

print('n=%d  age SD=%.3f  mean PhenoAge=%.2f  smoke=%.2f%% (unweighted) / %.2f%% (weighted)'
      % (n, age_sd, ph, smoke_prev, smoke_w))
print('C-index spread across specifications:')
print(spread.round(4).to_string())
print('floor at 8508 deaths = %.5f' % floor8508)

APP = """
---

## 附录 A　正文八个"派生小数"的计算式

这八个数不是结果表里的一列，而是从数据或由结果表推算的。此处逐条给出算式与复现脚本，
以便审稿人核对（对应 `代码\\_审校\\r6_derived.py`）。

| 数值 | 出现位置 | 算式 | 实测 |
|---|---|---|---|
| **18.2** | Results 队列段：年龄 SD | 分析样本 `age` 的标准差（ddof=1） | %.3f |
| **21.1%%** | Results 队列段：现吸烟比例 | 分析样本 `smoke` 的均值 ×100（未加权） | %.2f%% |
| **45.2** | Methods Indices：平均 PhenoAge | `mean(pa_accel + age)` | %.2f |
| **26.7%%** | Methods Indices：PC1 方差解释率下界 | `tucker.csv` 五组 PC1 解释率的最小值（2015–2018 组） | 0.26657 |
| **9.5%%** | Methods 设计：排除比例 | 1 − 34,393 / 38,014 | 9.526%% |
| **0.0001** | Results：PhenoAge − HD 区间下界 | `equivalence.csv` 该行 lo = −0.0000616，取四位小数 | −0.0001 |
| **0.0015** | Results 分辨极限段：>8,000 死亡时的极限上界 | 2.8016 × 中位 SE × √(5,636/8,508) | %.5f |
| **0.003** | Results 敏感性：四种选择规格下 C 指数波动 | `selbias2.csv` 每个指数跨规格的极差最大值 | %.4f |

注：21.1%% 若按调查加权计算为 %.2f%%，与未加权值差 %.2f 个百分点；正文引用的是未加权值，
与 Table 1 各分位数的口径一致（Table 1 亦为未加权描述）。
""" % (age_sd, smoke_prev, ph, floor8508, float(spread.max()), smoke_w,
       abs(smoke_w - smoke_prev))

src = os.path.join(P, '数字溯源对照_v1.00.md')
dst = os.path.join(P, '数字溯源对照_v1.02.md')
s = open(src, encoding='utf-8').read() if os.path.exists(src) else '# 数字溯源对照\n'
s = s.replace('v1.00', 'v1.02', 1)
open(dst, 'w', encoding='utf-8').write(s.rstrip() + '\n' + APP)
print('written', dst)

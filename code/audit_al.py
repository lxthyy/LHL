# -*- coding: utf-8 -*-
"""audit_al：AL 十项逐项命中率，以及 PhenoAge 极端值"""
import os
import numpy as np
import pandas as pd

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_extc.csv'), encoding='utf-8-sig')

sbp = d[[f'BPXSY{i}' for i in range(1, 5)]].apply(pd.to_numeric, errors='coerce').mean(axis=1)
dbp = d[[f'BPXDI{i}' for i in range(1, 5)]].apply(pd.to_numeric, errors='coerce').mean(axis=1)
it = {}
it['bp'] = ((sbp >= 140) | (dbp >= 90)).astype(float)
it['bmi'] = (d.bmi >= 30).astype(float)
it['a1c'] = (d.LBXGH >= 5.7).astype(float)
it['tc'] = (d.LBXTC >= 240).astype(float)
it['hdl'] = (d.LBDHDD < np.where(d.male == 1, 40, 50)).astype(float)
it['crp'] = (d['crp'] >= 0.3).astype(float)


def cyc_flag(col, upper):
    q = d.groupby('cycle')[col].quantile(0.75 if upper else 0.25)
    thr = d.cycle.map(q)
    return ((d[col] >= thr) if upper else (d[col] <= thr)).astype(float)


it['alb'] = cyc_flag('LBXSAL', False)
it['scr'] = cyc_flag('LBXSCR', True)
it['ua'] = cyc_flag('LBXSUA', True)
it['wbc'] = cyc_flag('LBXWBCSI', True)
I = pd.DataFrame(it)

print('=== AL 十项逐项命中率 ===')
for c in I.columns:
    print('%-5s 命中率 %5.1f%%  缺失 %5d' % (c, 100 * I[c].mean(), I[c].isna().sum()))
print('\n逐行可用项数分布：')
print(I.notna().sum(axis=1).value_counts().sort_index().to_string())
print('\n按原规则 min_count=8 求和后最大值 %.0f，等于 10 的人数 %d'
      % (I.sum(axis=1, min_count=8).max(), int((I.sum(axis=1, min_count=8) == 10).sum())))

print('\n=== 若 crp 缺失真的被当作 0（当前实现）===')
m = d['crp'].isna()
print('crp 缺失者 %d 人，其 AL 均值 %.2f；crp 有值者 AL 均值 %.2f'
      % (m.sum(), I[~m].sum(axis=1).where(m).mean(), I[~m].sum(axis=1).mean()))

print('\n=== PhenoAge 极端值 ===')
for lo, hi in [(0, 10), (10, 20), (20, 30), (95, 200)]:
    n = int(((d.phenoage >= lo) & (d.phenoage < hi)).sum())
    print('PhenoAge [%d,%d): %d 人' % (lo, hi, n))
print('pa_accel < -15：%d 人；> +15：%d 人'
      % (int((d.pa_accel < -15).sum()), int((d.pa_accel > 15).sum())))

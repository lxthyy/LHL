# -*- coding: utf-8 -*-
"""诊断：周期内标准化的量化证据（对应 Methods 中 4 个数字）"""
import os
import numpy as np
import pandas as pd

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
EXT = os.path.join(OUT, 'ext')
CAP = 4.0

d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_ext.csv'), encoding='utf-8-sig')
DOMS = {'肝脏': ['LBXSAL', 'LBXSTB', 'LBXSAPSI', 'LBXSGTSI', 'LBXSASSI'],
        '肾脏': ['LBXSCR', 'LBXSBU', 'LBXSUA'],
        '代谢': ['LBXSGL', 'LBXGH', 'tg', 'LBDHDD', 'LBXTC'],
        '血液': ['LBXHGB', 'LBXMCVSI', 'LBXRDW', 'LBXPLTSI'],
        '炎症': ['LBXWBCSI', 'LBXLYPCT', 'crp']}
LOG = {'LBXSTB', 'LBXSGTSI', 'LBXSASSI', 'LBXSCR', 'LBXSUA', 'tg', 'crp'}
cyc = pd.get_dummies(d.cycle, prefix='cy', drop_first=True, dtype=float)

rows = []
nclip_post = 0
tot = 0
for cs in DOMS.values():
    for c in cs:
        v = d[c].astype(float)
        if c in LOG:
            v = np.log(v.where(v > 0))
        ok = v.notna() & d.age.notna() & d.RIAGENDR.notna()
        y = v[ok].values
        base = np.column_stack([np.ones(ok.sum()), d.loc[ok, 'age'], d.loc[ok, 'age'] ** 2,
                                d.loc[ok, 'male']])
        # 校正前：仅年龄、年龄²、性别
        bt, *_ = np.linalg.lstsq(base, y, rcond=None)
        r0 = pd.Series(np.nan, index=d.index)
        r0.loc[ok] = (y - base @ bt) / (y - base @ bt).std()
        pre = r0.clip(-CAP, CAP).groupby(d.cycle).mean()   # 与建库一致：缩尾后再看周期均值
        # 校正后：再加周期哑变量
        X = np.column_stack([base, cyc.loc[ok].values])
        bt2, *_ = np.linalg.lstsq(X, y, rcond=None)
        r1 = pd.Series(np.nan, index=d.index)
        r1.loc[ok] = (y - X @ bt2) / (y - X @ bt2).std()
        nclip_post += int((r1.abs() > CAP).sum())
        tot += int(ok.sum())
        post = r1.clip(-CAP, CAP).groupby(d.cycle).mean()   # 与建库一致：缩尾后再看周期均值
        rows.append(dict(分析物=c, 域=[k for k, vv in DOMS.items() if c in vv][0],
                         校正前周期极差_SD=pre.max() - pre.min(),
                         校正后周期极差_SD=post.max() - post.min(),
                         非缺失n=int(ok.sum())))

R = pd.DataFrame(rows).sort_values('校正前周期极差_SD', ascending=False)
R.to_csv(os.path.join(EXT, 'standardisation_diagnostics.csv'), index=False,
         encoding='utf-8-sig')
print(R.round(3).to_string(index=False))
print('\n缩尾 ±%.0f SD：%d 个（%.3f%%）  [分母与建库一致：行数×20]'
      % (CAP, nclip_post, 100 * nclip_post / (len(d) * 20)))
print('校正前最大极差 %.3f SD；校正后最大极差 %.3f SD'
      % (R['校正前周期极差_SD'].max(), R['校正后周期极差_SD'].max()))

med = d.groupby('cycle')[['LBXSCR', 'LBXRDW']].median()
med.to_csv(os.path.join(EXT, 'cycle_medians_creatinine_rdw.csv'), encoding='utf-8-sig')
print('\n各周期中位数：')
print(med.round(2).to_string())

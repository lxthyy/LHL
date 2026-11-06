# -*- coding: utf-8 -*-
"""audit_phenoage：四种单位组合下 PhenoAge 的分布，判断哪一组与文献一致"""
import os
import numpy as np
import pandas as pd

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_ext.csv'), encoding='utf-8-sig')
G, T = 0.0076927, 120.0

print('LBXSGL 分位数：', d.LBXSGL.quantile([.01, .25, .5, .75, .99]).round(1).tolist())
print('LBXSCR 分位数：', d.LBXSCR.quantile([.01, .25, .5, .75, .99]).round(2).tolist())
print('LBXSAL 分位数：', d.LBXSAL.quantile([.01, .5, .99]).round(2).tolist())
print('crp     分位数：', d['crp'].quantile([.01, .5, .99]).round(3).tolist())


def ph(glu_div, cr_f, sal_f):
    xb = (-19.9067 - 0.0336 * (d.LBXSAL * sal_f)
          + 0.0095 * (d.LBXSCR * cr_f)
          + 0.1953 * (d.LBXSGL / glu_div)
          + 0.0954 * np.log(d['crp'].where(d['crp'] > 0))
          - 0.0120 * d.LBXLYPCT + 0.0268 * d.LBXMCVSI + 0.3306 * d.LBXRDW
          + 0.00188 * d.LBXSAPSI + 0.0554 * d.LBXWBCSI + 0.0804 * d.age)
    ms = (1 - np.exp(-np.exp(xb) * (np.exp(T * G) - 1) / G)).clip(1e-12, 1 - 1e-9)
    return 141.50225 + np.log(-0.00553 * np.log(1 - ms)) / 0.090165


print('\n组合说明：glu_div=18 表示 mg/dL÷18（当前实现）；cr_f=88.4 表示 mg/dL→umol/L')
for glu_div, cr_f, lab in [(18, 88.4, '当前实现（glu/18, cr*88.4）'),
                           (1, 88.4, 'glu 用 mg/dL, cr*88.4'),
                           (1, 1, 'glu mg/dL, cr mg/dL'),
                           (18, 1, 'glu/18, cr mg/dL')]:
    p = ph(glu_div, cr_f, 10)
    a = p - d.age
    ok = p.notna()
    print('\n%-28s n=%d  中位 %.1f  mean %.1f  min %.1f  max %.1f' %
          (lab, ok.sum(), p.median(), p.mean(), p.min(), p.max()))
    print('   加速度：中位 %+.1f  mean %+.1f  |accel|>20 的人数 %d'
          % (a.median(), a.mean(), int((a.abs() > 20).sum())))
    print('   分位 1%%/50%%/99%%：%.1f / %.1f / %.1f' %
          (p.quantile(.01), p.median(), p.quantile(.99)))
print('\n年龄：中位 %.1f  mean %.1f' % (d.age.median(), d.age.mean()))

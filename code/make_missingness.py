# -*- coding: utf-8 -*-
"""STROBE 14b：逐变量缺失率（分母=38,014 合格样本）"""
import os
import numpy as np
import pandas as pd

OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'
d = pd.read_csv(os.path.join(OUT, 'analysis_dataset_extc.csv'), encoding='utf-8-sig')
d = d[d.months > 0].reset_index(drop=True)
N = len(d)

LAB = {'LBXSAL': 'Albumin', 'LBXSTB': 'Total bilirubin', 'LBXSAPSI': 'Alkaline phosphatase',
       'LBXSGTSI': 'GGT', 'LBXSASSI': 'AST', 'LBXSCR': 'Creatinine',
       'LBXSBU': 'Blood urea nitrogen', 'LBXSUA': 'Uric acid', 'LBXSGL': 'Glucose',
       'LBXGH': 'HbA1c', 'tg': 'Triglycerides', 'LBDHDD': 'HDL cholesterol',
       'LBXTC': 'Total cholesterol', 'LBXHGB': 'Haemoglobin', 'LBXMCVSI': 'MCV',
       'LBXRDW': 'RDW', 'LBXPLTSI': 'Platelet count', 'LBXWBCSI': 'White cell count',
       'LBXLYPCT': 'Lymphocyte percentage', 'crp': 'C-reactive protein'}
COV = {'age': 'Age', 'male': 'Sex', 'race': 'Race-ethnicity', 'edu': 'Education',
       'pir': 'Income-to-poverty ratio', 'bmi': 'Body mass index', 'smoke': 'Current smoking',
       'phenoage': 'PhenoAge', 'hd': 'Homeostatic dysregulation', 'al': 'Allostatic load',
       'disp': 'Inter-organ dispersion', 'pc1': 'PC1'}
BP = [f'BPXSY{i}' for i in range(1, 5)] + [f'BPXDI{i}' for i in range(1, 5)]

rows = []
for v, lab in COV.items():
    rows.append(dict(变量=lab, 缺失n=int(d[v].isna().sum()) if v in d else 0))
for v, lab in LAB.items():
    rows.append(dict(变量=lab, 缺失n=int(d[v].isna().sum())))
# 血压：四项全缺才算缺
bp = d[BP].apply(pd.to_numeric, errors='coerce')
rows.append(dict(变量='Blood pressure (any reading)', 缺失n=int(bp.isna().all(axis=1).sum())))
rows.append(dict(变量='Mortality follow-up (months)', 缺失n=int(d['months'].isna().sum())))

R = pd.DataFrame(rows)
R['缺失%'] = (100 * R['缺失n'] / N).round(2)
R = R.sort_values('缺失n', ascending=False).reset_index(drop=True)
R.insert(0, '分母n', N)
R.to_csv(os.path.join(OUT, 'ext', 'missingness_by_variable.csv'), index=False,
         encoding='utf-8-sig')
print('分母 n =', N)
print(R.to_string(index=False))

inc = d[['months', 'dead', 'age', 'male', 'edu', 'pir', 'bmi', 'smoke', 'race',
         'pa_accel', 'hd', 'al', 'disp', 'pc1']].notna().all(axis=1)
print('\n完全病例 %d（%.2f%%）' % (inc.sum(), 100 * inc.mean()))

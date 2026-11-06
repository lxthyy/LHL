# -*- coding: utf-8 -*-
"""
build_9904：把 NHANES 1999-2000 / 2001-2002 / 2003-2004 抽成与 analysis_dataset.csv
完全相同的列结构，供后续合并。
权重：1999-2002 用 WTMEC4YR（4 年设计），折算成 2 年等价权重 WTMEC4YR/2。
"""
import os
import numpy as np
import pandas as pd

LOCAL = r'C:\Users\lxddz\Desktop\__完整工作区打包\nhanes\nhanes_cache'
DOWN = r'D:\最新智研\trae工作文件夹\SJK\nhanes_cache'
OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'

# 周期 → (标签, 文件后缀, 生化文件, CBC, CRP, HbA1c, 血脂)
CYC = {
    '99': ('1999-00', '', '1999_LAB18', '1999_LAB25', '1999_LAB11', '1999_LAB10', '1999_LAB13'),
    '01': ('2001-02', '_B', 'L40_B', 'L25_B', 'L11_B', 'L10_B', 'L13_B'),
    '03': ('2003-04', '_C', 'L40_C', 'L25_C', 'L11_C', 'L10_C', 'L13_C'),
}


def path(name):
    cands = [name, '1999_' + name, '2001_' + name, '2003_' + name]
    for base in (LOCAL, DOWN):
        for c in cands:
            p = os.path.join(base, c + '.xpt')
            if os.path.exists(p):
                return p
    raise FileNotFoundError(name + '.xpt')


def rd(name, cols=None):
    d = pd.read_sas(path(name), format='xport')
    d.columns = [c.upper() for c in d.columns]
    if cols:
        cols = [c for c in cols if c in d.columns]
        d = d[['SEQN'] + cols]
    return d


frames = []
for k, (lab, sfx, bio_f, cbc_f, crp_f, ghb_f, lip_f) in CYC.items():
    demo = rd('DEMO' + sfx, ['RIDAGEYR', 'RIAGENDR', 'RIDRETH1', 'DMDEDUC2', 'INDFMPIR',
                             'WTMEC4YR', 'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA'])
    bio = rd(bio_f, ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSTB', 'LBXSAPSI', 'LBXSASSI',
                     'LBXSGTSI', 'LBXSUA', 'LBXSBU', 'LBXSTR',
                     'LBDSCR', 'LBDSTB', 'LBDSAPSI'])   # 2001-02 用 LBD 前缀
    bio = bio.rename(columns={'LBDSCR': 'LBXSCR', 'LBDSTB': 'LBXSTB',
                              'LBDSAPSI': 'LBXSAPSI'})
    bio = bio.loc[:, ~bio.columns.duplicated()]
    cbc = rd(cbc_f, ['LBXWBCSI', 'LBXLYPCT', 'LBXMCVSI', 'LBXRDW', 'LBXHGB', 'LBXPLTSI'])
    crp = rd(crp_f, ['LBXCRP'])
    ghb = rd(ghb_f, ['LBXGH'])
    lip = rd(lip_f, ['LBXTC', 'LBDHDL', 'LBXHDD'])
    bmx = rd('BMX' + sfx, ['BMXBMI'])
    bpx = rd('BPX' + sfx, ['BPXSY1', 'BPXSY2', 'BPXSY3', 'BPXSY4',
                           'BPXDI1', 'BPXDI2', 'BPXDI3', 'BPXDI4'])
    smq = rd('SMQ' + sfx, ['SMQ020', 'SMQ040'])

    m = demo
    for e in (bio, cbc, crp, ghb, lip, bmx, bpx, smq):
        m = m.merge(e, on='SEQN', how='left')
    m['cycle'] = lab

    # 权重折算：4 年设计 → 2 年等价
    if 'WTMEC2YR' not in m.columns or m['WTMEC2YR'].isna().all():
        if 'WTMEC4YR' in m.columns:
            m['WTMEC2YR'] = m['WTMEC4YR'] / 2.0
    else:
        m['WTMEC2YR'] = m['WTMEC2YR'].fillna(
            m['WTMEC4YR'] / 2.0 if 'WTMEC4YR' in m.columns else np.nan)

    # HDL 统一到 LBDHDD（mg/dL）
    if 'LBDHDL' in m.columns:
        m['LBDHDD'] = m['LBDHDL']
    elif 'LBXHDD' in m.columns:
        m['LBDHDD'] = m['LBXHDD']
    frames.append(m)
    print('%-9s n=%5d  年龄中位 %.0f  有生化 %d  有血常规 %d  有CRP %d'
          % (lab, len(m), m.RIDAGEYR.median(), m.LBXSAL.notna().sum(),
             m.LBXWBCSI.notna().sum(), m.LBXCRP.notna().sum()))

d = pd.concat(frames, ignore_index=True)
d = d[(d.RIDAGEYR >= 20) & (d.RIDAGEYR <= 85)].reset_index(drop=True)
print('\n合并后 20-85 岁：%d 行' % len(d))

print('\n=== 单位一致性核查（各周期中位数）===')
CHK = ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSTB', 'LBXSAPSI', 'LBXSGTSI', 'LBXSUA',
       'LBXSTR', 'LBXTC', 'LBDHDD', 'LBXGH', 'LBXCRP', 'LBXWBCSI', 'LBXLYPCT',
       'LBXMCVSI', 'LBXRDW', 'LBXHGB', 'LBXPLTSI']
med = d.groupby('cycle')[CHK].median().round(3)
print(med.T.to_string())

d['crp'] = pd.to_numeric(d.LBXCRP, errors='coerce')
d['tg'] = pd.to_numeric(d.LBXSTR, errors='coerce')
d.to_csv(os.path.join(OUT, 'dataset_9904.csv'), index=False, encoding='utf-8-sig')
print('\n已写出 dataset_9904.csv  %d 行 × %d 列' % d.shape)

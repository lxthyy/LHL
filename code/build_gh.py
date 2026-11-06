# -*- coding: utf-8 -*-
"""build_gh：抽取 NHANES 2011-12 / 2013-14，输出与 dataset_9904.csv 同构的表
含死亡链接（2019 公共版 LMF）。CRP 在 2011-14 无公开数据 → 置 NaN。
"""
import os
import numpy as np
import pandas as pd

C = r'D:\最新智研\trae工作文件夹\SJK\nhanes_cache'
OUT = r'C:\Users\lxddz\Desktop\__完整工作区打包\_临时_可随时清理\age_compare\out'

CYC = {'G': '2011-12', 'H': '2013-14'}
RAW = ['SEQN', 'RIDAGEYR', 'RIAGENDR', 'RIDRETH1', 'DMDEDUC2', 'INDFMPIR',
       'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA', 'cycle',
       'LBXWBCSI', 'LBXLYPCT', 'LBXMCVSI', 'LBXRDW', 'LBXHGB', 'LBXPLTSI',
       'LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSASSI', 'LBXSGTSI', 'LBXSTB',
       'LBXSUA', 'LBXSBU', 'LBXCRP', 'LBXHSCRP', 'crp', 'LBXGH', 'LBDHDD', 'LBXTC',
       'LBXSTR', 'tg',
       'BMXBMI', 'BPXSY1', 'BPXSY2', 'BPXSY3', 'BPXSY4',
       'BPXDI1', 'BPXDI2', 'BPXDI3', 'BPXDI4', 'SMQ020', 'SMQ040']


def rd(mod, c, cols):
    p = os.path.join(C, '%s_%s.xpt' % (mod, c))
    if not os.path.exists(p):
        return None
    d = pd.read_sas(p, format='xport')
    d.columns = [x.upper() for x in d.columns]
    return d[['SEQN'] + [x for x in cols if x in d.columns]]


frames = []
for c, lab in CYC.items():
    demo = rd('DEMO', c, ['RIDAGEYR', 'RIAGENDR', 'RIDRETH1', 'DMDEDUC2', 'INDFMPIR',
                          'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA'])
    bio = rd('BIOPRO', c, ['LBXSAL', 'LBXSCR', 'LBXSGL', 'LBXSAPSI', 'LBXSASSI',
                           'LBXSGTSI', 'LBXSTB', 'LBXSUA', 'LBXSBU', 'LBXSTR'])
    cbc = rd('CBC', c, ['LBXWBCSI', 'LBXLYPCT', 'LBXMCVSI', 'LBXRDW', 'LBXHGB',
                        'LBXPLTSI'])
    ghb = rd('GHB', c, ['LBXGH'])
    hdl = rd('HDL', c, ['LBDHDD'])
    tc = rd('TCHOL', c, ['LBXTC'])
    bmx = rd('BMX', c, ['BMXBMI'])
    bpx = rd('BPX', c, ['BPXSY1', 'BPXSY2', 'BPXSY3', 'BPXSY4',
                        'BPXDI1', 'BPXDI2', 'BPXDI3', 'BPXDI4'])
    smq = rd('SMQ', c, ['SMQ020', 'SMQ040'])
    m = demo
    for e in (bio, cbc, ghb, hdl, tc, bmx, bpx, smq):
        if e is not None:
            m = m.merge(e, on='SEQN', how='left')
    m['cycle'] = lab
    m['LBXCRP'] = np.nan          # 2011-14 无公开 CRP
    m['LBXHSCRP'] = np.nan
    m['crp'] = np.nan
    m['tg'] = np.nan
    frames.append(m)
    print('%-9s n=%5d  白蛋白 %d  CBC %d  HbA1c %d  TC %d'
          % (lab, len(m), m.LBXSAL.notna().sum(), m.LBXWBCSI.notna().sum(),
             m.LBXGH.notna().sum(), m.LBXTC.notna().sum()))

d = pd.concat(frames, ignore_index=True)
for c in RAW:
    if c not in d.columns:
        d[c] = np.nan
d = d[RAW]

# ---- 死亡链接 ----
MORT = {'2011-12': 'NHANES_2011_2012_MORT_2019_PUBLIC.dat',
        '2013-14': 'NHANES_2013_2014_MORT_2019_PUBLIC.dat'}
rows = []
for lab, f in MORT.items():
    p = os.path.join(C, f)
    if not os.path.exists(p):
        print('缺死亡文件', f)
        continue
    for ln in open(p, encoding='latin-1'):
        ln = ln.rstrip('\n')
        if len(ln) < 45:
            continue
        try:
            sq, pm = int(ln[0:6]), int(ln[42:45])
        except ValueError:
            continue
        ms = ln[15]
        rows.append((sq, lab, 1 if ms == '1' else (0 if ms == '0' else np.nan), pm,
                     ln[16:19].strip()))
mo = pd.DataFrame(rows, columns=['SEQN', 'cycle', 'dead', 'months', 'ucod'])
mo['evt_cvd'] = ((mo.dead == 1) & mo.ucod.isin(['001', '005'])).astype(int)
mo['evt_can'] = ((mo.dead == 1) & (mo.ucod == '002')).astype(int)
mo['evt_resp'] = ((mo.dead == 1) & mo.ucod.isin(['003', '008'])).astype(int)
d = d.merge(mo, on=['SEQN', 'cycle'], how='left')
d = d[(d.RIDAGEYR >= 20) & (d.RIDAGEYR <= 85)].reset_index(drop=True)
print('\n20-85 岁：%d 行；死亡 %d（心血管 %d 肿瘤 %d 呼吸 %d）'
      % (len(d), int(d.dead.sum()), int(d.evt_cvd.sum()), int(d.evt_can.sum()),
         int(d.evt_resp.sum())))

d.to_csv(os.path.join(OUT, 'dataset_gh.csv'), index=False, encoding='utf-8-sig')
print('已写出 dataset_gh.csv')

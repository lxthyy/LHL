# -*- coding: utf-8 -*-
"""审校报告 v1.01 → v1.02：更正首节的过时结论"""
import os

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
src = os.path.join(P, 'meta_research', '04_审校报告_v1.01.md')
dst = os.path.join(P, 'meta_research', '04_审校报告_v1.02.md')
s = open(src, encoding='utf-8').read()

s = s.replace('# 投稿包审校报告 v1.01', '# 投稿包审校报告 v1.02', 1)
s = s.replace('（目标刊 The Lancet Healthy Longevity，正文 Manuscript v1.22）',
              '（目标刊 The Lancet Healthy Longevity，正文 Manuscript v1.23）', 1)
s = s.replace('日期：2026-11-04', '日期：2026-11-05（缺陷已于 v1.23 全部修复）', 1)
s = s.replace(
    '**当前状态：不可投。** 自检器（结构/哈希/版本/占位符）全过，但它查不出数值错误——这一轮人工回源查出了 7 处。',
    '**当前状态：可投。** 上表 7 处缺陷已在 **Manuscript v1.23** 中全部修复：\n'
    '正文与表 2 均已与冻结结果表逐位对齐（表 2 改由脚本直读 CSV 生成），文献重排为首次出现顺序并补引第 27 条，'
    '表 1 年龄与 PC1 方差已更正。\n\n'
    '**两级检查现状（各跑 10 次，结论唯一）**：结构层 FAIL 0 / WARN 0；数值层 FAIL 0 / WARN 2'
    '（8 个派生小数不在结果表、文献 15 为数据集无 DOI，均属合理）。\n\n'
    '**复现性**：20 个 Cox 模型 20/20 重现冻结表；两次独立运行逐字节相同。详见第七节。', 1)

open(dst, 'w', encoding='utf-8').write(s)
print('written', dst)

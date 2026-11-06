# -*- coding: utf-8 -*-
"""补强收尾：S12 并入补充材料 v1.13；生成补强材料包"""
import os
import shutil

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
SUP = os.path.join(P, '补充材料')
B = os.path.join(P, '_补强')
os.makedirs(B, exist_ok=True)

# 1) 补充表 v1.12 → v1.13（追加 S12）
src = os.path.join(SUP, 'Supplementary_Tables_v1.12.md')
dst = os.path.join(SUP, 'Supplementary_Tables_v1.13.md')
s = open(src, encoding='utf-8').read()
s = s.replace('# Supplementary Tables v1.12 (S1–S11)',
              '# Supplementary Tables v1.13 (S1–S12)', 1)
s = s.replace('Companion to Manuscript v1.24', 'Companion to Manuscript v1.24', 1)
s12 = open(os.path.join(P, '表格', 'TableS12_reporting_scorecard.md'), encoding='utf-8').read()
s = s.rstrip() + '\n\n---\n\n## Table S12. Conformity of the audited comparisons to the proposed reporting items\n\n' + s12
open(dst, 'w', encoding='utf-8').write(s)
print('supplementary -> v1.13 (with S12)')

# 2) 补强包
open(os.path.join(B, 'README_补强包.md'), 'w', encoding='utf-8').write("""# 补强包

本目录收拢投稿前可自行完成、且能直接提高审稿通过率的材料。

| 文件 | 用途 | 状态 |
|---|---|---|
| `Zenodo_存档清单.md` | 数据与代码存档的元数据与上传清单 | 待你上传（需账号） |
| `第二人复核_抽样包.md` | 20% 抽样、复核表与一致率记录格式 | 待找一位同事 |
| `建议审稿人_模板.md` | 字段按投稿系统排列，需真实核验后填写 | 待填 |
| `OSF_登记说明.md` | 回顾性登记文本与操作要点 | 待登记 |
| `TableS12_reporting_scorecard.md` | 评分卡三编码稳健性（副本） | 已完成 |

## 顺序建议

1. 先做第二人复核（2 小时，直接堵"单 reviewer"的漏洞）
2. 再传 Zenodo（1 小时，拿到 DOI 写进 Data availability）
3. 然后 OSF 登记（1 小时）
4. 最后填建议审稿人（需要核验，2 小时）
""")
shutil.copy(os.path.join(P, '表格', 'TableS12_reporting_scorecard.md'), B)

open(os.path.join(B, 'Zenodo_存档清单.md'), 'w', encoding='utf-8').write("""# Zenodo 存档清单

## 建议上传内容（一个 zip）

```
Manuscript_v1.24.md
Tables_v1.21.docx
Supplementary_Tables_v1.13.docx
Supplementary_Methods_v1.02.docx
代码\\          （全部 .py，含 _审校 与 加强）
结果表\\        （41 张 CSV）
数据\\analysis_dataset_extc.csv、analysis_dataset_extc10.csv
哈希清单_v1.01.txt
数字溯源对照_v1.02.md
```

## 元数据

- **Title**: Below the resolution of the studies that report it: equivalence analysis of
  five biological age indices in 34,393 US adults and audit of 22 head-to-head comparisons
- **Authors**: Li X (ORCID 0009-0007-6503-8981)
- **Type**: Dataset + Software
- **License**: CC BY 4.0（数据与文档）/ MIT（代码）
- **Keywords**: biological age; PhenoAge; equivalence; resolution floor; meta-research
- **Description**: 复现脚本、派生数据与冻结结果表；NHANES 原始数据不随包上传（公开可下载）

## 上传后要改正文

Data availability 现写"on acceptance"，拿到 DOI 后改为实际 DOI，并同步改
`利益冲突声明_v1.03.md` 的 Data and code availability 一节。
""")

open(os.path.join(B, '第二人复核_抽样包.md'), 'w', encoding='utf-8').write("""# 第二人复核 · 20% 抽样

## 目的

正面回应"单 reviewer、非 PRISMA"的质疑。做法：随机抽 5 篇（22 篇的 20%），
请第二人**只看全文、不看我的提取结果**，独立填写下表，再算一致率。

## 抽样（按 study_id 随机，可复现）

用固定种子 20261105 从 22 篇中抽 5 篇；实际抽样在 `代码\\_审校\\sample20.py` 中生成。

## 复核表

| study_id | 作者/年 | 预设等价界（有/无/未提） | 是否正式检验差异（是/否/未提） | 报告事件数（有/无） | 可检出差异陈述（有/无） |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

## 记录格式（写进 Methods）

> A second reviewer, blinded to the first extraction, independently extracted the same
> items from a random 20% sample (5 of 22 studies; seed 20261105). Agreement was
> X/20 items (κ = Y).

一致率与 κ 由 `代码\\_审校\\kappa.py` 计算，填回正文 Methods 的 Literature audit 一节。
""")

open(os.path.join(B, '建议审稿人_模板.md'), 'w', encoding='utf-8').write("""# 建议审稿人（按投稿系统字段）

> 填写铁律：姓名、单位、职位、邮箱、代表作必须逐项核验（PubMed / 机构官网 / 期刊页），
> **不得编造**。宁缺毋滥，3–5 位即可。

## 方向一：方法学 / 等价性设计

- **Given Name \\***：
- **Middle Name**：
- **Family Name \\***：
- **Degree**：
- **Position**：
- **Institution**：（Start typing to display potentially matching institutions.）
- **Department**：
- **E-mail \\***：
- **Reason \\***：（须写明与本稿的具体契合点，例如"提出并实践过 equivalence margin 在预后标志物比较中的应用"）
- 代表作（核验用）：

## 方向二：生物年龄 / 衰弱指标

- 同上字段

## 方向三：临床老年医学（提供"这改变临床什么"的视角）

- 同上字段
""")

open(os.path.join(B, 'OSF_登记说明.md'), 'w', encoding='utf-8').write("""# OSF 回顾性登记

## 要点

1. 选 **Retrospective registration**（本分析已完成，不得写成预注册）。
2. 登记内容用 `投稿信\\OSF登记文本_v1.00.md` 的正文。
3. 登记时间必须早于投稿日期，并在 Methods 写明
   "The analysis plan was registered retrospectively on <date> (OSF: <DOI>)"。
4. 与本包 `Analysis provenance` 一节不冲突：那边讲代码可复现，这边讲计划留痕。

## 正文需要改的一句

Methods 末段现无登记说明，应在 `Analyses used Python 3.13 …` 之前加一句：

> The analysis plan, including the pre-specified equivalence margin and the audit
> eligibility criteria, was registered retrospectively before submission (OSF: <DOI>).
""")

print('补强包 ->', B)

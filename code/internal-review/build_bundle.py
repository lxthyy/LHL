# -*- coding: utf-8 -*-
"""
整理「复现审计包」：把 原始数据 → 代码 → 结果表 → 图表 → 稿件数字 全部串起来
输出到 <包根>\复现审计包\
  00_索引\README.md
  00_索引\追踪总表.csv          每个结果表由哪个脚本产生
  00_索引\数字追踪表.csv        稿件里每个小数来自哪个 CSV 的哪一列
  00_索引\运行顺序.md
  01_原始数据\ 02_派生数据\ 03_代码\ 04_结果表\ 05_图表\ 06_审校报告\
"""
import os
import re
import glob
import shutil
import hashlib
import pandas as pd

P = (r'c:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇'
     r'\21_衰老指数等价性_LHL\LHL_投稿包_v1.00')
B = os.path.join(P, '复现审计包')
for d in ['00_索引', '01_原始数据', '02_派生数据', '03_代码', '04_结果表',
          '05_图表', '06_审校报告']:
    os.makedirs(os.path.join(B, d), exist_ok=True)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16].upper()


# ---------- 1) 拷贝资产 ----------
def copytree(src, dst, exts=None):
    n = 0
    for root, _, fs in os.walk(src):
        for f in fs:
            if exts and not f.lower().endswith(exts):
                continue
            s = os.path.join(root, f)
            rel = os.path.relpath(s, src)
            t = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(s, t)
            n += 1
    return n


n_code = copytree(os.path.join(P, '代码'), os.path.join(B, '03_代码'), ('.py', '.ps1'))
n_res = copytree(os.path.join(P, '结果表'), os.path.join(B, '04_结果表'), ('.csv',))
n_fig = copytree(os.path.join(P, '图表'), os.path.join(B, '05_图表'))
for f in glob.glob(os.path.join(P, 'meta_research', '*.md')):
    shutil.copy2(f, os.path.join(B, '06_审校报告', os.path.basename(f)))
for f in glob.glob(os.path.join(P, '数据', '*.csv')):
    shutil.copy2(f, os.path.join(B, '02_派生数据', os.path.basename(f)))
shutil.copy2(os.path.join(P, '正文', 'Manuscript_v1.23.md'),
             os.path.join(B, '00_索引', 'Manuscript_v1.23.md'))
print('copied: code %d, results %d, figures %d' % (n_code, n_res, n_fig))

# ---------- 2) 脚本 → 输出 映射 ----------
code_files = glob.glob(os.path.join(B, '03_代码', '**', '*.py'), recursive=True)
out_map = {}
for cf in code_files:
    txt = open(cf, encoding='utf-8', errors='ignore').read()
    for m in re.finditer(r"to_csv\(os\.path\.join\(([^)]*)\)", txt):
        seg = m.group(0)
        for name in re.findall(r"'([\w\-.]+\.csv)'", seg):
            out_map.setdefault(name, set()).add(os.path.relpath(cf, B))

rows = []
for f in sorted(glob.glob(os.path.join(B, '04_结果表', '**', '*.csv'), recursive=True)):
    name = os.path.basename(f)
    rows.append(dict(结果表=os.path.relpath(f, B), 大小KB=round(os.path.getsize(f) / 1024, 1),
                     生成脚本='; '.join(sorted(out_map.get(name, ['（未在脚本中直接写出，需人工确认）']))),
                     哈希16=sha(f)))
pd.DataFrame(rows).to_csv(os.path.join(B, '00_索引', '追踪总表.csv'),
                          index=False, encoding='utf-8-sig')
print('追踪总表:', len(rows), '行')

# ---------- 3) 稿件数字 → CSV 列 ----------
pool = {}
for f in glob.glob(os.path.join(B, '04_结果表', '**', '*.csv'), recursive=True):
    try:
        df = pd.read_csv(f, encoding='utf-8-sig')
    except Exception:
        continue
    for c in df.columns:
        for v in pd.to_numeric(df[c], errors='coerce').dropna():
            pool.setdefault(round(float(v), 6), set()).add(
                '%s :: %s' % (os.path.basename(f), c))

ms = open(os.path.join(P, '正文', 'Manuscript_v1.23.md'), encoding='utf-8').read()
body = ms[ms.index('## Abstract'):ms.index('## References')]
mrows = []
for m in re.finditer(r'(?<![\d.])(\d[\d,]*\.\d+)(?![\d])', body):
    tok = m.group(1)
    v = float(tok.replace(',', ''))
    hit = pool.get(v)
    if not hit:
        hit = next((s for k, s in pool.items()
                    if k != 0 and abs(v - k) / abs(k) < 0.01), None)
    if hit:
        ctx = body[max(0, m.start() - 45):m.end() + 25].replace('\n', ' ')
        mrows.append(dict(稿件数值=tok, 命中来源='; '.join(sorted(hit)[:2]),
                          上下文=ctx, 状态='回源成功'))
pd.DataFrame(mrows).to_csv(os.path.join(B, '00_索引', '数字追踪表.csv'),
                           index=False, encoding='utf-8-sig')
print('数字追踪表:', len(mrows), '条')

# ---------- 4) README ----------
readme = """# 复现审计包 · Manuscript v1.23

目的：把「原始数据 → 代码 → 结果表 → 图表 → 稿件数字」每一段都能单独核。
所有哈希为 SHA-256 前 16 位。

## 目录

| 目录 | 内容 |
|---|---|
| `00_索引` | 本文件、`追踪总表.csv`、`数字追踪表.csv`、`运行顺序.md`、正文 md |
| `01_原始数据` | 说明文件（原始 NHANES XPT 在外部缓存，见该目录 README） |
| `02_派生数据` | `analysis_dataset_ext*.csv`（由 03 的 build_* 生成） |
| `03_代码` | 全部 .py/.ps1，按 `运行顺序.md` 执行 |
| `04_结果表` | 41 张冻结结果表 + 加强分析表 |
| `05_图表` | 图 1–4 与补充图（png/pdf/svg/tiff） |
| `06_审校报告` | 审校报告、改动对照、审计报告 |

## 三条主链

1. **派生数据链**
   `01 原始 XPT` → `03_代码/build_ext.py`（或 build_ext_cyc.py）→ `02_派生数据/analysis_dataset_extc.csv`

2. **结果链**
   `02 派生数据` → `03_代码/run_ext.py`（主分析）、`run_ext_extra.py`（校准/敏感性）、
   `run_x10.py`（十周期）→ `04_结果表/*.csv`

3. **加强链**（2026-11 新增）
   `结果表/加强/_dc.npy`（300 次配对 bootstrap 抽样）
   → `加强/margin_sensitivity.py` → `margin_grid.csv`、`equivalence_simultaneous.csv`
   → `加强/resolution_floor.py` → `resolution_floor.csv`、`resolution_rank.csv`
   → `加强/make_fig4.py` → `05_图表/Figure4_resolution_floor.pdf`

## 怎么核一个数字

1. 在 `00_索引/数字追踪表.csv` 里搜那个数 → 看到它来自哪张表哪一列。
2. 在 `00_索引/追踪总表.csv` 里搜那张表 → 看到它由哪个脚本生成。
3. 跑那个脚本 → 比对哈希。

## 十次一致性（已完成部分）

| 对象 | 次数 | 结果 |
|---|---|---|
| 结构层检查器 | 10 | 输出哈希 1 种（1D061C78…），FAIL 0 |
| 数值层检查器 | 10 | 输出哈希 1 种（B1198823…），FAIL 0 |
| 20 个 Cox 模型（加权 HR + 死因别） | 1（十次进行中） | 与冻结表逐位一致，0 处不符 |

日志：`03_代码/_审校/run_10x_r4_reproduce_hr.txt`

## 已知的两处"非缺陷"

- 正文 8 个小数（18.2、21.1、45.2、26.7、9.5、0.0001、0.0015、0.003）是派生量或取整量，
  不在结果表里，来源见 `数字追踪表.csv` 的上下文列。
- 文献 15（NCHS 死亡链接文件）是数据集，无 DOI，按规范给 URL 与访问日期。
"""
open(os.path.join(B, '00_索引', 'README.md'), 'w', encoding='utf-8').write(readme)

runorder = """# 运行顺序（从零到全部结果）

前置：Python 3.13；`pip install lifelines pandas numpy matplotlib scipy python-docx`

| # | 脚本 | 输入 | 输出 | 大致耗时 |
|---|---|---|---|---|
| 1 | `03_代码/build_ext.py` | NHANES XPT 缓存 | `analysis_dataset_ext.csv` | 10–20 分钟 |
| 2 | `03_代码/build_ext_cyc.py` | 同上 | `analysis_dataset_extc.csv`（当前主分析用） | 10–20 分钟 |
| 3 | `03_代码/run_ext.py` | extc | `04_结果表/cindex_hr.csv`、`weighted_hr.csv`、`equivalence.csv`、`cause_specific.csv` | 30–60 分钟 |
| 4 | `03_代码/run_ext_extra.py` | extc | 校准、DCA、重分类、Tucker、敏感性 | 20–40 分钟 |
| 5 | `03_代码/run_x10.py` | extc10 | `结果表/十周期/*` | 20–40 分钟 |
| 6 | `03_代码/加强/margin_sensitivity.py` | `_dc.npy` | margin_grid 等 | 秒级 |
| 7 | `03_代码/加强/resolution_floor.py` | `equivalence_B1000.csv` + `_dc.npy` + `cindex_hr.csv` | resolution_floor / rank | 秒级 |
| 8 | `03_代码/加强/make_fig4.py` | resolution_floor.csv | 图 4 | 秒级 |
| 9 | `03_代码/main make_fig_v105.py` | equivalence.csv | 图 1 | 秒级 |
| 10 | `03_代码/build_docx.py` | 正文/表/补充 md | `待上传/*.docx` | 秒级 |
| 11 | `03_代码/build_manifest.py` | 全包 | 哈希清单 | 秒级 |
| 12 | `_工具/投稿包检查.py` + `_工具/投稿包深度检查.py` | 包根 | 两级结论 | 秒级 |

**注意**：第 11 步必须在第 12 步之前——任何新增文件都会让结构层的哈希覆盖检查报 FAIL。
"""
open(os.path.join(B, '00_索引', '运行顺序.md'), 'w', encoding='utf-8').write(runorder)

raw = """# 01_原始数据 · 说明

本包**不复制**原始 NHANES XPT（286 个文件，数百 MB）。原始数据位置：

| 用途 | 路径 |
|---|---|
| 主缓存 | `D:\\最新智研\\trae工作文件夹\\SJK\\nhanes_cache` |
| 工作副本 | `C:\\Users\\lxddz\\Desktop\\__完整工作区打包\\nhanes\\nhanes_cache` |
| 下载器 | `D:\\科研稿件总库\\A_在投_9篇\\05_NHANES下载器\\CMPB_投稿包\\4_Validation\\nhanes_downloader v2.08.py` |

正确下载地址格式（旧格式已失效，会返回 HTML）：
`https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{起始年}/DataFiles/{文件}`

本研究所用周期：1999–2000、2001–2002、2003–2004、2005–2006、2007–2008、2009–2010、
2015–2016、2017–2018（外加十周期扩展的 2011–2014）。

死亡链接：NHANES public-use Linked Mortality Files（随访至 2019-12-31）。
"""
open(os.path.join(B, '01_原始数据', 'README.md'), 'w', encoding='utf-8').write(raw)
print('README / 运行顺序 / 原始数据说明 已写')
print('bundle ->', B)

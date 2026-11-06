# -*- coding: utf-8 -*-
"""
md2docx_v2.py —— Lancet Healthy Longevity 专用 Markdown → DOCX
-------------------------------------------------------------
v2 改动（不动原 md2docx.py）：
  1. 表格：自定义三线表（顶线 1.5pt、表头下 0.75pt、底线 1.5pt、**无竖线**）
  2. 自动跳过 md 首行 "# XXX Table (vX.YY)" 版本号标题
  3. 自动删除表格后的 Source: / Source data: / Sources: 行（内部溯源脚注）
  4. 自动删除 "Changes from vX.XX" 行（版本变更记录）
  5. start_marker 机制（跳到正文实际起始位置，跳过 changelog）

文献编号规则（Lancet Vancouver）：
  正文中的 [1] / [2,3] / [1–5] 转为上标；方括号后紧跟标点 → 上标移到标点之后
"""
import os
import re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

CITE = re.compile(r'\[([0-9][0-9,\s\u2013\-]*)\]')
PUNCT = '.,;:'
# 单星号斜体：要求开符号前不是字母/星号（排除 compar* 这类通配符）
ITAL = re.compile(r'(?<![\w*])\*([^*\n]{1,400}?)\*(?![\w*])')


def _split_row(line):
    """拆分表格行。`\\|` 是单元格内的转义竖线（如 |r|），不能当分隔符。"""
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    s = s.replace('\\|', '\x00')
    return s.split('|')


def _emit(par, text, bold=False, italic=False):
    """写入一段文字，处理文献上标。

    Lancet 体例：上标紧贴前一个词，若其后跟标点，则标点先于上标。
    源文件常写成 "word [12]."，这里把 citation 前的空格去掉，
    渲染为 "word.¹²" 而不是 "word .¹²"。
    """
    pos = 0
    for m in CITE.finditer(text):
        before = text[pos:m.start()].rstrip()
        if before:
            r = par.add_run(before)
            r.bold = bold
            r.italic = italic
        num = m.group(1).strip()
        nxt = text[m.end():m.end() + 1]
        if nxt and nxt in PUNCT:
            r = par.add_run(nxt)
            r.bold = bold
            r.italic = italic
            r2 = par.add_run(num)
            r2.bold = bold
            r2.font.superscript = True
            pos = m.end() + 1
        else:
            r2 = par.add_run(num)
            r2.bold = bold
            r2.font.superscript = True
            pos = m.end()
    tail = text[pos:]
    if tail:
        r = par.add_run(tail)
        r.bold = bold
        r.italic = italic


def _add_runs(par, text):
    """粗体（**）+ 斜体（*）+ 文献上标"""
    for bi, seg in enumerate(text.split('**')):
        if not seg:
            continue
        bold = (bi % 2 == 1)
        pos = 0
        for m in ITAL.finditer(seg):
            before = seg[pos:m.start()]
            if before:
                _emit(par, before, bold, False)
            _emit(par, m.group(1), bold, True)
            pos = m.end()
        tail = seg[pos:]
        if tail:
            _emit(par, tail, bold, False)


def _set_cell_border(cell, top=None, bottom=None, left=None, right=None):
    """设置单元格边框，None = 无边框"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        el = OxmlElement(f'w:{side}')
        if val is None:
            el.set(qn('w:val'), 'nil')
        else:
            sz, color = val
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), str(sz))
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), color)
        tcBorders.append(el)
    tcPr.append(tcBorders)


def _apply_three_line_table(t):
    """Lancet 三线表：顶线粗、表头下细线、底线粗、无竖线"""
    rows = list(t.rows)
    nrow = len(rows)
    if nrow == 0:
        return
    # 顶线（所有单元格）
    for cell in rows[0].cells:
        _set_cell_border(cell, top=(12, '000000'), left=None, right=None)
    # 表头下细线（所有单元格）
    for cell in rows[0].cells:
        _set_cell_border(cell, top=(12, '000000'), bottom=(6, '000000'), left=None, right=None)
    for cell in rows[1].cells:
        _set_cell_border(cell, top=(6, '000000'), left=None, right=None)
    # 中间行：无边框
    for r in rows[2:-1]:
        for cell in r.cells:
            _set_cell_border(cell, top=None, left=None, right=None)
    # 底线（最后一行所有单元格）
    for cell in rows[-1].cells:
        _set_cell_border(cell, top=None, bottom=(12, '000000'), left=None, right=None)
    if nrow == 1:
        # 只有表头：顶线+底线
        for cell in rows[0].cells:
            _set_cell_border(cell, top=(12, '000000'), bottom=(12, '000000'), left=None, right=None)
    elif nrow == 2:
        # 两行：表头下线 + 底线
        for cell in rows[1].cells:
            _set_cell_border(cell, top=(6, '000000'), bottom=(12, '000000'), left=None, right=None)


def _is_sep(line):
    return set(line.replace('|', '').strip()) <= set('-: ')


def _should_skip_line(line):
    """v2: 判断这行是否应该跳过（不进 docx）"""
    s = line.strip()
    if not s:
        return False
    # 版本号标题 "# Table 1 (v1.01)" / "# Supplementary Tables v1.14 (S1–S13)"
    if re.match(r'^#\s+(Table|Supplementary|STROBE|Declaration|Cover|Title|利益冲突|投稿信|正文|补充|标题页).*(v\d+\.\d+)', s, re.I):
        return True
    if re.match(r'^#\s+Manuscript\s+v\d+\.\d+', s, re.I):
        return True
    # changelog
    if re.match(r'^\*\*Changes from v\d+\.\d+', s, re.I):
        return True
    if 'changes from v1.01' in s.lower():
        return True
    # 内部溯源脚注：只跳过"短 + 带代码路径"的那种，避免误删整个 Sources 文献块
    if re.match(r'^Source[s]?(\s+data)?:', s, re.I) and len(s) < 200 \
            and ('`' in s or re.search(r'\.(csv|py|xlsx|json)\b', s)):
        return True
    return False


def _assemble_paragraphs(lines):
    """按 CommonMark 规则把 md 行组装成段落。

    规则：连续的**非空行**属于同一段落（直到空行才断段）；标题、表格、
    引用、水平线各自独立；列表项（- / 1.）吸收其后的续行。

    此前按"一行一段"渲染，导致两个后果：
      · 折行的参考文献、折行的标题被拆成多段，跨行的 *斜体* 无法配对；
      · 折行的说明句被拆散或被后续逻辑错误吞并。
    """
    out = []
    buf = None

    def flush():
        nonlocal buf
        if buf is not None:
            out.append(buf)
            buf = None

    for ln in lines:
        s = ln.rstrip()
        if not s:
            flush()
            out.append('')
            continue

        is_list = re.match(r'^(\d+\.|[-*])\s', s) is not None
        is_atomic = (s.startswith('#') or s.startswith('|')
                     or s.startswith('>') or s.startswith('[')
                     or s.strip() == '---')

        if is_atomic:
            flush()
            out.append(s)
            continue

        if is_list:
            flush()
            buf = s
            continue

        # 普通续行
        if buf is None:
            buf = s
        else:
            buf = buf + ' ' + s.strip()

    flush()
    return out


def md_to_docx(md_path, docx_path, start_marker=None, font_pt=11,
               landscape_from=None, title=None):
    doc = Document()
    st = doc.styles['Normal']
    st.font.name = 'Times New Roman'
    st.font.size = Pt(font_pt)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.5

    for s in ('Heading 1', 'Heading 2', 'Heading 3'):
        doc.styles[s].font.name = 'Times New Roman'
        doc.styles[s].font.color.rgb = None

    lines = open(md_path, encoding='utf-8').read().split('\n')

    # start_marker: 跳过 changelog，从正文实际起始位置开始
    if start_marker:
        for k, ln in enumerate(lines):
            if ln.startswith(start_marker):
                lines = lines[k:]
                break

    lines = _assemble_paragraphs(lines)

    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()

        # v2: 跳过不该进 docx 的行
        if _should_skip_line(ln):
            i += 1
            continue

        # 三线表处理
        if (ln.startswith('|') and i + 1 < len(lines)
                and _is_sep(lines[i + 1])):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if _is_sep(lines[i]):
                    i += 1
                    continue
                rows.append([c.strip().replace('\x00', '|')
                             for c in _split_row(lines[i])])
                i += 1
            ncol = max(len(r) for r in rows)
            t = doc.add_table(rows=len(rows), cols=ncol)
            # v2: 不设 style，后面手动加三线
            t.style = None
            for r_, row in enumerate(rows):
                for c_, v in enumerate(row):
                    cell = t.cell(r_, c_)
                    cell.text = ''
                    p = cell.paragraphs[0]
                    p.paragraph_format.line_spacing = 1.0
                    p.paragraph_format.space_after = Pt(0)
                    _add_runs(p, v)
                    if r_ == 0:
                        for run in p.runs:
                            run.bold = True
            # v2: 应用三线表
            _apply_three_line_table(t)
            doc.add_paragraph('')
            continue

        if ln.startswith('#### '):
            doc.add_heading(ln[5:].strip(), level=3)
        elif ln.startswith('### '):
            doc.add_heading(ln[4:].strip(), level=3)
        elif ln.startswith('## '):
            doc.add_heading(ln[3:].strip(), level=2)
        elif ln.startswith('# '):
            doc.add_heading(ln[2:].strip(), level=1)
        elif ln.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.line_spacing = 1.5
            _add_runs(p, ln[2:])
        elif ln.startswith('>'):
            txt = ln.lstrip('>').strip()
            if txt:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.6)
                p.paragraph_format.right_indent = Cm(0.6)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                _add_runs(p, txt)
        elif ln.strip() and ln.strip() != '---':
            p = doc.add_paragraph()
            _add_runs(p, ln)
        i += 1

    doc.save(docx_path)
    print('  ->', os.path.basename(docx_path))
    return docx_path

# -*- coding: utf-8 -*-
"""
md2docx.py —— 通用 Markdown → DOCX（本包专用）
------------------------------------------------
处理：标题、段落、粗体、项目符号、管道表格、上标文献编号。

文献编号规则（Lancet Vancouver）：
  正文中的 [1] / [2,3] / [1–5] 转为**上标**；若方括号后紧跟 . , ; :
  则把上标移到该标点之后（Lancet 要求编号在标点后）。
"""
import os
import re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.section import WD_ORIENT

CITE = re.compile(r'\[([0-9][0-9,\s\u2013\-]*)\]')
PUNCT = '.,;:'


def _add_runs(par, text):
    """粗体 + 文献上标"""
    # 先按 ** 切分粗体
    for bi, seg in enumerate(text.split('**')):
        if not seg:
            continue
        bold = (bi % 2 == 1)
        pos = 0
        for m in CITE.finditer(seg):
            before = seg[pos:m.start()]
            if before:
                r = par.add_run(before)
                r.bold = bold
            num = m.group(1).strip()
            nxt = seg[m.end():m.end() + 1]
            if nxt and nxt in PUNCT:
                r = par.add_run(nxt)
                r.bold = bold
                r2 = par.add_run(num)
                r2.bold = bold
                r2.font.superscript = True
                pos = m.end() + 1
            else:
                r2 = par.add_run(num)
                r2.bold = bold
                r2.font.superscript = True
                pos = m.end()
        tail = seg[pos:]
        if tail:
            r = par.add_run(tail)
            r.bold = bold


def _is_sep(line):
    return set(line.replace('|', '').strip()) <= set('-: ')


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
    if start_marker:
        for k, ln in enumerate(lines):
            if ln.startswith(start_marker):
                lines = lines[k:]
                break

    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        # 表格
        if (ln.startswith('|') and i + 1 < len(lines)
                and _is_sep(lines[i + 1])):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if _is_sep(lines[i]):
                    i += 1
                    continue
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            ncol = max(len(r) for r in rows)
            t = doc.add_table(rows=len(rows), cols=ncol)
            t.style = 'Table Grid'
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

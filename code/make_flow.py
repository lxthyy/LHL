# -*- coding: utf-8 -*-
"""STROBE 13c 样本流程图（v2.00）：箭头从排除前节点分出；十周期面板独立来源"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FIG = (r'C:\Users\lxddz\Desktop\科研稿件总库\A_在投_9篇\21_衰老指数等价性_LHL'
       r'\LHL_投稿包_v1.00\图表')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'pdf.fonttype': 42, 'svg.fonttype': 'none'})

fig, ax = plt.subplots(figsize=(7.4, 7.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 12)
ax.axis('off')


def box(x, y, w, h, txt, fc='#E8F0FE'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.10',
                                linewidth=1.0, edgecolor='#333333', facecolor=fc))
    ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', linespacing=1.5)


def arrow(x1, y1, x2, y2, dashed=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                 mutation_scale=9, linewidth=0.9,
                                 color='#333333',
                                 linestyle='--' if dashed else '-'))


# ---- 主链（x 中心 5.4）----
box(3.1, 10.2, 4.6, 1.15,
    'NHANES 1999–2018, aged 20–85 years\n'
    'Eight cycles with serum CRP\nn = 38,037')
box(3.1, 8.5, 4.6, 1.0, 'With mortality follow-up\nrecord\nn = 38,014')
box(3.1, 6.8, 4.6, 1.0,
    'Complete data for five indices,\ncovariates and outcome\nn = 34,393 (5,636 deaths)')
box(3.1, 4.9, 4.6, 1.0,
    'Cause-specific window 1999–2014\nn = 25,678 (5,360 deaths)')

# ---- 排除框（左侧）----
box(0.15, 10.2, 2.55, 1.15, 'No mortality\nfollow-up record\nn = 23', '#FCE8E6')
box(0.15, 8.5, 2.55, 1.0, 'Missing index or\ncovariate\nn = 3,621 (1,552 deaths)', '#FCE8E6')
box(0.15, 6.8, 2.55, 1.0, 'Outside window 2015–2018\n(cause codes\nunavailable)\nn = 8,715', '#FCE8E6')

# ---- 十周期面板（右侧，独立来源）----
box(8.5, 8.5, 3.3, 1.0,
    'NHANES 1999–2018, aged 20–85\nten cycles (no CRP needed)\nn = 49,366', '#F1F3F4')
box(8.5, 6.8, 3.3, 1.0,
    'Complete data for three\nCRP-free indices\nn = 43,701 (6,457 deaths)', '#F1F3F4')
box(8.5, 5.3, 3.3, 0.95,
    'Ten-cycle extension:\nseparate analysis, not pooled\nwith the main results', '#F1F3F4')

# ---- 主链箭头 ----
arrow(5.4, 10.2, 5.4, 9.55)
arrow(5.4, 8.5, 5.4, 7.85)
arrow(5.4, 6.8, 5.4, 5.95)
ax.text(5.55, 6.36, 'Restricted to 1999–2014', fontsize=7, style='italic',
        ha='left', va='center', color='#333333')

# ---- 排除箭头（从排除前的节点分出）----
arrow(3.1, 10.75, 2.75, 10.75, dashed=True)
arrow(3.1, 9.0, 2.75, 9.0, dashed=True)
arrow(3.1, 7.3, 2.75, 7.3, dashed=True)

# ---- 十周期面板 ----
arrow(10.15, 8.5, 10.15, 7.85)
ax.text(10.30, 8.17, '−5,665\n(missing data)', fontsize=6.8, style='italic',
        ha='left', va='center', color='#333333')

# ---- 分隔线 ----
ax.plot([7.85, 7.85], [4.6, 11.6], color='#CCCCCC', linewidth=0.8,
        linestyle=(0, (4, 4)))

ax.text(5.4, 3.9,
        'Main analysis: eight cycles, five indices.\n'
        'Ten-cycle extension is a separate, non-pooled panel.',
        ha='center', va='center', fontsize=7.5, style='italic')
ax.text(5.4, 11.75, 'Figure S3. Participant flow', ha='center', va='center',
        fontsize=9.5, fontweight='bold')

for ext in ('pdf', 'png', 'svg'):
    fig.savefig(os.path.join(FIG, 'FigureS3_participant_flow_v2.00.%s' % ext),
                dpi=400 if ext == 'png' else None, bbox_inches='tight')
print('已写出 FigureS3_participant_flow_v2.00.pdf/png/svg')

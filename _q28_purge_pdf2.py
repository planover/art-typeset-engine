# -*- coding: utf-8 -*-
"""彻底去 PDF 口径（用户 2026-11-16 第三次点名），精确版：
- 占位符保护规则句里的反面示例（「PDF N 起」/「怎么还说PDF呢」必须保留字面，否则禁令被改反）
- 带数字的页码引用：PDF 20（印刷 8）→ 文档印刷 8 页；纯 PDF N → 文档印刷 (N-12) 页
- 活工序卡「回 PDF 原页」→「回 md 文档锚点篇目」
- 不做全局 replace，避免误伤
"""
from pathlib import Path
import re

PH = "@@PDFLIT@@"

def protect(s):
    # 保护反面示例与用户原话里的字面 PDF
    s = s.replace("「PDF N 起」", "「%s N 起」" % PH)
    s = s.replace("『PDF N 起』", "『%s N 起』" % PH)
    s = s.replace("还说PDF呢", "还说%s呢" % PH)
    s = s.replace("怎么还说 PDF 呢", "怎么还说 %s 呢" % PH)
    return s

def to_print(n):
    return max(1, n - 12)

def clean(s):
    s = protect(s)
    # 带印刷标注
    s = re.sub(r"PDF\s*\d+\s*（印刷\s*(\d+)\s*）",
               lambda m: "文档印刷 %s 页" % m.group(1), s)
    # 双页
    s = re.sub(r"PDF\s*(\d+)\s*\+\s*(\d+)",
               lambda m: "文档印刷 %d+%d 页" % (to_print(int(m.group(1))),
                                            to_print(int(m.group(2)))), s)
    # 纯数字：213 是总页数，保留
    s = re.sub(r"PDF\s*(\d+)\b",
               lambda m: ("原书 %s 页" % m.group(1) if int(m.group(1)) == 213
                          else "文档印刷 %d 页" % to_print(int(m.group(1)))), s)
    # 描述性提法（无数字）
    s = s.replace("回 PDF 原页逐字核对", "回 md 文档锚点篇目逐字核对")
    s = s.replace("回 PDF 原页", "回 md 文档锚点篇目")
    s = s.replace("PDF物理页＝目录页＋12", "锚点 sNN 对应目录印刷页")
    s = s.replace("PDF 物理页＝目录页＋12", "锚点 sNN 对应目录印刷页")
    s = s.replace("pypdf 按页抽全文", "按 md 文档锚点抽取")
    s = s.replace("「篇目→PDF页」地图", "「篇目→锚点」地图")
    s = s.replace("pages[PDF页]", "pages[文档锚点]")
    s = s.replace("PDF页", "文档页")
    s = s.replace("PDF 页", "文档页")
    s = s.replace("PDF 213 页", "原书 213 页")
    # 还原保护
    s = s.replace(PH, "PDF")
    return s

files = [
    Path(r"C:\Users\admin\Documents\tietu\醒与悟1.0_金句台账.md"),
    Path(r"C:\Users\admin\Documents\tietu\名画融合文字图系列_完整记忆_20261101.md"),
    Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\memory\MEMORY.md"),
    Path(r"C:\Users\admin\.workbuddy-ai\skills\local-art-typeset\SKILL.md"),
]
for p in files:
    s = p.read_text(encoding="utf-8")
    n = s.count("PDF")
    s2 = clean(s)
    p.write_text(s2, encoding="utf-8")
    print(p.name, "原", n, "→ 现", s2.count("PDF"))

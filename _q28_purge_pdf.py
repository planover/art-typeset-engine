# -*- coding: utf-8 -*-
"""用户 2026-11-16 第三次点名收尾：清除六处历史条目里的「PDF N 起」导航话术，
并把口径规则的源从 txt 物理页彻底改为 md 文档锚点。"""
from pathlib import Path

# 历史条目的物理页 → md 文档印刷页（物理页 - 12）
SWAP = [
    ("从 PDF 73 起开采", "从文档印刷 61 页起开采"),
    ("从 PDF 92 起（", "从文档印刷 80 页起（"),
    ("从 PDF 92 起开采", "从文档印刷 80 页起开采"),
    ("从 PDF 93 起（", "从文档印刷 81 页起（"),
    ("从 PDF 99 起（", "从文档印刷 87 页起（"),
    ("Q25 从 PDF 92 起", "Q25 从文档印刷 80 页起"),
]

targets = [
    Path(r"C:\Users\admin\Documents\tietu\醒与悟1.0_金句台账.md"),
    Path(r"C:\Users\admin\Documents\tietu\名画融合文字图系列_完整记忆_20261101.md"),
]
for p in targets:
    s = p.read_text(encoding="utf-8")
    n = 0
    for a, b in SWAP:
        if a in s:
            n += s.count(a)
            s = s.replace(a, b)
    # 口径说明去 PDF 提法
    s = s.replace("**PDF 物理页 = 目录印刷页 + 12**",
                  "**旧转写版物理页 = 目录印刷页 + 12（仅历史溯源；导航一律用 md 文档锚点 sNN／印刷页）**")
    p.write_text(s, encoding="utf-8")
    print(p.name, "替换", n, "处")

# MEMORY.md 规则升级：源从 txt 物理页 → md 文档锚点
p = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\memory\MEMORY.md")
s = p.read_text(encoding="utf-8")
old = [l for l in s.splitlines() if l.startswith("> **【口径修正")]
if old:
    new = ("> **【口径修正 · 2026-11-13 提出 / 2026-11-16 用户第三次点名后彻底执行】"
           "原文一律读 md 文档 `C:\\Users\\admin\\Documents\\tietu\\醒与悟1.0.md`（锚点 sNN 对应目录印刷页），"
           "**不是**转写 txt 的物理页；交付话术只说「**文档 N 起**」，"
           "禁止出现「PDF N 起」——用户原话「不是说了读MD文件吗？怎么还说PDF呢？」＝连提法都算违规。"
           "台账/完整记忆/SKILL/交付说明/对话回复六处统一。")
    s = s.replace(old[0], new)
    p.write_text(s, encoding="utf-8")
    print("MEMORY.md 规则已升级为 md 文档口径")

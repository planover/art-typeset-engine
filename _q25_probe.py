# -*- coding: utf-8 -*-
"""Q25 出库取证：抽取醒与悟1.0.pdf 物理页 89-102 的逐页全文。"""
import fitz
from pathlib import Path

PDF = Path(r"C:\Users\admin\Documents\tietu\醒与悟1.0.pdf")
OUT = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp\q25_pages_89_102.txt")

doc = fitz.open(PDF)
lines = []
for p in range(89, 103):          # 1-based 物理页
    text = doc[p - 1].get_text("text")
    lines.append(f"\n{'=' * 30} [PDF 物理页 {p} / 印刷页 {p - 12}] {'=' * 30}\n")
    lines.append(text)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("".join(lines), encoding="utf-8")
print(f"pages={doc.page_count} written={OUT} bytes={OUT.stat().st_size}")

# -*- coding: utf-8 -*-
"""Q26 GO：把 PDF 物理页 97（0-based 96）渲染成高清图供逐字目验，并打印逐行文本。"""
import pymupdf
from pathlib import Path

PDF = r"C:\Users\admin\Documents\tietu\醒与悟1.0.pdf"
TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
doc = pymupdf.open(PDF)

for i in (96, 97):
    page = doc[i]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2.4, 2.4))
    out = TMP / f"q26_page{i+1}.png"
    pix.save(out)
    print("saved", out, pix.width, "x", pix.height)
    print("---- 逐行文本 ----")
    for ln in page.get_text("text").splitlines():
        if ln.strip():
            print(repr(ln))
    print("=" * 60)

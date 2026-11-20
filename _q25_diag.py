# -*- coding: utf-8 -*-
"""Q25 诊断：保留未达标成图，打印真实行带与各切片口径，生成 1:1 目验缩略。"""
from pathlib import Path
from PIL import Image
import numpy as np
from art_typeset import recipe, verify, spec

TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
R = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets\q25.json")
BASE = spec.CACHE / "q25_base.png"
OUT = TMP / "q25_v2diag.png"

r = recipe.load(str(R))
recipe.render(r, BASE, OUT, verify_after=False, dark_bg=True)

A, B = verify.load_pair(OUT, BASE)
ink = np.abs(A - B).max(axis=2) > 40
x0, x1 = verify._ink_x_range(ink)
bands = verify.find_bands(ink, x0, x1)
print("\n=== 真实行带 %d 条 (x %d:%d) ===" % (len(bands), x0, x1))
for i, b in enumerate(bands):
    print("  band%-2d y[%4d,%4d] h=%3d ink=%d" %
          (i, b[0], b[1], b[1] - b[0], int(ink[b[0]:b[1], x0:x1].sum())))

for sl in [(1, 5), (1, 3), (1, 4), (1, 6), (1, 7)]:
    rep = verify.verify(OUT, BASE, dark_bg=True, body_band_slice=sl, verbose=False)
    c = rep["checks"]
    print("slice %-6s accent=%6.2f%% ink=%5d  credit=%s  en=%s  layers=%d  ok=%s" %
          (str(sl), rep["accent_ratio"] * 100, rep["body_ink"],
           c["contrast_credit"]["value"], c["contrast_en"]["value"],
           len(rep["layers"]), rep["ok"]))

view = Image.open(OUT).convert("RGB")
view.thumbnail((768, 1024), Image.LANCZOS)
view.save(TMP / "q25_v2diag_view.png")
# 下半 1:1 裁切（文字区）
crop = Image.open(OUT).convert("RGB").crop((0, 1250, 1536, 2048))
crop.save(TMP / "q25_v2diag_bottom.png")
print("\nview:", TMP / "q25_v2diag_view.png")

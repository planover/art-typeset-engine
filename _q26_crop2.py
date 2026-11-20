# -*- coding: utf-8 -*-
"""Q26：两幅终选的多 crop_x 3:4 底图 + 16x8 网格 + 目验拼版。"""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
W, H = 1536, 2048

CANDS = {"lane": [0.30, 0.45, 0.60], "shenzhou": [0.35, 0.5, 0.65]}

rep, views = [], []
for name, crops in CANDS.items():
    im = Image.open(CACHE / f"q26_{name}.jpg").convert("RGB")
    print(f"\n### {name} {im.size} ratio {im.size[0]/im.size[1]:.2f}")
    cw = int(round(im.size[1] * W / H))
    for cx in crops:
        left = int(round((im.size[0] - cw) * cx))
        base = im.crop((left, 0, left + cw, im.size[1])).resize((W, H), Image.LANCZOS)
        tag = f"{name}_cx{int(cx*100)}"
        base.save(TMP / f"q26_{tag}.png")
        a = np.asarray(base, dtype=np.int32)
        lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
        CW, CH = W // 16, H // 8
        lines = [f"[{tag}]\n"]
        for r in range(8):
            row = []
            for c in range(16):
                cell = lum[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW]
                row.append(f"{int(np.median(cell)):>3}/{int(np.std(cell)):>2}")
            lines.append(f"r{r}: " + " ".join(row) + "\n")
        txt = "".join(lines)
        rep.append(txt)
        print(txt)
        views.append((tag, base.copy()))
    full = im.copy(); full.thumbnail((1200, 800), Image.LANCZOS)
    full.save(TMP / f"q26_{name}_full.png")

(TMP / "q26_grid2.txt").write_text("".join(rep), encoding="utf-8")

TW, TH, cols = 320, 427, 3
rows = (len(views) + cols - 1) // cols
sheet = Image.new("RGB", (cols * TW, rows * (TH + 22)), (240, 240, 240))
d = ImageDraw.Draw(sheet)
for i, (tag, v) in enumerate(views):
    x, y = (i % cols) * TW, (i // cols) * (TH + 22)
    sheet.paste(v.resize((TW - 6, TH - 6), Image.LANCZOS), (x + 3, y + 3))
    d.text((x + 5, y + TH), tag, fill=(10, 10, 10))
sheet.save(TMP / "q26_crops2.png")
print("saved", TMP / "q26_crops2.png")

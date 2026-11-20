# -*- coding: utf-8 -*-
"""下载 Inness《Moonrise》1887 高清原图 -> 3:4 底图 + 1:1 目验图 + 高分网格探针。"""
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
URL = "https://upload.wikimedia.org/wikipedia/commons/5/59/Moonrise_by_George_Inness_1887.jpeg"
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"

src = CACHE / "q25_inness_moonrise.jpg"
if not src.exists():
    req = Request(URL, headers={"User-Agent": UA})
    with urlopen(req, timeout=60) as r:
        data = r.read()
    src.write_bytes(data)
    print("downloaded", len(data), "bytes")
else:
    print("cached", src.stat().st_size, "bytes")

im = Image.open(src).convert("RGB")
print("original size", im.size)
W, H = 1536, 2048

# 3:4 中心裁切（原图 1.51 横幅），可微调 crop_x
def crop34(im, cx=0.5):
    w, h = im.size
    nw = int(round(h * W / H))
    left = int(round((w - nw) * cx))
    return im.crop((left, 0, left + nw, h)).resize((W, H), Image.LANCZOS)

base = crop34(im, 0.5)
base.save(TMP / "q25_base.png")

# 目验：原图全幅 + 3:4 底图缩略
full = im.copy(); full.thumbnail((900, 900), Image.LANCZOS)
full.save(TMP / "q25_inness_full.png")
view = base.copy(); view.thumbnail((768, 1024), Image.LANCZOS)
view.save(TMP / "q25_inness_34.png")

# 高分网格
a = np.asarray(base, dtype=np.int32)
lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
COLS, ROWS = 16, 8
CW, CH = W // COLS, H // ROWS
lines = ["16x8 网格 median / std（3:4 底图）\n"]
for r in range(ROWS):
    row = []
    for c in range(COLS):
        cell = lum[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW]
        row.append(f"{int(np.median(cell)):>3}/{int(np.std(cell)):>2}")
    lines.append(f"r{r}: " + " ".join(row) + "\n")
# 全图与下半统计
lower = lum[H // 2:, :]
lines.append(f"\n下半 y1024-2048: median={int(np.median(lower))} std={int(np.std(lower))} "
             f"p10={int(np.percentile(lower, 10))} p90={int(np.percentile(lower, 90))}\n")
(TMP / "q25_inness_grid.txt").write_text("".join(lines), encoding="utf-8")
print("".join(lines))

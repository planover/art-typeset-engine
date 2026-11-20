# -*- coding: utf-8 -*-
"""Q26 候选画高清下载 + 多 crop_x 的 3:4 底图 + 16x8 网格 + 目验拼版。"""
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw
import numpy as np, io

TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
CACHE.mkdir(parents=True, exist_ok=True)
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"
W, H = 1536, 2048

CANDS = {
    "qiuying": ("https://upload.wikimedia.org/wikipedia/commons/6/67/Qiu_Ying_-_Saying_Farewell_at_Xunyang_-_Google_Art_Project.jpg",
                [0.10, 0.35, 0.55, 0.75]),
    "lane":    ("https://upload.wikimedia.org/wikipedia/commons/e/e1/A_Calm_Sea%2C_by_Fitz_Henry_Lane%2C_c._1860%2C_oil_on_canvas_-_Cape_Ann_Museum_-_Gloucester%2C_MA_-_DSC01126.jpg",
                [0.34, 0.5, 0.66]),
}


def get(name, url):
    p = CACHE / f"q26_{name}.jpg"
    if p.exists():
        return p
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=120) as r:
        data = r.read()
    p.write_bytes(data)
    print("downloaded", name, len(data))
    return p


def grid(im, tag):
    a = np.asarray(im, dtype=np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    COLS, ROWS = 16, 8
    CW, CH = W // COLS, H // ROWS
    lines = [f"[{tag}] 16x8 median/std\n"]
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            cell = lum[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW]
            row.append(f"{int(np.median(cell)):>3}/{int(np.std(cell)):>2}")
        lines.append(f"r{r}: " + " ".join(row) + "\n")
    print("".join(lines))
    return "".join(lines)


report = []
views = []
for name, (url, crops) in CANDS.items():
    im = Image.open(get(name, url)).convert("RGB")
    print(f"\n### {name} original {im.size} ratio {im.size[0]/im.size[1]:.2f}")
    cw = int(round(im.size[1] * W / H))
    for cx in crops:
        left = int(round((im.size[0] - cw) * cx))
        base = im.crop((left, 0, left + cw, im.size[1])).resize((W, H), Image.LANCZOS)
        tag = f"{name}_cx{cx}"
        report.append(grid(base, tag))
        views.append((tag, base.copy()))
        base.save(TMP / f"q26_{tag}.png")
    # 原图整体缩略
    full = im.copy(); full.thumbnail((1400, 700), Image.LANCZOS)
    full.save(TMP / f"q26_{name}_full.png")

(TMP / "q26_grid.txt").write_text("".join(report), encoding="utf-8")

# 拼版：每行 1 个 tag 3 张缩略 + 标签
TW, TH = 300, 400
cols = 4
rows = (len(views) + cols - 1) // cols
sheet = Image.new("RGB", (cols * TW, rows * (TH + 20)), (245, 245, 245))
d = ImageDraw.Draw(sheet)
for i, (tag, v) in enumerate(views):
    x, y = (i % cols) * TW, (i // cols) * (TH + 20)
    sheet.paste(v.resize((TW - 6, TH - 6), Image.LANCZOS), (x + 3, y + 3))
    d.text((x + 4, y + TH), tag, fill=(15, 15, 15))
sheet.save(TMP / "q26_crops.png")
print("saved", TMP / "q26_crops.png")

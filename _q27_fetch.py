# -*- coding: utf-8 -*-
"""Q27 GO：下载 Commons 原图 → 裁装裱边 → 3:4 预处理 → 48px 滑窗复测干净矩形 → 目验图。"""
from pathlib import Path
from PIL import Image, ImageDraw
from urllib.request import Request, urlopen
import json, io
import numpy as np
import sys


def prep(im, W=1536, H=2048):
    im = im.convert("RGB")
    a = np.asarray(im, np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    h, w = lum.shape
    band = max(3, int(min(h, w) * 0.02))
    edge = np.concatenate([lum[:band].ravel(), lum[-band:].ravel(),
                           lum[:, :band].ravel(), lum[:, -band:].ravel()])
    inner = lum[band:-band, band:-band]
    if np.median(edge) < np.median(inner) - 30:
        k = int(min(h, w) * 0.04)
        im = im.crop((k, k, w - k, h - k))
    w, h = im.size
    ratio = W / H
    if w / h > ratio:
        nw = int(round(h * ratio)); left = (w - nw) // 2
        im = im.crop((left, 0, left + nw, h))
    else:
        nh = int(round(w / ratio)); top = (h - nh) // 2
        im = im.crop((0, top, w, top + nh))
    return im.resize((W, H), Image.LANCZOS)


def probe(im, W=1536, H=2048, COLS=16, ROWS=8):
    a = np.asarray(im, dtype=np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    CW, CH = W // COLS, H // ROWS
    med = np.zeros((ROWS, COLS), np.int32); std = np.zeros((ROWS, COLS), np.int32)
    for r in range(ROWS):
        for c in range(COLS):
            cell = lum[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW]
            med[r, c] = int(np.median(cell)); std[r, c] = int(np.std(cell))
    return med, std


def clean_rect(im, dark=True, S=48, STEP=32):
    a = np.asarray(im, np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    H, W = lum.shape
    ys = list(range(0, H - S + 1, STEP))
    xs = list(range(0, W - S + 1, STEP))
    ok = np.zeros((len(ys), len(xs)), bool)
    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            c = lum[y:y + S, x:x + S]
            m = np.median(c)
            ok[i, j] = ((m <= 45) if dark else (m >= 150)) and (np.std(c) <= 25)
    best = (0, 0, 0, 0, 0)
    hist = np.zeros(len(xs), np.int32)
    for i in range(len(ys)):
        hist = np.where(ok[i], hist + 1, 0)
        stack = []
        for j in range(len(xs) + 1):
            h = int(hist[j]) if j < len(xs) else 0
            while stack and hist[stack[-1]] >= h:
                ht = int(hist[stack.pop()]); j0 = stack[-1] + 1 if stack else 0
                area = ht * (j - j0)
                if area > best[0]:
                    best = (area, i - ht + 1, i, j0, j - 1)
            stack.append(j)
    _, i0, i1, j0, j1 = best
    if not best[0]:
        return (0, 0, 0, 0)
    return (ys[i0], ys[i1] + S, xs[j0], xs[j1] + S)


CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
META = json.loads((CACHE / "q27_commons_meta.json").read_text(encoding="utf-8"))
it = META[2]
url = it["url"].split("?utm_source=")[0]
print("URL:", url)
print("COMMONS:", it["title"], "|", it["artist"], "|", it["date"], "|", it["license"])

UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"
req = Request(url, headers={"User-Agent": UA})
with urlopen(req, timeout=90) as r:
    raw = r.read()
src = Image.open(io.BytesIO(raw)).convert("RGB")
print("原图尺寸:", src.size)
src.save(CACHE / "q27_original.jpg", quality=94)

im = prep(src)
im.save(CACHE / "q27_base.png")
print("底图:", im.size, "->", CACHE / "q27_base.png")

med, std = probe(im)
print("16x8 中位/标准差：")
for r in range(8):
    print("  r%d med %s" % (r, " ".join("%3d" % v for v in med[r])))
    print("     std %s" % (" ".join("%3d" % v for v in std[r])))

rect = clean_rect(im, dark=True)
print("48px 滑窗最大干净矩形 (y0,y1,x0,x1):", rect,
      "宽高", rect[3] - rect[2], "x", rect[1] - rect[0])

# 目验图：整幅 + 干净矩形 + 预设文字块（1050x900）叠框
view = im.resize((768, 1024), Image.LANCZOS)
d = ImageDraw.Draw(view)
def box(b, color, width=4):
    y0, y1, x0, x1 = b
    d.rectangle([x0 // 2, y0 // 2, x1 // 2, y1 // 2], outline=color, width=width)
box(rect, (255, 80, 40))
view.save(CACHE / "q27_view.png")
print("目验图:", CACHE / "q27_view.png", "（橙框＝最大干净矩形）")

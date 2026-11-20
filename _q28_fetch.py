# -*- coding: utf-8 -*-
"""Q28 决赛三张：下载原图 → 3:4 裁切 → 48px 滑窗干净矩形 → 橙框目验图。

候选 10 = Winslow Homer《Boys Fishing》(1880)｜12 = Kuindzhi《North》｜01 = Yun Shouping 册页
"""
from pathlib import Path
from PIL import Image, ImageDraw
from urllib.request import Request, urlopen
import json, io, re, time
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
META = json.loads((TMP / "q28_commons_meta.json").read_text(encoding="utf-8"))
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"


def fetch(it):
    """Commons 429 限流时多源回退：原图 → 1600px thumb → 1100px thumb。"""
    u = it["url"].split("?")[0]
    urls = [u]
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/([^/]+)/([^/]+)/(.+)$", u)
    if m:
        base, h1, h2, name = m.groups()
        urls.append("%s/thumb/%s/%s/%s/1600px-%s" % (base, h1, h2, name, name))
    if it.get("thumb"):
        urls.append(it["thumb"].split("?")[0])
    for url in urls:
        try:
            req = Request(url, headers={"User-Agent": UA,
                                        "Referer": "https://commons.wikimedia.org/"})
            with urlopen(req, timeout=60) as r:
                data = r.read()
            print("  fetched %d bytes | %s" % (len(data), url[:110]), flush=True)
            return data
        except Exception as e:
            print("  fail %s | %s" % (str(e)[:60], url[:110]), flush=True)
            time.sleep(3)
    raise RuntimeError("all sources 429")


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


def clean_rect(im, S=48, STEP=32):
    a = np.asarray(im, np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    H, W = lum.shape
    ys = list(range(0, H - S + 1, STEP)); xs = list(range(0, W - S + 1, STEP))
    ok = np.zeros((len(ys), len(xs)), bool)
    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            c = lum[y:y + S, x:x + S]
            ok[i, j] = (np.median(c) >= 150) and (np.std(c) <= 25)
    best = (0, 0, 0, 0, 0); hist = np.zeros(len(xs), np.int32)
    for i in range(len(ys)):
        hist = np.where(ok[i], hist + 1, 0); stack = []
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


views = []
for idx in (10, 12, 1):
    it = META[idx]
    raw = Image.open(io.BytesIO(fetch(it)))
    p = prep(raw)
    rect = clean_rect(p)
    tag = "q28_cand%d" % idx
    p.save(TMP / (tag + "_base.png"))
    v = p.copy()
    d = ImageDraw.Draw(v)
    y0, y1, x0, x1 = rect
    d.rectangle((x0, y0, x1, y1), outline=(255, 120, 20), width=8)
    d.text((x0 + 12, y0 + 12), "%d  %dx%d" % (idx, x1 - x0, y1 - y0),
           fill=(255, 120, 20))
    v.save(TMP / (tag + "_view.png"))
    a = np.asarray(p, np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    cell = lum[y0:y1, x0:x1]
    print(idx, it["title"][5:60], "| 原尺寸", raw.size, "| 干净矩形", rect,
          "| 矩形中位", int(np.median(cell)), "std", round(float(np.std(cell)), 1),
          "|", it["artist"][:40])
    views.append(v.resize((512, 683), Image.LANCZOS))

sheet = Image.new("RGB", (512 * 3, 683), (245, 245, 245))
for i, v in enumerate(views):
    sheet.paste(v, (512 * i, 0))
sheet.save(TMP / "q28_final3.png")
print("对比图:", TMP / "q28_final3.png")

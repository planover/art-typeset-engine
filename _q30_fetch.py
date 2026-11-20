# -*- coding: utf-8 -*-
"""Q30 决赛候选：下载原图 → 3:4 裁切 → 48px 干净矩形 → 橙框目验图。"""
from pathlib import Path
from PIL import Image, ImageDraw
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json, io
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
META = json.loads((TMP / "q30_commons_meta.json").read_text(encoding="utf-8"))
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"
API = "https://commons.wikimedia.org/w/api.php"

CAND = {
    0: "Hodler_Thunersee1909",
    1: "Rembrandt_Prodigal",
    2: "Ruysdael_Winter",
    3: "Ruysdael_Tour",
    26: "Cuyp_Ice",
}


def thumb_url(title, width=1280):
    q = urlencode({"action": "query", "titles": title, "prop": "imageinfo",
                   "iiprop": "url", "iiurlwidth": width, "format": "json"})
    d = json.loads(urlopen(Request(API + "?" + q, headers={"User-Agent": UA}), timeout=30).read().decode())
    p = list(d["query"]["pages"].values())[0]
    ii = p["imageinfo"][0]
    return ii.get("thumburl") or ii["url"]


def prep(im, W=1536, H=2048, crop_x=0.5):
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
        nw = int(round(h * ratio)); left = int((w - nw) * crop_x)
        im = im.crop((left, 0, left + nw, h))
    else:
        nh = int(round(w / ratio)); top = (h - nh) // 2
        im = im.crop((0, top, w, top + nh))
    return im.resize((W, H), Image.LANCZOS)


def clean_rect(im, dark=False, S=48, STEP=32):
    a = np.asarray(im, np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    H, W = lum.shape
    ys = list(range(0, H - S + 1, STEP)); xs = list(range(0, W - S + 1, STEP))
    ok = np.zeros((len(ys), len(xs)), bool)
    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            c = lum[y:y + S, x:x + S]; m = np.median(c)
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
    if not best[0]: return (0, 0, 0, 0)
    return (ys[i0], ys[i1] + S, xs[j0], xs[j1] + S)


for idx, tag in CAND.items():
    it = META[idx]
    try:
        url = thumb_url(it["title"], 1280)
        raw = Image.open(io.BytesIO(urlopen(Request(url, headers={"User-Agent": UA}), timeout=60).read()))
    except Exception as e:
        print(tag, "SKIP:", str(e)[:80], flush=True); continue
    print(tag, "原图", raw.size, flush=True)
    im = prep(raw)
    im.save(TMP / ("q30_%s_base.png" % tag))
    dark = (it.get("mode") == "dark")
    r = clean_rect(im, dark=dark)
    print("  矩形", (r[3]-r[2], r[1]-r[0]), "mode", "dark" if dark else "light", flush=True)
    view = im.copy()
    d = ImageDraw.Draw(view)
    d.rectangle((r[2], r[0], r[3], r[1]), outline=(255, 140, 0), width=5)
    view.resize((768, 1024), Image.LANCZOS).save(TMP / ("q30_%s_view.png" % tag))

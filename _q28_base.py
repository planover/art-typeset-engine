# -*- coding: utf-8 -*-
"""Q28 底图定稿：尝试 1920px 合规 thumb 提升清晰度；失败则沿用 1280px 版。

输出 q28_base.png（1536×2048），并复测文字目标区亮度带。
"""
from pathlib import Path
from PIL import Image
from urllib.request import Request, urlopen
import json, io, shutil, re, time
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
META = json.loads((TMP / "q28_commons_meta.json").read_text(encoding="utf-8"))
IT = META[10]
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"
base1280 = TMP / "q28_cand10_base.png"

thumb = IT["thumb"].split("?")[0]
cand = [re.sub(r"/\d+px-", "/1920px-", thumb),
        re.sub(r"/\d+px-", "/2560px-", thumb), thumb]
data = None
for u in cand:
    try:
        req = Request(u, headers={"User-Agent": UA,
                                  "Referer": "https://commons.wikimedia.org/"})
        with urlopen(req, timeout=60) as r:
            d = r.read()
        im = Image.open(io.BytesIO(d)).convert("RGB")
        print("got", im.size, u[-70:], flush=True)
        if im.width > 1500:
            data, src, size = d, u, im.size
            break
    except Exception as e:
        print("fail", str(e)[:70], u[-70:], flush=True)
        time.sleep(2)

if data is None:
    shutil.copyfile(base1280, TMP / "q28_base.png")
    print("沿用 1280px 版底图:", base1280, flush=True)
else:
    # 与 _q28_fetch.prep 完全一致的 3:4 处理
    im = Image.open(io.BytesIO(data)).convert("RGB")
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
    ratio = 1536 / 2048
    if w / h > ratio:
        nw = int(round(h * ratio)); left = (w - nw) // 2
        im = im.crop((left, 0, left + nw, h))
    else:
        nh = int(round(w / ratio)); top = (h - nh) // 2
        im = im.crop((0, top, w, top + nh))
    im.resize((1536, 2048), Image.LANCZOS).save(TMP / "q28_base.png")
    print("高清版底图:", size, "->", TMP / "q28_base.png", flush=True)

b = np.asarray(Image.open(TMP / "q28_base.png").convert("RGB"), np.int32)
L = (b[..., 0] * 2126 + b[..., 1] * 7152 + b[..., 2] * 722) // 10000
for name, (y0, y1, x0, x1) in {"上半文字区": (80, 820, 140, 1180),
                                "全幅": (0, 2048, 0, 1536)}.items():
    c = L[y0:y1, x0:x1]
    print(name, "median", int(np.median(c)), "std", round(float(np.std(c)), 1),
          "dark_ratio", round(float((c < 110).mean()), 3))

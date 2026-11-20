# -*- coding: utf-8 -*-
"""下载 Compton 雪景并预处理为 1536×2048 底图，验证雪地净度。"""
from pathlib import Path
from PIL import Image
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json, io
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
UA = "WorkBuddyArtTypeset/1.0 (local research)"
API = "https://commons.wikimedia.org/w/api.php"
TITLE = "File:Edward Theodore Compton Hochkalter im Winter.jpg"

q = urlencode({"action": "query", "titles": TITLE, "prop": "imageinfo",
               "iiprop": "url", "iiurlwidth": 1280, "format": "json"})
d = json.loads(urlopen(Request(API + "?" + q, headers={"User-Agent": UA}), timeout=30).read().decode())
u = list(d["query"]["pages"].values())[0]["imageinfo"][0]["thumburl"]
raw = Image.open(io.BytesIO(urlopen(Request(u, headers={"User-Agent": UA}), timeout=40).read())).convert("RGB")
print("原图", raw.size)

# 内联 prep：裁装裱边 + 3:4 居中
a = np.asarray(raw, np.int32)
lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
h, w = lum.shape
band = max(3, int(min(h, w) * 0.02))
edge = np.concatenate([lum[:band].ravel(), lum[-band:].ravel(),
                       lum[:, :band].ravel(), lum[:, -band:].ravel()])
inner = lum[band:-band, band:-band]
if np.median(edge) < np.median(inner) - 30:
    k = int(min(h, w) * 0.04)
    raw = raw.crop((k, k, w - k, h - k))
W, H = 1536, 2048
w, h = raw.size
ratio = W / H
if w / h > ratio:
    nw = int(round(h * ratio)); left = (w - nw) // 2
    raw = raw.crop((left, 0, left + nw, h))
else:
    nh = int(round(w / ratio)); top = (h - nh) // 2
    raw = raw.crop((0, top, w, top + nh))
im = raw.resize((W, H), Image.LANCZOS)
im.save(TMP / "q29_compton_base.png")
print("底图已存", im.size)

a = np.asarray(im, np.int32)
lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
for y in (900, 1100, 1300, 1500, 1700, 1900):
    c = lum[y:y + 40, 80:1450]
    print("y%d 中位%d std%d" % (y, int(np.median(c)), int(np.std(c))))
im.resize((768, 1024), Image.LANCZOS).save(TMP / "q29_compton_view.png")

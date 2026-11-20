# -*- coding: utf-8 -*-
"""Q26：下载 Richards《Quiet Seascape》高清 thumb，取元数据，生成 3:4 底图与目验图。"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from PIL import Image
import json, re, io
import numpy as np

UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"
API = "https://commons.wikimedia.org/w/api.php"
TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
TITLE = "File:William Trost Richards - Quiet Seascape - 80.67 - Minneapolis Institute of Arts.jpg"


def api(p):
    p = dict(p); p["format"] = "json"
    return json.loads(urlopen(Request(API + "?" + urlencode(p), headers={"User-Agent": UA}),
                              timeout=40).read().decode("utf-8"))


d = api({"action": "query", "titles": TITLE, "prop": "imageinfo",
         "iiprop": "url|size|extmetadata", "iiurlwidth": 3800})
pg = list(d["query"]["pages"].values())[0]
ii = pg["imageinfo"][0]
em = ii.get("extmetadata") or {}


def clean(k):
    v = (em.get(k) or {}).get("value", "")
    return re.sub(r"<[^>]+>", "", v).strip()


print("size", ii["width"], "x", ii["height"], "-> thumb", ii["thumbwidth"], ii["thumbheight"])
for k in ("ObjectName", "Artist", "DateTimeOriginal", "ImageDescription", "Credit", "LicenseShortName"):
    print(f"  [{k}] {clean(k)[:300]}")

p = CACHE / "q26_richards.jpg"
if not p.exists() or p.stat().st_size < 300_000:
    url = ii["thumburl"].split("?")[0]
    p.write_bytes(urlopen(Request(url, headers={"User-Agent": UA}), timeout=180).read())
print("downloaded", p.stat().st_size)

im = Image.open(p).convert("RGB")
W, H = 1536, 2048
cw = int(round(im.size[1] * W / H))
left = (im.size[0] - cw) // 2
base = im.crop((left, 0, left + cw, im.size[1])).resize((W, H), Image.LANCZOS)
base.save(CACHE / "q26_base.png")
print("base saved", base.size)

v = base.copy(); v.thumbnail((760, 1013), Image.LANCZOS); v.save(TMP / "q26_richards_view.png")
f = im.copy(); f.thumbnail((1200, 700), Image.LANCZOS); f.save(TMP / "q26_richards_full.png")

a = np.asarray(base, np.int32)
lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
CW, CH = W // 16, H // 8
for r in range(8):
    print(f"r{r}: " + " ".join(
        f"{int(np.median(lum[r*CH:(r+1)*CH, c*CW:(c+1)*CW])):>3}/"
        f"{int(np.std(lum[r*CH:(r+1)*CH, c*CW:(c+1)*CW])):>2}" for c in range(16)))

# -*- coding: utf-8 -*-
"""Q26 选画：Commons 搜未用画家（亮底优先，供深字），16x8 亮度带探针 + 目验拼版。

主题「你改变不了任何人，只能顺应」→ 偏好平静水面 / 随势山水 / 静默光气。
"""
from pathlib import Path
from PIL import Image, ImageDraw
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json, io, time, re
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
TMP.mkdir(parents=True, exist_ok=True)
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"

QUERIES = [
    "Claude Lorrain landscape painting",
    "Jacob van Ruisdael landscape",
    "Aelbert Cuyp landscape cattle",
    "Fitz Henry Lane calm sea",
    "Isaac Levitan autumn river",
    "Arkhip Kuindzhi birch grove",
    "Huang Gongwang Fuchun Mountains",
    "Wang Ximeng thousand li rivers mountains",
    "Qiu Ying landscape painting",
    "Shen Zhou landscape painting",
]

API = "https://commons.wikimedia.org/w/api.php"


def api(params):
    params = dict(params)
    params["format"] = "json"
    url = API + "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch(url):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=40) as r:
        return r.read()


def prep(im, W=1536, H=2048):
    im = im.convert("RGB")
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


def max_rect(ok, COLS=16, ROWS=8):
    hist = np.zeros(COLS, np.int32); best = (0, 0, 0, 0, 0)
    for r in range(ROWS):
        hist = np.where(ok[r], hist + 1, 0)
        stack = []
        for c in range(COLS + 1):
            h = int(hist[c]) if c < COLS else 0
            while stack and hist[stack[-1]] >= h:
                ht = int(hist[stack.pop()]); c0 = stack[-1] + 1 if stack else 0
                area = ht * (c - c0)
                if area > best[0]:
                    best = (area, r - ht + 1, r, c0, c - 1)
            stack.append(c)
    return best


seen, items = set(), []
for q in QUERIES:
    try:
        data = api({
            "action": "query", "generator": "search",
            "gsrsearch": q + " filemime:image/jpeg", "gsrnamespace": 6,
            "gsrlimit": 10,
            "prop": "imageinfo", "iiprop": "url|size|extmetadata",
            "iiurlwidth": 900,
        })
    except Exception as e:
        print("API FAIL", q, e); continue
    pages = (data.get("query") or {}).get("pages") or {}
    for p in pages.values():
        title = p.get("title", "")
        if title in seen:
            continue
        seen.add(title)
        ii = (p.get("imageinfo") or [{}])[0]
        thumb = ii.get("thumburl") or ii.get("url")
        if not thumb:
            continue
        low = title.lower()
        if any(x in low for x in ("catalogue", "magazine", "book ", "cover", "poster",
                                  "signature", "detail", "stamp", "seal", "map")):
            continue
        em = ii.get("extmetadata") or {}
        def clean(k):
            v = (em.get(k) or {}).get("value", "")
            return re.sub(r"<[^>]+>", "", v).strip()[:120]
        items.append({
            "q": q, "title": title, "thumb": thumb, "url": ii.get("url"),
            "w": ii.get("width"), "h": ii.get("height"),
            "artist": clean("Artist"), "date": clean("DateTimeOriginal"),
            "license": clean("LicenseShortName"), "desc": clean("ImageDescription"),
        })
    print(f"query ok: {q} -> {len(items)}")
    time.sleep(0.3)

print(f"candidates={len(items)}")
ok = []
for i, it in enumerate(items):
    try:
        raw = fetch(it["thumb"])
        im = Image.open(io.BytesIO(raw))
        p = prep(im)
        med, std = probe(p)
        it["bd"] = max_rect((med <= 45) & (std <= 25))
        it["bl"] = max_rect((med >= 150) & (std <= 25))
        it["gmed"] = int(np.median(med)); it["gstd"] = int(np.std(med))
        it["view"] = p.copy()
        ok.append(it)
    except Exception as e:
        it["err"] = str(e)
    time.sleep(0.1)

ok.sort(key=lambda r: r["bl"][0], reverse=True)
lines = [f"Commons 候选 {len(items)}，探针成功 {len(ok)}｜按亮带面积排序\n", "=" * 118 + "\n"]
for r in ok:
    lines.append(
        f"亮{r['bl'][0]:>3} r{r['bl'][1]}-{r['bl'][2]}c{r['bl'][3]}-{r['bl'][4]} | "
        f"暗{r['bd'][0]:>3} r{r['bd'][1]}-{r['bd'][2]}c{r['bd'][3]}-{r['bd'][4]} | "
        f"中位{r['gmed']:>3} std{r['gstd']:>3} | {r['artist'][:24]:<24} | {r['title'][5:70]}\n"
    )
(TMP / "q26_commons.txt").write_text("".join(lines), encoding="utf-8")
(TMP / "q26_commons_meta.json").write_text(
    json.dumps(ok, ensure_ascii=False, indent=2,
               default=lambda o: "<img>" if isinstance(o, Image.Image) else str(o)),
    encoding="utf-8")

TH_W, TH_H, LABEL, PC, PR = 192, 256, 22, 5, 6
for page in range((min(len(ok), 30) + 29) // 30):
    chunk = ok[page * 30:(page + 1) * 30]
    sheet = Image.new("RGB", (PC * TH_W, PR * (TH_H + LABEL)), (245, 245, 245))
    d = ImageDraw.Draw(sheet)
    for i, r in enumerate(chunk):
        x, y = (i % PC) * TH_W, (i // PC) * (TH_H + LABEL)
        sheet.paste(r["view"].resize((TH_W - 6, TH_H - 6), Image.LANCZOS), (x + 3, y + 3))
        d.text((x + 4, y + TH_H), f"{page * 30 + i:02d} {r['title'][5:31]}", fill=(15, 15, 15))
    sp = TMP / f"q26_sheet{page}.png"
    sheet.save(sp)
    print("sheet:", sp)
print("".join(lines[:16]))

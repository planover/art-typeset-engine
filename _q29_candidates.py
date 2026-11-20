# -*- coding: utf-8 -*-
"""Q29 选画：主题「选择与被选择」→ 岔路/分岔路口/两条路/对角构图。
画家全系列未用（已用 48 位，避开霍默/惠斯勒/理查兹/英尼斯/特沃克特曼/莱德/雷东/博尔赫/弘仁/古邨/塔德玛/毕沙罗/菲耶斯塔德）。
第零条亮度带筛 + 48px 滑窗干净矩形反查，产出排序表 + 拼版供 1:1 目验。
"""
from pathlib import Path
from PIL import Image, ImageDraw
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json, io, time, re
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"
API = "https://commons.wikimedia.org/w/api.php"

QUERIES = [
    "crossroads painting landscape fork road",
    "John Atkinson Grimshaw painting",
    "Hugh Bolton Jones painting landscape",
    "Walter Launt Palmer painting",
    "Charles Warren Eaton painting",
    "Thomas Hill painting landscape Yosemite",
    "Edward Theodore Compton painting",
    "Akseli Gallen-Kallela painting landscape",
    "Eero Jarnefelt painting",
    "Carl Fredrik Hill painting",
    "Ivan Shishkin forest painting",
    "Arkhip Kuindzhi red sunset painting",
    "Konstantin Bogaevsky painting",
    "Nicholas Roerich landscape painting",
    "Stanislaw Wyspianski painting",
    "Ferdinand Hodler lake landscape",
    "Giovanni Segantini painting",
    "Anton Mauve landscape painting",
    "Willem Maris painting",
    "Charles-Francois Daubigny painting",
    "Narcisse Virgilio Diaz painting",
    "Henri-Joseph Harpignies painting",
    "Alexandre Legros painting",
    "Adolphe Monticelli painting",
]

def api(params):
    params = dict(params); params["format"] = "json"
    req = Request(API + "?" + urlencode(params), headers={"User-Agent": UA})
    with urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch(url):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=40) as r:
        return r.read()

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

def clean_rect(im, dark=False, S=48, STEP=32):
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

seen, items = set(), []
for q in QUERIES:
    try:
        data = api({
            "action": "query", "generator": "search",
            "gsrsearch": q + " filemime:image/jpeg", "gsrnamespace": 6,
            "gsrlimit": 8, "prop": "imageinfo",
            "iiprop": "url|size|extmetadata", "iiurlwidth": 1100,
        })
    except Exception as e:
        print("API FAIL", q, e, flush=True); continue
    for p in ((data.get("query") or {}).get("pages") or {}).values():
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
                                  "signature", "detail", "stamp", "seal", "map", "frame")):
            continue
        em = ii.get("extmetadata") or {}
        def clean(k):
            v = (em.get(k) or {}).get("value", "")
            return re.sub(r"<[^>]+>", "", v).strip()[:160]
        items.append({
            "q": q, "title": title, "thumb": thumb, "url": ii.get("url"),
            "w": ii.get("width"), "h": ii.get("height"),
            "artist": clean("Artist"), "date": clean("DateTimeOriginal"),
            "license": clean("LicenseShortName"), "desc": clean("ImageDescription"),
        })
    print("query ok:", q, "->", len(items), flush=True)
    time.sleep(0.15)

print("candidates=", len(items), flush=True)
ok = []
for idx, it in enumerate(items):
    try:
        p = prep(Image.open(io.BytesIO(fetch(it["thumb"]))))
        med, std = probe(p)
        it["light_cells"] = int(((med >= 150) & (std <= 25)).sum())
        it["dark_cells"] = int(((med <= 45) & (std <= 25)).sum())
        it["gmed"] = int(np.median(med))
        it["view"] = p.copy()
        ok.append(it)
    except Exception as e:
        it["err"] = str(e)
    if idx % 25 == 0:
        print("probe", idx, "/", len(items), flush=True)
    time.sleep(0.06)

# 亮底深字优先（Q28 亮底弓形 → Q29 可走暗底或另一版式；两榜都留）
ok.sort(key=lambda r: max(r["light_cells"], r["dark_cells"]), reverse=True)
for it in ok[:36]:
    light = it["light_cells"] >= it["dark_cells"]
    it["rect"] = clean_rect(it["view"], dark=(not light))
    w = it["rect"][3] - it["rect"][2]; h = it["rect"][1] - it["rect"][0]
    it["rw"], it["rh"] = w, h
    it["mode"] = "dark" if not light else "light"
    print("rect", w, "x", h, it["mode"], it["artist"][:20], it["title"][5:55], flush=True)

lines = [f"Commons 候选 {len(items)}，探针成功 {len(ok)}｜按最大干净格数排序\n",
         "=" * 120 + "\n"]
for i, r in enumerate(ok):
    rect = r.get("rect")
    rs = (f"{r['rw']}x{r['rh']}" if rect else "-")
    lines.append(f"{i:>3} 亮{r['light_cells']:>3} 暗{r['dark_cells']:>3} 矩形{rs:>10} {r.get('mode','-'):>5} 中位{r['gmed']:>3} | "
                 f"{r['artist'][:26]:<26} | {r['title'][5:78]}\n")
(TMP / "q29_commons.txt").write_text("".join(lines), encoding="utf-8")
(TMP / "q29_commons_meta.json").write_text(
    json.dumps(ok, ensure_ascii=False, indent=2,
               default=lambda o: "<img>" if isinstance(o, Image.Image) else str(o)),
    encoding="utf-8")

TH_W, TH_H, LABEL, PC, PR = 192, 256, 22, 5, 6
for page in range((min(len(ok), 60) + 29) // 30):
    chunk = ok[page * 30:(page + 1) * 30]
    sheet = Image.new("RGB", (PC * TH_W, PR * (TH_H + LABEL)), (245, 245, 245))
    d = ImageDraw.Draw(sheet)
    for i, r in enumerate(chunk):
        x, y = (i % PC) * TH_W, (i // PC) * (TH_H + LABEL)
        sheet.paste(r["view"].resize((TH_W - 6, TH_H - 6), Image.LANCZOS), (x + 3, y + 3))
        d.text((x + 4, y + TH_H), f"{page * 30 + i:02d} {r['title'][5:31]}", fill=(15, 15, 15))
    sp = TMP / f"q29_sheet{page}.png"
    sheet.save(sp)
    print("sheet:", sp, flush=True)
print("".join(lines[:24]))

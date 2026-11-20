# -*- coding: utf-8 -*-
"""Q34 选画：主题「放弃讨好/有策略地对人好」→ 边界/独处/清醒/选择与拒绝意象。
画家全系列未用（53 位）。第零条亮度带 + 48px 滑窗干净矩形，产出排序表 + 拼版供 1:1 目验。
预先规避 Q29 教训：优先整幅或大半幅纯净背景，文字块按全宽（≥78%）设计。
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
    "solitary woman painting contemplating window",
    "person standing alone painting back view",
    "Vilhelm Hammershoi interior solitary figure",
    "Carl Gustav Carus landscape painting",
    "Caspar David Friedrich woman at window",
    "Johan Christian Dahl landscape painting",
    "Ferdinand Hodler landscape lake painting",
    "Thomas Fearnley landscape painting",
    "Ivan Shishkin forest painting",
    "Isaac Levitan landscape painting",
    "Arkhip Kuindzhi landscape painting",
    "Winslow Homer woman painting",
    "John Singer Sargent portrait woman",
    "Gustav Klimt portrait painting",
    "Egon Schiele portrait painting",
    "Amedeo Modigliani portrait painting",
    "James McNeill Whistler portrait painting",
    "Sandro Botticelli portrait painting",
    "Johannes Vermeer woman painting",
    " Rembrandt portrait woman painting",
    "Jiří Voják landscape painting",
    "Helene Schjerfbeck self portrait",
    "Verner von Heidenstam landscape",
    "Akseli Gallen-Kallela portrait",
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
    if not best[0]:
        return (0, 0, 0, 0)
    return (ys[i0], ys[i1] + S, xs[j0], xs[j1] + S)

seen, items = set(), []
for q in QUERIES:
    try:
        data = api({"action": "query", "generator": "search",
                    "gsrsearch": q + " filemime:image/jpeg", "gsrnamespace": 6,
                    "gsrlimit": 8, "prop": "imageinfo",
                    "iiprop": "url|size|extmetadata", "iiurlwidth": 1100})
    except Exception as e:
        print("API FAIL", q, str(e)[:60], flush=True); continue
    for p in ((data.get("query") or {}).get("pages") or {}).values():
        title = p.get("title", "")
        if title in seen: continue
        seen.add(title)
        ii = (p.get("imageinfo") or [{}])[0]
        thumb = ii.get("thumburl") or ii.get("url")
        if not thumb: continue
        low = title.lower()
        if any(x in low for x in ("catalogue", "magazine", "book ", "cover", "poster",
                                  "signature", "detail", "stamp", "seal", "map", "frame")):
            continue
        em = ii.get("extmetadata") or {}
        def clean(k):
            v = (em.get(k) or {}).get("value", "")
            return re.sub(r"<[^>]+>", "", v).strip()[:160]
        items.append({"q": q, "title": title, "thumb": thumb, "url": ii.get("url"),
                      "w": ii.get("width"), "h": ii.get("height"),
                      "artist": clean("Artist"), "date": clean("DateTimeOriginal"),
                      "license": clean("LicenseShortName"), "desc": clean("ImageDescription")})
    print("query ok:", q, "->", len(items), flush=True)
    time.sleep(0.18)

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

ok.sort(key=lambda r: max(r["light_cells"], r["dark_cells"]), reverse=True)
for it in ok[:36]:
    light = it["light_cells"] >= it["dark_cells"]
    it["rect"] = clean_rect(it["view"], dark=(not light))
    r = it["rect"]
    it["rw"], it["rh"] = r[3] - r[2], r[1] - r[0]
    it["mode"] = "dark" if not light else "light"
    print("rect", it["rw"], "x", it["rh"], it["mode"], it["artist"][:20], it["title"][5:55], flush=True)

lines = ["Commons 候选 %d，探针成功 %d｜按最大干净格数排序\n" % (len(items), len(ok)), "=" * 120 + "\n"]
for i, r in enumerate(ok):
    rect = r.get("rect")
    rs = ("%dx%d" % (r["rw"], r["rh"])) if rect else "-"
    lines.append("%3d 亮%3d 暗%3d 矩形%10s %5s 中位%3d | %-26s | %s\n" % (
        i, r["light_cells"], r["dark_cells"], rs, r.get("mode", "-"), r["gmed"],
        r["artist"][:26], r["title"][5:78]))
(TMP / "q34_commons.txt").write_text("".join(lines), encoding="utf-8")
(TMP / "q34_commons_meta.json").write_text(
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
        d.text((x + 4, y + TH_H), "%02d %s" % (page * 30 + i, r["title"][5:31]), fill=(15, 15, 15))
    sp = TMP / ("q34_sheet%d.png" % page)
    sheet.save(sp)
    print("sheet:", sp, flush=True)
print("".join(lines[:24]))

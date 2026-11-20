# -*- coding: utf-8 -*-
"""Q26 换画筛选：发光主义/色调主义大片均匀亮场 → 3:4 裁切后测「干净矩形」面积排序。

干净定义 = 48px 窗 median≥150 且 std≤25（与 spec.BG_DARK_TEXT_MIN / BG_STD_MAX 一致）。
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from PIL import Image, ImageDraw
import json, io, time, re
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"
API = "https://commons.wikimedia.org/w/api.php"

QUERIES = [
    "Sanford Robinson Gifford landscape",
    "John Frederick Kensett lake",
    "Martin Johnson Heade marsh sunset",
    "Jasper Francis Cropsey autumn",
    "William Trost Richards seascape",
    "Alfred Thompson Bricher coast",
]


def api(p):
    p = dict(p); p["format"] = "json"
    return json.loads(urlopen(Request(API + "?" + urlencode(p), headers={"User-Agent": UA}),
                              timeout=30).read().decode("utf-8"))


def clean_rect(im, S=48, STEP=16):
    a = np.asarray(im, np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    H, W = lum.shape
    ys = list(range(40, H - S, STEP)); xs = list(range(30, W - S, STEP))
    ok = np.zeros((len(ys), len(xs)), bool)
    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            c = lum[y:y + S, x:x + S]
            ok[i, j] = (np.median(c) >= 150) and (np.std(c) <= 25)
    best = (0, None)
    for i0 in range(0, len(ys), 4):
        for i1 in range(i0 + 1, len(ys)):
            col = ok[i0:i1 + 1].all(axis=0)
            run = 0; st = 0; bl = 0; bs = 0
            for j, v in enumerate(list(col) + [False]):
                if v:
                    if run == 0: st = j
                    run += 1
                    if run > bl: bl, bs = run, st
                else:
                    run = 0
            area = (i1 - i0 + 1) * bl
            if area > best[0]:
                best = (area, (ys[i0], ys[i1] + S, xs[bs], xs[bs + bl - 1] + S))
    return best


seen, items = set(), []
for q in QUERIES:
    try:
        d = api({"action": "query", "generator": "search",
                 "gsrsearch": q + " filemime:image/jpeg", "gsrnamespace": 6, "gsrlimit": 8,
                 "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 760})
    except Exception as e:
        print("FAIL", q, e); continue
    for p in (d.get("query") or {}).get("pages", {}).values():
        t = p.get("title", "")
        if t in seen: continue
        seen.add(t)
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("url"): continue
        low = t.lower()
        if any(x in low for x in ("catalogue", "book", "cover", "detail", "signature", "stamp")):
            continue
        items.append({"title": t, "thumb": ii.get("thumburl") or ii["url"],
                      "w": ii.get("width"), "h": ii.get("height"),
                      "artist": re.sub(r"<[^>]+>", "", (ii.get("extmetadata") or {}).get("Artist", {}).get("value", ""))[:40]})
    time.sleep(0.4)

print("候选", len(items))
res = []
for it in items:
    try:
        raw = urlopen(Request(it["thumb"], headers={"User-Agent": UA}), timeout=40).read()
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        w, h = im.size
        cw = int(round(h * 1536 / 2048))
        if w > cw:
            left = (w - cw) // 2
            base = im.crop((left, 0, left + cw, h))
        else:
            nh = int(round(w * 2048 / 1536)); top = (h - nh) // 2
            base = im.crop((0, top, w, top + nh))
        base = base.resize((1536, 2048), Image.LANCZOS)
        area, box = clean_rect(base)
        y0, y1, x0, x1 = box
        it.update(area=area, box=box, wh=(x1 - x0, y1 - y0), view=base)
        res.append(it)
    except Exception as e:
        pass

res.sort(key=lambda r: r["area"], reverse=True)
print("\n排名（干净矩形面积 → 宽×高 @ y0-1 / x0-1）")
for r in res[:12]:
    print(f"  {r['area']:>7}  {r['wh'][0]:>4}x{r['wh'][1]:<4} y{r['box'][0]}-{r['box'][1]} x{r['box'][2]}-{r['box'][3]}  {r['artist'][:22]:<22} {r['title'][5:60]}")

json.dump([{k: v for k, v in r.items() if k != "view"} for r in res],
          open(TMP / "q26_luminist.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

TW, TH, cols = 300, 400, 5
top = res[:10]
rows = (len(top) + cols - 1) // cols
sheet = Image.new("RGB", (cols * TW, rows * (TH + 20)), (240, 240, 240))
d = ImageDraw.Draw(sheet)
for i, r in enumerate(top):
    x, y = (i % cols) * TW, (i // cols) * (TH + 20)
    sheet.paste(r["view"].resize((TW - 6, TH - 6), Image.LANCZOS), (x + 3, y + 3))
    d.text((x + 4, y + TH), f"{i} {r['wh'][0]}x{r['wh'][1]}", fill=(10, 10, 10))
sheet.save(TMP / "q26_luminist_sheet.png")
print("saved", TMP / "q26_luminist_sheet.png")

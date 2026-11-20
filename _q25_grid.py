# -*- coding: utf-8 -*-
"""Q25 选画：对缓存候选做 3:4 裁切 + 16x8 亮度带网格探针，并生成目验 contact sheet。

第零条：浅字需底色中位 <=45，深字需 >=150；中间调 60-110 不选；std <=25。
"""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
TMP = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")
OUT = TMP / "q25_grid.txt"
W, H = 1536, 2048
COLS, ROWS = 16, 8
CW, CH = W // COLS, H // ROWS

# 只看候选原图 jpg（排除 view/png 中间产物）
cands = sorted(p for p in CACHE.glob("*.jpg"))


def prep(p: Path) -> Image.Image:
    im = Image.open(p).convert("RGB")
    w, h = im.size
    ratio = W / H
    if w / h > ratio:
        nw = int(round(h * ratio))
        left = (w - nw) // 2
        im = im.crop((left, 0, left + nw, h))
    else:
        nh = int(round(w / ratio))
        top = (h - nh) // 2
        im = im.crop((0, top, w, top + nh))
    return im.resize((W, H), Image.LANCZOS)


def grid(im: Image.Image):
    a = np.asarray(im, dtype=np.int32)
    lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
    med = np.zeros((ROWS, COLS), dtype=np.int32)
    std = np.zeros((ROWS, COLS), dtype=np.int32)
    dark = np.zeros((ROWS, COLS), dtype=np.float32)
    for r in range(ROWS):
        for c in range(COLS):
            cell = lum[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW]
            med[r, c] = int(np.median(cell))
            std[r, c] = int(np.std(cell))
            dark[r, c] = float((cell < 80).mean())
    return med, std, dark


def max_rect(ok: np.ndarray):
    """最大全 1 矩形，返回 (面积, r0, r1, c0, c1)。"""
    hist = np.zeros(COLS, dtype=np.int32)
    best = (0, 0, 0, 0, 0)
    for r in range(ROWS):
        hist = np.where(ok[r], hist + 1, 0)
        stack = []
        for c in range(COLS + 1):
            hcur = int(hist[c]) if c < COLS else 0
            while stack and hist[stack[-1]] >= hcur:
                height = int(hist[stack.pop()])
                c0 = stack[-1] + 1 if stack else 0
                area = height * (c - c0)
                if area > best[0]:
                    best = (area, r - height + 1, r, c0, c - 1)
            stack.append(c)
    return best


rows = []
for p in cands:
    try:
        im = prep(p)
        med, std, dark = grid(im)
        okd = (med <= 45) & (std <= 25)
        okl = (med >= 150) & (std <= 25)
        bd = max_rect(okd)
        bl = max_rect(okl)
        rows.append({
            "name": p.name, "im": im, "med": med, "std": std, "dark": dark,
            "bd": bd, "bl": bl,
            "gmed": int(np.median(med)), "gstd": int(np.std(med)),
        })
    except Exception as e:
        rows.append({"name": p.name, "err": str(e)})

rows_ok = [r for r in rows if "err" not in r]
rows_ok.sort(key=lambda r: max(r["bd"][0], r["bl"][0]), reverse=True)

lines = [f"候选 {len(rows)} 张，成功 {len(rows_ok)} 张\n",
         "排序键 = max(暗带矩形格数, 亮带矩形格数)；矩形 = (面积,r0,r1,c0,c1)\n",
         "=" * 100 + "\n"]
for r in rows_ok:
    lines.append(
        f"{r['name']:<34} 暗{r['bd'][0]:>3}格 r{r['bd'][1]}-{r['bd'][2]} c{r['bd'][3]}-{r['bd'][4]} | "
        f"亮{r['bl'][0]:>3}格 r{r['bl'][1]}-{r['bl'][2]} c{r['bl'][3]}-{r['bl'][4]} | "
        f"全图中位{r['gmed']:>3} 网格std{r['gstd']:>3}\n"
    )
for r in rows:
    if "err" in r:
        lines.append(f"ERR {r['name']}: {r['err']}\n")
OUT.write_text("".join(lines), encoding="utf-8")

# contact sheet：前 60 名，每页 5x6 = 30 张
TH_W, TH_H, LABEL = 192, 256, 22
PAGE_COLS, PAGE_ROWS = 5, 6
for page in range(2):
    chunk = rows_ok[page * 30:(page + 1) * 30]
    if not chunk:
        break
    sheet = Image.new("RGB", (PAGE_COLS * TH_W, PAGE_ROWS * (TH_H + LABEL)), (245, 245, 245))
    d = ImageDraw.Draw(sheet)
    for i, r in enumerate(chunk):
        x, y = (i % PAGE_COLS) * TH_W, (i // PAGE_COLS) * (TH_H + LABEL)
        sheet.paste(r["im"].resize((TH_W - 6, TH_H - 6), Image.LANCZOS), (x + 3, y + 3))
        d.text((x + 4, y + TH_H), f"{page * 30 + i:02d} {r['name'][:26]}", fill=(20, 20, 20))
    sp = TMP / f"q25_sheet{page}.png"
    sheet.save(sp)
    print(f"sheet {page}: {sp} ({len(chunk)} imgs)")

print(f"grid report: {OUT}")
print("".join(lines[:18]))

# -*- coding: utf-8 -*-
"""Q30：对标题所在的岸线/倒影交界带做轻度大羽化柔光，把 std 26→<25。
只处理 y=1150-1360 的窄带（标题＋正文首行所在），不动上半山峦与下半纯水。
烘制后的底图同时作为 verify 的 base（Q29 军规）。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
src = TMP / "q30_base.png"
im = Image.open(src).convert("RGB")
W, H = im.size

# 取带内主色（浅蓝灰）作柔光色，避免偏黄
a = np.asarray(im, np.int32)
lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
band = lum[1460:1500, 300:1200]
tint_rgb = tuple(int(v) for v in np.median(a[1460:1500, 300:1200].reshape(-1, 3), axis=0))
print("柔光色", tint_rgb, "带中位", int(np.median(band)))

mask = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask)
d.rectangle((90, 1160, 1446, 1350), fill=95)
mask = mask.filter(ImageFilter.GaussianBlur(75))
tint = Image.new("RGB", (W, H), tint_rgb)
out = Image.composite(tint, im, mask)
out.save(TMP / "q30_base_baked.png")
print("烘制完成")

o = np.asarray(out, np.int32)
ol = (o[..., 0] * 2126 + o[..., 1] * 7152 + o[..., 2] * 722) // 10000
for y in (1200, 1250, 1300, 1350, 1450):
    c = ol[y:y + 40, 80:1450]
    print("y%d 中位%d std%d" % (y, int(np.median(c)), int(np.std(c))))
out.resize((768, 1024), Image.LANCZOS).save(TMP / "q30_baked_view.png")

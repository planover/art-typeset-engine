# -*- coding: utf-8 -*-
"""全宽柔光烘进底图：x=60-1476, y=60-640（文字区），大羽化 120px。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
src = TMP / "q29_Hill_YosemiteBridalVeil_base.png"
im = Image.open(src).convert("RGB")
W, H = im.size

mask = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask)
d.rectangle((60, 60, 1476, 690), fill=125)
mask = mask.filter(ImageFilter.GaussianBlur(105))
tint = Image.new("RGB", (W, H), (248, 236, 214))
out = Image.composite(tint, im, mask)
out.save(TMP / "q29_base.png")
print("烘制完成")

a = np.asarray(out, np.int32)
lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
for y in (250, 450, 550):
    c = lum[y:y + 40, 80:1450]
    print("y%d 中位%d std%d" % (y, int(np.median(c)), int(np.std(c))))

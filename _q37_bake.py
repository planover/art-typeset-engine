# -*- coding: utf-8 -*-
"""Q37：文字区下半（y560-960）做大羽化柔光，把数钱老妇淡化到半透明背景，
文字压在柔光幕上不与人脸硬撞。取暗主色，90px 高斯。同步作 verify base。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
im = Image.open(TMP / "q37_base.png").convert("RGB")
W, H = im.size
a = np.asarray(im, np.int32)
tint_rgb = tuple(int(v) for v in np.median(a[200:500, 100:900].reshape(-1, 3), axis=0))
print("柔光色", tint_rgb)

mask = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask)
# 文字覆盖的下半区 y560-960，全宽 x60-1476
d.rectangle((60, 560, 1476, 960), fill=130)
mask = mask.filter(ImageFilter.GaussianBlur(85))
tint = Image.new("RGB", (W, H), tint_rgb)
out = Image.composite(tint, im, mask)
out.save(TMP / "q37_base_baked.png")

o = np.asarray(out, np.int32)
ol = (o[..., 0] * 2126 + o[..., 1] * 7152 + o[..., 2] * 722) // 10000
for y in (618, 657, 708, 748, 789, 828, 875, 933):
    c = ol[y:y + 22, 80:1450]
    print("y%d 中位%d std%d" % (y, int(np.median(c)), int(np.std(c))))
out.resize((768, 1024), Image.LANCZOS).save(TMP / "q37_baked_view.png")

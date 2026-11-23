# -*- coding: utf-8 -*-
"""Q36：对英文/款识所在的"暗背景→火光"过渡带做大羽化柔光。
只处理 x151-1385 文字覆盖区的下半（y460-980），取极暗主色；
林肯主体在 x600-1100/y950+，高斯羽化 90px 保留轮廓。
烘制底图同步作 verify base（Q29 军规）。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
im = Image.open(TMP / "q36_base.png").convert("RGB")
W, H = im.size
a = np.asarray(im, np.int32)
tint_rgb = tuple(int(v) for v in np.median(a[200:400, 100:900].reshape(-1, 3), axis=0))
print("柔光色", tint_rgb)

mask = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask)
# 主柔化区：文字覆盖的暗区，y450-970，x100-1400
d.rectangle((100, 450, 1400, 970), fill=115)
mask = mask.filter(ImageFilter.GaussianBlur(90))
tint = Image.new("RGB", (W, H), tint_rgb)
out = Image.composite(tint, im, mask)
out.save(TMP / "q36_base_baked.png")

o = np.asarray(out, np.int32)
ol = (o[..., 0] * 2126 + o[..., 1] * 7152 + o[..., 2] * 722) // 10000
for y in (500, 834, 880, 935):
    c = ol[y:y + 20, 80:1450]
    print("y%d 中位%d std%d" % (y, int(np.median(c)), int(np.std(c))))
out.resize((768, 1024), Image.LANCZOS).save(TMP / "q36_baked_view.png")

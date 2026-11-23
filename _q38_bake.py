# -*- coding: utf-8 -*-
"""Q38：金黄绢底撞「色相差强调识别」算法——整片正文区被误判为金色（强调29%）。
对文字覆盖区 y350-1050 做中性灰柔光（把金黄压成中性米灰，色相差 R-B 从 60+ 降到 <18），
保留下半老虎原色与上部装裱边框。同步作 verify base。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
im = Image.open(TMP / "q38_base.png").convert("RGB")
W, H = im.size
a = np.asarray(im, np.int32)
# 取净绢区中位亮度，做成中性灰（R=G=B）
lum = int(np.median((a[400:900, 100:900] * [0.299, 0.587, 0.114]).sum(axis=2)))
tint_rgb = (lum, lum, lum)
print("中性灰", tint_rgb, "原绢底 R-B=", int(np.median(a[400:900, 100:900, 0] - a[400:900, 100:900, 2])))

mask = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask)
d.rectangle((60, 350, 1476, 1050), fill=225)
mask = mask.filter(ImageFilter.GaussianBlur(75))
tint = Image.new("RGB", (W, H), tint_rgb)
out = Image.composite(tint, im, mask)
out.save(TMP / "q38_base_baked.png")

# 测中和后的色相差与 std
o = np.asarray(out, np.int32)
ol = (o[..., 0] * 2126 + o[..., 1] * 7152 + o[..., 2] * 722) // 10000
for y in (500, 700, 900):
    c = o[y:y+30, 100:1400]
    print("y%d R-B中位%d std%.1f" % (y, int(np.median(c[...,0]-c[...,2])), np.std(ol[y:y+30, 80:1450])))
out.resize((768, 1024), Image.LANCZOS).save(TMP / "q38_baked_view.png")

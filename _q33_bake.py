# -*- coding: utf-8 -*-
"""Q33：对前两行正文所在的淡金云纹理带做轻度大羽化柔光，std 26→<25。
只处理 y=190-330 的窄带，不动下方纯净湖面与树梢。烘制底图同步作为 verify base（Q29 军规）。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
im = Image.open(TMP / "q33_base.png").convert("RGB")
W, H = im.size
a = np.asarray(im, np.int32)
# 取带内主色（淡金米白）
tint_rgb = tuple(int(v) for v in np.median(a[360:420, 300:1200].reshape(-1, 3), axis=0))
print("柔光色", tint_rgb)

mask = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask)
d.rectangle((90, 190, 1446, 330), fill=100)
mask = mask.filter(ImageFilter.GaussianBlur(85))
tint = Image.new("RGB", (W, H), tint_rgb)
out = Image.composite(tint, im, mask)
out.save(TMP / "q33_base_baked.png")

o = np.asarray(out, np.int32)
ol = (o[..., 0] * 2126 + o[..., 1] * 7152 + o[..., 2] * 722) // 10000
for y in (229, 270, 310, 400):
    c = ol[y:y + 32, 151:1385]
    print("y%d 中位%d std%d" % (y, int(np.median(c)), int(np.std(c))))
out.resize((768, 1024), Image.LANCZOS).save(TMP / "q33_baked_view.png")

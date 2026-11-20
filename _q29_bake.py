# -*- coding: utf-8 -*-
"""把柔光衬底烘进底图：verify 用原图算背景 std，烘进去后数值与视觉一致。
文字区 (x 97-780, y 90-810)，暖白 250,236,208，alpha 118，140px 羽化。
"""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np

TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
src = TMP / "q29_base.png"
im = Image.open(src).convert("RGB")
W, H = im.size
# 文字块范围（按实测墨区）；略微外扩让羽化过渡自然
X0, X1 = 40, 860
Y0, Y1 = 40, 860

mask = Image.new("L", (W, H), 0)
from PIL import ImageDraw
d = ImageDraw.Draw(mask)
d.rectangle((X0, Y0, X1, Y1), fill=118)
mask = mask.filter(ImageFilter.GaussianBlur(150))

tint = Image.new("RGB", (W, H), (250, 236, 208))
out = Image.composite(tint, im, mask)
out.save(TMP / "q29_base_baked.png")
print("烘制完成", TMP / "q29_base_baked.png")

# 验证文字区 std 降幅
a = np.asarray(out.convert("RGB"), np.int32)
lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
for y in (250, 450, 600, 700):
    cell = lum[y:y + 48, 100:780]
    print("y=%d 中位%d std%d" % (y, int(np.median(cell)), int(np.std(cell))))

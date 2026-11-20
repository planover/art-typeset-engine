# -*- coding: utf-8 -*-
"""Q27 新字体入场三查：能打开 → 0 缺字 → 字号可辨（目验 q27_fonttest.png）。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(r"C:\Users\admin\.workbuddy-ai\fonts")
TITLE = "过度谦虚是自降价值"
BODY = ("不分场合，不适当的谦虚，有的时候就是在自降价值，谦虚用错了对象，会被误认为是一种无能和弱，"
        "别人不仅不会尊重你，甚至还会看不起你，拿捏你。如果不是和比自己优秀很多的人沟通，和大部分的人沟通，"
        "实际上不怎么需要谦虚，一旦在一开始你就谦虚起来，有些心里没数的人，就会傲慢起来，无礼起来，"
        "到后面你的气场再想提起来，就会增加很多难度，过度谦虚有的时候是在降低气场，不利于维护自己威信和利益。")
CHARS = sorted(set(TITLE + BODY))
CAND = {
    "mashan": D / "MaShanZheng-Regular.ttf",
    "qingke": D / "ZCOOLQingKeHuangYou-Regular.ttf",
    "smiley": D / "smiley" / "SmileySans-Oblique.ttf",
    "song": Path(r"C:\Windows\Fonts\STZHONGS.TTF"),
    "hei": Path(r"C:\Windows\Fonts\simhei.ttf"),
}


def bitmap(font, ch, box=110):
    im = Image.new("L", (box, box), 0)
    ImageDraw.Draw(im).text((6, 2), ch, font=font, fill=255)
    return im.tobytes()


report = {}
for key, path in CAND.items():
    if not path.exists():
        print(key, "MISSING", path); continue
    f = ImageFont.truetype(str(path), 64)
    nd = bitmap(f, "\ue000")            # 私有区必缺，作为 .notdef 基准
    missing = [ch for ch in CHARS if bitmap(f, ch) == nd or
               Image.frombytes("L", (110, 110), bitmap(f, ch)).getbbox() is None]
    report[key] = missing
    print("%-8s 字体打开 OK｜字符 %d｜缺字 %d %s" %
          (key, len(CHARS), len(missing), "".join(missing[:20])))

# 字号可辨：80px 标题 + 32px 正文样本
sheet = Image.new("RGB", (1200, 460), (18, 26, 38))
d = ImageDraw.Draw(sheet)
y = 20
for key in ("mashan", "qingke", "smiley"):
    p = CAND.get(key)
    if not p or not p.exists():
        continue
    f = ImageFont.truetype(str(p), 80)
    d.text((20, y), TITLE, font=f, fill=(238, 226, 196))
    d.text((1000, y + 20), key, font=ImageFont.truetype(str(CAND["song"]), 24),
           fill=(240, 158, 64))
    y += 140
out = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q27_fonttest.png")
sheet.save(out)
print("目验图:", out)

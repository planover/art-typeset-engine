# -*- coding: utf-8 -*-
"""Q28 字体入场三查：能打开 → 0 缺字 → 字号可辨（亮底深字目验 q28_fonttest.png）。

Q27 用 mashan/song/playfair/hei；Q28 换 qingke/serif/inter/kai 四体，
且这次是亮底深字，样张必须按亮底出（Q27 样张是暗底，不能直接借）。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(r"C:\Users\admin\.workbuddy-ai\fonts")
TITLE = "没那么多三观一致"
BODY = ("其实没有那么多所谓三观一致的人，人们只不过是为了自己各种各样的目的，"
        "把那个当下的自己伪装成了你的同类，让你觉得遇到了三观一致，很合得来的人，"
        "实际上你们是完全不同的两类人。")
CHARS = sorted(set(TITLE + BODY))
CAND = {
    "qingke": D / "ZCOOLQingKeHuangYou-Regular.ttf",
    "smiley": D / "smiley" / "SmileySans-Oblique.ttf",
    "serif": Path(r"C:\Windows\Fonts\NotoSerifSC-VF.ttf"),
    "song": Path(r"C:\Windows\Fonts\STZHONGS.TTF"),
    "kai": D / "LXGWWenKai-Regular.ttf",
    "hei": Path(r"C:\Windows\Fonts\simhei.ttf"),
    "inter": D / "Inter[opsz,wght].ttf",
}


def bitmap(font, ch, box=110):
    im = Image.new("L", (box, box), 0)
    ImageDraw.Draw(im).text((6, 2), ch, font=font, fill=255)
    return im.tobytes()


for key, path in CAND.items():
    if not path.exists():
        print(key, "MISSING", path); continue
    try:
        f = ImageFont.truetype(str(path), 64)
    except Exception as e:
        print(key, "OPEN FAIL", e); continue
    nd = bitmap(f, "\ue000")
    if key == "inter":
        chars = sorted(set("In truth there are not so many people who share your values"))
    else:
        chars = CHARS
    missing = [ch for ch in chars if bitmap(f, ch) == nd or
               Image.frombytes("L", (110, 110), bitmap(f, ch)).getbbox() is None]
    print("%-8s 打开 OK｜字符 %d｜缺字 %d %s" %
          (key, len(chars), len(missing), "".join(missing[:20])))

# 亮底深字样张：80px 标题候选 + 38px 正文
sheet = Image.new("RGB", (1240, 620), (236, 228, 206))
d = ImageDraw.Draw(sheet)
y = 24
for key in ("qingke", "smiley", "serif"):
    p = CAND.get(key)
    if not p or not p.exists():
        continue
    f = ImageFont.truetype(str(p), 80)
    d.text((20, y), TITLE, font=f, fill=(38, 34, 30))
    d.text((980, y + 22), key, font=ImageFont.truetype(str(CAND["hei"]), 26), fill=(168, 52, 32))
    y += 180
for key in ("serif", "song", "kai"):
    p = CAND.get(key)
    if not p or not p.exists():
        continue
    f = ImageFont.truetype(str(p), 36)
    d.text((20, y), "把那个当下的自己伪装成了你的同类", font=f, fill=(38, 34, 30))
    d.text((980, y + 4), key, font=ImageFont.truetype(str(CAND["hei"]), 22), fill=(168, 52, 32))
    y += 62
out = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q28_fonttest.png")
sheet.save(out)
print("目验图:", out)

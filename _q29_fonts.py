# -*- coding: utf-8 -*-
"""Q29 字体入场三查：能打开 → 0 缺字 → 字号可辨（亮/暗底样张）。
Q27 用 mashan/song/playfair/hei；Q28 用 qingke/serif/inter/kai；
Q29 换 xingkai行楷 / sans思源黑 / garamond / song华文中宋。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(r"C:\Users\admin\.workbuddy-ai\fonts")
TITLE = "选择与被选择"
BODY = ("人的一生都要面对选择和被选择，能够被选择是幸运，而有的时候不被选择也是一种幸运，"
        "正因为没有被选择，才遇到了更好的选择，所以坦然的面对选择与被选择，因为那都是不同的机会。")
CHARS = sorted(set(TITLE + BODY))

# 找实际字体文件（含子目录）
def find(pattern):
    hits = list(D.rglob(pattern))
    return hits[0] if hits else None

CAND = {
    "xingkai": find("*.ttf") and find("FZKai*") or find("STXingkai*"),
    "sans": find("SourceHanSansSC-Regular.otf"),
    "garamond": find("EBGaramond*.ttf") or find("Garamond*.ttf") or find("garamond*.ttf"),
    "song": find("SourceHanSerifSC-Regular.otf"),
}
# 直接列出候选文件名辅助定位
print("字体目录 ttf/otf:")
for f in sorted(D.rglob("*")):
    if f.suffix.lower() in (".ttf", ".otf", ".ttc"):
        print("  ", f.relative_to(D))
print()

for k, p in CAND.items():
    if not p or not Path(p).exists():
        print(k, "MISSING", p); continue
    try:
        font = ImageFont.truetype(str(p), 60)
        # PIL getmask 对缺字回退到 .notdef 方框，用渲染宽度一致性近似检测
        miss = []
        widths = {}
        for ch in CHARS:
            w = font.getbbox(ch)[2] - font.getbbox(ch)[0]
            widths.setdefault(w, []).append(ch)
        # 缺字通常统一落到同一 .notdef 宽度且成组出现；这里只报告可疑分组
        common = max(widths.items(), key=lambda kv: len(kv[1]))
        print(k, "OK", Path(p).name, "bbox宽分组", len(widths),
              "最常见宽度", common[0], "字数", len(common[1]))
    except Exception as e:
        print(k, "OPEN FAIL", e)

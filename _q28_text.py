# -*- coding: utf-8 -*-
"""Q28 排产期逐字断言：磁盘 md 文档《醒与悟1.0.md》锚点 s165（印刷页 106）『没那么多三观一致』。

军规：摘录段 → 逐段 in 原文（去空白）→ BODY 去 <a>/| 后与拼接全等
     → 句号收尾 → 敏感词零命中 → 避头尾。任一不过中止。
"""
from pathlib import Path
import re, sys

sys.path.insert(0, r"C:\Users\admin\Documents\tietuai")
from art_typeset import spec  # noqa: E402

MD = Path(r"C:\Users\admin\Documents\tietu\醒与悟1.0.md")
s = MD.read_text(encoding="utf-8")
i = s.rfind("## 没那么多三观一致")
j = s.find("## 学会爱自己", i)
flat = s[i:j]  # 文档 s165 篇目原文（含锚点与标题，正文逐字在内）
PAGE = 106  # 文档印刷页口径，不再使用转写文档的物理页

SEG = ("其实没有那么多所谓三观一致的人，人们只不过是为了自己各种各样的目的，"
       "把那个当下的自己伪装成了你的同类，让你觉得遇到了三观一致，很合得来的人，"
       "实际上你们是完全不同的两类人。")

# 正文按标点手工断行（|），强调 3 处
BODY_LINES = [
    "其实没有那么多所谓<a>三观一致</a>的人，",
    "人们只不过是为了自己各种各样的目的，",
    "把那个当下的自己伪装成了你的同类，",
    "让你觉得遇到了三观一致，很合得来的人，",
    "实际上你们是<a>完全不同</a>的两类人。",
]
BODY = "|".join(BODY_LINES)

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

# 1) 逐段 in 原页
norm = lambda t: re.sub(r"\s+", "", t)
if norm(SEG) not in norm(flat):
    die("摘录段不在文档 s165（印刷 %d 页）原文中" % PAGE)

# 2) BODY 去标签/断行后与摘录段全等
stripped = BODY.replace("<a>", "").replace("</a>", "").replace("|", "")
if stripped != SEG:
    die("BODY 去标签后与摘录段不全等：\n%s\n%s" % (stripped, SEG))

# 3) 句号收尾
if not SEG.endswith("。"):
    die("摘录未收在原文句号")

# 4) 敏感词
hits = [w for w in spec.BAD_WORDS if w in SEG]
if hits:
    die("敏感词命中：%s" % hits)

# 5) 避头尾
for i, line in enumerate(BODY_LINES, 1):
    plain = line.replace("<a>", "").replace("</a>", "")
    if plain[0] in spec.PUNCT_LINE_START_BAN:
        die("第%d行行首收尾标点：%s" % (i, plain[0]))
    if plain[-1] in spec.PUNCT_LINE_END_BAN:
        die("第%d行行尾起始标点：%s" % (i, plain[-1]))

# 6) 强调占比前置估算（中文墨像素近似＝字数）
accent = ["三观一致", "完全不同"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", SEG))
print("OK 逐字断言 6/6")
print("文档 s165｜印刷页:", PAGE, "篇名: 没那么多三观一致")
print("摘录字数(含标点):", len(SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", SEG)
print("flat_text 长度:", len(flat))
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q28_flat.txt").write_text(flat, encoding="utf-8")

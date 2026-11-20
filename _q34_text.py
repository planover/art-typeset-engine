# -*- coding: utf-8 -*-
"""Q33 排产期逐字断言：md 文档《醒与悟1.0.md》锚点 s283（印刷 121 页）『想成熟，从放弃做好人开始』。

单段 153 字。强调按字数反推（去标点约 135 字，8% 需约 11 字），选 2 处共 16 字。
军规：摘录段 → in 原文（去空白）→ BODY 去 <a>/| 后与拼接全等
     → 句号收尾 → 敏感词零命中 → 避头尾。任一不过中止。
"""
from pathlib import Path
import re, sys

sys.path.insert(0, r"C:\Users\admin\Documents\tietuai")
from art_typeset import spec  # noqa: E402

MD = Path(r"C:\Users\admin\Documents\tietu\醒与悟1.0.md")
s = MD.read_text(encoding="utf-8")
parts = re.split(r"<a id=\"s(\d+)\"></a>\n### (.+?)\n", s)
flat = ""
for k in range(1, len(parts), 3):
    if int(parts[k]) == 283:
        flat = parts[k + 2].split("<a id=")[0].strip()
        break
if not flat:
    print("FAIL: md 文档未找到 s283 篇目")
    sys.exit(1)

SEG = ("很多人成熟是从放弃做大众眼里的好人开始，并不是说做一个伤害别人的坏人，"
       "而是要选择性的做一个好人。你的好要因人而异，否则你的好不仅会廉价，"
       "还会纵容别人对你的不好。无论你跟人是一个什么样的亲人关系，恋人关系，朋友关系，"
       "还是合作关系，你都必须有策略，有手段的对他好，没策略，没手段的对人好，"
       "最后往往受伤的是自己。")

# 正文按标点手工断行（|），强调 3 处 4 字词
BODY_LINES = [
    "很多人成熟是从<a>放弃做大众眼里的好人</a>开始，",
    "并不是说做一个伤害别人的坏人，",
    "而是要选择性的做一个好人。",
    "你的好要因人而异，",
    "否则你的好不仅会廉价，还会纵容别人对你的不好。",
    "无论你跟人是一个什么样的亲人关系，恋人关系，朋友关系，",
    "还是合作关系，你都必须<a>有策略，有手段</a>的对他好，",
    "没策略，没手段的对人好，最后往往受伤的是自己。",
]
BODY = "|".join(BODY_LINES)

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

def norm(t):
    return re.sub(r"\s+", "", t)

if norm(SEG) not in norm(flat):
    die("摘录段不在文档 s267（印刷 120 页）原文中")

stripped = BODY.replace("<a>", "").replace("</a>", "").replace("|", "")
if stripped != SEG:
    die("BODY 去标签后与摘录段不全等：\n%s\n%s" % (stripped, SEG))

if not SEG.endswith("。"):
    die("摘录未收在原文句号")

hits = [w for w in spec.BAD_WORDS if w in SEG]
if hits:
    die("敏感词命中：%s" % hits)

for i, line in enumerate(BODY_LINES, 1):
    plain = line.replace("<a>", "").replace("</a>", "")
    if plain[0] in spec.PUNCT_LINE_START_BAN:
        die("第%d行行首收尾标点：%s" % (i, plain[0]))
    if plain[-1] in spec.PUNCT_LINE_END_BAN:
        die("第%d行行尾起始标点：%s" % (i, plain[-1]))

accent = ["放弃做大众眼里的好人", "有策略，有手段"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", SEG))
print("OK 逐字断言 6/6")
print("文档 s283｜印刷页:", 121, "篇名: 想成熟，从放弃做好人开始")
print("摘录字数(含标点):", len(SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", SEG)
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q34_flat.txt").write_text(flat, encoding="utf-8")

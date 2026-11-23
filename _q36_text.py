# -*- coding: utf-8 -*-
"""Q36 逐字断言：md 文档《醒与悟2.0.md》锚点 sec-057 第1条『投资自己』。

跨文档开采：2.0 锚点格式为 sec-NNN，话术「文档 2.0 起」。
去掉段首列表编号「1，」（结构性标记，非正文文字）；其余逐字保留。
"""
from pathlib import Path
import re, sys

sys.path.insert(0, r"C:\Users\admin\Documents\tietuai")
from art_typeset import spec  # noqa: E402

MD = Path(r"C:\Users\admin\Documents\tietu\醒与悟2.0.md")
s = MD.read_text(encoding="utf-8")
parts = re.split(r"<a id=\"(sec-\d+)\"></a>\s*\n#{1,4}\s*(.+?)\n", s)
flat = ""
for k in range(1, len(parts), 3):
    if parts[k] == "sec-057":
        flat = parts[k + 2].split("<a id=")[0].strip()
        break
if not flat:
    print("FAIL: md 文档 2.0 未找到 sec-057")
    sys.exit(1)

SEG = ("不要管别人怎么说你，怎么看你，把所有时间精力都用来操心自己，投资自己。"
       "在你没有钱之前不要去思考别人的事。"
       "地球不需要你拯救，需要拯救的是你自己。"
       "每个人最重要的是自己的注意力和自己的时间，因为人与人之间，唯一公平的只有时间。"
       "只思考和自己前途未来相关的事。其他的事情跟你没有任何关系。"
       "多看一眼，多停留一秒都是浪费时间。"
       "能够让你变得越来越牛的只有投资自己，投资自己的外表，投资自己的健康，投资自己的头脑。"
       "要让每一天的自己都比昨天强那么一点点。")

BODY_LINES = [
    "不要管别人怎么说你，怎么看你，",
    "把所有时间精力都用来操心自己，<a>投资自己</a>。",
    "在你没有钱之前不要去思考别人的事。",
    "<a>地球不需要你拯救</a>，需要拯救的是你自己。",
    "每个人最重要的是自己的注意力和自己的时间，",
    "因为人与人之间，唯一公平的只有时间。",
    "只思考和自己前途未来相关的事。",
    "其他的事情跟你没有任何关系。",
    "多看一眼，多停留一秒都是浪费时间。",
    "能够让你变得越来越牛的只有<a>投资自己</a>，",
    "投资自己的外表，投资自己的健康，投资自己的头脑。",
    "要让每一天的自己都比昨天强那么一点点。",
]
BODY = "|".join(BODY_LINES)

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

# 原文整段含列表编号「1，」，去掉编号后应逐字相等
src_seg = flat.split("\n\n")[1]
if src_seg.startswith("1，"):
    src_seg = src_seg[2:]
if re.sub(r"\s+", "", src_seg) != re.sub(r"\s+", "", SEG):
    die("摘录段与 sec-057 第1条不全等：\n%s\n%s" % (src_seg, SEG))
stripped = BODY.replace("<a>", "").replace("</a>", "").replace("|", "")
if stripped != SEG:
    die("BODY 去标签后与摘录段不全等")
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

accent = ["投资自己", "地球不需要你拯救", "投资自己"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", SEG))
print("OK 逐字断言 6/6")
print("文档 2.0｜锚点 sec-057 第1条｜篇名: 第八节让自己増値")
print("摘录字数(含标点):", len(SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", SEG)
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q36_flat.txt").write_text(flat, encoding="utf-8")

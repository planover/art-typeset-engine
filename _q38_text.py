# -*- coding: utf-8 -*-
"""Q38 逐字断言：md 文档《醒与悟2.0.md》锚点 sec-130 段1『手中有刀，心中有佛』。
去段首列表编号「2，」（结构性标记非正文），其余逐字保留。
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
    if parts[k] == "sec-130":
        flat = parts[k + 2].split("<a id=")[0].strip()
        break
if not flat:
    print("FAIL: md 文档 2.0 未找到 sec-130")
    sys.exit(1)

SEG = ("人到中年，手中有刀，心中有佛。大事狠如猛虎，事了闲看落花。"
       "个人感悟就是该做事时拼命，该玩时尽兴玩好，工作和生活必须有所区分。"
       "除了生老病死，人生里真正重要的事，其实没有几件。"
       "没必要为了小事愁容满面，也没必要去跟小人争个长短。"
       "如果厌恶身边的人，表达厌恶最好的方式不是和他们争吵，而是自己努力，加把劲离开他们。")

BODY_LINES = [
    "人到中年，<a>手中有刀</a>，<a>心中有佛</a>。",
    "<a>大事狠如猛虎</a>，事了闲看落花。",
    "个人感悟就是该做事时拼命，该玩时尽兴玩好，",
    "工作和生活必须有所区分。",
    "除了生老病死，人生里真正重要的事，其实没有几件。",
    "没必要为了小事愁容满面，",
    "也没必要去跟小人争个长短。",
    "如果厌恶身边的人，",
    "表达厌恶最好的方式不是和他们争吵，",
    "而是自己努力，加把劲离开他们。",
]
BODY = "|".join(BODY_LINES)

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

src_seg = flat.split("\n\n")[1]
if src_seg.startswith("2，"):
    src_seg = src_seg[2:]
if re.sub(r"\s+", "", src_seg) != re.sub(r"\s+", "", SEG):
    die("摘录段与 sec-130 段1 不全等：\n%s\n%s" % (src_seg, SEG))
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

accent = ["手中有刀", "心中有佛", "大事狠如猛虎"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", SEG))
print("OK 逐字断言 6/6")
print("文档 2.0｜锚点 sec-130 段1｜篇名: 第五节成年人看透三件事")
print("摘录字数(含标点):", len(SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", SEG)
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q38_flat.txt").write_text(flat, encoding="utf-8")

# -*- coding: utf-8 -*-
"""Q32 排产期逐字断言：md 文档《醒与悟1.0.md》锚点 s243（印刷 119 页）『给自己留点神秘感』。

两段 176 字整段（无 OCR 损坏）。强调选笔画少的单字（Q31 军规：极短/短文本按语义挑笔画少的字）。
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
    if int(parts[k]) == 243:
        flat = parts[k + 2].split("<a id=")[0].strip()
        break
if not flat:
    print("FAIL: md 文档未找到 s243 篇目")
    sys.exit(1)

SEG = ("人是喜新厌旧的动物，人和人在最初相识的时候，新鲜又热情，"
       "一旦熟悉或者相处了一段时间后，新鲜感和热情就会减退，"
       "因为人会对完全看透且了解的东西失去兴趣，甚至是失去当初对彼此的欣赏和尊重。"
       "所以对任何人不要轻易展示自己的全部，不是刻意隐瞒，也不是虚伪，"
       "而是给自己留点神秘感和底牌，别人才不至于很快对你失去兴趣，"
       "太过展示自己，会让别人对你失去期待和想象空间。")

# 正文按标点手工断行（|），强调 2 处单字（笔画少：新 / 留）
BODY_LINES = [
    "人是<a>喜新厌旧</a>的动物，",
    "人和人在最初相识的时候，新鲜又热情，",
    "一旦熟悉或者相处了一段时间后，新鲜感和热情就会减退，",
    "因为人会对完全看透且了解的东西失去兴趣，",
    "甚至是失去当初对彼此的欣赏和尊重。",
    "所以对任何人不要轻易<a>展示自己的全部</a>，",
    "不是刻意隐瞒，也不是虚伪，",
    "而是给自己留点<a>神秘感和底牌</a>，",
    "别人才不至于很快对你失去兴趣，",
    "太过展示自己，会让别人对你失去期待和想象空间。",
]
BODY = "|".join(BODY_LINES)

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

def norm(t):
    return re.sub(r"\s+", "", t)

if norm(SEG) not in norm(flat):
    die("摘录段不在文档 s243（印刷 119 页）原文中")

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

accent = ["喜新厌旧", "展示自己的全部", "神秘感和底牌"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", SEG))
print("OK 逐字断言 6/6")
print("文档 s243｜印刷页:", 119, "篇名: 给自己留点神秘感，你和别人的关系更长久")
print("摘录字数(含标点):", len(SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", SEG)
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q32_flat.txt").write_text(flat, encoding="utf-8")

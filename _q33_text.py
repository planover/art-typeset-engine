# -*- coding: utf-8 -*-
"""Q33 排产期逐字断言：md 文档《醒与悟1.0.md》锚点 s267（印刷 120 页）『你看不懂的那些潜规则』。

单段 103 字。强调按字数反推（去标点约 90 字，8% 需约 8 字），选 3 处 4 字词共 12 字。
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
    if int(parts[k]) == 267:
        flat = parts[k + 2].split("<a id=")[0].strip()
        break
if not flat:
    print("FAIL: md 文档未找到 s267 篇目")
    sys.exit(1)

SEG = ("成年人一定要明白，别人的答非所问，就是不想说最真实的答案，"
       "只不过不想让你尴尬，敬而远之就是，不想跟你有过多交集，"
       "沉默不语和不回复，就是拒绝，闪烁不定，就是在说谎，"
       "忽冷忽热，就是你偶尔有点用，但又不是很有用。")

# 正文按标点手工断行（|），强调 3 处 4 字词
BODY_LINES = [
    "成年人一定要明白，别人的<a>答非所问</a>，",
    "就是不想说最真实的答案，",
    "只不过不想让你尴尬，",
    "敬而远之就是，不想跟你有过多交集，",
    "<a>沉默不语</a>和不回复，就是拒绝，",
    "闪烁不定，就是在说谎，",
    "<a>忽冷忽热</a>，就是你偶尔有点用，但又不是很有用。",
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

accent = ["答非所问", "沉默不语", "忽冷忽热"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", SEG))
print("OK 逐字断言 6/6")
print("文档 s267｜印刷页:", 120, "篇名: 你看不懂的那些潜规则")
print("摘录字数(含标点):", len(SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", SEG)
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q33_flat.txt").write_text(flat, encoding="utf-8")

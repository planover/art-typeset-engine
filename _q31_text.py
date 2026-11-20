# -*- coding: utf-8 -*-
"""Q31 排产期逐字断言：md 文档《醒与悟1.0.md》锚点 s213（印刷 112 页）『执着，说明你见得太少』。

只取第一段 71 字整段——第二段有 OCR 损坏（「就不谈定了」），按军规不硬修、整段跳过。
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
    if int(parts[k]) == 213:
        flat = parts[k + 2].split("<a id=")[0].strip()
        break
if not flat:
    print("FAIL: md 文档未找到 s213 篇目")
    sys.exit(1)

SEG = ("见得少了，就会特别容易执着，对一个人执着，对一件事执着，对一个东西执着，"
       "当你执着于某个人，某个东西的时候，说明你还未曾拥有，或者无法真正拥有。")

# 正文按标点手工断行（|），强调 2 处
BODY_LINES = [
    "见得<a>少</a>了，就会特别容易执着，",
    "对一个人执着，对一件事执着，对一个东西执着，",
    "当你执着于某个人，某个东西的时候，",
    "说明你还未曾拥有，或者无法真正拥有。",
]
BODY = "|".join(BODY_LINES)

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

def norm(t):
    return re.sub(r"\s+", "", t)

if norm(SEG) not in norm(flat):
    die("摘录段不在文档 s213（印刷 112 页）原文中")

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

accent = ["执着", "未曾拥有"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", SEG))
print("OK 逐字断言 6/6")
print("文档 s213｜印刷页:", 112, "篇名: 执着，说明你见得太少")
print("摘录字数(含标点):", len(SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", SEG)
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q31_flat.txt").write_text(flat, encoding="utf-8")

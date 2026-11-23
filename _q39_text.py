# -*- coding: utf-8 -*-
"""Q39 逐字断言：md 文档《醒与悟2.0.md》锚点 sec-138 段6『吃苦的本质』。
去段首列表编号「7，」（结构性标记非正文），其余逐字保留。
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
    if parts[k] == "sec-138":
        flat = parts[k + 2].split("<a id=")[0].strip()
        break
if not flat:
    print("FAIL: md 文档 2.0 未找到 sec-138")
    sys.exit(1)

SEG = ("核桃，没有华丽的外表，却有充实的大脑。"
       "很多人认为忍受贫穷就是吃苦，这是错的，"
       "<a>吃苦的本质</a>，是长时间为了某个目标<a>聚焦的能力</a>，"
       "放弃娱乐生活，放弃无意义的社交，放弃无意义的消费，"
       "以及在过程中不被理解的孤独。"
       "它本质是一种自控能力，自制能力，和深度思考的能力。")

BODY_LINES = [
    "核桃，没有华丽的外表，",
    "却有充实的大脑。",
    "很多人认为忍受贫穷就是吃苦，这是错的，",
    "<a>吃苦的本质</a>，是长时间为了某个目标<a>聚焦的能力</a>，",
    "放弃娱乐生活，放弃无意义的社交，",
    "放弃无意义的消费，",
    "以及在过程中不被理解的孤独。",
    "它本质是一种自控能力，自制能力，",
    "和深度思考的能力。",
]
BODY = "|".join(BODY_LINES)
CLEAN_SEG = SEG.replace("<a>", "").replace("</a>", "")

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

src_seg = flat.split("\n\n")[6]
if src_seg.startswith("7，"):
    src_seg = src_seg[2:]
if re.sub(r"\s+", "", src_seg) != re.sub(r"\s+", "", CLEAN_SEG):
    die("摘录段与 sec-138 段6 不全等：\n%s\n%s" % (src_seg, CLEAN_SEG))
stripped = BODY.replace("<a>", "").replace("</a>", "").replace("|", "")
if stripped != CLEAN_SEG:
    die("BODY 去标签后与摘录段不全等")
if not CLEAN_SEG.endswith("。"):
    die("摘录未收在原文句号")
hits = [w for w in spec.BAD_WORDS if w in CLEAN_SEG]
if hits:
    die("敏感词命中：%s" % hits)
for i, line in enumerate(BODY_LINES, 1):
    plain = line.replace("<a>", "").replace("</a>", "")
    if plain[0] in spec.PUNCT_LINE_START_BAN:
        die("第%d行行首收尾标点：%s" % (i, plain[0]))
    if plain[-1] in spec.PUNCT_LINE_END_BAN:
        die("第%d行行尾起始标点：%s" % (i, plain[-1]))

accent = ["吃苦的本质", "聚焦的能力"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", CLEAN_SEG))
print("OK 逐字断言 6/6")
print("文档 2.0｜锚点 sec-138 段6｜篇名: 第十三节读书不如学人性")
print("摘录字数(含标点):", len(CLEAN_SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", CLEAN_SEG)
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q39_flat.txt").write_text(flat, encoding="utf-8")

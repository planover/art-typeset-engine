# -*- coding: utf-8 -*-
"""Q37 逐字断言：md 文档《醒与悟2.0.md》锚点 sec-097 段2『人情比钱更贵』。
去段首列表编号「第六，」（结构性标记非正文），其余逐字保留。
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
    if parts[k] == "sec-097":
        flat = parts[k + 2].split("<a id=")[0].strip()
        break
if not flat:
    print("FAIL: md 文档 2.0 未找到 sec-097")
    sys.exit(1)

SEG = ("能用钱解决的事，尽量不要用熟人帮忙，是人都有局限性。"
       "搬家呢，不要找朋友，即使你们关系再好，他们也弄不好。"
       "因为干的好也没有什么好处，就算你给好处，他们又不好意思要。"
       "你记住，他不要钱，这个活他就不可能干的好。"
       "以后遇到问题，直接花钱找陌生人。"
       "因为我们对陌生人的服务不满意，我们可以提出来。"
       "而我们对熟人不能不满意。"
       "能用钱解决的事儿，不要欠人情，因为人情比钱更贵。")

BODY_LINES = [
    "能用钱解决的事，<a>尽量不要用熟人帮忙</a>，",
    "是人都有局限性。",
    "搬家呢，不要找朋友，即使你们关系再好，",
    "他们也弄不好。",
    "因为干的好也没有什么好处，",
    "就算你给好处，他们又不好意思要。",
    "你记住，他不要钱，这个活他就不可能干的好。",
    "以后遇到问题，直接花钱找陌生人。",
    "因为我们对陌生人的服务不满意，我们可以提出来。",
    "而我们对熟人不能不满意。",
    "能用钱解决的事儿，<a>不要欠人情</a>，",
    "因为<a>人情比钱更贵</a>。",
]
BODY = "|".join(BODY_LINES)

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

src_seg = flat.split("\n\n")[2]
if src_seg.startswith("第六，"):
    src_seg = src_seg[3:]
if re.sub(r"\s+", "", src_seg) != re.sub(r"\s+", "", SEG):
    die("摘录段与 sec-097 段2 不全等：\n%s\n%s" % (src_seg, SEG))
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

accent = ["尽量不要用熟人帮忙", "不要欠人情", "人情比钱更贵"]
accent_chars = sum(len(x) for x in accent)
body_chars = len(re.sub(r"[，。、；：？！]", "", SEG))
print("OK 逐字断言 6/6")
print("文档 2.0｜锚点 sec-097 段2｜篇名: 第九节被人尊崇的社交法则")
print("摘录字数(含标点):", len(SEG), " 去标点:", body_chars)
print("强调:", accent, "共", accent_chars, "字  粗估占比 %.2f%%" % (100 * accent_chars / body_chars))
print("正文行:", len(BODY_LINES))
print("段:", SEG)
Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q37_flat.txt").write_text(flat, encoding="utf-8")

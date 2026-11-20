# -*- coding: utf-8 -*-
"""Q27 排产期逐字断言（Q21 血的教训）：摘录段唯一真相源 → in 原页 → BODY 全等 → 句号 → 敏感词 → 避头尾。"""
import re, sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\admin\Documents\tietuai")
from art_typeset import spec

FULL = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\醒与悟1.0_全文.txt")
s = FULL.read_text(encoding="utf-8")
parts = re.split(r"\[第(\d+)页\]", s)
pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
flat = re.sub(r"\s+", "", pages[105])

SEGS = [
    "不分场合，不适当的谦虚，有的时候就是在自降价值，谦虚用错了对象，会被误认为是一种无能和弱，别人不仅不会尊重你，甚至还会看不起你，拿捏你。",
    "如果不是和比自己优秀很多的人沟通，和大部分的人沟通，实际上不怎么需要谦虚，一旦在一开始你就谦虚起来，有些心里没数的人，就会傲慢起来，无礼起来，到后面你的气场再想提起来，就会增加很多难度，过度谦虚有的时候是在降低气场，不利于维护自己威信和利益。",
]

BODY = (
    "不分场合，不适当的谦虚，有的时候就是在<a>自降价值</a>，|"
    "谦虚用错了对象，会被误认为是一种无能和弱，|"
    "别人不仅不会尊重你，甚至还会看不起你，拿捏你。|"
    "如果不是和比自己优秀很多的人沟通，和大部分的人沟通，|"
    "实际上<a>不怎么需要谦虚</a>，一旦在一开始你就谦虚起来，|"
    "有些心里没数的人，就会傲慢起来，无礼起来，|"
    "到后面你的气场再想提起来，就会增加很多难度，|"
    "过度谦虚有的时候是在<a>降低气场</a>，不利于维护自己威信和利益。"
)

for i, seg in enumerate(SEGS, 1):
    assert seg in flat, "段%d 不是原页连续子串" % i
    print("段%d in 原页 True｜%d 字" % (i, len(seg)))

clean = spec.strip_tags(BODY)
target = "".join(SEGS)
assert clean == target, "BODY 与摘录不符：%d vs %d" % (len(clean), len(target))
print("BODY 去标签后逐字全等：%d / %d 字" % (len(clean), len(target)))
assert clean.endswith("。"), "未收在原文句号"
print("句号收尾 OK")
hit = [w for w in spec.BAD_WORDS if w in clean]
assert not hit, "敏感词命中：%s" % hit
print("敏感词零命中 OK")

# 避头尾（与 preflight.check_line_breaks 同口径）
for i, ln in enumerate(BODY.split("|"), 1):
    p = ln.replace("<a>", "").replace("</a>", "").strip()
    assert p[0] not in spec.PUNCT_LINE_START_BAN, "第%d行行首标点" % i
    assert p[-1] not in spec.PUNCT_LINE_END_BAN, "第%d行行尾标点" % i
    print("  行%d %2d字 %s" % (i, len(p), p[:12] + "…"))
print("避头尾 8/8 行通过｜强调 3 处共 %d 字｜占比基线 %.2f%%" %
      (len("自降价值不怎么需要谦虚降低气场"),
       100 * len("自降价值不怎么需要谦虚降低气场") / len(clean)))

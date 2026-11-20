# -*- coding: utf-8 -*-
"""Q27 配方生成器：把 PDF 105 原页全文、逐字摘录、文案与参数写进 presets/q27.json。"""
import json, re
from pathlib import Path

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
FULL = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\醒与悟1.0_全文.txt")
parts = re.split(r"\[第(\d+)页\]", FULL.read_text(encoding="utf-8"))
pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
flat_text = pages[105].strip()

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
EN = (
    "Modesty that is out of place, or modesty offered at the wrong time, is sometimes nothing but a way "
    "of lowering your own value. When it is directed at the wrong person, it will be mistaken for "
    "incompetence and weakness; not only will others fail to respect you, they may even look down on you "
    "and take advantage of you. Unless you are speaking with someone far more accomplished than yourself, "
    "with most people there is in fact little need to be modest. Once you begin by being modest, some "
    "people who have no sense of their own measure will grow arrogant and rude, and later, when you try "
    "to lift your presence again, it becomes far harder. Excessive modesty sometimes lowers that presence, "
    "and does nothing to protect your authority or your interests."
)

ROLES = (["title"] + ["body%d" % i for i in range(1, 9)] +
         ["en%d" % i for i in range(1, 11)] + ["credit"])

recipe = {
    "id": "Q27",
    "no": 95,
    "title": "过度谦虚是自降价值",
    "body": BODY,
    "en": EN,
    "credit": "原作 詹姆斯·麦克尼尔·惠斯勒《夜曲》约1875 · 布面油画",
    "source": {"page": 105, "segments": SEGS, "flat_text": flat_text},
    "meta": {
        "essay": "谦虚需要分场合和情况",
        "artist": "詹姆斯·麦克尼尔·惠斯勒（James Abbott McNeill Whistler, 1834–1903）",
        "painting": "夜曲（Nocturne）",
        "year": "约1875（1870年代）",
        "medium": "布面油画",
        "collection": "美国白宫（White House, Washington, D.C.）／白宫历史协会",
        "license": "Public domain（PD-Art，1903 年卒／1923 年前出版）",
        "layout": "暗底浅字＋标题 wave:32 波纹形变（非纯横排）＋正文八行按标点手工断行，整块右移压进下半纯净深蓝水面、避开左侧钟塔与金色倒影；与 Q26 亮底深字纯横排题跋式全面对跖",
        "accent": "灯火琥珀金 240,158,64 ＋ 2px 细下划线",
        "score": 0,
        "final_png": "",
        "draft": "v1",
        "band_roles": ROLES,
        "body_band_slice": [1, 9],
    },
    "params": {
        "title_font": "mashan",
        "body_font": "song",
        "en_font": "playfair",
        "credit_font": "hei",
        "inline_accent": "<a>",
        "accent_underline": "2:10:255,190,80:230",
        "accent_fill": "255,190,80",
        "fill": "252,246,226",
        "en_fill": "226,216,194",
        "credit_fill": "208,198,176",
        "pos": "lower",
        "align": "center",
        "x_shift": "160",
        "y_shift": "0",
        "wrap": "0",
        "block_width": "66%",
        "en_width": "960",
        "title_size": "80",
        "body_size": "32",
        "en_size": "26",
        "credit_size": "21",
        "title_gap": "56",
        "en_gap": "24",
        "credit_gap": "20",
        "title_lh": "1.20",
        "line_gap": "1.35",
        "scrim": "0",
        "text_grain": "0.10",
        "grain": "0.10",
        "body_align": "left",
        "title_align": "center",
        "warp": "wave:32",
    },
    "pdca": {
        "go": "回 PDF 105（印刷 93）原页取证：篇名「谦虚需要分场合和情况」两段 189 字整段 in 原页、收句号、敏感词零命中；99 玄学整篇、100 两性/阶层表述、101 换环境段（器物名词＋低磁场玄学前缀）、102–104 弱势阶层与真实案件、104 道德绑架篇 OCR 重度损坏、105 从人性角度看问题（与 Q17/Q26 人性链相邻）、105–106 喜欢的本质（与 Q15/Q24 相邻）均整篇/整段跳过",
        "see": {},
        "think": {},
        "iterations": [],
        "score": 0,
        "final_png": "",
    },
}
out = ROOT / "art_typeset" / "presets" / "q27.json"
out.write_text(json.dumps(recipe, ensure_ascii=False, indent=2), encoding="utf-8")
print("written:", out, "| roles:", len(ROLES), "| body chars:", len(BODY.replace("|", "")))

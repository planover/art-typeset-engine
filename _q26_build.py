# -*- coding: utf-8 -*-
"""Q26 配方（终版方向）：Richards《静海》亮底深字，标题单行 + 正文自动折 4 行 + 英文 5 行。"""
import json, re, pymupdf
from pathlib import Path

PDF = r"C:\Users\admin\Documents\tietu\醒与悟1.0.pdf"
OUT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets\q26.json")

SEG = ("永远不要试图去改变一个人，是任何人。因为你改不了，很多人连自己想改变自己都很难，"
       "我们又怎么可能去改变别人呢，改变意味着要对抗一个人的基因，是反人性的，"
       "而人性只能顺应，就好像你改变不了世界和社会，只能调整和适应。")
page_text = pymupdf.open(PDF)[96].get_text("text")
assert SEG in re.sub(r"\s+", "", page_text)
assert SEG.endswith("。")

ACC = ["对抗一个人的基因", "只能顺应"]
BODY = SEG
for a in ACC:
    BODY = BODY.replace(a, f"<a>{a}</a>")
clean = BODY.replace("<a>", "").replace("</a>", "")
assert clean == SEG
BAD = ("风水", "命理", "玄学", "算命", "八字", "印星", "背禄", "阶层", "弱势", "白嫖", "官微信")
assert not [w for w in BAD if w in clean]
print("总字", len(SEG), "| 强调", sum(len(a) for a in ACC), "字")

EN = ("Never try to change a person, anyone. Because you cannot: most people find it hard "
      "enough to change themselves, so how could we change others? Change means fighting a "
      "person's genes, it goes against human nature, and human nature can only be followed, "
      "just as you cannot change the world and society, only adjust and adapt.")
CREDIT = "原作 威廉·特罗斯特·理查兹《静海》1883 · 布面油画"

preset = {
    "id": "Q26",
    "no": 94,
    "title": "你改变不了任何人",
    "body": BODY,
    "en": EN,
    "credit": CREDIT,
    "source": {"page": 97, "segments": [SEG], "flat_text": page_text},
    "meta": {
        "essay": "你改变不了任何人",
        "artist": "威廉·特罗斯特·理查兹（William Trost Richards, 1833–1905）",
        "painting": "静海（Quiet Seascape）",
        "year": "1883",
        "medium": "布面油画",
        "collection": "明尼阿波利斯美术馆（80.67）",
        "license": "Public domain（PD-Art）",
        "layout": "亮底深字：整块压进雾光天空带（std 5–9），标题单行＋正文自动折 4 行＋英文 5 行；与 Q25 暗底奶油字＋标题 arc 全面对跖",
        "accent": "绛朱 186,54,36 ＋ 2px 细下划线",
        "score": 0,
        "final_png": "",
        "draft": "v7",
    },
    "params": {
        "title_font": "xingkai",
        "body_font": "kai",
        "credit_font": "song",
        "en_font": "garamond",
        "inline_accent": "<a>",
        "accent_underline": "2:9:186,54,36:225",
        "pos": "middle",
        "align": "center",
        "x_shift": "0",
        "y_shift": "-256",
        "wrap": "27",
        "block_width": "52%",
        "en_width": "720",
        "title_size": "72",
        "body_size": "28",
        "en_size": "25",
        "credit_size": "20",
        "title_gap": "18",
        "en_gap": "16",
        "credit_gap": "12",
        "title_lh": "1.20",
        "line_gap": "1.33",
        "scrim": "0",
        "fill": "46,38,30",
        "en_fill": "74,62,50",
        "credit_fill": "92,78,62",
        "accent_fill": "186,54,36",
        "text_grain": "0.12",
        "grain": "0.10",
    },
    "pdca": {},
}
OUT.write_text(json.dumps(preset, ensure_ascii=False, indent=2), encoding="utf-8")
print("written", OUT)

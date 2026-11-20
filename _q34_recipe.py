# -*- coding: utf-8 -*-
"""生成 Q34 / 第 102 张配方。

文案：md 文档《醒与悟1.0.md》锚点 s283（印刷 121 页）单段 153 字。
配画：待选画定案后填。
"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("很多人成熟是从放弃做大众眼里的好人开始，并不是说做一个伤害别人的坏人，"
       "而是要选择性的做一个好人。你的好要因人而异，否则你的好不仅会廉价，"
       "还会纵容别人对你的不好。无论你跟人是一个什么样的亲人关系，恋人关系，朋友关系，"
       "还是合作关系，你都必须有策略，有手段的对他好，没策略，没手段的对人好，"
       "最后往往受伤的是自己。")

BODY = ("很多人成熟是从<a>放弃做大众眼里的好人</a>开始，|"
        "并不是说做一个伤害别人的坏人，|"
        "而是要选择性的做一个好人。|"
        "你的好要因人而异，|"
        "否则你的好不仅会廉价，还会纵容别人对你的不好。|"
        "无论你跟人是一个什么样的亲人关系，恋人关系，朋友关系，|"
        "还是合作关系，你都必须<a>有策略，有手段</a>的对他好，|"
        "没策略，没手段的对人好，最后往往受伤的是自己。")

EN = ("Maturity often begins when you stop trying to be everyone's idea of a good person — "
      "not by becoming cruel, but by choosing whom to be good to. Your kindness should depend "
      "on the person; otherwise it becomes cheap, and quietly teaches them to treat you badly. "
      "Whatever the relationship — family, love, friendship, or work — love with strategy, "
      "with boundaries. Goodness without strategy only hurts you in the end.")

ROLES_PLACEHOLDER = ["title"] + ["body%d" % i for i in range(1, 9)] + ["en%d" % i for i in range(1, 5)] + ["credit"]
BODY_SLICE = [1, 9]

ARTIST = "伊萨克·列维坦（Isaac Levitan, 1860–1900）"
PAINTING = "伏尔加河（Волга / Volga）"
YEAR = "1889"
MEDIUM = "布面油画"
COLLECTION = "普廖斯列维坦故居博物馆藏"
LICENSE = "Public domain（PD-Art-two-auto，1900 年卒）"
CREDIT = "原作 %s《%s》%s · %s" % (ARTIST, PAINTING, YEAR, MEDIUM)
DARK = False

PARAMS = {
    "title_font": "song",
    "body_font": "serif",
    "en_font": "garamond",
    "credit_font": "kai",
    "inline_accent": "<a>",
    "accent_underline": "1:9:168,52,32:200",
    "accent_fill": "168,52,32",
    "fill": "18,16,14" if not DARK else "244,236,212",
    "en_fill": "26,22,18" if not DARK else "232,224,200",
    "credit_fill": "28,24,20" if not DARK else "226,216,190",
    "pos": "top",
    "align": "center",
    "x_shift": "0",
    "y_shift": "40",
    "wrap": "0",
    "block_width": "80%",
    "en_width": "1240",
    "title_size": "82",
    "body_size": "34",
    "en_size": "26",
    "credit_size": "21",
    "title_gap": "30",
    "en_gap": "18",
    "credit_gap": "26",
    "title_lh": "1.16",
    "line_gap": "1.20",
    "scrim": "0",
    "text_grain": "0.05",
    "grain": "0.0",
    "body_align": "left",
    "title_align": "center",
}

data = {
    "id": "Q34",
    "no": 102,
    "title": "想成熟，从放弃做好人开始",
    "body": BODY,
    "en": EN,
    "credit": CREDIT,
    "source": {
        "doc": "醒与悟1.0.md",
        "anchor": "s283",
        "page": 121,
        "segments": [SEG],
        "flat_text": (TMP / "q34_flat.txt").read_text(encoding="utf-8"),
    },
    "meta": {
        "essay": "想成熟，从放弃做好人开始",
        "artist": ARTIST,
        "painting": PAINTING,
        "year": YEAR,
        "medium": MEDIUM,
        "collection": COLLECTION,
        "license": LICENSE,
        "layout": ("亮底深字＋文字压上半幅极净浅色天空（y200–900 中位 170–198、std 8–15），"
                   "下半保留孤帆与辽阔河面——『放弃讨好、有边界地航行』的视觉双关："
                   "船不依赖任何人，自己选择方向；"
                   "华文中宋标题＋思源宋正文八行按标点手工断行＋Garamond 英文＋霞鹜文楷款识四体混排；"
                   "与 Q33 淡金晨雾／黑体／中部块全面对跖"),
        "accent": "绛朱 168,52,32 ＋ 1px 发丝下划线",
        "score": 0,
        "final_png": "",
        "draft": "v1",
        "band_roles": ROLES_PLACEHOLDER,
        "body_band_slice": BODY_SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": "从 md 文档《醒与悟1.0.md》锚点 s268（印刷 121 页）起筛除：s268 官杀术语、"
              "s271 过于听话（命理词）、s274/s285 离开与价值（与 Q15/Q16/Q26/Q30 价值链撞）、"
              "s275 向上社交（阶层词）、s282 结婚对象（八字词）、s284 越现实（阶层词）、"
              "s286 人一主动（与 Q32 神秘感链撞）、s287 没目的（弱势词）、s288 钱保护系统（风水词）、"
              "s292 穷人命运（弱势词）、s293 讨厌勇气（八字词）、s294 蠢好人（弱势词）整篇跳过；"
              "s283 放弃做好人 153 字定稿（零 OCR 损坏），逐字断言 6/6",
        "see": {},
        "think": "",
        "iterations": 0,
        "score": 0,
        "final_png": "",
    },
}

out = ROOT / "q34.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out)
print("body chars:", len(SEG), "en words:", len(EN.split()))

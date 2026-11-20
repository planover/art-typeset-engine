# -*- coding: utf-8 -*-
"""生成 Q30 / 第 98 张配方。

文案：md 文档《醒与悟1.0.md》锚点 s186（印刷 117 页）「高质量的关系」95 字。
配画：待选画定案后填 ARTIST/PAINTING/YEAR/MEDIUM/COLLECTION/LICENSE。
版式：待选画定案后填 PARAMS。
"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("所有让其中一方觉得委屈的关系，都是错误的关系，高质量的关系应该是让自己获益的同时，"
       "也不让对方吃亏，无论生意还是恋爱，如果不是，那说明其中一方并没有把另一方视为重要的人，"
       "或者只想做一锤子买卖。")

BODY = ("所有让其中一方觉得<a>委屈</a>的关系，|"
        "都是错误的关系，|"
        "高质量的关系应该是让自己<a>获益</a>的同时，|"
        "也不让对方吃亏，|"
        "无论生意还是恋爱，如果不是，|"
        "那说明其中一方并没有把另一方视为重要的人，|"
        "或者只想做<a>一锤子买卖</a>。")

EN = ("Any relationship in which one side feels wronged is the wrong relationship. "
      "A high-quality relationship should benefit you while leaving the other side no worse off — "
      "in business or in love, if it does not, it means one of you does not regard the other as truly important, "
      "or is simply out for a one-time deal.")

ROLES = (["title"] + ["body%d" % i for i in range(1, 8)] +
         ["en%d" % i for i in range(1, 4)] + ["credit"])
BODY_SLICE = [1, 8]

ARTIST = "费迪南德·霍德勒（Ferdinand Hodler, 1853–1918）"
PAINTING = "图恩湖的对称倒影（Thunersee mit symmetrischer Spiegelung）"
YEAR = "1909"
MEDIUM = "布面油画"
COLLECTION = "私人藏（artbook 图版，Wikidata Q117599181）"
LICENSE = "Public domain（PD-Art / PD-old-auto-expired，1918 年卒）"
CREDIT = "原作 费迪南德·霍德勒《图恩湖的对称倒影》1909 · 布面油画"
DARK = False

PARAMS = {
    "title_font": "smiley",
    "body_font": "serif",
    "en_font": "playfair",
    "credit_font": "kai",
    "inline_accent": "<a>",
    "accent_underline": "2:9:178,52,32:230",
    "accent_fill": "178,52,32",
    "fill": "18,24,34" if not DARK else "240,228,202",
    "en_fill": "24,30,42" if not DARK else "228,216,192",
    "credit_fill": "22,28,38" if not DARK else "220,208,184",
    "pos": "lower",
    "align": "center",
    "x_shift": "0",
    "y_shift": "60",
    "wrap": "0",
    "block_width": "82%",
    "en_width": "1260",
    "title_size": "84",
    "body_size": "34",
    "en_size": "26",
    "credit_size": "21",
    "title_gap": "32",
    "en_gap": "18",
    "credit_gap": "24",
    "title_lh": "1.16",
    "line_gap": "1.16",
    "scrim": "0",
    "text_grain": "0.05",
    "grain": "0.0",
    "body_align": "left",
    "title_align": "center",
}

data = {
    "id": "Q30",
    "no": 98,
    "title": "高质量的关系",
    "body": BODY,
    "en": EN,
    "credit": CREDIT,
    "source": {
        "doc": "醒与悟1.0.md",
        "anchor": "s186",
        "page": 117,
        "segments": [SEG],
        "flat_text": (TMP / "q30_flat.txt").read_text(encoding="utf-8"),
    },
    "meta": {
        "essay": "高质量的关系",
        "artist": ARTIST,
        "painting": PAINTING,
        "year": YEAR,
        "medium": MEDIUM,
        "collection": COLLECTION,
        "license": LICENSE,
        "layout": ("亮底深字＋文字压下半浅蓝水面，与上半山峦形成上下镜像呼应——"
                   "对称倒影即「高质量关系双向映照/互惠平衡」的视觉双关；"
                   "得意黑标题＋思源宋正文七行按标点手工断行＋Playfair 英文＋霞鹜文楷款识四体混排；"
                   "与 Q29 亮底上半横排、行楷波纹全面对跖"),
        "accent": "绛朱 178,52,32 ＋ 1px 发丝下划线",
        "score": 0,
        "final_png": "",
        "draft": "v1",
        "band_roles": ROLES,
        "body_band_slice": BODY_SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": "从 md 文档《醒与悟1.0.md》锚点 s176 起筛除：s176 弱才喜欢抱团（八字/弱势词）、"
              "s177 取舍（与 Q29 选择链撞）、s178 本性难移（家暴/犯罪负面）、s179 做礼物别做废物（废物标签攻击）、"
              "s180 想赚钱和想有钱（风水/阶层词）、s182 背禄体质/s188 命运结构/s192 朋友圈价值（命理词）、"
              "s183 男女阴阳身份（两性）、s189 最有效的拒绝（蠢人标签）、s199 量力而为（弱者/廉价）整篇跳过；"
              "s186 高质量的关系 95 字定稿，逐字断言 6/6",
        "see": {},
        "think": "",
        "iterations": 0,
        "score": 0,
        "final_png": "",
    },
}

out = ROOT / "q30.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out)
print("roles:", len(ROLES), "body chars:", len(SEG), "en words:", len(EN.split()))

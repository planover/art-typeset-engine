# -*- coding: utf-8 -*-
"""生成 Q29 / 第 97 张配方。

文案：md 文档《醒与悟1.0.md》锚点 s175（印刷 110 页）「选择与被选择」84 字。
配画：待选画定案后填 ARTIST/PAINTING/YEAR/MEDIUM/COLLECTION/LICENSE。
版式：待选画定案后填 PARAMS。
"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("人的一生都要面对选择和被选择，能够被选择是幸运，"
       "而有的时候不被选择也是一种幸运，正因为没有被选择，才遇到了更好的选择，"
       "所以坦然的面对选择与被选择，因为那都是不同的机会。")

BODY = ("人的一生都要面对<a>选择和被选择</a>，|"
        "能够被选择是幸运，|"
        "而有的时候不被选择也是一种幸运，|"
        "正因为没有被选择，才遇到了<a>更好</a>的选择，|"
        "所以坦然的面对选择与被选择，|"
        "因为那都是不同的机会。")

EN = ("In life we all have to face being chosen and being passed over. To be chosen is a kind of luck, "
      "and sometimes, not being chosen is a kind of luck too — precisely because we were not chosen, "
      "we met a better choice. So face being chosen and being passed over with equanimity, "
      "for they are simply different opportunities.")

# 首渲 find_bands 实测 12 层：title + body1-6 + en1-4 + credit
ROLES = (["title"] + ["body%d" % i for i in range(1, 7)] +
         ["en%d" % i for i in range(1, 4)] + ["credit"])

ARTIST = "托马斯·希尔（Thomas Hill, 1825–1908）"
PAINTING = "优胜美地，新娘面纱瀑布（Yosemite, Bridal Veil Falls）"
YEAR = "1895"
MEDIUM = "布面油画"
COLLECTION = "美国白宫藏（白宫历史协会，977.1331.1）"
LICENSE = "Public domain（PD-Art / PD-old-auto-expired，1908 年卒）"
CREDIT = "原作 托马斯·希尔《优胜美地，新娘面纱瀑布》1895 · 布面油画"
DARK = False

PARAMS = {
    "title_font": "xingkai",
    "body_font": "sans",
    "en_font": "garamond",
    "credit_font": "song",
    "inline_accent": "<a>",
    "accent_underline": "1:9:190,60,50:220",
    "accent_fill": "190,60,50",
    "fill": "38,34,30" if not DARK else "244,234,208",
    "en_fill": "50,44,38" if not DARK else "230,220,196",
    "credit_fill": "52,46,40" if not DARK else "222,212,188",
    "pos": "top",
    "align": "center",
    "x_shift": "0",
    "y_shift": "20",
    "wrap": "0",
    "block_width": "78%",
    "en_width": "1260",
    "title_size": "76",
    "body_size": "30",
    "en_size": "25",
    "credit_size": "21",
    "title_gap": "16",
    "en_gap": "8",
    "credit_gap": "26",
    "title_lh": "1.10",
    "line_gap": "1.05",
    "scrim": "0",
    "text_grain": "0.05",
    "grain": "0.0",
    "body_align": "left",
    "title_align": "center",
    "warp": "wave:14",
    "warp_body": "off",
}

data = {
    "id": "Q29",
    "no": 97,
    "title": "选择与被选择",
    "body": BODY,
    "en": EN,
    "credit": CREDIT,
    "source": {
        "doc": "醒与悟1.0.md",
        "anchor": "s175",
        "page": 110,
        "segments": [SEG],
        "flat_text": (TMP / "q29_flat.txt").read_text(encoding="utf-8"),
    },
    "meta": {
        "essay": "选择与被选择",
        "artist": ARTIST,
        "painting": PAINTING,
        "year": YEAR,
        "medium": MEDIUM,
        "collection": COLLECTION,
        "license": LICENSE,
        "layout": ("亮底深字＋标题轻度波纹（warp wave:14，仅标题形变，正文保持横排）区别于 Q28 整块弓形；"
                   "行楷标题＋思源黑正文六行按标点手工断行＋EB Garamond 英文＋华文中宋款识四体混排；"
                   "文字压上半幅浅色天空（底图预先做大羽化柔光烘制消解云层纹理，中位 218–223、std 3.6–23），"
                   "下方两峰之间的开阔谷口、瀑布与独行者完整保留——未走的路即「更好的选择」；"
                   "与 Q28 亮底弓形在标题手法与字体上拉开"),
        "accent": "绛朱 190,60,50 ＋ 1px 发丝下划线",
        "score": 0,
        "final_png": "",
        "draft": "v1",
        "band_roles": ROLES,
        "body_band_slice": [1, 7],
    },
    "params": PARAMS,
    "pdca": {
        "go": "从 md 文档《醒与悟1.0.md》锚点 s166（印刷 106）起筛除：s166 学会爱自己（与 Q15/Q27 相邻）、"
              "s167 同情心太强（弱势词）、s169 顺应人性（与 Q26 相邻）、s170 配得感（弱势词）、s171 女孩子青春（两性贬低）、"
              "s176 弱才喜欢抱团（八字/弱势词）、s180 想赚钱想有钱（风水/阶层词）、s181 气场少说话（与 Q27 相邻）、"
              "s182 背禄体质/ s188 命运结构（命理词）、s192 朋友圈价值（命理词）整篇跳过；"
              "s175 选择与被选择 84 字定稿，逐字断言 6/6",
        "see": {},
        "think": "",
        "iterations": 0,
        "score": 0,
        "final_png": "",
    },
}

out = ROOT / "q29.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out)
print("roles:", len(ROLES))
print("body chars:", len(SEG), "en words:", len(EN.split()))

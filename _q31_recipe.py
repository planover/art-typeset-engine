# -*- coding: utf-8 -*-
"""生成 Q31 / 第 99 张配方。

文案：md 文档《醒与悟1.0.md》锚点 s213（印刷 112 页）第一段 71 字。
配画：待选画定案后填。
版式：待选画定案后填（按 Q29/Q30 教训：文字块≥78% 满足 verify x 基准，柔光烘底预案）。
"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("见得少了，就会特别容易执着，对一个人执着，对一件事执着，对一个东西执着，"
       "当你执着于某个人，某个东西的时候，说明你还未曾拥有，或者无法真正拥有。")

BODY = ("见得<a>少</a>了，就会特别容易执着，|"
        "对一个人执着，对一件事执着，对一个东西执着，|"
        "当你执着于某个人，某个东西的时候，|"
        "说明你还未曾拥有，或者无法真正拥有。")

EN = ("Seeing too little, one clings easily — to a person, to a thing, to an outcome. "
      "To cling to someone or something is to admit you have never truly had it, or never can. "
      "Once you have seen more and possessed more, you no longer hold on so tightly; "
      "the more you have seen, the calmer you become.")

ROLES_PLACEHOLDER = ["title"] + ["body%d" % i for i in range(1, 5)] + ["en%d" % i for i in range(1, 4)] + ["credit"]
BODY_SLICE = [1, 5]

ARTIST = "托马斯·费恩利（Thomas Fearnley, 1802–1842）"
PAINTING = "风景习作（Landscape study）"
YEAR = "1833"
MEDIUM = "纸本油画"
COLLECTION = "挪威国家美术馆藏（NG.M.02598）"
LICENSE = "Public domain（PD-Art / PD-old-auto-expired，1842 年卒；馆藏照片 CC BY 4.0）"
CREDIT = "原作 %s《%s》%s · %s" % (ARTIST, PAINTING, YEAR, MEDIUM)
DARK = False

PARAMS = {
    "title_font": "mashan",
    "body_font": "serif",
    "en_font": "times",
    "credit_font": "kai",
    "inline_accent": "<a>",
    "accent_underline": "0:9:136,84,64:140",
    "accent_fill": "136,84,64",
    "fill": "16,14,12" if not DARK else "244,234,208",
    "en_fill": "22,18,14" if not DARK else "230,220,196",
    "credit_fill": "26,22,18" if not DARK else "222,212,188",
    "pos": "top",
    "align": "center",
    "x_shift": "0",
    "y_shift": "40",
    "wrap": "0",
    "block_width": "80%",
    "en_width": "1200",
    "title_size": "84",
    "body_size": "36",
    "en_size": "27",
    "credit_size": "21",
    "title_gap": "32",
    "en_gap": "18",
    "credit_gap": "36",
    "title_lh": "1.16",
    "line_gap": "1.22",
    "scrim": "0",
    "text_grain": "0.05",
    "grain": "0.0",
    "body_align": "left",
    "title_align": "center",
}

data = {
    "id": "Q31",
    "no": 99,
    "title": "执着，说明你见得太少",
    "body": BODY,
    "en": EN,
    "credit": CREDIT,
    "source": {
        "doc": "醒与悟1.0.md",
        "anchor": "s213",
        "page": 112,
        "segments": [SEG],
        "flat_text": (TMP / "q31_flat.txt").read_text(encoding="utf-8"),
    },
    "meta": {
        "essay": "执着，说明你见得太少",
        "artist": ARTIST,
        "painting": PAINTING,
        "year": YEAR,
        "medium": MEDIUM,
        "collection": COLLECTION,
        "license": LICENSE,
        "layout": ("亮底深字＋文字压上半幅极净浅色天空（y200–1000 std 8–12，天然纯净无需烘底）"
                   "＋下半保留极简地平线、远山、水面与疏落树丛——「未见全貌时的执着 vs 见多后的坦然」的视觉双关；"
                   "马善政毛笔标题＋思源宋正文四行按标点手工断行＋Times 英文＋霞鹜文楷款识四体混排；"
                   "与 Q30 深蓝水面镜像／下半块／得意黑标题全面对跖"),
        "accent": "绛朱 178,52,32 ＋ 1px 发丝下划线",
        "score": 0,
        "final_png": "",
        "draft": "v1",
        "band_roles": ROLES_PLACEHOLDER,
        "body_band_slice": BODY_SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": "从 md 文档《醒与悟1.0.md》锚点 s187（印刷 117）起筛除：s187 姿态（与 Q25/Q27 撞链）、"
              "s188 命运结构（八字词）、s189 最有效的拒绝（蠢人标签）、s190 厉害比对他好重要（与 Q27/Q30 撞链）、"
              "s192 朋友圈价值（命理词）、s197 情绪（阶层词）、s199 量力而为（弱者/廉价词）、"
              "s200 不被情绪利用（与 Q26 撞）、s202 受气体质（与 Q27 撞）、"
              "s209 姿态放很低（脑残粉标签）、s212 费力不讨好（拯救情结）、s214 隐性价值（两性标签）整篇跳过；"
              "s213 第一段 71 字定稿（第二段 OCR 损坏整段跳过），逐字断言 6/6",
        "see": {},
        "think": "",
        "iterations": 0,
        "score": 0,
        "final_png": "",
    },
}

out = ROOT / "q31.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out)
print("body chars:", len(SEG), "en words:", len(EN.split()))

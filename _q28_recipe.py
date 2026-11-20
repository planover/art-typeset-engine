# -*- coding: utf-8 -*-
"""生成 Q28 / 第 96 张配方。

文案：md 文档《醒与悟1.0.md》锚点 s165（印刷 106 页）「没那么多三观一致」85 字。
配画：Winslow Homer《Boys Fishing, Gloucester Harbor》1880 纸本水彩（第 48 位新画家）。
版式：亮底深字 + 短文本系列首次「整块弓形形变」(warp_body on)，文字压上半纸白，
      两个男孩与倒影完整留在下方；与 Q27 暗底浅字下半块全面对跖。
"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("其实没有那么多所谓三观一致的人，人们只不过是为了自己各种各样的目的，"
       "把那个当下的自己伪装成了你的同类，让你觉得遇到了三观一致，很合得来的人，"
       "实际上你们是完全不同的两类人。")

BODY = ("其实没有那么多所谓<a>三观一致</a>的人，|"
        "人们只不过是为了自己各种各样的目的，|"
        "把那个当下的自己伪装成了你的同类，|"
        "让你觉得遇到了三观一致，很合得来的人，|"
        "实际上你们是<a>完全不同</a>的两类人。")

EN = ("In truth, there are not so many people who truly share your values. "
      "People simply, for all kinds of their own purposes, disguise the self they happen "
      "to be at that moment as someone of your own kind, so that you believe you have met "
      "a person who sees the world as you do and gets along with you effortlessly, when in "
      "fact the two of you are entirely different kinds of people.")

# 首渲前按预估给 roles；首渲后用 find_bands 实测层数回填（Q24/Q25/Q27 三次教训）
ROLES = (["title"] + ["body%d" % i for i in range(1, 6)] +
         ["en%d" % i for i in range(1, 7)] + ["credit"])

data = {
    "id": "Q28",
    "no": 96,
    "title": "没那么多三观一致",
    "body": BODY,
    "en": EN,
    "credit": "原作 温斯洛·霍默《男孩垂钓，格洛斯特港》1880 · 纸本水彩",
    "source": {
        "doc": "醒与悟1.0.md",
        "anchor": "s165",
        "page": 106,
        "segments": [SEG],
        "flat_text": (TMP / "q28_flat.txt").read_text(encoding="utf-8"),
    },
    "meta": {
        "essay": "没那么多三观一致",
        "artist": "温斯洛·霍默（Winslow Homer, 1836–1910）",
        "painting": "男孩垂钓，格洛斯特港（Boys Fishing, Gloucester Harbor）",
        "year": "1880",
        "medium": "纸本水彩",
        "collection": "私人藏（2018 纽约苏富比 lot 33；Commons 图为苏富比拍卖图录）",
        "license": "Public domain（PD-Art / PD-old-auto-expired，1910 年卒）",
        "layout": "亮底深字＋短文本系列首次整块弓形形变（warp arc:-34 且 warp_body on）；"
                  "得意黑斜体标题＋思源宋正文五行按标点手工断行＋Inter 英文＋文楷款识四体混排；"
                  "文字压上半纸白留白，两个背向而坐的男孩、帆船与倒影完整留在下半幅；"
                  "与 Q27 暗底浅字、下半块、毛笔标题全面对跖",
        "accent": "赭朱 168,52,32 ＋ 1px 发丝下划线（短文本按占比反推，共 8 字）",
        "score": 0,
        "final_png": "",
        "draft": "v1",
        "band_roles": ROLES,
        "body_band_slice": [1, 6],
    },
    "params": {
        "title_font": "smiley",
        "body_font": "serif",
        "en_font": "inter",
        "credit_font": "kai",
        "inline_accent": "<a>",
        "accent_underline": "2:9:168,52,32:220",
        "accent_fill": "168,52,32",
        "fill": "40,36,32",
        "en_fill": "58,52,46",
        "credit_fill": "52,46,40",
        "pos": "top",
        "align": "center",
        "x_shift": "-110",
        "y_shift": "30",
        "wrap": "0",
        "block_width": "64%",
        "en_width": "980",
        "title_size": "84",
        "body_size": "40",
        "en_size": "27",
        "credit_size": "21",
        "title_gap": "34",
        "en_gap": "12",
        "credit_gap": "26",
        "title_lh": "1.18",
        "line_gap": "1.20",
        "scrim": "0",
        "text_grain": "0.06",
        "grain": "0.06",
        "body_align": "left",
        "title_align": "center",
        "warp": "arc:-34",
        "warp_body": "off",
    },
    "pdca": {
        "go": "从 md 文档《醒与悟1.0.md》印刷 94 页(s148)起筛除：s148 位置决定价值（阶层/职业贬低）＋喜欢的本质续段（主题相邻）整篇跳过；"
              "s149 强者的兽性（基因决定命运与 Q26 相邻）跳过；s150–s152 太完美/欲望/执念跳过；"
              "s153 真话给对的人、s154 别问忙吗（与 Q27 自降价值相邻）跳过；s155–s159 落后地方/蠢人/得势失势/弱势思维敏感词整篇跳过；"
              "s161 太清高影响财运、s163 悟透命理玄学＋s164 先卖出去再说（命理玄学＋与 Q22 万事俱备主题撞）跳过；"
              "s165 定稿没那么多三观一致，85 字一段，md 文档锚点逐字断言 6/6",
        "see": {},
        "think": "",
        "iterations": 0,
        "score": 0,
        "final_png": "",
    },
}

out = ROOT / "q28.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out)
print("roles:", len(ROLES), ROLES)
print("body chars:", len(SEG), "en words:", len(EN.split()))

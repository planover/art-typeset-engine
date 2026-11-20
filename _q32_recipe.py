# -*- coding: utf-8 -*-
"""生成 Q32 / 第 100 张配方（里程碑）。

文案：md 文档《醒与悟1.0.md》锚点 s243（印刷 119 页）两段 174 字。
配画：待选画定案后填。
"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("人是喜新厌旧的动物，人和人在最初相识的时候，新鲜又热情，"
       "一旦熟悉或者相处了一段时间后，新鲜感和热情就会减退，"
       "因为人会对完全看透且了解的东西失去兴趣，甚至是失去当初对彼此的欣赏和尊重。"
       "所以对任何人不要轻易展示自己的全部，不是刻意隐瞒，也不是虚伪，"
       "而是给自己留点神秘感和底牌，别人才不至于很快对你失去兴趣，"
       "太过展示自己，会让别人对你失去期待和想象空间。")

BODY = ("人是<a>喜新厌旧</a>的动物，|"
        "人和人在最初相识的时候，新鲜又热情，|"
        "一旦熟悉或者相处了一段时间后，新鲜感和热情就会减退，|"
        "因为人会对完全看透且了解的东西失去兴趣，|"
        "甚至是失去当初对彼此的欣赏和尊重。|"
        "所以对任何人不要轻易<a>展示自己的全部</a>，|"
        "不是刻意隐瞒，也不是虚伪，|"
        "而是给自己留点<a>神秘感和底牌</a>，|"
        "别人才不至于很快对你失去兴趣，|"
        "太过展示自己，会让别人对你失去期待和想象空间。")

EN = ("People are naturally drawn to novelty. At first acquaintance, everything feels fresh and warm; "
      "but once familiarity sets in, that freshness fades — we lose interest in what we think we fully "
      "understand, and even the admiration we once felt begins to slip. So never show everything of "
      "yourself at once. This is not deception, nor dishonesty; it is leaving a little mystery and "
      "something held back, so others do not lose interest too quickly. Give too much of yourself away, "
      "and you leave them nothing to anticipate, nothing to imagine.")

ROLES_PLACEHOLDER = ["title"] + ["body%d" % i for i in range(1, 11)] + ["en%d" % i for i in range(1, 4)] + ["credit"]
BODY_SLICE = [1, 11]

ARTIST = "阿尔希普·库因哲（Arkhip Kuindzhi, 1841–1910）"
PAINTING = "第聂伯河上的夜月"
YEAR = "1882"
MEDIUM = "布面油画"
COLLECTION = "俄罗斯国家博物馆藏"
LICENSE = "Public domain（PD-old-auto-expired，1910 年卒）"
CREDIT = "原作 %s《%s》%s · %s" % (ARTIST, PAINTING, YEAR, MEDIUM)
DARK = True

PARAMS = {
    "title_font": "qingke",
    "body_font": "serif",
    "en_font": "garamond",
    "credit_font": "kai",
    "inline_accent": "<a>",
    "accent_underline": "1:9:168,52,32:180",
    "accent_fill": "168,52,32",
    "fill": "20,18,16" if not DARK else "246,238,214",
    "en_fill": "26,22,18" if not DARK else "234,226,202",
    "credit_fill": "30,26,22" if not DARK else "226,216,190",
    "pos": "middle",
    "align": "center",
    "x_shift": "0",
    "y_shift": "0",
    "wrap": "0",
    "block_width": "76%",
    "en_width": "1340",
    "title_size": "82",
    "body_size": "32",
    "en_size": "25",
    "credit_size": "21",
    "title_gap": "34",
    "en_gap": "16",
    "credit_gap": "26",
    "title_lh": "1.16",
    "line_gap": "1.16",
    "scrim": "0",
    "text_grain": "0.05",
    "grain": "0.0",
    "body_align": "left",
    "title_align": "center",
}

data = {
    "id": "Q32",
    "no": 100,
    "title": "给自己留点神秘感",
    "body": BODY,
    "en": EN,
    "credit": CREDIT,
    "source": {
        "doc": "醒与悟1.0.md",
        "anchor": "s243",
        "page": 119,
        "segments": [SEG],
        "flat_text": (TMP / "q32_flat.txt").read_text(encoding="utf-8"),
    },
    "meta": {
        "essay": "给自己留点神秘感，你和别人的关系更长久",
        "artist": ARTIST,
        "painting": PAINTING,
        "year": YEAR,
        "medium": MEDIUM,
        "collection": COLLECTION,
        "license": LICENSE,
        "layout": ("暗底浅字（中位 1 的纯净夜河）+ 文字压中部纯黑河面 y600–1400，"
                   "上方月轮与云层、下方远岸篝火完整保留——『留点神秘感/底牌』的视觉双关："
                   "月光只照亮局部，其余隐在暗处，正是想象空间；"
                   "庆科黄油体标题＋思源宋正文十行按标点手工断行＋EB Garamond 英文＋霞鹜文楷款识四体混排；"
                   "与 Q31 亮底空旷／毛笔标题／上半块全面对跖，第 100 张里程碑"),
        "accent": "绛朱 168,52,32 ＋ 1px 发丝下划线",
        "score": 0,
        "final_png": "",
        "draft": "v1",
        "band_roles": ROLES_PLACEHOLDER,
        "body_band_slice": BODY_SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": "从 md 文档《醒与悟1.0.md》锚点 s214（印刷 112 页）起筛除：s214 隐性价值（两性标签）、"
              "s216 好的关系相互旺（与 Q30 撞链）、s217 短视（阶层表述）、s219 人品（OCR 损坏）、"
              "s221 值钱的话/ s226 利他思维/ s227 做桩思维（术数词与 Q15/Q16 撞链）、"
              "s230 巨婴思维（可悲幼稚标签）、s241 冷与独（与 Q27 撞链）、s242 你越在乎（OCR 重度损坏）、"
              "s245 改命（风水命理词）整篇跳过；s243 两段 174 字定稿（零 OCR 损坏），逐字断言 6/6",
        "see": {},
        "think": "",
        "iterations": 0,
        "score": 0,
        "final_png": "",
    },
}

out = ROOT / "q32.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out)
print("body chars:", len(SEG), "en words:", len(EN.split()))

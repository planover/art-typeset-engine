# -*- coding: utf-8 -*-
"""生成 Q39 / 第 107 张配方。文案：md 文档《醒与悟2.0.md》锚点 sec-138 段6 124 字。"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("核桃，没有华丽的外表，却有充实的大脑。"
       "很多人认为忍受贫穷就是吃苦，这是错的，"
       "吃苦的本质，是长时间为了某个目标聚焦的能力，"
       "放弃娱乐生活，放弃无意义的社交，放弃无意义的消费，"
       "以及在过程中不被理解的孤独。"
       "它本质是一种自控能力，自制能力，和深度思考的能力。")

BODY = ("核桃，没有华丽的外表，|"
        "却有充实的大脑。|"
        "很多人认为忍受贫穷就是吃苦，这是错的，|"
        "<a>吃苦的本质</a>，是长时间为了某个目标<a>聚焦的能力</a>，|"
        "放弃娱乐生活，放弃无意义的社交，|"
        "放弃无意义的消费，|"
        "以及在过程中不被理解的孤独。|"
        "它本质是一种自控能力，自制能力，|"
        "和深度思考的能力。")

EN = ("A walnut has no flashy shell, yet inside is a solid brain. Many people think enduring "
      "poverty is what it means to suffer — but that's wrong. The essence of hardship is the "
      "ability to stay focused on one goal for a long time: giving up entertainment, meaningless "
      "socializing and pointless spending, and bearing the misunderstanding and loneliness along "
      "the way. At its core, it is self-control, discipline, and the capacity for deep thought.")

ROLES = ["title"] + ["body%d" % i for i in range(1, 10)] + ["en%d" % i for i in range(1, 5)] + ["credit"]
SLICE = [1, 10]
ARTIST = "让-西梅翁·夏尔丹（Jean Siméon Chardin, 1699–1779）"; PAINTING = "水果与陶罐静物"; YEAR = "18世纪"; MEDIUM = "布面油画"
COLLECTION = "鹿特丹博伊曼斯·范伯宁恩博物馆藏"; LICENSE = "Public domain（PD-old-auto-expired，1779 年卒）"
CREDIT = "原作 %s《%s》%s · %s" % (ARTIST, PAINTING, YEAR, MEDIUM)
DARK = True

PARAMS = {
    "title_font": "song", "body_font": "serif", "en_font": "times", "credit_font": "kai",
    "inline_accent": "<a>", "accent_underline": "1:9:168,52,32:200", "accent_fill": "168,52,32",
    "fill": "18,16,14" if not DARK else "244,236,212",
    "en_fill": "26,22,18" if not DARK else "232,224,200",
    "credit_fill": "28,24,20" if not DARK else "226,216,190",
    "pos": "top", "align": "center", "x_shift": "0", "y_shift": "40", "wrap": "0",
    "block_width": "80%", "en_width": "1240",
    "title_size": "82", "body_size": "34", "en_size": "26", "credit_size": "21",
    "title_gap": "30", "en_gap": "18", "credit_gap": "26",
    "title_lh": "1.16", "line_gap": "1.20", "scrim": "0", "text_grain": "0.05", "grain": "0.0",
    "body_align": "left", "title_align": "center",
}

data = {
    "id": "Q39", "no": 107, "title": "吃苦的本质",
    "body": BODY, "en": EN, "credit": CREDIT,
    "source": {"doc": "醒与悟2.0.md", "anchor": "sec-138", "page": 138,
               "segments": [SEG], "flat_text": (TMP / "q39_flat.txt").read_text(encoding="utf-8")},
    "meta": {
        "essay": "第十三节读书不如学人性 · 段6", "artist": ARTIST, "painting": PAINTING,
        "year": YEAR, "medium": MEDIUM, "collection": COLLECTION, "license": LICENSE,
        "layout": ("暗底浅字＋文字压上半幅极净暗背景（y200–800 中位 21–32、std 7–12），"
                   "下半几只苹果与一只陶罐——夏尔丹式极简静物即『核桃没有华丽外表却有充实大脑』："
                   "朴素器物里藏着专注与自制的分量；"
                   "宋体标题＋思源宋正文九行按标点手工断行＋Times 英文＋霞鹜文楷款识四体混排；"
                   "与 Q35 银壶静物/Q37 数钱老妇同为暗底但更极简、器物更少"), "accent": "绛朱 168,52,32 ＋ 1px 发丝下划线",
        "score": 0, "final_png": "", "draft": "v1",
        "band_roles": ROLES, "body_band_slice": SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": ("从 md 文档《醒与悟2.0.md》锚点 sec-131 起扫候选："
               "sec-131 大苦大乐（与成长主题近）、sec-132 熟人际/选爱（关系链撞）、"
               "sec-133 会哭孩子（与 Q35 边界链近）、sec-136 短期快感（与 Q36 投资自己撞）、"
               "sec-137 消化痛苦/别诉苦（与 sec-131 近）、sec-139 放弃做好人（与 Q34 撞）、"
               "sec-140 谈钱花钱（与 Q37 人情比钱撞）、sec-141 独处/能力导向（与 Q36 撞）、"
               "sec-142~146 情绪/焦虑篇（主题不合）整篇跳过；"
               "sec-138 段6「吃苦的本质」124 字定稿（去编号「7，」结构标记），断言 6/6"),
        "see": {}, "think": "", "iterations": 0, "score": 0, "final_png": "",
    },
}
out = ROOT / "q39.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out, "| body:", len(SEG), "字 | en:", len(EN.split()), "词")

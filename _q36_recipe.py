# -*- coding: utf-8 -*-
"""生成 Q36 / 第 104 张配方。
文案：md 文档《醒与悟2.0.md》锚点 sec-057 第1条 217 字（跨文档开采）。
"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("不要管别人怎么说你，怎么看你，把所有时间精力都用来操心自己，投资自己。"
       "在你没有钱之前不要去思考别人的事。"
       "地球不需要你拯救，需要拯救的是你自己。"
       "每个人最重要的是自己的注意力和自己的时间，因为人与人之间，唯一公平的只有时间。"
       "只思考和自己前途未来相关的事。其他的事情跟你没有任何关系。"
       "多看一眼，多停留一秒都是浪费时间。"
       "能够让你变得越来越牛的只有投资自己，投资自己的外表，投资自己的健康，投资自己的头脑。"
       "要让每一天的自己都比昨天强那么一点点。")

BODY = ("不要管别人怎么说你，怎么看你，|"
        "把所有时间精力都用来操心自己，<a>投资自己</a>。|"
        "在你没有钱之前不要去思考别人的事。|"
        "<a>地球不需要你拯救</a>，需要拯救的是你自己。|"
        "每个人最重要的是自己的注意力和自己的时间，|"
        "因为人与人之间，唯一公平的只有时间。|"
        "只思考和自己前途未来相关的事。|"
        "其他的事情跟你没有任何关系。|"
        "多看一眼，多停留一秒都是浪费时间。|"
        "能够让你变得越来越牛的只有<a>投资自己</a>，|"
        "投资自己的外表，投资自己的健康，投资自己的头脑。|"
        "要让每一天的自己都比昨天强那么一点点。")

EN = ("Don't mind what others say or think of you. Pour your time and energy into yourself — "
      "that is the only investment that counts. Before you have money, other people's problems "
      "are not your business. The world does not need saving; you do. Your attention and your "
      "time are your most precious assets, because time is the only thing distributed equally. "
      "Think only about your own future. Everything else is none of your concern. Invest in your "
      "appearance, your health, and your mind — and be a little better today than you were yesterday.")

ROLES_PLACEHOLDER = ["title"] + ["body%d" % i for i in range(1, 13)] + ["en%d" % i for i in range(1, 6)] + ["credit"]
BODY_SLICE = [1, 13]

ARTIST = "伊斯特曼·约翰逊（Eastman Johnson, 1824–1906）"
PAINTING = "林肯的少年时代（Boyhood of Lincoln）"
YEAR = "约1868"
MEDIUM = "布面油画"
COLLECTION = "芝加哥历史博物馆藏"
LICENSE = "Public domain（PD-old-auto-expired，1906 年卒）"
CREDIT = "原作 %s《%s》%s · %s" % (ARTIST, PAINTING, YEAR, MEDIUM)
DARK = True

PARAMS = {
    "title_font": "qingke", "body_font": "sans", "en_font": "garamond", "credit_font": "kai",
    "inline_accent": "<a>", "accent_underline": "1:9:168,52,32:200", "accent_fill": "168,52,32",
    "fill": "18,16,14" if not DARK else "244,236,212",
    "en_fill": "26,22,18" if not DARK else "232,224,200",
    "credit_fill": "28,24,20" if not DARK else "226,216,190",
    "pos": "top", "align": "center", "x_shift": "0", "y_shift": "40", "wrap": "0",
    "block_width": "80%", "en_width": "1240",
    "title_size": "82", "body_size": "32", "en_size": "26", "credit_size": "21",
    "title_gap": "30", "en_gap": "18", "credit_gap": "26",
    "title_lh": "1.16", "line_gap": "1.20", "scrim": "0", "text_grain": "0.05", "grain": "0.0",
    "body_align": "left", "title_align": "center",
}

data = {
    "id": "Q36", "no": 104, "title": "投资自己",
    "body": BODY, "en": EN, "credit": CREDIT,
    "source": {"doc": "醒与悟2.0.md", "anchor": "sec-057", "page": 57,
               "segments": [SEG], "flat_text": (TMP / "q36_flat.txt").read_text(encoding="utf-8")},
    "meta": {
        "essay": "第八节让自己増値 · 第1条", "artist": ARTIST, "painting": PAINTING,
        "year": YEAR, "medium": MEDIUM, "collection": COLLECTION, "license": LICENSE,
        "layout": ("暗底浅字＋文字压上半幅极净暗背景（y200–900 中位 7–8、std 2–17），"
                   "少年林肯在右侧暗处读书自学——『把时间精力收回到自己身上』的视觉双关；"
                   "庆科黄油标题＋思源黑正文十二行按标点手工断行＋Garamond 英文＋霞鹜文楷款识四体混排；"
                   "与 Q35 暗底奢华静物／宋体／上半块区分：本张极暗自学场景／庆科黄油标题／长文净暗区"),
        "accent": "绛朱 168,52,32 ＋ 1px 发丝下划线",
        "score": 0, "final_png": "", "draft": "v1",
        "band_roles": ROLES_PLACEHOLDER, "body_band_slice": BODY_SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": ("1.0 文档 s308 已到末尾；2.0–5.0 锚点格式 sec-NNN，文风偏口语问答/数字列表/OCR 差。"
               "按「不硬修不勉强」原则从 md 文档《醒与悟2.0.md》锚点 sec-057 第1条开采 217 字"
               "（去段首列表编号「1，」结构标记，其余逐字保留），断言 6/6。"
               "筛除：sec-051 好说话（与 Q35 撞链）、sec-063 领导潜台词（与 Q33 撞链）、"
               "sec-003~008 操控术（主题不合规）、3.0 房产问答/4.0-5.0 无短篇整篇跳过"),
        "see": {}, "think": "", "iterations": 0, "score": 0, "final_png": "",
    },
}
out = ROOT / "q36.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out, "| body:", len(SEG), "字 | en:", len(EN.split()), "词")

# -*- coding: utf-8 -*-
"""生成 Q37 / 第 105 张配方。文案：md 文档《醒与悟2.0.md》锚点 sec-097 段2 177 字。"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("能用钱解决的事，尽量不要用熟人帮忙，是人都有局限性。"
       "搬家呢，不要找朋友，即使你们关系再好，他们也弄不好。"
       "因为干的好也没有什么好处，就算你给好处，他们又不好意思要。"
       "你记住，他不要钱，这个活他就不可能干的好。"
       "以后遇到问题，直接花钱找陌生人。"
       "因为我们对陌生人的服务不满意，我们可以提出来。"
       "而我们对熟人不能不满意。"
       "能用钱解决的事儿，不要欠人情，因为人情比钱更贵。")

BODY = ("能用钱解决的事，<a>尽量不要用熟人帮忙</a>，|"
        "是人都有局限性。|"
        "搬家呢，不要找朋友，即使你们关系再好，|"
        "他们也弄不好。|"
        "因为干的好也没有什么好处，|"
        "就算你给好处，他们又不好意思要。|"
        "你记住，他不要钱，这个活他就不可能干的好。|"
        "以后遇到问题，直接花钱找陌生人。|"
        "因为我们对陌生人的服务不满意，我们可以提出来。|"
        "而我们对熟人不能不满意。|"
        "能用钱解决的事儿，<a>不要欠人情</a>，|"
        "因为<a>人情比钱更贵</a>。")

EN = ("If money can solve it, don't ask a friend — everyone has their limits. "
      "Don't call on friends to help you move, no matter how close you are; they still won't do it "
      "well. Even if you pay them back, they'll be too embarrassed to take it. And if they won't "
      "take money, they won't do a proper job. Next time, just hire a stranger. With a stranger, "
      "you can say the service wasn't good enough. With a friend, you can't. Use money instead of "
      "owing a favor — a favor costs more than money ever will.")

ROLES = ["title"] + ["body%d" % i for i in range(1, 13)] + ["en%d" % i for i in range(1, 6)] + ["credit"]
SLICE = [1, 13]
ARTIST = "约翰·格奥尔格·迈耶圈作（Circle of Johann Georg Meyer, 1813–1871）"; PAINTING = "数钱的老妇（Geldzählendes Mütterchen）"; YEAR = "19世纪"; MEDIUM = "木板油画"
COLLECTION = "私人藏（Dorotheum 图版）"; LICENSE = "Public domain（PD-old-100）"
CREDIT = "原作 %s《%s》%s · %s" % (ARTIST, PAINTING, YEAR, MEDIUM)
DARK = True

PARAMS = {
    "title_font": "hei", "body_font": "serif", "en_font": "times", "credit_font": "kai",
    "inline_accent": "<a>", "accent_underline": "1:9:168,52,32:200", "accent_fill": "168,52,32",
    "fill": "18,16,14" if not DARK else "255,252,245",
    "en_fill": "26,22,18" if not DARK else "250,246,232",
    "credit_fill": "28,24,20" if not DARK else "245,238,218",
    "pos": "top", "align": "center", "x_shift": "0", "y_shift": "40", "wrap": "0",
    "block_width": "80%", "en_width": "1240",
    "title_size": "80", "body_size": "32", "en_size": "26", "credit_size": "21",
    "title_gap": "30", "en_gap": "18", "credit_gap": "26",
    "title_lh": "1.16", "line_gap": "1.20", "scrim": "0", "text_grain": "0.05", "grain": "0.0",
    "body_align": "left", "title_align": "center",
}

data = {
    "id": "Q37", "no": 105, "title": "人情比钱更贵",
    "body": BODY, "en": EN, "credit": CREDIT,
    "source": {"doc": "醒与悟2.0.md", "anchor": "sec-097", "page": 97,
               "segments": [SEG], "flat_text": (TMP / "q37_flat.txt").read_text(encoding="utf-8")},
    "meta": {
        "essay": "第九节被人尊崇的社交法则 · 段2", "artist": ARTIST, "painting": PAINTING,
        "year": YEAR, "medium": MEDIUM, "collection": COLLECTION, "license": LICENSE,
        "layout": ("暗底浅字＋文字压上半幅极净暗背景（y200–500 中位 40–44、std 4–10），"
                   "下半老妇独坐数钱——『用钱解决、不欠人情』的视觉双关：钱货两清、谁也不欠谁；"
                   "黑体标题＋思源宋正文十二行按标点手工断行＋Times 英文＋霞鹜文楷款识四体混排；"
                   "与 Q36 炉火苦读／庆科黄油区分：本张数钱老妇／黑体／极简室内"), "accent": "绛朱 168,52,32 ＋ 1px 发丝下划线",
        "score": 0, "final_png": "", "draft": "v1",
        "band_roles": ROLES, "body_band_slice": SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": ("从 md 文档《醒与悟2.0.md》锚点 sec-058 起扫 43 篇候选："
               "sec-058/059 牛人特征/弱者思维（列表长篇）、sec-061~065 职场潜规则（与 Q35 边界链撞）、"
               "sec-067~083 情感篇（与已出关系链撞）、sec-091 段4 不在乎别人看法（与 Q36 撞链）、"
               "sec-091 段1/段0 含 OCR 损坏（■=/＜=）、sec-095 功利社交（阶层词）、"
               "sec-100 心理博弈（弱势词）整篇跳过；sec-097 段2「人情比钱更贵」177 字定稿"
               "（去段首编号「第六，」结构标记），逐字断言 6/6"),
        "see": {}, "think": "", "iterations": 0, "score": 0, "final_png": "",
    },
}
out = ROOT / "q37.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out, "| body:", len(SEG), "字 | en:", len(EN.split()), "词")

# -*- coding: utf-8 -*-
"""生成 Q38 / 第 106 张配方。文案：md 文档《醒与悟2.0.md》锚点 sec-130 段1 152 字。"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("人到中年，手中有刀，心中有佛。大事狠如猛虎，事了闲看落花。"
       "个人感悟就是该做事时拼命，该玩时尽兴玩好，工作和生活必须有所区分。"
       "除了生老病死，人生里真正重要的事，其实没有几件。"
       "没必要为了小事愁容满面，也没必要去跟小人争个长短。"
       "如果厌恶身边的人，表达厌恶最好的方式不是和他们争吵，而是自己努力，加把劲离开他们。")

BODY = ("人到中年，<a>手中有刀</a>，<a>心中有佛</a>。|"
        "<a>大事狠如猛虎</a>，事了闲看落花。|"
        "个人感悟就是该做事时拼命，该玩时尽兴玩好，|"
        "工作和生活必须有所区分。|"
        "除了生老病死，人生里真正重要的事，其实没有几件。|"
        "没必要为了小事愁容满面，|"
        "也没必要去跟小人争个长短。|"
        "如果厌恶身边的人，|"
        "表达厌恶最好的方式不是和他们争吵，|"
        "而是自己努力，加把劲离开他们。")

EN = ("In middle age, carry a blade in one hand and a Buddha in the other. "
      "Be fierce as a tiger when the moment demands it; when it's over, sit quietly and watch the "
      "flowers fall. Work hard when it's time to work, and play wholeheartedly when it's time to "
      "play — keep the two apart. Apart from birth, aging, illness and death, there are very few "
      "things that truly matter. Don't wear yourself out over small grievances, and don't waste "
      "breath arguing with petty people. If you dislike someone, the best way to show it is not "
      "to argue — it's to work harder and leave them behind.")

ROLES = ["title"] + ["body%d" % i for i in range(1, 11)] + ["en%d" % i for i in range(1, 6)] + ["credit"]
SLICE = [1, 11]
ARTIST = "岸竹堂（Kishi Chikudō, 1856–1897）"; PAINTING = "虎与幼虎"; YEAR = "1892"; MEDIUM = "绢本设色六曲屏风"
COLLECTION = "大都会艺术博物馆藏（MET）"; LICENSE = "CC0（Met Open Access）"
CREDIT = "原作 %s《%s》%s · %s" % (ARTIST, PAINTING, YEAR, MEDIUM)
DARK = False

PARAMS = {
    "title_font": "xingkai", "body_font": "serif", "en_font": "garamond", "credit_font": "kai",
    "inline_accent": "<a>", "accent_underline": "1:9:190,20,30:120", "accent_fill": "190,20,30",
    "fill": "18,16,14" if not DARK else "244,236,212",
    "en_fill": "26,22,18" if not DARK else "232,224,200",
    "credit_fill": "28,24,20" if not DARK else "226,216,190",
    "pos": "top", "align": "center", "x_shift": "0", "y_shift": "180", "wrap": "0",
    "block_width": "80%", "en_width": "1240",
    "title_size": "82", "body_size": "34", "en_size": "26", "credit_size": "21",
    "title_gap": "30", "en_gap": "18", "credit_gap": "26",
    "title_lh": "1.16", "line_gap": "1.20", "scrim": "0", "text_grain": "0.05", "grain": "0.0",
    "body_align": "left", "title_align": "center",
}

data = {
    "id": "Q38", "no": 106, "title": "手中有刀，心中有佛",
    "body": BODY, "en": EN, "credit": CREDIT,
    "source": {"doc": "醒与悟2.0.md", "anchor": "sec-130", "page": 130,
               "segments": [SEG], "flat_text": (TMP / "q38_flat.txt").read_text(encoding="utf-8")},
    "meta": {
        "essay": "第五节成年人看透三件事 · 段1", "artist": ARTIST, "painting": PAINTING,
        "year": YEAR, "medium": MEDIUM, "collection": COLLECTION, "license": LICENSE,
        "layout": ("亮底深字＋文字压中部极净绢面（y400–900 中位 154–162、std 1–7 系列最净），"
                   "上部留装裱边框、下部猛虎与幼虎完整——『大事狠如猛虎，事了闲看落花』直白点题："
                   "虎的刚猛与绢面的宁静并置即刚柔并济；"
                   "行楷标题＋思源宋正文十行按标点手工断行＋Garamond 英文＋霞鹜文楷款识四体混排；"
                   "与 Q37 暗底数钱老妇亮暗对跖"), "accent": "绛朱 168,52,32 ＋ 1px 发丝下划线",
        "score": 0, "final_png": "", "draft": "v1",
        "band_roles": ROLES, "body_band_slice": SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": ("从 md 文档《醒与悟2.0.md》锚点 sec-098 起扫 49 篇候选："
               "sec-098 群发祝福（含 OCR 乱码 10u）、sec-099 利益至上（与 Q35 关系链撞）、"
               "sec-100 心理博弈（弱势词）、sec-102~117 婚恋篇（关系链撞）、"
               "sec-118~125 育儿篇（主题不合）、sec-126~129 忠告篇（与 Q36/Q37 撞链）、"
               "sec-136 短期快感（与 Q36 投资自己略近）、sec-139 放弃做好人（与 Q34 撞链）"
               "整篇跳过；sec-130 段1「手中有刀心中有佛」152 字定稿（去编号「2，」结构标记），断言 6/6"),
        "see": {}, "think": "", "iterations": 0, "score": 0, "final_png": "",
    },
}
out = ROOT / "q38.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out, "| body:", len(SEG), "字 | en:", len(EN.split()), "词")

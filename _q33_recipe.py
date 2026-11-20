# -*- coding: utf-8 -*-
"""生成 Q33 / 第 101 张配方。

文案：md 文档《醒与悟1.0.md》锚点 s267（印刷 120 页）单段 103 字。
配画：待选画定案后填。
"""
from pathlib import Path
import json

ROOT = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets")
TMP = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")

SEG = ("成年人一定要明白，别人的答非所问，就是不想说最真实的答案，"
       "只不过不想让你尴尬，敬而远之就是，不想跟你有过多交集，"
       "沉默不语和不回复，就是拒绝，闪烁不定，就是在说谎，"
       "忽冷忽热，就是你偶尔有点用，但又不是很有用。")

BODY = ("成年人一定要明白，别人的<a>答非所问</a>，|"
        "就是不想说最真实的答案，|"
        "只不过不想让你尴尬，|"
        "敬而远之就是，不想跟你有过多交集，|"
        "<a>沉默不语</a>和不回复，就是拒绝，|"
        "闪烁不定，就是在说谎，|"
        "<a>忽冷忽热</a>，就是你偶尔有点用，但又不是很有用。")

EN = ("Grown-ups need to read the unspoken. When someone answers a question with something else, "
      "they are avoiding the truth — only sparing you embarrassment. Keeping their distance means "
      "they want no more involvement. Silence and no reply mean no. Hesitation means a lie. "
      "Hot one day, cold the next — it means you are occasionally useful, but not essential.")

ROLES_PLACEHOLDER = ["title"] + ["body%d" % i for i in range(1, 8)] + ["en%d" % i for i in range(1, 5)] + ["credit"]
BODY_SLICE = [1, 8]

ARTIST = "卡尔·古斯塔夫·卡鲁斯（Carl Gustav Carus, 1789–1869）"
PAINTING = "晨雾（Morgennebel）"
YEAR = "约1825"
MEDIUM = "布面油画"
COLLECTION = "柏林老国家美术馆藏（SMB）"
LICENSE = "Public domain（PD-Art / PD-old-auto-expired，1869 年卒）"
CREDIT = "原作 %s《%s》%s · %s" % (ARTIST, PAINTING, YEAR, MEDIUM)
DARK = False

PARAMS = {
    "title_font": "hei",
    "body_font": "sans",
    "en_font": "inter",
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
    "title_size": "80",
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
    "id": "Q33",
    "no": 101,
    "title": "你看不懂的那些潜规则",
    "body": BODY,
    "en": EN,
    "credit": CREDIT,
    "source": {
        "doc": "醒与悟1.0.md",
        "anchor": "s267",
        "page": 120,
        "segments": [SEG],
        "flat_text": (TMP / "q33_flat.txt").read_text(encoding="utf-8"),
    },
    "meta": {
        "essay": "你看不懂的那些潜规则",
        "artist": ARTIST,
        "painting": PAINTING,
        "year": YEAR,
        "medium": MEDIUM,
        "collection": COLLECTION,
        "license": LICENSE,
        "layout": ("亮底深字＋文字压上半幅淡金晨雾天空（y200–1100 中位 177–234、std 10–23 天然达标无需烘底），"
                   "下半深暗树梢与水面完整保留——『答非所问/沉默不语/忽冷忽热』皆如晨雾中若隐若现的信号；"
                   "黑体标题＋思源黑正文七行按标点手工断行＋Inter 英文＋霞鹜文楷款识四体混排；"
                   "与 Q32 极暗底月夜／庆科黄油体／中部块全面对跖"),
        "accent": "绛朱 168,52,32 ＋ 1px 发丝下划线",
        "score": 0,
        "final_png": "",
        "draft": "v1",
        "band_roles": ROLES_PLACEHOLDER,
        "body_band_slice": BODY_SLICE,
    },
    "params": PARAMS,
    "pdca": {
        "go": "从 md 文档《醒与悟1.0.md》锚点 s244（印刷 120 页）起筛除：s244 行为背后（八字/阶层词）、"
              "s245 改命（风水命理词）、s246 强弱思维（弱势词）、s248 适当自我（OCR 损坏+弱势链）、"
              "s249 装X（OCR 损坏）、s250 过早拥有（与 Q32 神秘感链撞）、s252 强者无情绪（弱势词）、"
              "s254 不该有的别强求（命理词）、s255 PUA体质（列表格式+弱势链）、s259 别把自己当人（训狗比喻）、"
              "s260 能量磁场（玄学词）、s261 抬杠贫穷体质（弱势词）、s265 真情留不住人（训狗比喻+弱势链）整篇跳过；"
              "s267 潜规则 103 字定稿（零 OCR 损坏），逐字断言 6/6",
        "see": {},
        "think": "",
        "iterations": 0,
        "score": 0,
        "final_png": "",
    },
}

out = ROOT / "q33.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方:", out)
print("body chars:", len(SEG), "en words:", len(EN.split()))

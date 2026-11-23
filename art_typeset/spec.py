# -*- coding: utf-8 -*-
"""规格层：把「写在记忆里的军规」变成代码常量。

这是六层流水线的唯一真相源之一。任何硬门槛、参数默认值、组合冲突
都只在这里定义一次，preflight / verify / recipe / derive 全部引用本模块。

改这里的常量 = 改全系列的验收标准，请同步更新文档与记忆。
"""
from __future__ import annotations

# ---------------------------------------------------------------- 路径
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent                       # C:\Users\admin\Documents\tietuai
CONTENT = PROJECT.parent / "tietu"          # C:\Users\admin\Documents\tietu
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
PRESETS = ROOT / "presets"
GOLDEN = ROOT / "golden"
LEGACY_TOOL = PROJECT / "local_typeset.py"
PYTHON = Path(r"C:\Users\admin\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe")

# ---------------------------------------------------------------- 画布与命名
CANVAS = (1536, 2048)          # 3:4 直出，不可变
DPI_RATIO = 1536 / 2048

# 已交付张数：口径分母（「资产可复现率 = 可复现配方数 / 本常量」）。
# 2026-11-12 第 93 张（Q25）交付后 = 93；**每次交付新张必须递增这里**，
# 禁止在 methodology / 文档里另写死数字。
TOTAL_DELIVERED = 104

# ---------------------------------------------------------------- 硬门槛
# 字号下限（2026-11-01 用户指令）：先定字号再削内容，不许先塞内容再压字号
FONT_MIN = {"title": 72, "body": 28, "en": 25, "credit": 19}
FONT_TITLE_PREFERRED = (76, 88)

# 清晰度（每层单独测，以最弱层为准，低于即不交付）
CONTRAST_MIN = {"title": 5.0, "body": 5.0, "en": 4.0, "credit": 3.5}
BG_STD_MAX = 25.0              # 文字区底色局部标准差
BG_DARK_RATIO_MAX = 0.15      # 亮底深字时的暗占比上限；暗底浅字不适用
ACCENT_RATIO_RANGE = (0.08, 0.15)   # 强调像素 / 正文区中文墨像素
BBOX_MARGIN_MIN = 80           # 包围盒四边最小距离

# ---- 强调占比口径（2026-11-10 固化；此前每次手写脚本切法都不同，同一张能算出
#      12.57 / 14.16 / 18.54 / 20.09 四个值。钉死如下，禁止再用「目视达标」换口径）：
#  · 区域 = 从第一条正文行带起点到最后一条正文行带终点的【连续 y 区间】，
#    含行间空白（装饰下划线会落在行间，不得排除）
#  · 分母 = 该区间内所有「成图 vs 原图」差分墨像素（不含英文/标题带）
#  · 分子 = 其中满足色相差 (R-G>18 且 R-B>30) 的像素，含金色下划线
#  · 禁设绝对亮度阈值（第 85 张：R>90 会漏掉深朱）
#  · 故 Q21 严格口径为 20.09%（超标），历史记录的 12.57% 是「仅行带内部 +
#    R>140 亮度门槛」的偏松口径，已列为待复核项，不回溯改已交付成图。
ACCENT_POLICY = "continuous_band_with_underline_v1"

# 底色亮度带（第 87 张）：浅字需 ≤45，深字需 ≥150，中间调 60–110 两头不讨好
BG_LIGHT_TEXT_MAX = 45
BG_DARK_TEXT_MIN = 150
BG_MIDTONE = (60, 110)

# ---------------------------------------------------------------- 排版多样性
# 用户第 32 条：连续两张不得同为纯横排；每 5 张至少 2 张非横排
NON_HORIZONTAL_MIN_IN_5 = 2

# ---------------------------------------------------------------- 文本纪律
BAD_WORDS = (
    "风水", "命理", "玄学", "算命", "八字", "印星", "背禄",
    "阶层", "弱势", "白嫖", "官微信",
)
INLINE_TAG = "<a>"
MANUAL_BREAK = "|"

# 避头尾（2026-11-12 第 94 张 Q26）：中文断行后，收尾标点不得落在行首，
# 起始标点不得落在行尾。旧流程靠 --wrap 自动折行，Q26 v10 出现「，很多人」
# 顶格（标点落行首）——字都没错，但排版一眼可辨地错。改为手工断行 + 门禁校验。
PUNCT_LINE_START_BAN = "，。、；：？！）》」』”’·…"
PUNCT_LINE_END_BAN = "（《「『“‘"

# ---------------------------------------------------------------- 93 参数默认值
# 从 local_typeset.py 的 argparse 逐条抄录（2026-11-10 体检）。
# 注意：默认值里 --en-size 23 / --credit-size 18 低于本文件 FONT_MIN，
# 这正是「少写一行就悄悄出一张不达标图」的根源，preflight 会强制拦截。
DEFAULTS = {
    "size": "1536x2048", "font": "serif",
    "title_font": None, "body_font": None, "credit_font": None,
    "title_size": 92, "body_size": 46, "en_size": 23, "credit_size": 18,
    "title_weight": 700, "title_lh": 1.34, "body_weight": 400,
    "spacing": 0, "body_spacing": 0, "line_gap": 1.60,
    "pos": "top", "align": "center", "title_align": None, "body_align": None,
    "wrap": 0, "wrap_indent": 1, "marker": None, "marker_fill": None,
    "block_width": None, "x_shift": 0, "y_shift": 0,
    "vertical": "off", "rotate": 0,
    "fill": "43,38,33", "accent_prefix": None, "accent_fill": None,
    "accent_size": 0, "accent_underline": None, "overline": None,
    "inline_accent": None, "fill_gradient": None,
    "stroke": 0, "stroke_color": "255,255,255", "shadow": None,
    "emboss": None, "shadow_color": "0,0,0", "glow": None,
    "glow_color": "255,255,255", "halo": None, "reflect": 0.0,
    "text_grain": 0.0, "aux_bottom": "off", "aux_align": None,
    "aux_x_shift": 0, "aux_fill": None, "aux_glow": None, "aux_shadow": None,
    "scrim": 0.0, "scrim_color": "246,240,228", "block_scrim": None,
    "lead_bar": None, "crop_x": 0.5, "crop_bottom": 0.0,
    "title_gap": 0, "body_pos": None, "body_x_shift": 0, "body_y_shift": 0,
    "occlude": None, "en_fill": None, "en_gap": 0, "en_width": None,
    "en_pos": None, "en_align": None, "en_x_shift": 0, "en_y_shift": 0,
    "first_indent": 0, "en_italic": "off", "en_weight": 0, "credit_gap": 0,
    "en_font": "times", "accent_echo": None, "credit_fill": None,
    "warp": None, "warp_body": "off", "perspective": None, "texture": None,
    "vertical_gap": 26, "aux_lift": 0, "credit_bottom": "off", "grain": 0.25,
}

# 文本四项（非数值参数，单独列）
TEXT_KEYS = ("title", "body", "en", "credit")
INPUT_KEYS = ("base", "out")

# ---------------------------------------------------------------- 参数类型
INT_KEYS = {
    "title_size", "body_size", "en_size", "credit_size", "title_weight",
    "body_weight", "spacing", "body_spacing", "wrap", "wrap_indent",
    "x_shift", "y_shift", "accent_size", "stroke", "aux_x_shift",
    "title_gap", "body_x_shift", "body_y_shift", "en_gap", "en_x_shift",
    "en_y_shift", "first_indent", "en_weight", "credit_gap",
    "vertical_gap", "aux_lift",
}
FLOAT_KEYS = {
    "title_lh", "line_gap", "rotate", "reflect", "text_grain", "scrim",
    "crop_x", "crop_bottom", "grain",
}
CHOICES = {
    "pos": ("top", "upper", "middle", "lower", "bottom"),
    "align": ("left", "center", "right"),
    "title_align": ("left", "center", "right"),
    "body_align": ("left", "center", "right"),
    "vertical": ("on", "off"),
    "aux_bottom": ("on", "off"),
    "aux_align": ("left", "center", "right"),
    "body_pos": ("top", "upper", "middle", "lower", "bottom"),
    "en_pos": ("top", "upper", "middle", "lower", "bottom"),
    "en_align": ("left", "center", "right"),
    "en_italic": ("on", "off"),
    "warp_body": ("on", "off"),
    "credit_bottom": ("on", "off"),
}

# ---------------------------------------------------------------- 组合冲突表
# 每一条都对应一个真实事故。severity: "error" 拒绝出图 / "warn" 提示
CONFLICTS = [
    # (条件 lambda, 说明, 级别, 事故出处)
    (lambda c: c.get("warp") and c.get("vertical") == "on",
     "--warp 与 --vertical 不能共存：竖排分支会完全忽略 it['warp']，形变静默失效",
     "error", "第86张"),
    (lambda c: c.get("aux_bottom") == "on" and c.get("en_width"),
     "--aux-bottom on 叠 --en-width 限宽会裁掉英文首行",
     "error", "第88张/Q20"),
    (lambda c: c.get("perspective") and c.get("body_pos"),
     "--perspective 与 --body-pos 同用时正文分块分支被跳过（工具内有 `and not args.perspective`）",
     "error", "源码 1072 行"),
    (lambda c: c.get("perspective") and (c.get("x_shift") or c.get("y_shift") or c.get("pos") != "top"),
     "--perspective 落地后位置由目标四边形决定，--pos/--x-shift/--y-shift 静默失效",
     "warn", "源码 1186 行"),
    (lambda c: c.get("warp") and not c.get("title_gap"),
     "用 --warp 必须显式给 --title-gap（≥幅度值）：_h() 只按 幅度×1.15 估算撑高，"
     "标题与正文零间距时波浪下探会压进正文首行",
     "error", "第88张 v2 修订"),
    (lambda c: c.get("warp") and c.get("title_gap", 0) < 40
     and c.get("warp", "").startswith("wave"),
     "wave 幅度 ≥30 时 --title-gap 建议 ≥40",
     "warn", "SKILL.md"),
    (lambda c: c.get("perspective") and len(strip_tags(c.get("body", ""))) > 45,
     "长文＋全译英不做整块透视：会把长英文重采样得又小又淡，且揉碎文字行带导致强调占比测不准",
     "error", "Q21 主动撤回 / Q20 已判断过"),
    (lambda c: c.get("perspective") and len(c.get("en", "")) > 90,
     "英文副标超过 90 字符时整块透视会压糊，形变只给标题或短句",
     "error", "Q21"),
    (lambda c: c.get("inline_accent") is None and INLINE_TAG in c.get("body", ""),
     "BODY 含 <a> 标签但没传 --inline-accent：标签会被当字面印上画面",
     "error", "第68张"),
    (lambda c: c.get("accent_underline") and len(str(c.get("accent_underline")).split(":")) != 4,
     "--accent-underline 必须是四段格式 粗:下移:R,G,B:透明度",
     "error", "Q21"),
    (lambda c: c.get("credit_gap", 0) and 0 < c["credit_gap"] < 20,
     "--credit-gap 过小会让款识压住英文末行（第75张 14→32 才分开；Q21 用 22 实测安全）",
     "warn", "第75张"),
    (lambda c: c.get("en_italic") == "on" and c.get("en_font") != "times",
     "--en-italic 曾硬编码 timesi.ttf，非 times 字族可能回退或变形，出图前确认",
     "warn", "MEMORY.md"),
    (lambda c: c.get("block_width") and c.get("aux_bottom") == "on",
     "--block-width 与 --aux-bottom 同用需复核辅助块宽度是否被主块限宽影响",
     "warn", "Q20"),
]


def strip_tags(text: str) -> str:
    """去掉内联强调标签与手工断行符，得到「排入画面的字面文本」。"""
    return (text or "").replace(INLINE_TAG, "").replace("</a>", "").replace(MANUAL_BREAK, "")


def all_param_names() -> set[str]:
    return set(DEFAULTS) | set(TEXT_KEYS) | set(INPUT_KEYS) | {"hrule", "vrule"}

# -*- coding: utf-8 -*-
"""测量层（方案 3 的 Measure pass）：真实墨迹盒，取代经验系数。

这是【只读旁路预测器】：不改 local_typeset.py 一行，不参与渲染，
只在出图前预测块高、标题下缘、正文上缘、画布溢出与重叠风险。

为什么必须有它：
  legacy 的 build_block._h() 用 font.size * lh + abs(幅度) * 1.15 估算行高，
  warp 撑高估不准 → 第 88 张 v1 波浪标题压进正文首行（用户当场指出）。
  rotate / perspective 变形后尺寸也不回流给布局 → Q21 出现 1550px 块溢出画布。

本模块用 PIL 的 getbbox / getlength 拿到「真实字形墨迹盒」，
给出布局期的几何事实，供 preflight 做「块间不重叠约束」判定。
未来若要重写布局内核（方案 3 完整版），本模块就是现成的 Measure pass。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import ImageFont

from . import shaping, spec

# 与 legacy 保持一致的字体池（只读引用，不复制字体文件）
FONT_DIR = Path(r"C:\Users\admin\.workbuddy-ai\fonts")
FONTS = {
    "serif": r"C:\Windows\Fonts\NotoSerifSC-VF.ttf",
    "sans": r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
    "kai": str(FONT_DIR / "LXGWWenKai-Regular.ttf"),
    "smiley": str(FONT_DIR / "smiley" / "SmileySans-Oblique.ttf"),
    "song": r"C:\Windows\Fonts\STZHONGS.TTF",
    "hei": r"C:\Windows\Fonts\simhei.ttf",
    "xingkai": r"C:\Windows\Fonts\STXINGKA.TTF",
    "qingke": str(FONT_DIR / "ZCOOLQingKeHuangYou-Regular.ttf"),
    "mashan": str(FONT_DIR / "MaShanZheng-Regular.ttf"),
}
LATIN_FONTS = {
    "times": r"C:\Windows\Fonts\times.ttf",
    "garamond": str(FONT_DIR / "EBGaramond[wght].ttf"),
    "playfair": str(FONT_DIR / "PlayfairDisplay[wght].ttf"),
    "inter": str(FONT_DIR / "Inter[opsz,wght].ttf"),
    "symbols": str(FONT_DIR / "NotoSansSymbols[wght].ttf"),
    "symbols2": str(FONT_DIR / "NotoSansSymbols2-Regular.ttf"),
}


@dataclass
class Line:
    text: str
    role: str
    font_key: str
    size: int
    # 真实墨迹盒（相对该行基线原点）
    ink_top: float = 0.0
    ink_bottom: float = 0.0
    width: float = 0.0
    y0: float = 0.0       # 预测在块内的顶边
    y1: float = 0.0       # 预测在块内的底边


@dataclass
class Layout:
    lines: list[Line] = field(default_factory=list)
    block_w: float = 0.0
    block_h: float = 0.0
    notes: list[str] = field(default_factory=list)


def _font(key: str, size: int, latin: bool = False) -> ImageFont.FreeTypeFont:
    table = LATIN_FONTS if latin else FONTS
    path = table.get(key) or (LATIN_FONTS["times"] if latin else FONTS["serif"])
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype(FONTS["serif"], size)


def _ink_box(f: ImageFont.FreeTypeFont, text: str):
    """真实墨迹盒：用 getbbox 而非 font.size * 系数。

    经 shaping 适配层，未来开启 RAQM 时无需改本函数。
    """
    if not text:
        return 0, 0, 0
    _, b = shaping.measure(text, f)
    return b[1], b[3], b[2] - b[0]   # ink_top, ink_bottom, width


def _wrap_latin(f, text: str, max_width: float) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and f.getlength(trial) > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def predict(recipe: dict) -> Layout:
    """按配方预测布局几何（只读，不渲染）。"""
    p = dict(spec.DEFAULTS)
    p.update({k: v for k, v in (recipe.get("params") or {}).items() if v not in (None, "")})

    def as_int(k, d=0):
        try:
            return int(p.get(k, d))
        except (TypeError, ValueError):
            return d

    def as_float(k, d=0.0):
        try:
            return float(p.get(k, d))
        except (TypeError, ValueError):
            return d

    lay = Layout()
    y = float(spec.PAD if hasattr(spec, "PAD") else 160)  # 块内上边距
    PAD = 160
    y = float(PAD)

    title_f = _font(p.get("title_font") or p.get("font") or "serif", as_int("title_size", 92))
    body_f = _font(p.get("body_font") or p.get("font") or "serif", as_int("body_size", 46))
    en_f = _font(p.get("en_font") or "times", as_int("en_size", 23), latin=True)
    credit_f = _font(p.get("credit_font") or p.get("font") or "serif", as_int("credit_size", 18))

    # ---- 标题（可能多行，用 | 手工断行）
    title_lines = str(recipe.get("title", "")).split("|")
    for t in title_lines:
        top, bot, w = _ink_box(title_f, spec.strip_tags(t))
        lh = as_float("title_lh", 1.34) * as_int("title_size", 92)
        gap_after = as_int("title_gap", 0)
        warp = str(p.get("warp") or "")
        extra = 0.0
        if warp:
            # 真实估算：warp 逐字旋转后墨迹盒会向下延伸，取振幅的实测比例而非固定 1.15
            try:
                amp = abs(float(warp.split(":")[1]))
                extra = amp * 1.15  # 保留 legacy 口径以便对照；本模块会显式报告它
                lay.notes.append("warp 振幅 %.0f → legacy 估算撑高 %.1f（本模块标注为【估算】）" % (amp, extra))
            except (IndexError, ValueError):
                pass
        L = Line(t, "title", str(p.get("title_font") or "song"),
                 as_int("title_size", 92), top, bot, w, y, y + lh + extra)
        lay.lines.append(L)
        y = L.y1 + gap_after

    title_bottom = lay.lines[-1].y1 if lay.lines else y

    # ---- 正文（| 手工断行优先，否则按 wrap 折）
    body_raw = str(recipe.get("body", ""))
    body_lines = ([x for x in body_raw.split("|") if x] if "|" in body_raw
                  else [body_raw[i:i + as_int("wrap", 0) or len(body_raw) or 1]
                        for i in range(0, len(body_raw), as_int("wrap", 0) or max(len(body_raw), 1))])
    body_first_top = None
    for t in body_lines:
        clean = spec.strip_tags(t)
        top, bot, w = _ink_box(body_f, clean)
        lh = as_float("line_gap", 1.60) * as_int("body_size", 46) / 1.6 * 1.12
        # legacy 横排行距 = f.size * 1.12（580 行）；这里用真实墨迹高作对照
        real_h = bot - top
        L = Line(clean, "body", str(p.get("body_font") or "kai"),
                 as_int("body_size", 46), top, bot, w, y, y + max(lh, real_h))
        if body_first_top is None:
            body_first_top = y + top
        lay.lines.append(L)
        y = L.y1

    # ---- 英文（忠实模拟 legacy：只有显式 --en-width 才折行；
    #      没有时英文一整行撑开块宽 —— 这正是 Q21 v4 报 1550px 溢出的根因）
    en_text = str(recipe.get("en", ""))
    en_w = as_int("en_width", 0)
    en_lines = _wrap_latin(en_f, en_text, en_w) if en_w else [en_text]
    for t in en_lines:
        top, bot, w = _ink_box(en_f, t)
        lh = as_int("en_size", 23) * 1.55
        L = Line(t, "en", str(p.get("en_font") or "times"), as_int("en_size", 23),
                 top, bot, w, y, y + lh)
        lay.lines.append(L)
        y = L.y1 + as_int("en_gap", 0)

    # ---- 款识
    cr = str(recipe.get("credit", ""))
    if cr:
        top, bot, w = _ink_box(credit_f, cr)
        L = Line(cr, "credit", str(p.get("credit_font") or "hei"),
                 as_int("credit_size", 18), top, bot, w,
                 y + as_int("credit_gap", 0), y + as_int("credit_gap", 0) + as_int("credit_size", 18) * 1.4)
        lay.lines.append(L)
        y = L.y1

    lay.block_w = max((l.width for l in lay.lines), default=0) + 2 * PAD
    lay.block_h = y + PAD
    lay.notes.append("块预测 %.0f×%.0f px（含 PAD 320）" % (lay.block_w, lay.block_h))
    lay.title_bottom = title_bottom
    lay.body_first_top = body_first_top
    return lay


def constraints(recipe: dict, lay: Layout | None = None) -> dict:
    """块间不重叠 + 画布溢出 + 呼吸缝 —— 布局期硬约束。"""
    lay = lay or predict(recipe)
    p = dict(spec.DEFAULTS)
    p.update({k: v for k, v in (recipe.get("params") or {}).items() if v not in (None, "")})

    issues = []

    # ① 标题与正文的呼吸缝：warp 必须有 title_gap，且缝 ≥ 0
    gap = getattr(lay, "title_bottom", None)
    bft = getattr(lay, "body_first_top", None)
    if gap is not None and bft is not None:
        clearance = bft - gap
        if clearance < 0:
            issues.append("标题下缘与正文首行重叠 %.0f px（第 88 张 v1 同款）" % abs(clearance))
        elif clearance < 12 and p.get("warp"):
            issues.append("warp 标题与正文呼吸缝仅 %.0f px，建议 --title-gap ≥40" % clearance)

    # ② 块宽溢出画布（Q21 去掉透视后 1550 > 1536）
    if lay.block_w > spec.CANVAS[0] and not p.get("perspective") and not p.get("block_width"):
        issues.append("预测块宽 %.0f px > 画布 %d px，需 --en-width 折行或 --block-width 限宽"
                      % (lay.block_w, spec.CANVAS[0]))

    # ③ 块高溢出画布
    if lay.block_h > spec.CANVAS[1]:
        issues.append("预测块高 %.0f px > 画布 %d px" % (lay.block_h, spec.CANVAS[1]))

    # ④ 字号下限（与 preflight 双保险）
    for layer, key in (("title", "title_size"), ("body", "body_size"),
                       ("en", "en_size"), ("credit", "credit_size")):
        try:
            if int(p.get(key, spec.DEFAULTS[key])) < spec.FONT_MIN[layer]:
                issues.append("%s 低于字号下限" % key)
        except (TypeError, ValueError):
            pass

    return {"ok": not issues, "issues": issues, "layout": lay}


def render(lay: Layout) -> str:
    out = ["=== 布局期真实墨迹盒预测（只读，不改渲染）==="]
    for l in lay.lines:
        out.append("  %-7s y[%6.0f,%6.0f]  墨迹盒[%5.0f,%5.0f] 宽%6.0f  %s"
                   % (l.role, l.y0, l.y1, l.ink_top, l.ink_bottom, l.width,
                      l.text[:26]))
    for n in lay.notes:
        out.append("  · " + n)
    return "\n".join(out)

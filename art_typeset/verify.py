# -*- coding: utf-8 -*-
"""测量层：出图即出三项数字 + 底色均匀度，不达标不落盘。

把「每次手写临时 numpy 脚本」固化成 verify(final, base, recipe)。
暗底浅字用「亮端 p99 ÷ 底色」，亮底深字用「底色 ÷ 暗端 p1」（第 85 张）。
分母一律取正文区中文墨像素，绝不用「成图 vs 原图」全部差分像素（第 88 张）。
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from . import spec


def _lum(a: np.ndarray) -> np.ndarray:
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def load_pair(final, base):
    A = np.asarray(Image.open(final).convert("RGB")).astype(np.int32)
    B = np.asarray(Image.open(base).convert("RGB")).astype(np.int32)
    return A, B


def _ink_x_range(ink: np.ndarray, min_col_px: int = 5,
                 base_lo: int = 80, base_hi: int = 1450) -> tuple[int, int]:
    """自适应探测有效墨区的 x 范围，但只向外扩展、不向内收窄。

    设计约束（2026-11-11 P1 回归保护）：
      端正横排图的墨区通常落在 [80,1450] 内部（文字居中、左右留白多）。
      若无条件向内收窄到实际墨区，会改变 bg 统计，把本来达标的图误判为不达标，
      触发 render 删图 —— 这是破坏性回归。
      因此：墨区完全在基准内 → 维持基准（端正图 100% 不变）；
            墨区超出基准（旋转/形变/透视）→ 扩展到实际墨区。
    """
    col_sums = ink.sum(axis=0)
    has_ink = col_sums > min_col_px
    xs = np.where(has_ink)[0]
    if len(xs) < 10:
        return base_lo, base_hi  # 回退历史默认
    x_lo, x_hi = int(xs.min()) - 8, int(xs.max()) + 8  # 留 8px 防边缘锯齿
    # 只向外扩展：超出基准才取墨区边界，否则维持基准（不向内收窄）
    out_lo = x_lo if x_lo < base_lo else base_lo
    out_hi = x_hi if x_hi > base_hi else base_hi
    return max(out_lo, 0), min(out_hi, ink.shape[1])


def find_bands(ink: np.ndarray, x0: int = None, x1: int = None,
               min_px: int = 25, min_height: int = 6):
    """按逐行墨量把文字聚成行带，用于分层测量。

    x0/x1 缺省时自适应探测（_ink_x_range）；显式传入则用传入值（向后兼容）。
    """
    if x0 is None or x1 is None:
        x0, x1 = _ink_x_range(ink)
    rows = ink[:, x0:x1].sum(axis=1)
    on = rows > min_px
    bands, start = [], None
    for y, v in enumerate(on):
        if v and start is None:
            start = y
        if not v and start is not None:
            if y - start >= min_height:
                bands.append((start, y))
            start = None
    if start is not None:
        bands.append((start, len(on)))
    return bands


def _gold_mask(rgb: np.ndarray, ink: np.ndarray) -> np.ndarray:
    """色相差识别彩色强调：R 明显高于 G/B。禁设绝对亮度阈值（第 85 张）。"""
    return ink & ((rgb[..., 0] - rgb[..., 1]) > 18) & \
                 ((rgb[..., 0] - rgb[..., 2]) > 30)


def verify(final, base, *, dark_bg: bool = True,
           body_band_slice=(1, 5), verbose: bool = True,
           roles: list = None) -> dict:
    """返回结构化报告。dark_bg=True 表示浅字压暗底。

    body_band_slice：行带列表中「中文正文四行」的切片（默认 1:5，
    即跳过标题带 0、取四条正文带、排除英文与款识）。

    roles：显式声明每条行带的角色（2026-11-12 Q25）。默认硬编码 8 层
    「标题1+正文4+英文2+款识1」，配方行数一变就整体错位：Q24 是层数多
    （真款识落到 band10），Q25 是层数少（真款识被误标成 en1，导致
    contrast_credit=None 假 FAIL）。配方可用 meta.band_roles 声明真实结构。
    """
    A, B = load_pair(final, base)
    La, Lb = _lum(A), _lum(B)
    ink = np.abs(A - B).max(axis=2) > 40
    H, W = ink.shape

    # 自适应探测有效墨区 x 范围（形变图支持，q18 不再需要 measured_by 绕过）
    x0, x1 = _ink_x_range(ink)
    bands = find_bands(ink, x0, x1)
    if roles is None:
        roles = ["title", "body1", "body2", "body3", "body4", "en1", "en2", "credit"]

    layers = []
    for i, (y0, y1) in enumerate(bands):
        m = ink[y0:y1, x0:x1]
        fg = La[y0:y1, x0:x1][m]
        bg = Lb[y0:y1, x0:x1][~m]
        if len(fg) < 50:
            continue
        if dark_bg:
            ratio = float(np.percentile(fg, 99) / max(np.median(bg), 1))
        else:
            ratio = float(np.median(bg) / max(np.percentile(fg, 1), 1))
        layers.append({
            "role": roles[i] if i < len(roles) else "band%d" % i,
            "y": (y0, y1), "contrast": round(ratio, 2),
            "bg_median": round(float(np.median(bg)), 1),
            "bg_std": round(float(bg.std()), 1),
            "bg_dark_ratio": round(float((bg < 70).mean()), 3),
            "ink": int(m.sum()),
        })

    # ---- 强调占比（口径见 spec.ACCENT_POLICY，禁止临时改切法）
    # 连续 y 区间：从首条正文行带起点到末条正文行带终点，含行间空白
    # （3px 金色下划线会落在行间，排除它等于换口径刷数字）
    lo, hi = body_band_slice
    body_bands = bands[lo:hi]
    gold_total = ink_body = 0
    if body_bands:
        y0, y1 = body_bands[0][0], body_bands[-1][1]
        m = ink[y0:y1, x0:x1]
        g = _gold_mask(A[y0:y1, x0:x1], m)
        gold_total, ink_body = int(g.sum()), int(m.sum())
    accent_ratio = gold_total / max(ink_body, 1)

    # ---- 包围盒四边
    ys, xs = np.where(ink)
    bbox = {
        "top": int(ys.min()), "bottom": int(H - 1 - ys.max()),
        "left": int(xs.min()), "right": int(W - 1 - xs.max()),
    }

    # ---- 判定
    def layer_ratio(role_prefix):
        vals = [l["contrast"] for l in layers if l["role"].startswith(role_prefix)]
        return min(vals) if vals else None

    checks = {}
    for layer, floor in spec.CONTRAST_MIN.items():
        r = layer_ratio(layer)
        checks["contrast_" + layer] = {
            "value": r, "floor": floor, "pass": r is not None and r >= floor}

    stds = [l["bg_std"] for l in layers]
    checks["bg_std"] = {
        "value": round(max(stds), 1) if stds else None,
        "floor": spec.BG_STD_MAX,
        "pass": bool(stds) and max(stds) <= spec.BG_STD_MAX}
    lo_r, hi_r = spec.ACCENT_RATIO_RANGE
    checks["accent_ratio"] = {
        "value": round(accent_ratio, 4), "range": (lo_r, hi_r),
        "pass": lo_r <= accent_ratio <= hi_r}
    checks["bbox"] = {
        "value": bbox, "floor": spec.BBOX_MARGIN_MIN,
        "pass": all(v >= spec.BBOX_MARGIN_MIN for v in bbox.values())}
    # 未归类行带兜底（2026-11-12 Q24）：roles 只预设「标题1+正文4+英文2+款识1」
    # 共 8 层，正文 5 行或英文 4 行时多余的带会落到 bandN，最弱层就被漏判
    # （Q24 真款识 band10 仅 3.14:1，contrast_credit 却拿了英文行 4.29 蒙混过关）。
    # 保守做法：所有 bandN 按最严的 credit 门槛兜底，宁可误拦不可漏放。
    extras = [l["contrast"] for l in layers if l["role"].startswith("band")]
    checks["contrast_extra_bands"] = {
        "value": round(min(extras), 2) if extras else None,
        "floor": spec.CONTRAST_MIN["credit"],
        "pass": (not extras) or min(extras) >= spec.CONTRAST_MIN["credit"]}
    checks["layers_found"] = {"value": len(layers), "pass": len(layers) >= 6}

    passed = all(c["pass"] for c in checks.values())
    report = {
        "ok": passed, "checks": checks, "layers": layers,
        "bands": bands, "accent_ratio": round(accent_ratio, 4),
        "accent_pixels": gold_total, "body_ink": ink_body, "bbox": bbox,
    }
    if verbose:
        print(render(report))
    return report


def render(r: dict) -> str:
    out = ["=== 出图自检 ==="]
    for l in r["layers"]:
        out.append("  %-7s y[%4d,%4d] 对比 %5.2f:1  底中位 %5.1f  std %4.1f  暗占 %3.0f%%"
                   % (l["role"], l["y"][0], l["y"][1], l["contrast"],
                      l["bg_median"], l["bg_std"], l["bg_dark_ratio"] * 100))
    out.append("  强调占比 %.2f%%  (金 %d / 正文墨 %d，门槛 8–15%%)"
               % (r["accent_ratio"] * 100, r["accent_pixels"], r["body_ink"]))
    b = r["bbox"]
    out.append("  包围盒四边 上%d 下%d 左%d 右%d" %
               (b["top"], b["bottom"], b["left"], b["right"]))
    out.append("  ----  %s" % ("全部达标 ✅" if r["ok"] else "存在不达标 ❌"))
    for k, c in r["checks"].items():
        if not c["pass"]:
            out.append("  FAIL  %s: %s" % (k, c))
    return "\n".join(out)

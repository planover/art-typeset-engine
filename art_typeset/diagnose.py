# -*- coding: utf-8 -*-
"""首渲诊断层：FAIL 后先诊断再开药（2026-11-20 复盘固化）。

设计动机（方法论纠正）：
  Q31 强调超标 → 连调 alpha/饱和度/下划线 3 次无效，真凶是强调字笔画密度；
  Q32 边距不足 → 连调 block_width/en_width 2 次无效，真凶是款识折行；
  Q33 英文孤行 → 加宽 en_width 无效且压缩边距，真凶是 roles 少声明一层。
  三次都是「先调参后诊断」，违反 GO·SEE·THINK·DO 的 SEE 阶段。
  本模块把 SEE 固化成结构化诊断：一个命令输出全部真凶线索＋禁试清单。

用法：
  python -m art_typeset diagnose <final.png> <base.png> [--dark] [--roles title,body1,...]
  python -m art_typeset diagnose --recipe <qNN.json> <final.png> <base.png>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from . import spec, verify


def _band_detail(ink: np.ndarray, bands: list, x0: int, x1: int) -> list:
    """每条行带的真实 x 范围与墨量——定位 bbox 真凶。"""
    out = []
    for i, (y0, y1) in enumerate(bands):
        m = ink[y0:y1, :]
        ys, xs = np.where(m)
        if not len(xs):
            continue
        out.append({
            "i": i, "y": (int(y0), int(y1)),
            "x": (int(xs.min()), int(xs.max())),
            "ink": int(m.sum()),
            "cols_over_5": int((m.sum(axis=0) > 5).sum()),
        })
    return out


def _std_profile(base_lum: np.ndarray, bands: list, x0: int, x1: int) -> list:
    """每条行带的底色 std——定位 bg_std 真凶；附 std 沿 y 直方图。"""
    out = []
    for i, (y0, y1) in enumerate(bands):
        cell = base_lum[y0:y1, x0:x1]
        out.append({
            "i": i, "y": (int(y0), int(y1)),
            "std": round(float(cell.std()), 1),
            "median": round(float(np.median(cell)), 1),
        })
    return out


def _accent_breakdown(A: np.ndarray, ink: np.ndarray, bands: list,
                      body_slice: tuple, x0: int, x1: int) -> dict:
    """强调像素构成：下划线 vs 字本身笔画——决定该调参数还是换字。

    下划线墨色是 accent_fill 经 alpha 混合后的色值；字是纯 accent_fill。
    按色相差(R-G)分桶：色相差越大通常越接近纯强调色（字），越小越像淡混合（下划线）。
    """
    lo, hi = body_slice
    body_bands = bands[lo:hi]
    if not body_bands:
        return {"error": "body_band_slice 无对应行带"}
    y0, y1 = body_bands[0][0], body_bands[-1][1]
    m = ink[y0:y1, x0:x1]
    rgb = A[y0:y1, x0:x1]
    gold = verify._gold_mask(rgb, m)
    rg = (rgb[..., 0] - rgb[..., 1])[gold]
    rb = (rgb[..., 0] - rgb[..., 2])[gold]
    if not len(rg):
        return {"accent_pixels": 0}
    # 色相差分桶：>80 视为接近纯强调色（字），<=80 视为混合（下划线/抗锯齿边缘）
    pure = int((rg > 80).sum())
    mixed = int((rg <= 80).sum())
    return {
        "body_y": (int(y0), int(y1)),
        "accent_pixels": int(gold.sum()),
        "body_ink": int(m.sum()),
        "ratio": round(float(gold.sum() / max(m.sum(), 1)), 4),
        "rg_median": round(float(np.median(rg)), 1),
        "pure_ratio": round(pure / max(len(rg), 1), 3),
        "mixed_ratio": round(mixed / max(len(rg), 1), 3),
        "verdict": ("字笔画主导→换笔画少的强调字（Q31 军规）"
                    if pure / max(len(rg), 1) > 0.55
                    else "下划线/边缘主导→调下划线参数"),
    }


def _suggest_roles(bands: list, band_detail: list, title_size_hint: int = 60) -> dict:
    """按行带高度与顺序推断 roles：最高带=title，末尾带=credit，其余按位置分组。"""
    n = len(bands)
    if n < 3:
        return {"roles": [], "body_slice": [1, max(1, n - 1)], "confidence": "low"}
    heights = [b[1] - b[0] for b in bands]
    roles = []
    # 标题：首带若明显高（≥1.4×正文中位高）判 title，否则也按 title 计（系列惯例）
    roles.append("title")
    # 款识：末带通常最矮或接近英文高；系列惯例末带=credit
    # 中间带：正文（中文行，高≈字号×1.1）在前，英文（矮，高≈字号×0.7）在后
    body_h = np.median(heights[1:-1]) if n > 2 else heights[1]
    en_cut = None
    for i in range(1, n - 1):
        # 高度显著低于正文中位 → 英文起点
        if heights[i] < body_h * 0.72 and en_cut is None:
            en_cut = i
    body_end = en_cut if en_cut is not None else n - 1
    for i in range(1, body_end):
        roles.append("body%d" % i)
    en_start = body_end
    for i in range(en_start, n - 1):
        roles.append("en%d" % (i - en_start + 1))
    roles.append("credit")
    return {
        "roles": roles,
        "body_slice": [1, body_end],
        "confidence": "medium",
        "heights": heights,
        "note": "按高度推断，须与配方 source/BODY 行数核对后回填",
    }


def diagnose(final, base, *, dark_bg: bool = True, roles: list = None,
             body_slice: tuple = (1, 5), verbose: bool = True,
             recipe_loaded: bool = False) -> dict:
    """结构化诊断：一次性输出所有 FAIL 的真凶线索。"""
    A = np.asarray(Image.open(final).convert("RGB")).astype(np.int32)
    B = np.asarray(Image.open(base).convert("RGB")).astype(np.int32)
    H, W = A.shape[:2]
    ink = np.abs(A - B).max(axis=2) > 40
    x0, x1 = verify._ink_x_range(ink)
    bands = verify.find_bands(ink, x0, x1)

    detail = _band_detail(ink, bands, x0, x1)
    base_lum = verify._lum(B)
    stdprof = _std_profile(base_lum, bands, x0, x1)
    accent = _accent_breakdown(A, ink, bands, body_slice, x0, x1)
    suggestion = _suggest_roles(bands, detail)

    ys, xs = np.where(ink)
    bbox = {
        "top": int(ys.min()), "bottom": int(H - 1 - ys.max()),
        "left": int(xs.min()), "right": int(W - 1 - xs.max()),
    }
    # bbox 真凶：找出左右极值所在带
    edge_bands = []
    for d in detail:
        if (d["x"][0] <= bbox["left"] + 3 or d["x"][1] >= W - 1 - bbox["right"] - 3):
            edge_bands.append(d["i"])
    # bg_std 真凶
    std_bad = [s for s in stdprof if s["std"] > spec.BG_STD_MAX]

    report = {
        "bands": len(bands),
        "x_range": (x0, x1),
        "bbox": bbox,
        "bbox_edge_bands": edge_bands,
        "band_detail": detail,
        "std_profile": stdprof,
        "std_bad_bands": std_bad,
        "accent": accent,
        "roles_suggestion": suggestion,
        "actions": [],
        "recipe_loaded": recipe_loaded,
    }

    if not recipe_loaded:
        report["actions"].append({
            "fail": "diagnose_incomplete",
            "diagnose": "未读配方——body_slice 用默认 (1,5)、roles 未校验",
            "do": "重跑时加 --recipe=qNN.json 才能测准强调占比与角色错位",
            "forbid": "禁止据未读配方的强调占比下结论（默认切片可能只覆盖部分正文）",
        })

    # ---- 决策树：先诊断，再开药
    if any(v < spec.BBOX_MARGIN_MIN for v in bbox.values()):
        report["actions"].append({
            "fail": "bbox",
            "diagnose": "查 bbox_edge_bands 的行带内容：是款识折行（x 极宽、ink≈整行）、"
                        "还是画面光点被差分捕获（ink 小、位置孤立）",
            "do": "款识折行→删外文原名/长括号；画面光点→确认非文字后记录说明，不改块宽",
            "forbid": "禁止先调 block_width/en_width（Q32 教训：两次调宽无效）",
        })
    if std_bad:
        worst = max(std_bad, key=lambda s: s["std"])
        report["actions"].append({
            "fail": "bg_std",
            "diagnose": "std_bad_bands 定位超标带 y=%s；对照 std_profile 看是整幅纹理还是窄带交界"
                        % str(worst["y"]),
            "do": "窄带→对该 y 区间做轻度大羽化柔光烘底（Q29/Q30/Q33 军规），"
                  "烘制底图同步作 verify base；整幅纹理→换画",
            "forbid": "禁止改字号/位移（Q33 教训：先测 std 沿 y 分布）",
        })
    ratio = accent.get("ratio")
    if ratio is not None and not (spec.ACCENT_RATIO_RANGE[0] <= ratio <= spec.ACCENT_RATIO_RANGE[1]):
        report["actions"].append({
            "fail": "accent_ratio",
            "diagnose": "看 accent.verdict：字笔画主导（pure_ratio>0.55）还是下划线主导",
            "do": "字笔画主导→换笔画少的强调字（Q31：执着→少）；下划线主导→调下划线参数",
            "forbid": "禁止在字笔画主导时反复调 alpha/饱和度/厚度（Q31 三次无效）",
        })
    if roles and len(roles) != len(bands):
        report["actions"].append({
            "fail": "roles_mismatch",
            "diagnose": "配方声明 %d 层、实测 %d 层：多出或缺少的行带是真凶" % (len(roles), len(bands)),
            "do": "按 roles_suggestion 回填，并与 source/BODY 行数核对（Q33：英文 4 行就声明 4 个 en）",
            "forbid": "禁止加宽 en_width 试图减少行数（Q33：无效且压缩边距）",
        })

    if verbose:
        print(render(report))
    return report


def render(r: dict) -> str:
    out = ["=== 首渲诊断（先诊断后开药）===",
           "实测 %d 层｜x 范围 %s｜四边距 %s" % (r["bands"], r["x_range"], r["bbox"])]
    out.append("---- 行带明细（定位 bbox 真凶）")
    for d in r["band_detail"]:
        flag = " ◀BBOX边缘" if d["i"] in r["bbox_edge_bands"] else ""
        out.append("  band%02d y[%4d,%4d] x[%4d,%4d] ink=%6d%s" %
                   (d["i"], d["y"][0], d["y"][1], d["x"][0], d["x"][1], d["ink"], flag))
    out.append("---- 底色 std（定位 bg_std 真凶，门槛 %.1f）" % spec.BG_STD_MAX)
    for s in r["std_profile"]:
        flag = " ◀超标" if s["std"] > spec.BG_STD_MAX else ""
        out.append("  band%02d y[%4d,%4d] std=%5.1f 中位=%5.1f%s" %
                   (s["i"], s["y"][0], s["y"][1], s["std"], s["median"], flag))
    ac = r["accent"]
    if ac.get("accent_pixels"):
        out.append("---- 强调构成：%d px / %d = %.2f%%｜rg中位 %s｜纯色占比 %s｜%s" %
                   (ac["accent_pixels"], ac["body_ink"], ac["ratio"] * 100,
                    ac["rg_median"], ac["pure_ratio"], ac["verdict"]))
    sg = r["roles_suggestion"]
    out.append("---- 建议 roles（%s）：%s" % (sg["confidence"], ",".join(sg["roles"])))
    out.append("---- body_band_slice: %s" % sg["body_slice"])
    if r["actions"]:
        out.append("---- 行动清单（按序执行，勿跳步）")
        for i, a in enumerate(r["actions"], 1):
            out.append("  %d) [%s]" % (i, a["fail"]))
            out.append("     诊断：%s" % a["diagnose"])
            out.append("     处置：%s" % a["do"])
            out.append("     禁止：%s" % a["forbid"])
    else:
        out.append("---- 无 FAIL 线索，可继续 1:1 目验")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="首渲诊断：FAIL 后先诊断再开药")
    ap.add_argument("final", help="草稿成图 PNG")
    ap.add_argument("base", help="底图 PNG")
    ap.add_argument("--dark", action="store_true", help="暗底浅字")
    ap.add_argument("--recipe", help="配方 JSON（自动读 roles 与 body_band_slice）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    a = ap.parse_args(argv)

    roles = None
    body_slice = (1, 5)
    if a.recipe:
        r = json.loads(Path(a.recipe).read_text(encoding="utf-8"))
        roles = r.get("meta", {}).get("band_roles")
        body_slice = tuple(r.get("meta", {}).get("body_band_slice", [1, 5]))
    rep = diagnose(a.final, a.base, dark_bg=a.dark, roles=roles,
                   body_slice=body_slice, verbose=not a.json)
    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

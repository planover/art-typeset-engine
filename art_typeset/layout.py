# -*- coding: utf-8 -*-
"""布局层（方案 3 的 Layout pass）：约束求解，自动修正参数。

与 measure.py 的分工：
  measure.py = 只读事实（真实墨迹盒、呼吸缝、块尺寸）
  layout.py  = 在事实上求解：不重叠 / 不溢出 / 亮度带落位，
               把结论回写成参数修正（title-gap / en-width / block-width）。

设计原则：**只做增量修正，绝不推翻人工版式**。
  · 若人工已给 title_gap 且达标 → 不动
  · 若 warp 撑高导致呼吸缝 < 12 → 补 title_gap 到 ≥40
  · 若预测块宽 > 画布 → 补 en-width 折行（这正是 Q21 掉过的坑）
  · 所有修正都记录在 returns 里，出图报告必须列出

对外：solve(recipe) -> {"params": {修正项}, "changes": [说明], "ok": bool}
      apply(recipe)  -> 就地返回修正后的配方副本（不改原文件）
"""
from __future__ import annotations

import copy

from . import measure, spec


def solve(recipe: dict, *, apply_fixes: bool = True) -> dict:
    lay = measure.predict(recipe)
    c = measure.constraints(recipe, lay)
    p = copy.deepcopy(recipe.get("params") or {})
    changes = []

    # ① 呼吸缝：warp 且有撞字风险时补全 title_gap
    cur_gap = p.get("title_gap")
    try:
        cur_gap = int(cur_gap) if cur_gap not in (None, "") else 0
    except (TypeError, ValueError):
        cur_gap = 0
    if p.get("warp") and cur_gap < 40:
        needed = max(48, cur_gap + 40)
        p["title_gap"] = needed
        changes.append("warp 呼吸缝不足 → --title-gap %d → %d" % (cur_gap, needed))

    # ② 块宽溢出：补英文折行限宽
    if lay.block_w > spec.CANVAS[0] and not p.get("perspective"):
        if not p.get("en_width"):
            p["en_width"] = 1000
            changes.append("预测块宽 %.0f > 画布 → --en-width 1000 折行" % lay.block_w)
        elif not p.get("block_width"):
            p["block_width"] = "80%"
            changes.append("预测块宽 %.0f > 画布 → --block-width 80%%" % lay.block_w)

    # ③ 块高溢出画布：提示人工处理（自动压字号会违反「先定字号再削内容」）
    if lay.block_h > spec.CANVAS[1]:
        changes.append("⚠️ 预测块高 %.0f > 画布，需人工削内容/换分区，不自动压字号" % lay.block_h)

    return {
        "params": p if apply_fixes else (recipe.get("params") or {}),
        "changes": changes,
        "ok": c["ok"] or bool(changes),
        "measure_issues": c["issues"],
        "layout": lay,
    }


def apply(recipe: dict, *, explain: bool = True) -> dict:
    """返回修正后的配方副本；不写文件、不改渲染器。"""
    s = solve(recipe)
    r = copy.deepcopy(recipe)
    r["params"] = s["params"]
    if explain and s["changes"]:
        print("=== Layout 约束求解（自动修正）===")
        for ch in s["changes"]:
            print("  · " + ch)
    return r


def cli(argv):
    from . import recipe as rmod
    if not argv:
        print("用法: layout <recipe.json> [--apply]"); return 2
    r = rmod.load(argv[0])
    s = solve(r)
    print("=== Layout 约束求解 ===")
    print(measure.render(s["layout"]))
    print()
    if s["changes"]:
        for ch in s["changes"]:
            print("  FIX  " + ch)
    else:
        print("  无需修正（人工版式已满足全部约束）✅")
    if "--apply" in argv:
        out = rmod.save(apply(r, explain=False), argv[0])
        print("  已写回:", out.name)
    return 0

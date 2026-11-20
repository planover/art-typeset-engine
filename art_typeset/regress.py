# -*- coding: utf-8 -*-
"""全量回归：用配方重渲，与落盘交付图（golden 快照）逐像素比对。

与 golden.check() 的区别：golden.check 只验快照存在；本模块真的重渲。

    python -m art_typeset regress          # 全量
    python -m art_typeset regress Q21      # 单张
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from . import golden, recipe, spec

# 快照 ID → 配方文件 / 底图文件名（从抢救脚本的 BASE 常量自动探测）
PRESET = {
    "Q16": "q16.json", "Q17": "q17.json", "Q19": "q19_2.json",
    "Q20": "q20.json", "Q21": "q21.json",
}


def _base_for(r: dict) -> Path:
    script = spec.CACHE / r["_salvage"]["script"]
    s = script.read_text(encoding="utf-8")
    m = re.search(r"BASE\s*=\s*os\.path\.join\(HERE,\s*[\"']([^\"']+)", s)
    name = m.group(1) if m else r["_salvage"].get("base", "")
    p = spec.CACHE / name
    if not p.exists():
        alt = spec.CACHE / r["id"].lower() + "_base.png"
        if alt.exists():
            return alt
    return p


def run_one(rid: str) -> dict:
    preset = spec.PRESETS / PRESET.get(rid, rid.lower() + ".json")
    if not preset.exists():
        return {"ok": False, "reason": "配方不存在 %s" % preset.name}
    r = recipe.load(preset)
    base = _base_for(r)
    if not base.exists():
        return {"ok": False, "reason": "底图不存在 %s" % base.name}

    out = spec.CACHE / ("regress_%s.png" % rid)
    argv = recipe.compile_argv(r, base, out)
    p = subprocess.run(argv, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode:
        return {"ok": False, "reason": "渲染失败: " + (p.stderr or p.stdout)[-180:]}

    snap = spec.GOLDEN / ("%s.png" % rid)
    if not snap.exists():
        return {"ok": False, "reason": "快照缺失"}

    d = golden.compare(out, snap)
    d["preset"] = preset.name
    d["base"] = base.name
    return d


def cli(argv):
    ids = [argv[0]] if argv else list(PRESET)
    rows, ok_all = [], True
    print("=== 全量回归（重渲 → 逐像素比对）===")
    for rid in ids:
        d = run_one(rid)
        ok = bool(d.get("ok"))
        ok_all &= ok
        if ok:
            print("  %-4s %-14s max_diff=0  changed=0   ✅" %
                  (rid, d.get("preset", "")))
        else:
            print("  %-4s %-14s max_diff=%-4s changed=%-8s ❌ %s" %
                  (rid, d.get("preset", ""), d.get("max_diff", "-"),
                   d.get("changed_pixels", "-"), d.get("reason", "")))
        rows.append((rid, d))
    print("  ----  %d 张，%s" % (len(rows), "全部 max diff 0 ✅" if ok_all else "存在差异 ❌"))
    return 0 if ok_all else 1

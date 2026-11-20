# -*- coding: utf-8 -*-
"""配方层：JSON 是唯一真相源，渲染器是纯函数。

render(recipe, base, out) -> Path
    1. preflight 门禁（不通过不出图）
    2. 配方 → argv（唯一编译点，替换散落的 qXX_render.py）
    3. 调 legacy 工具
    4. verify 三项数字（不达标不落盘）
    5. 返回报告

配方结构（presets/qNN.json）：
{
  "id": "Q21", "no": 89, "title": "越值得做的事",
  "body": "...|<a>长期快乐</a>|...",
  "en": "...", "credit": "原作 ...",
  "source": {"page": 71, "segments": [...], "flat_text": "可选"},
  "meta": {"painting": "...", "artist": "...", "year": "...",
           "score": 92, "layout": "端正横排"},
  "params": { ... 仅写与默认值不同的项 ... }
}
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import layout, preflight, spec, verify


def resolve_path(path) -> Path:
    """配方路径解析：绝对路径原样；相对路径按「CWD → 工程根 → presets 目录
    → presets 目录/文件名」依次尝试。

    历史 bug（2026-11-11 收口）：配方实际在 art_typeset/presets/，而文档里
    `check presets/q21.json` 的写法在工程根下按 CWD 解析会 FileNotFound。
    现在两种口径都要能跑：
        python -m art_typeset check presets/q21.json
        python -m art_typeset check art_typeset/presets/q21.json
    """
    p = Path(path)
    if p.is_absolute():
        return p
    for cand in (p, spec.PROJECT / p, spec.PRESETS / p, spec.PRESETS / p.name):
        if cand.exists():
            return cand
    return p


def load(path) -> dict:
    return json.loads(resolve_path(path).read_text(encoding="utf-8"))


def save(recipe: dict, path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
    return p


def compile_argv(recipe: dict, base, out) -> list[str]:
    """配方 → 命令行。唯一编译点；未知参数在此被 preflight 拦下。"""
    cmd = [str(spec.PYTHON), str(spec.LEGACY_TOOL),
           "--base", str(base), "--out", str(out),
           "--size", "%dx%d" % spec.CANVAS]

    for key in spec.TEXT_KEYS:
        val = recipe.get(key, "")
        if val:
            cmd += ["--" + key, str(val)]

    params = recipe.get("params") or {}
    for key, val in params.items():
        if val is None or val == "" or val is False:
            continue
        flag = "--" + key.replace("_", "-")
        if isinstance(val, bool):
            cmd.append(flag)
        elif isinstance(val, list):
            for v in val:
                cmd += [flag, str(v)]
        else:
            cmd += [flag, str(val)]
    return cmd


def render(recipe: dict, base, out, *, strict: bool = True,
           verify_after: bool = True, dark_bg: bool = True,
           auto_layout: bool = True) -> dict:
    """纯函数式入口：同一配方 + 同一底图 ⇒ 同一成图。

    auto_layout=True 时先跑 Layout 约束求解，自动修正 title-gap / 溢出限宽；
    修正只作用于本次渲染的内存副本，**不写回配方文件**。
    """
    base, out = Path(base), Path(out)

    # ⓪ Layout 约束求解
    layout_changes = []
    if auto_layout:
        solved = layout.solve(recipe)
        layout_changes = solved["changes"]
        if layout_changes:
            print("=== Layout 约束求解（自动修正，仅本次渲染）===")
            for ch in layout_changes:
                print("  · " + ch)
            import copy
            recipe = copy.deepcopy(recipe)
            recipe["params"] = solved["params"]

    # ① 门禁
    rpt = preflight.run(recipe, strict=strict)
    print(rpt.render())

    # ② 编译 + ③ 渲染
    cmd = compile_argv(recipe, base, out)
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError("渲染失败：\n" + (r.stderr or r.stdout)[-2000:])
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "(无输出)")

    # ④ 测量
    report = {}
    if verify_after:
        sl = (recipe.get("meta") or {}).get("body_band_slice")
        br = (recipe.get("meta") or {}).get("band_roles")
        vkw = {}
        if sl:
            vkw["body_band_slice"] = tuple(sl)
        if br:
            vkw["roles"] = list(br)
        report = verify.verify(out, base, dark_bg=dark_bg, verbose=True, **vkw)
        if strict and not report["ok"]:
            print("  ⛔ 测量未达标，删除不合格成图：%s" % out.name)
            out.unlink(missing_ok=True)
    return {"preflight": rpt, "verify": report, "out": str(out),
            "argv": cmd, "layout_changes": layout_changes}

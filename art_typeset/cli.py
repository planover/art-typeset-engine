# -*- coding: utf-8 -*-
"""统一入口。

    python -m art_typeset check   presets/q21.json           # 只跑门禁
    python -m art_typeset render  presets/q21.json [out.png] [base.png] [--light|--dark]
                                                             # 门禁+渲染+测量（极性缺省自动探测）
    python -m art_typeset verify  final.png base.png [--light]  # 只测三项数字
python -m art_typeset diagnose final.png base.png [--light] [--recipe=qNN.json]  # 首渲诊断：FAIL 先诊断再开药
    python -m art_typeset golden  freeze Q21 final.png
    python -m art_typeset golden  check
    python -m art_typeset derive  presets/q21.json            # 台账行+交付骨架
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import derive, diagnose, golden, preflight, recipe, spec, verify

sys.stdout.reconfigure(encoding="utf-8")


def _detect_dark_bg(final, base) -> bool:
    """实测「字/底极性」：字墨比底亮 → 暗底浅字（dark_bg=True）。

    依据本次成图与底图的差分墨像素亮度中位数判定，不靠画作题材猜明暗。
    2026-11-11 第 90 张暴露：亮底深字被固定 dark_bg=True 误判 0.80:1 并删图；
    显式 --light / --dark 优先，本函数只在两者都未给时兜底。
    """
    import numpy as np
    A, B = verify.load_pair(final, base)
    La, Lb = verify._lum(A), verify._lum(B)
    ink = np.abs(A - B).max(axis=2) > 40
    if int(ink.sum()) < 500:            # 无可测文字：回退历史默认（暗底浅字）
        return True
    return float(np.median(La[ink])) >= float(np.median(Lb[~ink]))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]

    if cmd == "check":
        if not rest:
            print("用法: check <recipe.json> | check --all"); return 2
        if rest[0] == "--all":
            import glob
            files = sorted(glob.glob(str(spec.PRESETS / "*.json")))
            fails = 0
            for f in files:
                r = recipe.load(f)
                rpt = preflight.run(r, strict=False)
                print("[%s] %s" % ("✅" if rpt.ok else "⚠️", Path(f).name))
                if not rpt.ok:
                    fails += 1
                    for e in rpt.errors:
                        print("    FAIL  " + e)
            print("---- %d/%d 配方门禁通过，%d 份不通过" %
                  (len(files) - fails, len(files), fails))
            return 0 if fails == 0 else 1
        r = recipe.load(rest[0])
        rpt = preflight.run(r, strict=False)
        print(rpt.render())
        return 0 if rpt.ok else 1

    if cmd == "render":
        if not rest:
            print("用法: render <recipe.json> [out.png] [base.png] [--light|--dark]")
            return 2
        flags = [a for a in rest if a in ("--light", "--dark")]
        args = [a for a in rest if a not in ("--light", "--dark")]
        r = recipe.load(args[0])
        out = Path(args[1]) if len(args) > 1 else spec.GOLDEN / ("render_%s.png" % r.get("id", "tmp"))
        base = Path(args[2]) if len(args) > 2 else (spec.CACHE / ("%s_base.png" % r["id"].lower()))

        # 极性：显式 --light（亮底深字）/ --dark（暗底浅字）优先；
        # 都不给则渲染后按成图 vs 底图实测自动判定，避免亮底图被误判并删除。
        dark_bg = None
        if "--light" in flags:
            dark_bg = False
        elif "--dark" in flags:
            dark_bg = True

        # 先渲染不验（verify_after=False）：自动极性要等成图落盘才能实测，
        # 也避免「极性未定就删图」。测量统一在下面由本命令做一次。
        result = recipe.render(r, base, out, verify_after=False)
        if dark_bg is None:
            dark_bg = _detect_dark_bg(out, base)
            print("=== 自动探测极性：%s（可用 --light / --dark 覆盖）===" %
                  ("暗底浅字" if dark_bg else "亮底深字"))
        # 配方声明正文行带切片（2026-11-12 Q25）：verify 默认假设「正文恒 4 行」
        # 取 bands[1:5]，短句只有 2 行时会把英文行带算进强调占比分母、稀释数字。
        # 历史配方不带此字段 => 行为不变，golden 回归不受影响。
        sl = (r.get("meta") or {}).get("body_band_slice")
        br = (r.get("meta") or {}).get("band_roles")
        vkw = {}
        if sl:
            vkw["body_band_slice"] = tuple(sl)
        if br:
            vkw["roles"] = list(br)
        report = verify.verify(out, base, dark_bg=dark_bg, verbose=True, **vkw)
        result["verify"], result["dark_bg"] = report, dark_bg
        if not report["ok"]:
            print("  ⛔ 测量未达标，删除不合格成图：%s" % out.name)
            out.unlink(missing_ok=True)
            return 1
        return 0

    if cmd == "verify":
        if len(rest) < 2:
            print("用法: verify <final.png> <base.png> [--light]"); return 2
        dark = "--light" not in rest
        sl_flag = next((a for a in rest if a.startswith("--body-bands=")), None)
        br_flag = next((a for a in rest if a.startswith("--band-roles=")), None)
        vkw = {}
        if sl_flag:
            lo, hi = sl_flag.split("=", 1)[1].split(":")
            vkw["body_band_slice"] = (int(lo), int(hi))
        if br_flag:
            vkw["roles"] = br_flag.split("=", 1)[1].split(",")
        rep = verify.verify(rest[0], rest[1], dark_bg=dark, **vkw)
        return 0 if rep["ok"] else 1

    if cmd == "diagnose":
        # 首渲诊断：FAIL 后先诊断再开药（2026-11-20 复盘固化）
        if len(rest) < 2:
            print("用法: diagnose <final.png> <base.png> [--light] [--recipe=qNN.json]"); return 2
        dark = "--light" not in rest
        rp = next((a.split("=", 1)[1] for a in rest if a.startswith("--recipe=")), None)
        if rp is None and "--recipe" in rest:
            i = rest.index("--recipe")
            if i + 1 < len(rest):
                rp = rest[i + 1]
        vkw = {}
        if rp:
            r = recipe.load(Path(rp))
            vkw["roles"] = r.get("meta", {}).get("band_roles")
            vkw["body_slice"] = tuple(r.get("meta", {}).get("body_band_slice", [1, 5]))
            vkw["recipe_loaded"] = True
        diagnose.diagnose(rest[0], rest[1], dark_bg=dark, **vkw)
        return 0

    if cmd == "golden":
        if not rest:
            print("用法: golden freeze <ID> <png> | golden check"); return 2
        if rest[0] == "freeze":
            if len(rest) < 3:
                print("用法: golden freeze <ID> <png> [note]"); return 2
            p = golden.freeze(rest[1], Path(rest[2]), note=(rest[3] if len(rest) > 3 else ""))
            print("快照已存:", p)
        elif rest[0] == "check":
            rep = golden.check()
            print("回归 %d 张: %s" % (rep["count"], "全部 max diff 0 ✅" if rep["ok"] else "有差异 ❌"))
            for k, v in rep["results"].items():
                print("  %-6s %s" % (k, v))
        return 0

    if cmd == "derive":
        if not rest:
            print("用法: derive <recipe.json> | derive audit"); return 2
        if rest[0] == "audit":
            rep = derive.audit()
            print(derive.render_audit(rep))
            return 0 if rep["ok"] else 1
        r = recipe.load(rest[0])
        print("=== 台账行 ==="); print(derive.ledger_row(r))
        print(); print("=== 交付说明骨架 ==="); print(derive.delivery_skeleton(r))
        return 0

    if cmd == "retro":
        from . import retro
        return retro.cli(rest)

    if cmd == "methodology":
        from . import methodology
        return methodology.cli(rest)

    if cmd == "layout":
        from . import layout
        return layout.cli(rest)

    if cmd == "regress":
        from . import regress
        return regress.cli(rest)

    if cmd == "shaping":
        from . import shaping
        print(shaping.report())
        return 0

    if cmd == "measure":
        from . import measure
        if not rest:
            print("用法: measure <recipe.json>"); return 2
        r = recipe.load(rest[0])
        lay = measure.predict(r)
        print(measure.render(lay))
        print()
        c = measure.constraints(r, lay)
        print("约束：%s" % ("全部通过 ✅" if c["ok"] else "发现问题 ❌"))
        for i in c["issues"]:
            print("  - " + i)
        return 0 if c["ok"] else 1

    print("未知命令:", cmd)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

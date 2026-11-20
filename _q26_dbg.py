# -*- coding: utf-8 -*-
"""Q26 调试渲染：走配方→门禁→渲染（不自动删图），再单独打印 verify。"""
import sys
from pathlib import Path
sys.path.insert(0, r"C:\Users\admin\Documents\tietuai")
from art_typeset import recipe, preflight, verify, spec

rj = Path(r"C:\Users\admin\Documents\tietuai\art_typeset\presets\q26.json")
r = recipe.load(rj)
rpt = preflight.run(r, strict=False)
print(rpt.render())
if not rpt.ok:
    raise SystemExit("门禁未过")
out = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp\q26_dbg.png")
base = spec.CACHE / "q26_base.png"
res = recipe.render(r, base, out, verify_after=False)
print("saved", out)
rep = verify.verify(out, base, dark_bg=False, verbose=True)
print(json_ok := ("OK" if rep["ok"] else "NOT OK"))

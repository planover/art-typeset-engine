# -*- coding: utf-8 -*-
"""Q27 DO 第 1 轮：渲染草稿（不验）→ 探真实行带数与包围盒 → 目验。"""
from pathlib import Path
import numpy as np
from PIL import Image
from art_typeset import recipe, verify, spec

CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
r = recipe.load(spec.PRESETS / "q27.json")
base = CACHE / "q27_base.png"
out = CACHE / "q27_draft.png"
print(recipe.render(r, base, out, verify_after=False))

A, B = verify.load_pair(out, base)
ink = np.abs(A - B).max(axis=2) > 40
x0, x1 = verify._ink_x_range(ink)
bands = verify.find_bands(ink, x0, x1)
ys, xs = np.where(ink)
print("墨区 x:", x0, x1, "｜行带数:", len(bands))
for i, (a, b) in enumerate(bands):
    m = ink[a:b, x0:x1]
    print("  band%02d y=%4d-%4d h=%3d ink=%d" % (i, a, b, b - a, int(m.sum())))
print("包围盒 top/bottom/left/right =",
      int(ys.min()), int(ink.shape[0] - 1 - ys.max()),
      int(xs.min()), int(ink.shape[1] - 1 - xs.max()))

rep = verify.verify(out, base, dark_bg=True, verbose=True,
                    roles=r["meta"]["band_roles"],
                    body_band_slice=tuple(r["meta"]["body_band_slice"]))
print("ok =", rep["ok"], "accent =", rep.get("accent_ratio"), "bbox =", rep.get("bbox"))

im = Image.open(out).convert("RGB")
im.resize((768, 1024), Image.LANCZOS).save(CACHE / "q27_draft_view.png")
print("目验图:", CACHE / "q27_draft_view.png")

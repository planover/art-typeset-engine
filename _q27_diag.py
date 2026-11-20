# -*- coding: utf-8 -*-
"""Q27 SEE·诊断：英文行横线伪影的根因对照（4 变体各渲一次，拼版目验）。"""
import copy
from pathlib import Path
from PIL import Image, ImageDraw
from art_typeset import recipe, spec

CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
base = CACHE / "q27_base.png"
r0 = recipe.load(spec.PRESETS / "q27.json")

VARIANTS = {
    "A_原样": {},
    "B_去accent_underline": {"accent_underline": None},
    "C_en换garamond": {"en_font": "garamond"},
    "D_去grain": {"text_grain": "0", "grain": "0"},
    "E_去warp": {"warp": None},
}
ims = []
for name, delta in VARIANTS.items():
    r = copy.deepcopy(r0)
    for k, v in delta.items():
        if v is None:
            r["params"].pop(k, None)
        else:
            r["params"][k] = v
    out = CACHE / ("q27_diag_%s.png" % name[0])
    recipe.render(r, base, out, verify_after=False)
    crop = Image.open(out).convert("RGB").crop((400, 1440, 1480, 1620))
    crop = crop.resize((810, 135), Image.LANCZOS)
    ims.append((name, crop))
    print("rendered", name)

sheet = Image.new("RGB", (840, len(ims) * 165), (245, 245, 245))
d = ImageDraw.Draw(sheet)
for i, (name, im) in enumerate(ims):
    d.text((8, i * 165 + 3), name, fill=(20, 20, 20))
    sheet.paste(im, (15, i * 165 + 22))
p = CACHE / "q27_diag_sheet.png"
sheet.save(p)
print("sheet:", p)

# -*- coding: utf-8 -*-
"""生成重点候选的 1:1 目验图（含四角签名/印章区放大）。"""
from pathlib import Path
from PIL import Image

D = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
T = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp")

for name in ("q22b_moon_boat_0.jpg", "q24_ton_inness.jpg", "q23_cand_bocklin.jpg"):
    im = Image.open(D / name).convert("RGB")
    w, h = im.size
    # 整幅缩到 768 宽，另裁四角 1:1 区域
    full = im.copy()
    full.thumbnail((768, 1024), Image.LANCZOS)
    full.save(T / f"q25_view_{name.split('.')[0]}.png")
    # 底部 20% 带（常有签名）
    band = im.crop((0, int(h * 0.8), w, h))
    band.thumbnail((1200, 400), Image.LANCZOS)
    band.save(T / f"q25_band_{name.split('.')[0]}.png")
    print(name, im.size, "->", T / f"q25_view_{name.split('.')[0]}.png")

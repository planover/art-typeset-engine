# -*- coding: utf-8 -*-
"""清点成图文件名（画家查重）与候选底图缓存。"""
from pathlib import Path

CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
OUT = Path(r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp\q25_assets.txt")

pngs = sorted(p.name for p in CONTENT.glob("*.png"))
cands = sorted(p.name for p in CACHE.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))

lines = [f"PNG 成图 {len(pngs)} 张\n", "=" * 60 + "\n"]
lines += [p + "\n" for p in pngs]
lines.append(f"\n\n候选底图缓存 {len(cands)} 张\n" + "=" * 60 + "\n")
lines += [p + "\n" for p in cands]
OUT.write_text("".join(lines), encoding="utf-8")
print(f"pngs={len(pngs)} cands={len(cands)} out={OUT}")

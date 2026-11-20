# -*- coding: utf-8 -*-
"""Q26：采样底图配色 + 正文竖排列切分 + 逐字断言。"""
from PIL import Image
import numpy as np, re, json

BASE = r"C:\Users\admin\Documents\tietuai\.workbuddy-ai\tmp\q26_shenzhou_cx65.png"
im = Image.open(BASE).convert("RGB")
a = np.asarray(im, dtype=np.int32)


def patch(x0, y0, x1, y1, tag):
    p = a[y0:y1, x0:x1].reshape(-1, 3)
    print(f"{tag:<12} median={tuple(int(v) for v in np.median(p, axis=0))} "
          f"p10={tuple(int(v) for v in np.percentile(p,10,axis=0))} "
          f"p90={tuple(int(v) for v in np.percentile(p,90,axis=0))}")


patch(60, 620, 430, 900, "江面留白")
patch(60, 160, 400, 240, "淡粉天空")
patch(120, 1700, 400, 1900, "石绿点叶")
patch(620, 300, 700, 420, "柳枝墨")
patch(390, 1360, 470, 1500, "亭顶")
patch(60, 1950, 1400, 2030, "底边")

# ---- 正文竖排切分 ----
SEG = ("永远不要试图去改变一个人，是任何人。因为你改不了，很多人连自己想改变自己都很难，"
       "我们又怎么可能去改变别人呢，改变意味着要对抗一个人的基因，是反人性的，"
       "而人性只能顺应，就好像你改变不了世界和社会，只能调整和适应。")
print("\n总字数(含标点) =", len(SEG))
print("去标点字数 =", len(re.sub(r"[，。“”、]", "", SEG)))

# 按标点切分为竖排列（每列尽量均衡，切点只在标点后）
pieces = re.findall(r"[^，。]*[，。]", SEG)
print("标点片段:", pieces)
cols, cur = [], ""
for p in pieces:
    cur += p
    if len(cur) >= 17:
        cols.append(cur); cur = ""
if cur:
    cols.append(cur)
print("列数", len(cols))
for i, c in enumerate(cols):
    print(f"  列{i+1} ({len(c)}字): {c}")
print("拼回是否与原文全等:", "".join(cols) == SEG)

en = ("Never try to change a person, anyone. Because you cannot: most people find it hard "
      "enough to change themselves, so how could we change others? Change means fighting a "
      "person's genes, it goes against human nature, and human nature can only be followed, "
      "just as you cannot change the world and society, only adjust and adapt.")
print("\nEN chars =", len(en))
print("EN =", en)

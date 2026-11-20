# -*- coding: utf-8 -*-
"""Q26 SEE：逐行扫描左侧江面，找出真实「干净矩形」（median≥150 且局部 std≤18）。"""
from PIL import Image
import numpy as np

BASE = r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2\q26_base.png"
im = Image.open(BASE).convert("RGB")
a = np.asarray(im, np.int32)
lum = (a[..., 0] * 2126 + a[..., 1] * 7152 + a[..., 2] * 722) // 10000
H, W = lum.shape

# 用 48x48 滑窗（步长 16）算 std 与 median
S, STEP = 48, 16
ys = list(range(400, 1700 - S, STEP))
xs = list(range(40, 1000 - S, STEP))
ok = np.zeros((len(ys), len(xs)), bool)
med = np.zeros((len(ys), len(xs)))
for i, y in enumerate(ys):
    for j, x in enumerate(xs):
        c = lum[y:y + S, x:x + S]
        med[i, j] = np.median(c)
        ok[i, j] = (np.median(c) >= 150) and (np.std(c) <= 18)

# 最大全-ok 矩形（按面积）
best = (0, None)
for i0 in range(len(ys)):
    for i1 in range(i0 + 1, len(ys)):
        sub = ok[i0:i1 + 1]
        col = sub.all(axis=0)
        # 最长连续 True
        run = 0; start = 0; bl = 0; bs = 0
        for j, v in enumerate(list(col) + [False]):
            if v:
                if run == 0: start = j
                run += 1
                if run > bl: bl, bs = run, start
            else:
                run = 0
        area = (i1 - i0 + 1) * bl
        if area > best[0]:
            best = (area, (ys[i0], ys[i1], xs[bs], xs[bs + bl - 1] + S))

print("最大干净矩形 (y0,y1,x0,x1) =", best[1], " 面积格数 =", best[0])
y0, y1, x0, x1 = best[1]
print(f"宽 {x1-x0} 高 {y1-y0}")

# 每行可用右边界（用于验证矩形）
print("\n逐行右边界（y, 最右干净 x）:")
for y in range(y0, min(y1, 1500), 100):
    i = (y - ys[0]) // STEP
    if 0 <= i < len(ys):
        row = ok[i]
        right = None
        for j in range(len(xs) - 1, -1, -1):
            if row[j]:
                right = xs[j] + S; break
        print(f"  y={y}: x≤{right}  median≈{int(med[i, 0])}")

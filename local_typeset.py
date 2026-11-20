#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.0.0"]
# ///
"""
名画融合文字图 · 本地排版器 v2（零积分路线）

v2 相比 v1 新增：
  · 位置：--pos top|upper|middle|lower|bottom + --align left|center|right + 微调
  · 方向：--vertical 竖排（右起）｜--rotate 任意角度（斜排 / 倒置用 180）
  · 字体：--font / --title-font / --body-font …（含新装霞鹜文楷、得意黑）
  · 效果：--stroke 描边｜--shadow 阴影｜--glow 光晕｜--fill 单色｜--fill-gradient 渐变填充
  · 衬底：自动跟随文字块范围，不再是固定顶部

用法示例：
  uv run --with pillow python local_typeset.py --base 底图 --out 输出 \
    --title "主标题|第二行" --body "正文1|正文2" --en "English" --credit "原作 …" \
    --font smiley --pos bottom --align left --vertical on --rotate -6 \
    --fill "250,244,230" --shadow "4,6,18,150" --glow "26,90"
"""

import argparse
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat

FONT_DIR = r"C:\Users\admin\.workbuddy-ai\fonts"
FONTS = {
    "serif":   (r"C:\Windows\Fonts\NotoSerifSC-VF.ttf", "wght"),                     # 思源宋体
    "sans":    (r"C:\Windows\Fonts\NotoSansSC-VF.ttf", "wght"),                      # 思源黑体
    "kai":     (os.path.join(FONT_DIR, "LXGWWenKai-Regular.ttf"), None),             # 霞鹜文楷
    "smiley":  (os.path.join(FONT_DIR, "smiley", "SmileySans-Oblique.ttf"), None),   # 得意黑
    "song":    (r"C:\Windows\Fonts\STZHONGS.TTF", None),                             # 华文中宋
    "hei":     (r"C:\Windows\Fonts\simhei.ttf", None),                               # 黑体
    "xingkai": (r"C:\Windows\Fonts\STXINGKA.TTF", None),                             # 行楷
    "qingke":  (os.path.join(FONT_DIR, "ZCOOLQingKeHuangYou-Regular.ttf"), None),    # 站酷庆科黄油体（展示体）
    "mashan":  (os.path.join(FONT_DIR, "MaShanZheng-Regular.ttf"), None),            # 马善政毛笔（书法体）
}
LATIN_FONTS = {
    "times":    (r"C:\Windows\Fonts\times.ttf", None),                               # Times New Roman（默认）
    "garamond": (os.path.join(FONT_DIR, "EBGaramond[wght].ttf"), "wght"),            # EB Garamond（古典衬线）
    "playfair": (os.path.join(FONT_DIR, "PlayfairDisplay[wght].ttf"), "wght"),       # Playfair Display（时尚衬线）
    "inter":    (os.path.join(FONT_DIR, "Inter[opsz,wght].ttf"), "wght"),            # Inter（现代无衬线）
    "symbols":  (os.path.join(FONT_DIR, "NotoSansSymbols[wght].ttf"), "wght"),       # Noto Sans Symbols
    "symbols2": (os.path.join(FONT_DIR, "NotoSansSymbols2-Regular.ttf"), None),      # Noto Sans Symbols 2
}
# 斜体族：--en-italic on 时优先取同族斜体（2026-10-17 第 72 张修 bug：
# 旧实现硬编码 timesi.ttf，导致 --en-font garamond --en-italic on 实际渲染成 Times Italic）
LATIN_ITALICS = {
    "times":    r"C:\Windows\Fonts\timesi.ttf",
    "garamond": os.path.join(FONT_DIR, "EBGaramond-Italic[wght].ttf"),
    "playfair": os.path.join(FONT_DIR, "PlayfairDisplay-Italic[wght].ttf"),
    "inter":    os.path.join(FONT_DIR, "Inter-Italic[opsz,wght].ttf"),
}
FONT_LATIN = r"C:\Windows\Fonts\times.ttf"
PAD = 160  # 文字块四周留白，给描边 / 阴影 / 光晕用


def rgb(s):
    return tuple(int(v) for v in s.split(","))


def pxv(v, total):
    """把 '62%' 或 '1280' 解析成像素。"""
    v = str(v).strip()
    return int(total * float(v[:-1]) / 100) if v.endswith("%") else int(float(v))


def draw_rules(canvas, args, W, H):
    """在画布上绘制装饰线（把文字与画面元素缝合起来）。"""
    d = ImageDraw.Draw(canvas)
    for spec in args.hrule:
        y, th, col, al = spec.split(":")
        yy = pxv(y, H)
        d.line([(0, yy), (W, yy)], fill=rgb(col) + (int(al),), width=int(th))
    for spec in args.vrule:
        x, y0, y1, th, col, al = spec.split(":")
        xx = pxv(x, W)
        d.line([(xx, pxv(y0, H)), (xx, pxv(y1, H))], fill=rgb(col) + (int(al),), width=int(th))


def get_font(key, size, weight=None):
    path, axis = FONTS.get(key, FONTS["serif"])
    try:
        f = ImageFont.truetype(path, size)
    except Exception:
        f = ImageFont.truetype(FONTS["serif"][0], size)
    if weight and axis:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def echo_color(base, W, H, spec):
    """强调色从画面采样：取 (x%,y%) 周边区域中"最暗 25%"像素的中位色
    （即该坐标的笔触本色——robe/墨线/印色，避开大面积绢底的稀释），
    再压暗/提亮到墨色亮度带 (lum 0.05-0.13)，保留色相。"""
    x_pct, y_pct = spec
    x, y = int(W * x_pct / 100), int(H * y_pct / 100)
    r = max(6, int(min(W, H) * 0.015))
    box = (max(0, x - r), max(0, y - r), min(W, x + r), min(H, y + r))
    px = list(base.crop(box).getdata())
    if not px:
        return None
    lum = [(p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000 for p in px]
    order = sorted(range(len(px)), key=lambda i: lum[i])
    dark = [px[i] for i in order[:max(1, len(px) // 4)]]
    med = [sum(c) / len(dark) for c in zip(*dark)]
    lum2 = (med[0] * 299 + med[1] * 587 + med[2] * 114) / 1000 / 255
    if lum2 > 0.13:
        f = 0.13 / max(lum2, 1e-3)
        med = [min(255, v * f) for v in med]
    elif 0 < lum2 < 0.05:
        f = 0.05 / max(lum2, 1e-3)
        med = [min(255, v * f) for v in med]
    return tuple(int(v) for v in med)


def get_latin_font(key, size, weight=None, italic=False):
    """key 见 LATIN_FONTS；italic=True 时优先取同族斜体，无斜体族则回退 Times Italic。"""
    path, axis = LATIN_FONTS.get(key, LATIN_FONTS["times"])
    if italic:
        ipath = LATIN_ITALICS.get(key)
        if ipath and os.path.exists(ipath):
            path = ipath
        else:
            # 无同族斜体：回退 Times Italic，并如实告警（不静默换字体）
            print(f"[font-warn] {key} 无斜体族，英文斜体回退 Times Italic")
            path = LATIN_ITALICS["times"]
    try:
        f = ImageFont.truetype(path, size)
    except Exception:
        f = ImageFont.truetype(LATIN_FONTS["times"][0], size)
    if weight and axis:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def line_width(font, text, spacing):
    return sum(font.getlength(ch) for ch in text) + spacing * max(len(text) - 1, 0)


def draw_h(d, x, y, text, font, spacing, fill, stroke_w, stroke_fill):
    """水平绘制一行（支持字距与描边）。x=左边缘，y=ascender 顶。"""
    if spacing <= 0:
        d.text((x, y), text, font=font, fill=fill, anchor="la",
               stroke_width=stroke_w, stroke_fill=stroke_fill)
        return
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=font, fill=fill, anchor="la",
               stroke_width=stroke_w, stroke_fill=stroke_fill)
        cx += font.getlength(ch) + spacing


def draw_line(d, x, y, text, font, spacing, fill, stroke_w, stroke_fill,
              marker=None, marker_fill=None):
    """画一行；若行首命中 marker，则该标记用 marker_fill 单独着色。"""
    if marker and text.startswith(marker):
        draw_h(d, x, y, marker, font, spacing, marker_fill or fill, stroke_w, stroke_fill)
        x += font.getlength(marker) + spacing
        text = text[len(marker):]
    draw_h(d, x, y, text, font, spacing, fill, stroke_w, stroke_fill)


def wrap_cjk(text, n, indent, marker=None):
    """中文按字数折行；后续行用全角空格悬挂缩进（marker 后缩进对齐）。"""
    if n <= 0 or len(text) <= n:
        return [text]
    head = ""
    if marker and text.startswith(marker):
        head, text = marker, text[len(marker):]
    pad = "　" * indent
    lines, cur = [head + text[:n - len(head)]], ""
    rest = text[n - len(head):]
    while rest:
        lines.append(pad + rest[:n - indent])
        rest = rest[n - indent:]
    return lines


def split_inline(text, open_tag, close_tag):
    """把 'text' 按 <a>…</a> 拆成 [(kind, sub), …]，kind ∈ {"plain","accent"}。"""
    out, i = [], 0
    while i < len(text):
        o = text.find(open_tag, i)
        if o == -1:
            out.append(("plain", text[i:]))
            break
        if o > i:
            out.append(("plain", text[i:o]))
        c = text.find(close_tag, o + len(open_tag))
        if c == -1:
            out.append(("plain", text[o:]))
            break
        out.append(("accent", text[o + len(open_tag):c]))
        i = c + len(close_tag)
    return out


def wrap_cjk_segs(segs, n, indent, marker=None):
    """按字符累计折行；accent 段不拆；plain 段可拆。"""
    if not segs or n <= 0:
        return [segs] if segs else [[]]
    total = sum(len(t) for _, t in segs)
    if total <= n:
        return [segs]
    pad = ("plain", "　" * indent)
    lines, cur = [], []
    cur_len = 0
    for kind, t in segs:
        # 行首 marker 单独领一格
        if marker and kind == "plain" and t.startswith(marker) and not cur:
            cur.append(("head", marker))
            cur_len += len(marker)
            t = t[len(marker):]
            if not t:
                continue
        avail = n - cur_len
        if kind == "accent":
            if len(t) <= avail:
                cur.append((kind, t))
                cur_len += len(t)
            else:
                if cur:
                    lines.append(cur); cur, cur_len = [], 0
                cur.append((kind, t))
                cur_len = len(t)
            continue
        # plain 可拆
        while t:
            avail = n - cur_len
            if avail <= 0:
                lines.append(cur); cur, cur_len = [], 0
                avail = n
                if indent > 0:
                    cur.append(pad); cur_len += indent
            take = min(avail, len(t))
            cur.append((kind, t[:take]))
            cur_len += take
            t = t[take:]
    if cur:
        lines.append(cur)
    return lines


def line_width_segs(segs, font, spacing):
    """segs = [(kind, text), …]，算总像素宽。"""
    w = 0
    for _, t in segs:
        if t == "":
            continue
        w += sum(font.getlength(ch) for ch in t) + spacing * max(len(t) - 1, 0)
    return w


def draw_segs(d, x, y, segs, font, spacing, fill, accent_fill,
              stroke_w, stroke_fill, marker, marker_color,
              acc_underline=None):
    """按段着色绘制；可选在 accent 段下画下划线 acc_underline=(粗,下移,RGB,alpha)。"""
    cx = x
    for kind, t in segs:
        if kind == "head":
            col = marker_color or accent_fill
        elif kind == "accent":
            col = accent_fill
        else:
            col = fill
        if t:
            draw_h(d, cx, y, t, font, spacing, col, stroke_w, stroke_fill)
            w = sum(font.getlength(ch) for ch in t) + spacing * max(len(t) - 1, 0)
            if kind == "accent" and acc_underline is not None:
                th, off, uc, ua = acc_underline
                uy = y + font.size + int(off)
                d.line([(cx, uy), (cx + w, uy)],
                       fill=rgb(uc) + (int(ua),), width=int(th))
            cx += w


def wrap_latin(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def parse_warp(spec):
    """解析 --warp：
       arc:强度              —— 抛物线弓形（正=中段上拱，负=下弯），单位 px
       wave:振幅:周期        —— 正弦波，单位 px
       path:x1,y1;x2,y2;…    —— 折线路径，x 为行宽百分比(0-100)，y 为相对基线的 px 偏移（负=上）
    """
    parts = [p.strip() for p in spec.split(":")]
    mode = parts[0].lower()
    if mode == "arc":
        return ("arc", float(parts[1]) if len(parts) > 1 and parts[1] else 40.0, None)
    if mode == "wave":
        amp = float(parts[1]) if len(parts) > 1 and parts[1] else 30.0
        period = float(parts[2]) if len(parts) > 2 and parts[2] else 700.0
        return ("wave", amp, period)
    if mode == "path":
        pts = []
        for seg in parts[1].split(";"):
            if not seg.strip():
                continue
            xs, ys = seg.split(",")
            pts.append((float(xs), float(ys)))
        if len(pts) >= 2:
            return ("path", pts, None)
    return None


def warp_offset_slope(warp, c, total):
    """返回字心在基线方向 c 处的 (dy, 斜率 dy/dx)。"""
    mode = warp[0]
    if mode == "arc":
        st = warp[1]
        u = c / max(total, 1)
        dy = -st * 4 * u * (1 - u)
        slope = -st * 4 * (1 - 2 * u) / max(total, 1)
        return dy, slope
    if mode == "wave":
        amp, period = warp[1], warp[2]
        import math
        k = 2 * math.pi / max(period, 1)
        dy = amp * math.sin(k * c)
        slope = amp * k * math.cos(k * c)
        return dy, slope
    if mode == "path":
        pts = warp[1]
        u = c / max(total, 1) * 100.0
        if u <= pts[0][0]:
            (x0, y0), (x1, y1) = pts[0], pts[1]
        elif u >= pts[-1][0]:
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
        else:
            for i in range(len(pts) - 1):
                if pts[i][0] <= u <= pts[i + 1][0]:
                    (x0, y0), (x1, y1) = pts[i], pts[i + 1]
                    break
        span = max(x1 - x0, 1e-6)
        t = (u - x0) / span
        dy = y0 + (y1 - y0) * t
        slope = (y1 - y0) / (span / 100.0 * total)
        return dy, slope
    return 0.0, 0.0


def draw_warped_line(layer, segs, font, spacing, fill, accent, marker_col,
                     stroke_w, stroke_fill, x0, y0, warp, mask_layer=None):
    """沿曲线逐字排布：每字按局部切线角旋转，保留分段着色与行首标记。"""
    import math
    glyphs = []
    for kind, t in segs:
        col = marker_col if kind == "head" else (accent if kind == "accent" else fill)
        for ch in t:
            adv = font.getlength(ch) + spacing
            glyphs.append((ch, col, adv, kind))
    total = sum(g[2] for g in glyphs)
    if total <= 0:
        return
    ascent, descent = font.getmetrics()
    pad = max(8, stroke_w + 6)
    gh = int(ascent + descent) + pad * 2
    pts_drawn = []
    cursor = 0.0
    for ch, col, adv, kind in glyphs:
        c = cursor + adv / 2.0
        dy, slope = warp_offset_slope(warp, c, total)
        px, py = x0 + c, y0 + dy
        ang = math.degrees(math.atan(slope))
        gw = int(adv) + pad * 2
        tmp = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((pad, pad), ch, font=font, fill=col, anchor="la",
                                 stroke_width=stroke_w, stroke_fill=stroke_fill)
        if abs(ang) > 0.01:
            tmp = tmp.rotate(-ang, resample=Image.BICUBIC,
                             center=(pad, pad + ascent))
        layer.paste(tmp, (int(round(px - pad)), int(round(py - pad - ascent))), tmp)
        if mask_layer is not None:
            mtmp = Image.new("L", (gw, gh), 0)
            ImageDraw.Draw(mtmp).text((pad, pad), ch, font=font, fill=255, anchor="la")
            if abs(ang) > 0.01:
                mtmp = mtmp.rotate(-ang, resample=Image.BICUBIC,
                                   center=(pad, pad + ascent))
            mask_layer.paste(mtmp, (int(round(px - pad)), int(round(py - pad - ascent))), mtmp)
        pts_drawn.append((px, py))
        cursor += adv
    return pts_drawn


def draw_warped_rule(d, pts, off, thick, col, alpha, total):
    """沿曲线在字下方/上方画装饰线（下划线 / overline）。"""
    import math
    if len(pts) < 2:
        return
    line_pts = [(x, y + off) for x, y in pts]
    if thick <= 1:
        d.line(line_pts, fill=rgb(col) + (int(alpha),), width=1, joint="curve")
    else:
        # 粗线：沿法线上下偏移画多边形
        for (x1, y1), (x2, y2) in zip(line_pts[:-1], line_pts[1:]):
            ang = math.atan2(y2 - y1, x2 - x1)
            nx, ny = -math.sin(ang) * thick / 2, math.cos(ang) * thick / 2
            d.polygon([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
                       (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)],
                      fill=rgb(col) + (int(alpha),))


def parse_quad(spec, W, H):
    """解析 --perspective：tlx,tly,trx,try,brx,bry,blx,bly（画布百分比 0-100）→ 像素四点。"""
    v = [float(x) for x in spec.replace(" ", "").split(",")]
    if len(v) != 8:
        return None
    return [(v[0] / 100 * W, v[1] / 100 * H), (v[2] / 100 * W, v[3] / 100 * H),
            (v[4] / 100 * W, v[5] / 100 * H), (v[6] / 100 * W, v[7] / 100 * H)]


def _find_coeffs(pa, pb):
    """解 8 参数投影系数：把输出坐标 pa（目标四边形）映回输入坐标 pb（源四边形）。"""
    import numpy as np
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array(pb, dtype=np.float64).reshape(8)
    res = np.linalg.solve(A, B)
    return res.reshape(8)


def apply_perspective(layer, quad, verbose=True):
    """把文字层按投影变换躺进目标四边形；返回 (新层, 画布左上角坐标)。"""
    bbox = layer.getbbox()
    if bbox is None:
        return layer, (0, 0)
    src = [(bbox[0], bbox[1]), (bbox[2], bbox[1]),
           (bbox[2], bbox[3]), (bbox[0], bbox[3])]
    xs = [p[0] for p in quad]
    ys = [p[1] for p in quad]
    ox, oy = int(min(xs)), int(min(ys))
    ow, oh = int(max(xs) - ox) + 2, int(max(ys) - oy) + 2
    local = [(p[0] - ox, p[1] - oy) for p in quad]
    coeffs = _find_coeffs(local, src)
    out = layer.transform((ow, oh), Image.PERSPECTIVE, coeffs,
                          resample=Image.BICUBIC)
    if verbose:
        print(f"透视落地：源 {bbox[2]-bbox[0]}×{bbox[3]-bbox[1]}px → "
              f"目标四边形 {(int(xs[0]),int(ys[0]))}… 画布 {ow}×{oh}px @({ox},{oy})")
    return out, (ox, oy)


def parse_texture(spec):
    """解析 --texture：强度(0-1):模式(tint|erode|both)，模式默认 both。"""
    parts = [p.strip() for p in spec.split(":")]
    s = float(parts[0]) if parts[0] else 0.4
    s = min(max(s, 0.0), 1.0)
    mode = parts[1].lower() if len(parts) > 1 and parts[1] else "both"
    if mode not in ("tint", "erode", "both"):
        mode = "both"
    return s, mode


def apply_texture(canvas, base, s, mode):
    """局部纹理继承：
       tint  —— 笔画吸收字下画布的色偏（保亮度，不丢对比度）
       erode —— 画面高频纹理处「吃掉」笔画，边缘优先
    """
    import numpy as np
    W, H = canvas.size
    canv = np.asarray(canvas).astype(np.float32)
    rgb, a = canv[:, :, :3].copy(), canv[:, :, 3].copy()
    b = np.asarray(base.convert("RGB")).astype(np.float32)
    bl = (b[:, :, 0] * 299 + b[:, :, 1] * 587 + b[:, :, 2] * 114) / 1000.0
    if mode in ("tint", "both"):
        # 局部色偏：① 比率染色（保明度）② 叠加画布色偏方向（让深色也能被染暖/染冷）
        ratio = b / np.maximum(bl, 1.0)[:, :, None]
        chroma = b - bl[:, :, None]
        rgb = rgb * (1 - s) + rgb * ratio * s + chroma * s * 0.9
    if mode in ("erode", "both"):
        g = np.asarray(base.convert("L")).astype(np.float32)
        gy, gx = np.gradient(g)
        energy = np.hypot(gx, gy)
        # 按 90 分位归一化（用最大值会被个别强边缘吃掉全部动态范围）
        energy = np.clip(energy / max(float(np.percentile(energy, 90)), 1e-6), 0, 1)
        energy = np.asarray(Image.fromarray((energy * 255).astype(np.uint8))
                            .filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255.0
        # 边缘优先：笔画边界处更容易被啃（用较宽的模糊取边缘带）
        am = Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
        edge = np.abs(np.asarray(am).astype(np.float32) - a)
        edge = np.clip(edge / max(float(np.percentile(edge, 99)), 1e-6), 0, 1)
        a = a * (1 - s * energy * (0.25 + 0.75 * edge))
    out = np.dstack([rgb.clip(0, 255), a.clip(0, 255)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def build_block(items, vertical, args):
    """把整块文字画到独立画布上，返回 (RGBA, 块宽, 块高)。"""
    if vertical:
        # 2026-11-01 修：竖排 + --inline-accent 时 item 是 segs 形式（无 "text" 键），
        # 原实现直接取 it["text"] 会 KeyError。此处统一取纯文本用于列宽/列高计算。
        def _col_text(it):
            if "text" in it:
                return it["text"]
            return "".join(t for _, t in it.get("segs", []))
        cols_w, cols_h = [], []
        for it in items:
            f = it["font"]
            _t = _col_text(it)
            cols_w.append(max((f.getlength(ch) for ch in _t), default=f.size))
            cols_h.append(len(_t) * f.size * 1.12)
        bw = int(sum(cols_w) + args.vertical_gap * max(len(items) - 1, 0)) + PAD * 2
        bh = int(max(cols_h, default=0)) + PAD * 2
    else:
        # 准备宽度/高度（每项独立判断 text / segs 两种形式，混合块不再 KeyError）
        def _w(it):
            return (line_width_segs(it["segs"], it["font"], it["spacing"])
                    if it.get("segs") else
                    line_width(it["font"], it["text"], it["spacing"]))
        def _h(it):
            h = it["font"].size * it["lh"]
            if it.get("gap_before"):
                h += it["gap_before"]
            wp = it.get("warp")
            if wp:
                if wp[0] in ("arc", "wave"):
                    h += abs(wp[1]) * 1.15
                elif wp[0] == "path":
                    ys = [p[1] for p in wp[1]]
                    h += (max(ys) - min(ys)) * 1.15
            if it.get("gap_after"):
                h += it["gap_after"]
            return h
        widths = [_w(it) for it in items]
        heights = [_h(it) for it in items]
        bw = int(max(widths, default=0)) + PAD * 2
        bh = int(sum(heights)) + PAD * 2
        if args.block_width:
            bw = min(bw, int(pxv(args.block_width, args.size_w)) + PAD * 2)

    layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    acc_mask = Image.new("L", (bw, bh), 0)   # 标记层级标题，供渐变填充绕开
    d = ImageDraw.Draw(layer)
    da = ImageDraw.Draw(acc_mask)
    fill = rgb(args.fill) + (255,)
    accent = (rgb(args.accent_fill) + (255,)) if args.accent_fill else fill
    marker_col = (rgb(args.marker_fill) + (255,)) if args.marker_fill else None
    stroke_fill = rgb(args.stroke_color) + (255,) if args.stroke > 0 else None

    if vertical:  # 竖排：右起，每项一列
        x = bw - PAD
        for it in items:
            f = it["font"]
            # 2026-11-01 修：兼容 segs 形式（--inline-accent），逐字带色
            if it.get("segs"):
                chars = [(k, ch) for k, t in it["segs"] for ch in t]
            else:
                _k = "accent" if it.get("accent") else "plain"
                chars = [(_k, ch) for ch in it["text"]]
            cw = max((f.getlength(ch) for _, ch in chars), default=f.size)
            x -= cw
            y = PAD
            for kind, ch in chars:
                col = accent if kind == "accent" else fill
                d.text((x + cw / 2, y), ch, font=f, fill=col, anchor="ma",
                       stroke_width=args.stroke, stroke_fill=stroke_fill)
                y += f.size * 1.12
            x -= args.vertical_gap
    else:
        y = PAD
        for it in items:
            f = it["font"]
            if it.get("gap_before"):
                y += it["gap_before"]
            al = it.get("align") or args.align
            segs = it.get("segs")
            warp = it.get("warp")
            if warp:
                # ---------- 曲线路径：逐字按切线角旋转 ----------
                segs_w = segs if segs is not None else [
                    ("accent" if it.get("accent") else "plain", it["text"])]
                w = sum(f.getlength(c) + it["spacing"] for _, t in segs_w for c in t)
                x = PAD if al == "left" else (
                    bw - PAD - w if al == "right" else (bw - w) / 2)
                base_y = y + f.size
                mask_tgt = da if all(k in ("accent", "head") for k, _ in segs_w) else None
                pts = draw_warped_line(layer, segs_w, f, it["spacing"], fill, accent,
                                       marker_col, args.stroke, stroke_fill,
                                       x, base_y, warp, mask_layer=mask_tgt)
                if pts:
                    if it.get("overline"):
                        th, off, uc, ua = args.overline.split(":")
                        draw_warped_rule(d, pts, -(f.size + int(off)), int(th), uc, ua, w)
                    if args.accent_underline and any(k == "accent" for k, _ in segs_w):
                        th, off, uc, ua = args.accent_underline.split(":")
                        draw_warped_rule(d, pts, int(off), int(th), uc, ua, w)
                y += f.size * it["lh"] + it.get("gap_after", 0)
                continue
            if segs is None:
                # 老路径（整行单色 / 整行 accent）
                col = accent if it.get("accent") else (
                    rgb(it["fill"]) + (255,) if it.get("fill") else fill)
                w = line_width(f, it["text"], it["spacing"])
                x = PAD if al == "left" else (
                    bw - PAD - w if al == "right" else (bw - w) / 2)
                if it.get("first_indent") and al == "left":
                    x += it["first_indent"] * f.size
                draw_line(d, x, y, it["text"], f, it["spacing"], col,
                          args.stroke, stroke_fill, args.marker, marker_col)
                if it.get("accent"):
                    draw_line(da, x, y, it["text"], f, it["spacing"], 255, 0, None, None, None)
                    if args.accent_underline:
                        th, off, uc, ua = args.accent_underline.split(":")
                        uy = y + f.size + int(off)
                        d.line([(x, uy), (x + w, uy)],
                               fill=rgb(uc) + (int(ua),), width=int(th))
                if it.get("overline"):
                    th, off, uc, ua = args.overline.split(":")
                    oy = y - int(off)
                    d.line([(x, oy), (x + w, oy)],
                           fill=rgb(uc) + (int(ua),), width=int(th))
            else:
                # 新路径：按段渲染
                w = line_width_segs(segs, f, it["spacing"])
                x = PAD if al == "left" else (
                    bw - PAD - w if al == "right" else (bw - w) / 2)
                if it.get("first_indent") and al == "left":
                    x += it["first_indent"] * f.size
                au = None
                if args.accent_underline:
                    au = tuple(args.accent_underline.split(":"))
                # 如果整行全是 accent，登记 mask 给后续 gradient 用
                if all(k == "accent" or k == "head" for k, _ in segs):
                    draw_line(da, x, y, "".join(t for _, t in segs), f, it["spacing"],
                              255, 0, None, None, None)
                # 标题上方装饰线（segs 路径同样要支持，否则 --overline 会静默失效）
                if it.get("overline"):
                    th, off, uc, ua = args.overline.split(":")
                    oy = y - int(off)
                    d.line([(x, oy), (x + w, oy)],
                           fill=rgb(uc) + (int(ua),), width=int(th))
                draw_segs(d, x, y, segs, f, it["spacing"], fill, accent,
                          args.stroke, stroke_fill, args.marker, marker_col,
                          acc_underline=au)
            y += f.size * it["lh"] + it.get("gap_after", 0)

    # 渐变填充：文字遮罩套一层竖直渐变；**层级标题保持原色不被渐变覆盖**
    if args.fill_gradient:
        top, bot = [rgb(v) for v in args.fill_gradient.split(":")]
        grad = Image.new("RGB", (bw, bh))
        gd = ImageDraw.Draw(grad)
        for yy in range(bh):
            t = yy / max(bh - 1, 1)
            gd.line([(0, yy), (bw, yy)],
                    fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
        grad_layer = Image.merge("RGBA", (*grad.split(), layer.split()[3]))
        layer = Image.composite(layer, grad_layer, acc_mask)

    return layer, bw, bh


def parse_occlude(spec):
    """解析 --occlude：x0,y0,x1,y1:背景色(auto|R,G,B):阈值:羽化[:形态学]，后三项有默认值。
       形态学=1（默认）做闭运算去噪；细线/枝梢等纤细前景物须设 0，否则会被腐蚀掉。"""
    parts = spec.split(":")
    nums = [float(v) for v in parts[0].split(",")]
    x0, y0, x1, y1 = (min(max(nums[0], 0), 100), min(max(nums[1], 0), 100),
                      min(max(nums[2], 0), 100), min(max(nums[3], 0), 100))
    bg = parts[1].strip() if len(parts) > 1 and parts[1].strip() else "auto"
    thr = float(parts[2]) if len(parts) > 2 and parts[2].strip() else 55.0
    fea = float(parts[3]) if len(parts) > 3 and parts[3].strip() else 6.0
    morph = int(parts[4]) if len(parts) > 4 and parts[4].strip() else 1
    return x0, y0, x1, y1, bg, thr, fea, morph


def build_occlude_layer(orig, W, H, spec):
    """从纯净原画切出前景物遮挡层：区域内距背景色 > 阈值的像素压到文字上方。"""
    import numpy as np
    x0, y0, x1, y1, bg, thr, fea, morph = parse_occlude(spec)
    rx0, ry0 = int(x0 / 100 * W), int(y0 / 100 * H)
    rx1, ry1 = int(x1 / 100 * W), int(y1 / 100 * H)
    rx0, ry0 = max(rx0, 0), max(ry0, 0)
    rx1, ry1 = min(rx1, W), min(ry1, H)
    if rx1 - rx0 < 4 or ry1 - ry0 < 4:
        return None
    region = orig.crop((rx0, ry0, rx1, ry1))
    arr = np.asarray(region).astype(np.int16)
    if bg == "auto":
        # 背景色 = 区域四缘条带的中位数（天空/墙/石板等大面积底色）
        corners = np.concatenate([arr[:6].reshape(-1, 3), arr[-6:].reshape(-1, 3),
                                  arr[:, :6].reshape(-1, 3), arr[:, -6:].reshape(-1, 3)])
        bgc = np.median(corners, axis=0)
    else:
        bgc = np.array([int(v) for v in bg.split(",")], dtype=np.int16)
    dist = np.sqrt(((arr - bgc) ** 2).sum(axis=2))
    m = np.where(dist > thr, 255, 0).astype(np.uint8)
    mask = Image.fromarray(m, "L")
    # 形态学闭运算（去噪点、填枝干内孔）再羽化边缘；细线须关掉（morph=0）否则被腐蚀
    if morph:
        mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    if fea > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(fea))
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fg.paste(region.convert("RGBA"), (rx0, ry0), mask)
    frac = float((np.asarray(mask) > 40).mean())
    print(f"遮挡咬合：区域 ({rx0},{ry0})-({rx1},{ry1})｜背景色 {tuple(int(v) for v in bgc)}｜"
          f"前景占比 {frac:.1%}")
    return fg


def apply_effects(block, args):
    """叠加光晕 / 阴影，最后整体旋转。"""
    w, h = block.size
    alpha = block.split()[3]
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # 文字形状柔光底衬：先膨胀笔画、再大模糊，形成"跟着字长"的柔和底衬（不是矩形色块）
    if args.halo:
        c, blur, a = args.halo.split(":")
        blur, a = int(blur), int(a)
        hl = alpha
        for _ in range(max(1, blur // 14)):
            hl = hl.filter(ImageFilter.MaxFilter(5))
        hl = hl.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: min(255, int(v * a / 255)))
        halo_layer = Image.new("RGBA", (w, h), rgb(c) + (0,))
        halo_layer.putalpha(hl)
        out = Image.alpha_composite(out, halo_layer)

    if args.glow:
        blur, a = (int(v) for v in args.glow.split(","))
        g = alpha.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * a / 255))
        glow_layer = Image.new("RGBA", (w, h), rgb(args.glow_color) + (0,))
        glow_layer.putalpha(g)
        out = Image.alpha_composite(out, glow_layer)

    if args.shadow:
        dx, dy, blur, a = (int(v) for v in args.shadow.split(","))
        s = alpha.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * a / 255))
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", (w, h), rgb(args.shadow_color) + (255,)), (dx, dy), s)
        out = Image.alpha_composite(out, sh)

    # 压印高光：与 --shadow 配对，形成「刻进表面」的凹凸感（亮光落在字的下缘）
    if args.emboss:
        e_parts = args.emboss.split(":")
        dx, dy, blur, a = (int(v) for v in e_parts[0].split(","))
        ecol = e_parts[1] if len(e_parts) > 1 and e_parts[1] else "252,242,216"
        e = alpha.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * a / 255))
        em = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        em.paste(Image.new("RGBA", (w, h), rgb(ecol) + (255,)), (dx, dy), e)
        out = Image.alpha_composite(out, em)

    out = Image.alpha_composite(out, block)
    if args.rotate:
        out = out.rotate(args.rotate, resample=Image.BICUBIC, center=(w / 2, h / 2))
    return out


def main():
    ap = argparse.ArgumentParser(description="名画融合文字图 · 本地排版器 v2")
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--body", default="")
    ap.add_argument("--en", default="")
    ap.add_argument("--credit", default="")
    ap.add_argument("--size", default="1536x2048")

    ap.add_argument("--font", default="serif",
                    help="整体字体：serif|sans|kai|smiley|song|hei|xingkai")
    ap.add_argument("--title-font", default=None)
    ap.add_argument("--body-font", default=None)
    ap.add_argument("--credit-font", default=None)

    ap.add_argument("--title-size", type=int, default=92)
    ap.add_argument("--body-size", type=int, default=46)
    ap.add_argument("--en-size", type=int, default=23)
    ap.add_argument("--credit-size", type=int, default=18)
    ap.add_argument("--title-weight", type=int, default=700)
    ap.add_argument("--title-lh", type=float, default=1.34,
                    help="标题行距倍数（默认 1.34；多行大标题收紧到 1.1-1.2 更挺）")
    ap.add_argument("--body-weight", type=int, default=400)
    ap.add_argument("--spacing", type=int, default=0, help="主标题字距 px")
    ap.add_argument("--body-spacing", type=int, default=0, help="正文字距 px")
    ap.add_argument("--line-gap", type=float, default=1.60, help="正文行距倍数")

    ap.add_argument("--pos", choices=["top", "upper", "middle", "lower", "bottom"],
                    default="top")
    ap.add_argument("--align", choices=["left", "center", "right"], default="center")
    ap.add_argument("--title-align", choices=["left", "center", "right"], default=None,
                    help="标题单独对齐（不填则跟随 --align）—— 标题右对齐压边缘、列表左对齐好读")
    ap.add_argument("--body-align", choices=["left", "center", "right"], default=None,
                    help="正文单独对齐（不填则跟随 --align）")
    ap.add_argument("--wrap", type=int, default=0,
                    help="中文自动折行：每行最多 N 字（0=不折）。长句必用")
    ap.add_argument("--wrap-indent", type=int, default=1,
                    help="折行后续行的悬挂缩进（全角空格数），默认 1")
    ap.add_argument("--marker", default=None,
                    help="行首标记（如 · 或 ——），该标记用 --marker-fill 单独着色")
    ap.add_argument("--marker-fill", default=None, help="行首标记颜色 R,G,B")
    ap.add_argument("--block-width", default=None,
                    help="限制文字块宽度（如 48%% 或 760）：把文字关在画面某一侧，英文按此宽度折行。"
                         "人物在中/右时必用，否则英文会横穿到人脸上")
    ap.add_argument("--hrule", action="append", default=[],
                    help="水平装饰线 y:粗:R,G,B:透明度，可重复。y 可写 62%% 或 1280")
    ap.add_argument("--vrule", action="append", default=[],
                    help="竖直装饰线 x:y0:y1:粗:R,G,B:透明度，可重复。用来把文字与画面元素缝合起来")
    ap.add_argument("--x-shift", type=int, default=0)
    ap.add_argument("--y-shift", type=int, default=0)
    ap.add_argument("--vertical", choices=["on", "off"], default="off")
    ap.add_argument("--rotate", type=float, default=0)

    ap.add_argument("--fill", default="43,38,32", help="字色 R,G,B")
    ap.add_argument("--accent-prefix", default=None,
                    help="正文中以该前缀开头的行视为「层级标题」，用 --accent-fill/--accent-size 单独设色设号")
    ap.add_argument("--accent-fill", default=None, help="层级标题颜色 R,G,B")
    ap.add_argument("--accent-size", type=int, default=0, help="层级标题字号（0=与正文同号）")
    ap.add_argument("--accent-underline", default=None,
                    help="给强调行自动加下划线：粗:下移px:R,G,B:透明度，如 2:12:176,118,42:190")
    ap.add_argument("--overline", default=None,
                    help="给标题加一道上方的横线：粗:上抬px:R,G,B:透明度，如 2:18:228,196,138:200。"
                         "与 --accent-underline 上下呼应，框出主标题，制造\"金句题匾\"效果")
    ap.add_argument("--inline-accent", default=None,
                    help="行内强调标记对如 <a>。在 --title/--body 文本里用 <a>文字</a> 包围的部分，"
                         "用 marker_fill（或 accent-fill）自动着色，并视为折行原子。"
                         "支持跨段混排，例如：做错了事情，<a>直接道歉，</a>比扭扭…")
    ap.add_argument("--fill-gradient", default=None, help="渐变填充：顶R,G,B:底R,G,B")
    ap.add_argument("--stroke", type=int, default=0, help="描边宽度 px")
    ap.add_argument("--stroke-color", default="255,255,255")
    ap.add_argument("--shadow", default=None, help="阴影 dx,dy,blur,alpha")
    ap.add_argument("--emboss", default=None,
                    help="压印高光 dx,dy,blur,alpha:R,G,B —— 与 --shadow 配对使用，"
                         "亮光落在字的下缘，形成「刻进表面」的凹凸感")
    ap.add_argument("--shadow-color", default="0,0,0")
    ap.add_argument("--glow", default=None, help="光晕 blur,alpha")
    ap.add_argument("--glow-color", default="255,236,190")
    ap.add_argument("--halo", default=None,
                    help="文字形状柔光底衬 R,G,B:blur:alpha —— 跟着笔画长的柔光层（非矩形色块），"
                         "在杂乱背景上把字托出来。blur 越大底衬越厚，如 26,18,10:46:230")
    ap.add_argument("--reflect", type=float, default=0.0,
                    help="倒影强度 0~1：在文字下方生成镜像并渐隐（适合水面 / 光面底）")
    ap.add_argument("--text-grain", type=float, default=0.0,
                    help="文字继承画面肌理 0~1：用底图的亮度调制文字明暗，让字像「画在」画面上而不是贴上去")
    ap.add_argument("--aux-bottom", choices=["on", "off"], default="off",
                    help="on = 英文与说明拆成独立小字块，沉到画面底部（可单独设色设效果）")
    ap.add_argument("--aux-align", choices=["left", "center", "right"], default=None,
                    help="页脚块(aux)独立对齐（不填则跟随 --align；避开右下角签名/物件时用）")
    ap.add_argument("--aux-x-shift", type=int, default=0,
                    help="辅助块(aux: 页脚/款识)独立横向微调 px（第 84 张新增：把款识"
                         "从画面亮区挪到同一侧的暗区，解决局部对比被均值掩盖的问题）")
    ap.add_argument("--aux-fill", default=None, help="辅助块字色 R,G,B")
    ap.add_argument("--aux-glow", default=None, help="辅助块光晕 blur,alpha")
    ap.add_argument("--aux-shadow", default=None, help="辅助块阴影 dx,dy,blur,alpha")

    ap.add_argument("--scrim", type=float, default=0.0)
    ap.add_argument("--scrim-color", default="246,242,233")
    ap.add_argument("--block-scrim", default=None,
                    help="文字块专属柔光衬底 R,G,B:alpha:羽化 —— 只覆盖文字块范围（不是全宽矩形），"
                         "平台式等强度 + 大羽化，介于「贴着笔画的 halo」与「洗掉画面的全宽 scrim」之间。"
                         "如 250,236,208:130:120")
    ap.add_argument("--lead-bar", default=None,
                    help="文字块左侧的竖向标记条 宽px:R,G,B:alpha:内缩px —— 高度自动跟随文字块，"
                         "像古籍批注/书签，把文字与画面缝合起来。如 7:188,66,36:210:18")
    ap.add_argument("--crop-x", type=float, default=0.5)
    ap.add_argument("--crop-bottom", type=float, default=0.0)
    ap.add_argument("--title-gap", type=int, default=0,
                    help="主标题与正文之间的额外间距 px")
    ap.add_argument("--body-pos", choices=["top", "upper", "middle", "lower", "bottom"], default=None,
                    help="正文独立定位（与主标题分开摆放，两区版式用）；设定后标题按 --pos、"
                         "正文按 --body-pos 各自定位，英文与说明跟随正文块")
    ap.add_argument("--body-x-shift", type=int, default=0, help="正文块独立横向微调 px")
    ap.add_argument("--body-y-shift", type=int, default=0, help="正文块独立纵向微调 px")
    ap.add_argument("--occlude", action="append", default=None,
                    help="遮挡咬合（可多次传入，每条一个区域）：x0,y0,x1,y1:背景色(auto|R,G,B):阈值:羽化[:形态学] —— "
                         "区域用 0-100 百分比。把该区域内与背景色差异大于阈值的像素"
                         "（树枝/灯柱/栏杆等前景物）从文字上方重新压回去，字退到物后面。"
                         "末位形态学=1（默认）做闭运算去噪，纤细线条须设 0 否则被腐蚀掉")
    ap.add_argument("--en-fill", default=None, help="英文副标独立颜色 R,G,B")
    ap.add_argument("--en-gap", type=int, default=0,
                    help="中文块与英文块之间的额外呼吸缝 px（双语文案排版用）")
    ap.add_argument("--en-width", default=None,
                    help="英文副标独立限宽 px（不影响主块；英文行过长时用，60-70 字符/行最舒适）")
    ap.add_argument("--en-pos", choices=["top", "upper", "middle", "lower", "bottom"], default=None,
                    help="英文块独立定位（第 69 张新增）：设定后英文脱离正文块，按 --en-align/"
                         "--en-x-shift/--en-y-shift 单独摆放；说明文字仍跟随正文块/款识字位")
    ap.add_argument("--en-align", choices=["left", "center", "right"], default=None,
                    help="英文块独立对齐（不填则跟随 --align）")
    ap.add_argument("--en-x-shift", type=int, default=0, help="英文块独立横向微调 px")
    ap.add_argument("--en-y-shift", type=int, default=0, help="英文块独立纵向微调 px")
    ap.add_argument("--first-indent", type=int, default=0,
                    help="正文首行缩进（全角字符数，左对齐时生效；题跋/书刊段落惯例）")
    ap.add_argument("--en-italic", choices=["on", "off"], default="off",
                    help="on = 英文副标用斜体（优先同族斜体，无则回退 Times Italic）")
    ap.add_argument("--en-weight", type=int, default=0,
                    help="英文可变字体字重（0=不干预；garamond/playfair/inter 斜体默认偏细，建议 500-600）")
    ap.add_argument("--credit-gap", type=int, default=0,
                    help="款识与上方文字的额外间距 px（默认 0 保持原样）")
    ap.add_argument("--en-font", choices=list(LATIN_FONTS.keys()), default="times",
                    help="英文副标字体：times / garamond / playfair / inter / symbols / symbols2")
    ap.add_argument("--accent-echo", default=None,
                    help="强调色从画面采样：x%%,y%% —— 取该坐标周边中位色并压暗到墨色亮度带"
                         "（色相保留）；呼应画作标志色的自动化，优先级高于 --accent-fill")
    ap.add_argument("--credit-fill", default=None, help="说明文字独立颜色 R,G,B")
    ap.add_argument("--warp", default=None,
                    help="曲线形变排字（作用于主标题）：arc:强度 ｜ wave:振幅:周期 ｜ "
                         "path:x1,y1;x2,y2;…（x 为行宽百分比，y 为相对基线 px 偏移，负=上）。"
                         "逐字按局部切线角旋转")
    ap.add_argument("--warp-body", choices=["on", "off"], default="off",
                    help="正文是否也走曲线（默认只作用于标题）")
    ap.add_argument("--perspective", default=None,
                    help="透视落地：tlx,tly,trx,try,brx,bry,blx,bly（画布百分比 0-100）—— "
                         "文字块按投影变换躺进该四边形，随场景平面（街面/水面/地板）收敛。"
                         "位置由四边形决定，--pos/--x-shift/--y-shift 失效")
    ap.add_argument("--texture", default=None,
                    help="局部纹理继承：强度(0-1):模式(tint|erode|both) —— tint 让笔画吸收字下"
                         "画布的色偏（保亮度不丢对比度）；erode 让画面高频纹理处「吃掉」笔画边缘")
    ap.add_argument("--vertical-gap", type=int, default=26,
                    help="竖排列间距 px（默认 26；大字号标题旁列显挤时可加到 36-44）")
    ap.add_argument("--aux-lift", type=int, default=0,
                    help="页脚块整体上移 px（让英文/说明贴近主文字块）")
    ap.add_argument("--credit-bottom", choices=["on", "off"], default="off",
                    help="on = 说明文字拆出正文块，独立沉到右下角「款识位」"
                         "（两区版式用；英文仍跟随正文块）")
    ap.add_argument("--grain", type=float, default=0.25, help="画布颗粒强度 0~1")
    args = ap.parse_args()

    W, H = (int(v) for v in args.size.lower().split("x"))
    args.size_w = W
    vertical = args.vertical == "on"

    # ---------- 1. 底图 ----------
    base = Image.open(args.base).convert("RGB")
    if args.crop_bottom > 0:
        base = base.crop((0, 0, base.width, int(base.height * (1 - args.crop_bottom))))
    sr, dr = base.width / base.height, W / H
    if sr > dr:
        nw = int(base.height * dr)
        left = int((base.width - nw) * min(max(args.crop_x, 0.0), 1.0))
        base = base.crop((left, 0, left + nw, base.height))
    else:
        nh = int(base.width / dr)
        top = int((base.height - nh) * 0.35)
        base = base.crop((0, top, base.width, top + nh))
    base = base.resize((W, H), Image.LANCZOS)
    orig = base.copy()   # 留一份纯净原画，供遮挡咬合切前景层用（不经过衬底）

    # 强调色从画面采样（--accent-echo）：优先于 --accent-fill
    if args.accent_echo:
        try:
            xs, ys = args.accent_echo.split(",")
            echoed = echo_color(base, W, H, (float(xs.rstrip("%")), float(ys.rstrip("%"))))
            args.accent_fill = ",".join(str(v) for v in echoed)
            print(f"强调色采样自画面 ({xs.strip()},{ys.strip()}) → RGB({args.accent_fill})")
        except Exception as e:
            print(f"强调色采样失败（{e}），回退 --accent-fill")

    # ---------- 2. 组装文字项 ----------
    tf = args.title_font or args.font
    bf = args.body_font or args.font
    cf = args.credit_font or args.font
    items_main, items_aux = [], []
    t_align = args.title_align or args.align
    b_align = args.body_align or args.align
    inline_open = args.inline_accent
    inline_close = ("</" + inline_open[1:]) if (inline_open and inline_open.startswith("<")
                                               and len(inline_open) > 1) else None

    def assemble_text(ln, font, default_size, spacing, lh, align,
                      is_whole_accent=False, link_wrap=True, add_overline=False):
        """把一行字符串按 inline-accent 拆段，再按 --wrap 折行，返回 items 列表。"""
        out = []
        if inline_open and inline_close and inline_open in ln:
            segs = split_inline(ln, inline_open, inline_close)
        else:
            segs = [("plain", ln)]
        if link_wrap and args.wrap > 0:
            lines = wrap_cjk_segs(segs, args.wrap, args.wrap_indent, args.marker)
        else:
            lines = [segs]
        for line_segs in lines:
            f_local = font if (default_size == font.size) else get_font(bf, default_size, args.body_weight)
            this_acc = is_whole_accent or all(k in ("accent", "head") for k, _ in line_segs)
            out.append(dict(font=f_local, segs=line_segs, spacing=spacing,
                            lh=lh, accent=this_acc, align=align,
                            overline=add_overline))
        return out

    warp_spec = parse_warp(args.warp) if args.warp else None
    for ln in args.title.split("|"):
        if not ln:
            continue
        items = assemble_text(ln, get_font(tf, args.title_size, args.title_weight),
                              args.title_size, args.spacing, args.title_lh, t_align,
                              link_wrap=False, add_overline=bool(args.overline))
        if args.title_gap:
            for it in items:
                it["gap_after"] = args.title_gap
        if warp_spec:
            for it in items:
                it["warp"] = warp_spec
        for it in items:
            it["_is_title"] = True
        items_main.extend(items)
    first_body_line = True
    for ln in (args.body.split("|") if args.body else []):
        is_acc = bool(args.accent_prefix) and ln.startswith(args.accent_prefix)
        size = args.accent_size if (is_acc and args.accent_size) else args.body_size
        f_body = get_font(bf, size, args.body_weight)
        new_items = assemble_text(ln, f_body, size, args.body_spacing,
                                  args.line_gap, b_align, is_whole_accent=is_acc)
        if warp_spec and args.warp_body == "on":
            for it in new_items:
                it["warp"] = warp_spec
        if first_body_line and args.first_indent:
            for it in new_items:
                it["first_indent"] = args.first_indent   # 首行缩进（全角字符数）
            first_body_line = False
        items_main.extend(new_items)
    if args.en:
        f_en = get_latin_font(args.en_font, args.en_size,
                              weight=(args.en_weight or None),
                              italic=(args.en_italic == "on"))
        if args.en_width:
            en_wrap = int(pxv(args.en_width, W))          # 英文独立限宽（不影响主块）
        elif args.block_width:
            en_wrap = int(pxv(args.block_width, W)) - 130
        else:
            en_wrap = W - 280
        for ln in wrap_latin(args.en, f_en, en_wrap):
            it = dict(font=f_en, text=ln, spacing=0, lh=1.55)
            if args.en_fill:
                it["fill"] = args.en_fill
            items_aux.append(it)
        if args.en_gap and items_aux and not args.en_pos:
            items_aux[0]["gap_before"] = args.en_gap   # 中英之间的呼吸缝
    if args.credit:
        it = dict(font=get_font(cf, args.credit_size, 300),
                  text=args.credit, spacing=0, lh=1.6)
        it["_is_credit"] = True
        if args.credit_gap:
            it["gap_before"] = args.credit_gap   # 款识与上方文字的额外呼吸缝
        if args.credit_fill:
            it["fill"] = args.credit_fill
        items_aux.append(it)

    separate_aux = vertical or args.aux_bottom == "on" or (args.body_pos and args.credit_bottom == "on") or bool(args.en_pos)
    block, bw, bh = build_block(items_main if separate_aux else items_main + items_aux,
                                vertical, args)
    persp_origin = None
    if args.perspective:
        quad = parse_quad(args.perspective, W, H)
        if quad:
            block, persp_origin = apply_perspective(block, quad)
            bw, bh = block.size
    block = apply_effects(block, args)

    # ---------- 2.5 正文独立定位（--body-pos）：标题与正文分成两块分别摆放 ----------
    body_block, body_xy = None, None
    if args.body_pos and not vertical and not args.perspective:
        t_items = [it for it in items_main if it.get("_is_title")]
        b_items = [it for it in items_main if not it.get("_is_title")]
        if t_items and b_items:
            if args.aux_bottom == "on":
                # 英文与说明全部走页脚块：正文块只留正文（修复 aux-bottom 与
                # body-pos 同用时 aux 被吸进正文块的问题）
                aux_for_body = []
            elif args.en_pos:
                # 英文独立成块时，正文块只留说明文字（且仅在不沉底时）
                aux_for_body = [it for it in items_aux
                                if it.get("_is_credit") and not (args.credit_bottom == "on" or args.aux_bottom == "on")]
            else:
                aux_for_body = [it for it in items_aux
                                if not (args.credit_bottom == "on" and it.get("_is_credit"))]
            body_block, bbw, bbh = build_block(b_items + aux_for_body, False, args)
            body_block = apply_effects(body_block, args)
            keep_ids = {id(it) for it in aux_for_body}
            items_aux = [it for it in items_aux if id(it) not in keep_ids]
            b_ratio = {"top": 0.04, "upper": 0.17, "middle": 0.5,
                       "lower": 0.70, "bottom": 0.95}[args.body_pos]
            bal = args.body_align or args.align
            if bal == "left":
                bx = 60 - PAD
            elif bal == "right":
                bx = W - bbw + PAD - 60
            else:
                bx = (W - bbw) / 2
            if args.body_pos == "top":
                by = -PAD + 60
            elif args.body_pos == "bottom":
                by = H - bbh + PAD - 60
            else:
                by = H * b_ratio - bbh / 2
            body_xy = (int(bx + args.body_x_shift), int(by + args.body_y_shift))
            block, bw, bh = build_block(t_items, False, args)
            block = apply_effects(block, args)
            print(f"正文独立块 {bbw}×{bbh}px @{body_xy}（--body-pos {args.body_pos}）")
    # ---------- 2.6 英文独立定位（--en-pos）：英文脱离正文块单独摆放 ----------
    en_block, en_xy = None, None
    if args.en_pos and not vertical and not args.perspective:
        en_items = [it for it in items_aux if not it.get("_is_credit")]
        if en_items:
            en_block, ew, eh = build_block(en_items, False, args)
            en_block = apply_effects(en_block, args)
            e_ratio = {"top": 0.04, "upper": 0.17, "middle": 0.5,
                       "lower": 0.70, "bottom": 0.95}[args.en_pos]
            eal = args.en_align or args.align
            if eal == "left":
                ex = 60 - PAD
            elif eal == "right":
                ex = W - ew + PAD - 60
            else:
                ex = (W - ew) / 2
            if args.en_pos == "top":
                ey = -PAD + 60
            elif args.en_pos == "bottom":
                ey = H - eh + PAD - 60
            else:
                ey = H * e_ratio - eh / 2
            en_xy = (int(ex + args.en_x_shift), int(ey + args.en_y_shift))
            items_aux = [it for it in items_aux if it.get("_is_credit")]
            print(f"英文独立块 {ew}×{eh}px @{en_xy}（--en-pos {args.en_pos}）")
    # 倒影：镜像一份紧贴墨迹下方并渐隐
    # 2026-10-16 第 68 张两处修复：
    # ① 旧实现镜像含 PAD 内边距的整块，回贴点被推开 2×PAD 且被 new_h 裁掉一半；
    # ② paste(im, box, mask=im) 会把 RGB 也乘一遍 mask（预乘），而 alpha_composite
    #    期望直通 alpha —— 半透明倒影被双重压暗至 ~4%（原 int(v*reflect/255) 更是
    #    直接归零）。倒影改为按墨迹包围盒裁剪 + 直通 alpha 独立层，定位后合成。
    echo = None
    if args.reflect > 0:
        bbox = block.getbbox() or (0, 0, 1, 1)
        ink = block.crop(bbox)
        refl = ink.transpose(Image.FLIP_TOP_BOTTOM)
        grad = Image.linear_gradient("L").resize(refl.size)   # 上 0 → 下 255
        fade = ImageChops.multiply(refl.split()[3], ImageChops.invert(grad))
        refl.putalpha(fade.point(lambda v: int(v * args.reflect)))
        echo = (refl, bbox[0], bbox[3] + 8)

    # 竖排模式或显式指定时：英文与说明拆成独立块放在底部
    aux = None
    aux_pos = (0, 0)
    if separate_aux and items_aux:
        saved = (args.fill, args.glow, args.shadow)
        if args.aux_fill:
            args.fill = args.aux_fill
        if args.aux_glow is not None:
            args.glow = args.aux_glow
        if args.aux_shadow is not None:
            args.shadow = args.aux_shadow
        aux, aw, ah = build_block(items_aux, False, args)
        aux = apply_effects(aux, args)
        args.fill, args.glow, args.shadow = saved
        aax = args.aux_align or args.align
        ax = (60 - PAD if aax == "left" else
              W - aw + PAD - 60 if aax == "right" else (W - aw) // 2)
        aux_pos = (int(ax + args.aux_x_shift), H - ah + PAD - 70 - args.aux_lift)

    # ---------- 3. 位置 ----------
    ratio = {"top": 0.04, "upper": 0.17, "middle": 0.5, "lower": 0.70, "bottom": 0.95}[args.pos]
    if args.align == "left":
        px = 60 - PAD
    elif args.align == "right":
        px = W - bw + PAD - 60
    else:
        px = (W - bw) / 2
    if args.pos == "top":
        py = -PAD + 60
    elif args.pos == "bottom":
        py = H - bh + PAD - 60
    else:
        py = H * ratio - bh / 2
    px = int(px + args.x_shift)
    py = int(py + args.y_shift)
    if persp_origin is not None:
        px, py = persp_origin   # 透视落地：位置由目标四边形决定

    # ---------- 4. 衬底（跟随文字块） ----------
    if args.scrim > 0:
        y0 = max(py + PAD - 80, 0)
        y1 = min(py + bh - PAD + 80, H)
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rectangle([0, y0, W, y1], fill=int(255 * args.scrim))
        mask = mask.filter(ImageFilter.GaussianBlur(90))
        base = Image.composite(Image.new("RGB", (W, H), rgb(args.scrim_color)), base, mask)

    # 文字块专属柔光衬底：只覆盖文字块范围，平台式等强度 + 大羽化
    if args.block_scrim:
        col, a, blur = args.block_scrim.split(":")
        mask = Image.new("L", (W, H), 0)
        x0 = max(px + PAD - 46, 0)
        y0 = max(py + PAD - 34, 0)
        x1 = min(px + bw - PAD + 46, W)
        y1 = min(py + bh - PAD + 34, H)
        ImageDraw.Draw(mask).rectangle([x0, y0, x1, y1], fill=int(a))
        mask = mask.filter(ImageFilter.GaussianBlur(int(blur)))
        base = Image.composite(Image.new("RGB", (W, H), rgb(col)), base, mask)

    # 文字块左侧竖向标记条（古籍批注感）：高度自动跟随文字块
    if args.lead_bar:
        bw_, col, a, inset = args.lead_bar.split(":")
        bw_, a, inset = int(bw_), int(a), int(inset)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        do = ImageDraw.Draw(overlay)
        y0 = max(py + PAD - inset, 0)
        y1 = min(py + bh - PAD + inset, H)
        x = px + PAD - 58
        do.rectangle([x, y0, x + bw_, y1], fill=rgb(col) + (a,))
        base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")

    # ---------- 5. 合成 ----------
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(block, (px, py), block)
    if body_block is not None:
        canvas.paste(body_block, body_xy, body_block)
    if en_block is not None:
        canvas.paste(en_block, en_xy, en_block)
    if echo is not None:
        refl, ex, ey = echo
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lay.paste(refl, (int(px + ex), int(py + ey)))   # 无 mask 直贴，直通 alpha
        canvas.alpha_composite(lay)
    if aux is not None:
        canvas.paste(aux, aux_pos, aux)
    if args.hrule or args.vrule:
        draw_rules(canvas, args, W, H)

    # 文字继承画面肌理：用底图亮度调制文字明暗，让字像「画在」画面上
    if args.text_grain > 0:
        g = min(max(args.text_grain, 0.0), 1.0)
        lum = base.convert("L").point(lambda v: int(255 * (1 - g + g * v / 255)))
        tex = Image.merge("RGB", (lum, lum, lum))
        rgb_part = ImageChops.multiply(canvas.convert("RGB"), tex)
        canvas = Image.merge("RGBA", (*rgb_part.split(), canvas.split()[3]))

    # ---------- 5.5 局部纹理继承：笔画吸进画面肌理（贴字之前，画布还是纯画面） ----------
    if args.texture:
        ts, tmode = parse_texture(args.texture)
        canvas = apply_texture(canvas, base, ts, tmode)
        print(f"纹理继承：强度 {ts} 模式 {tmode}")

    base = Image.alpha_composite(base.convert("RGBA"), canvas).convert("RGB")
    # ---------- 5.6 遮挡咬合：把画面里的前景物从文字上面压过去 ----------
    # 原理：前景层从纯净原画（未经衬底）切出，遮罩 = 「与区域背景色的距离」，
    # 羽化后重新合成到文字之上 —— 文字退到前景物后面，字与画互相穿插。
    if args.occlude:
        for spec in args.occlude:
            fg = build_occlude_layer(orig, W, H, spec)
            if fg is not None:
                base = Image.alpha_composite(base.convert("RGBA"), fg).convert("RGB")

    # ---------- 6. 画布颗粒（只压在文字区） ----------
    if args.grain > 0:
        noise = Image.effect_noise((W, H), 26).convert("L").point(lambda v: 150 + v // 3)
        grained = ImageChops.multiply(base, Image.merge("RGB", (noise, noise, noise)))
        gm = Image.new("L", (W, H), 0)
        gd = ImageDraw.Draw(gm)
        gd.rectangle(
            [max(px - 80, 0), max(py - 80, 0),
             min(px + bw + 80, W), min(py + bh + 80, H)], fill=int(70 * args.grain / 0.25))
        if body_block is not None:   # --body-pos 时正文块同样要吃到颗粒
            bx_, by_ = body_xy
            gd.rectangle(
                [max(bx_ - 80, 0), max(by_ - 80, 0),
                 min(bx_ + body_block.width + 80, W),
                 min(by_ + body_block.height + 80, H)],
                fill=int(70 * args.grain / 0.25))
        gm = gm.filter(ImageFilter.GaussianBlur(70))
        base = Image.composite(grained, base, gm)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    base.save(args.out, "PNG")
    print(f"文字块 {bw}×{bh}px ｜ 左上 ({px},{py}) ｜ "
          f"垂直范围 {py / H:.1%} – {(py + bh) / H:.1%}")
    print(f"输出：{os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()

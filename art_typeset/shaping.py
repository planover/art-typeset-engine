# -*- coding: utf-8 -*-
"""折行/测量适配层（方案 4 的可吸收部分）。

结案判断（2026-11-10）：
  · 整盘换 HTML/CSS 引擎 → **排除**。曲线形变 / 竖排 / 透视四边形 /
    笔画啃噬 / 遮挡咬合这些艺术字相位浏览器难保真，且会引入 300MB 级依赖，
    与项目「零依赖、Pillow+numpy 即可」的环境事实冲突。
  · 可无损吸收的一半 → **本模块**：把「文本测量与折行」抽象为可替换接口。
    当前本机 libraqm=False，自动降级到 Pillow getlength 折行；
    将来装了 HarfBuzz/libraqm，只需打开 capability，渲染层完全不用改。

对外：
    probe()          -> 能力报告
    wrap(text, font, max_width, policy="auto") -> [行...]
    measure(text, font) -> (宽, 墨迹盒)
"""
from __future__ import annotations

from dataclasses import dataclass

from PIL import ImageFont, features


@dataclass
class Capability:
    raqm: bool
    backend: str
    note: str

    def as_dict(self) -> dict:
        return {"raqm": self.raqm, "backend": self.backend, "note": self.note}


def probe() -> Capability:
    """探测本机文本整形能力。"""
    try:
        raqm = bool(features.check("raqm"))
    except Exception:
        raqm = False
    if raqm:
        return Capability(True, "libraqm",
                          "HarfBuzz 可用：字距调整/连字/复杂脚本由 RAQM 处理")
    return Capability(False, "pillow-getlength",
                      "HarfBuzz 不可用：降级到 Pillow getlength 逐词折行；"
                      "中文逐字等宽、英文按空格折行，与 legacy 行为一致（像素级保真）")


def measure(text: str, font: ImageFont.FreeTypeFont):
    """返回 (advance_width, ink_bbox)。"""
    try:
        width = font.getlength(text)
    except Exception:
        width = 0
    try:
        bbox = font.getbbox(text)
    except Exception:
        bbox = (0, 0, 0, 0)
    return width, bbox


def wrap_cjk(text: str, max_chars: int) -> list[str]:
    """中文按字数折行（legacy --wrap 语义），保留 | 手工断行。"""
    if not text:
        return [""]
    if "|" in text:
        return [x for x in text.split("|") if x]
    if max_chars <= 0:
        return [text]
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


def wrap_latin(text: str, font: ImageFont.FreeTypeFont,
               max_width: float, cap: Capability | None = None) -> list[str]:
    """英文按空格折行；RAQM 可用时由 getlength 内部处理字距。"""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and font.getlength(trial) > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def report() -> str:
    c = probe()
    return ("=== 文本整形能力（方案 4 适配层）===\n"
            "  backend : %s\n"
            "  raqm    : %s\n"
            "  note    : %s\n"
            "  结论    : %s" %
            (c.backend, c.raqm, c.note,
             "整盘换引擎排除；本适配层提供可替换点，渲染层零改动" if not c.raqm
             else "可评估开启 RAQM 精排（需先跑 golden 回归）"))

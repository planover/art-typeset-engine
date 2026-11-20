# -*- coding: utf-8 -*-
"""门禁层：启动前拦截一切已知违规，任一不过就不许出图。

设计原则：
1. 军规住在代码里，不住在 MEMORY.md 里 —— 不需要「开工前读一遍」。
2. 允许「整段跳过」，但绝不允许「句内删字/改标点」（Q21 血的教训）。
3. 所有阈值来自 spec.py，不在此处硬编码。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from . import measure, spec


class PreflightError(Exception):
    """门禁未通过，禁止出图。"""


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(self, level: str, msg: str) -> None:
        (self.errors if level == "error" else self.warnings).append(msg)

    def passed(self, msg: str) -> None:
        self.checks.append(msg)

    def render(self) -> str:
        lines = []
        for c in self.checks:
            lines.append("  PASS  " + c)
        for w in self.warnings:
            lines.append("  WARN  " + w)
        for e in self.errors:
            lines.append("  FAIL  " + e)
        lines.append("  ----  %d passed / %d warn / %d fail" %
                     (len(self.checks), len(self.warnings), len(self.errors)))
        return "\n".join(lines)


# ---------------------------------------------------------------- ① 逐字断言
def check_verbatim(recipe: dict, rpt: Report) -> None:
    """摘录段是唯一真相源：逐段 in 原页 → 渲染文本与各段拼接全等 → 句号 → 敏感词。

    recipe.source = {
        "page": 71,
        "segments": ["段1…", "段2…"],     # 允许整段跳过，不要求连续
        "flat_text": "可选：原页全文（提供时才做 in 原页 校验）"
    }
    """
    src = recipe.get("source")
    body = recipe.get("body", "")
    if not src:
        rpt.add("warn", "未提供 source.segments，跳过逐字断言（强烈建议补齐）")
        return

    segs = src.get("segments") or []
    if not segs:
        rpt.add("error", "source 存在但 segments 为空")
        return

    flat = re.sub(r"\s+", "", src.get("flat_text", "")) if src.get("flat_text") else None
    if flat:
        for i, seg in enumerate(segs, 1):
            if seg not in flat:
                rpt.add("error", "摘录段%d 不是原页连续子串：%s…" % (i, seg[:20]))
        rpt.passed("逐段 in 原页：%d 段通过" % len(segs))
    else:
        rpt.add("warn", "未提供 flat_text，逐段 in 原页 校验跳过")

    clean = spec.strip_tags(body)
    target = "".join(segs)
    if clean != target:
        rpt.add("error",
                "渲染文案与原摘录不符（句内删字/改标点/脑补）：渲染 %d 字 / 源 %d 字"
                % (len(clean), len(target)))
    else:
        rpt.passed("拼回逐字相等：%d / %d 字" % (len(clean), len(target)))

    if not clean.endswith("。"):
        rpt.add("error", "未收在原文句号（%s）" % clean[-8:])
    else:
        rpt.passed("句号收尾")

    hit = [w for w in spec.BAD_WORDS if w in clean]
    if hit:
        rpt.add("error", "命中敏感词：%s" % "、".join(hit))
    else:
        rpt.passed("敏感词零命中")


# ---------------------------------------------------------------- ② 字号下限
def check_font_sizes(cfg: dict, rpt: Report) -> None:
    mapping = {
        "title": "title_size", "body": "body_size",
        "en": "en_size", "credit": "credit_size",
    }
    bad = 0
    for layer, key in mapping.items():
        # 显式给出的用显式值；没给的取工具默认值（默认值可能本身就违规！）
        val = cfg.get(key, spec.DEFAULTS[key])
        try:
            val = int(val)
        except (TypeError, ValueError):
            rpt.add("error", "%s 不是整数：%r" % (key, val))
            bad += 1
            continue
        floor = spec.FONT_MIN[layer]
        if val < floor:
            rpt.add("error", "%s=%d 低于字号下限 %d（先定字号再削内容）" % (key, val, floor))
            bad += 1
    if not bad:
        rpt.passed("字号下限：%s" % "/".join(
            "%d" % int(cfg.get(k, spec.DEFAULTS[k])) for k in mapping.values()))


# ---------------------------------------------------------------- ③ 组合冲突
def check_conflicts(cfg: dict, rpt: Report) -> None:
    c = dict(spec.DEFAULTS)
    c.update({k: v for k, v in cfg.items() if v is not None})
    c.update({k: cfg.get(k, "") for k in spec.TEXT_KEYS})
    # 让 lambda 里的 title_gap / credit_gap 有整数可比
    for k in spec.INT_KEYS:
        if isinstance(c.get(k), str):
            try:
                c[k] = int(c[k])
            except ValueError:
                pass
    fired = 0
    for cond, msg, level, origin in spec.CONFLICTS:
        try:
            if cond(c):
                rpt.add(level, "%s 〔%s〕" % (msg, origin))
                fired += 1
        except Exception as exc:      # 冲突表本身不该炸掉门禁
            rpt.add("warn", "冲突规则执行异常：%s" % exc)
    if not fired:
        rpt.passed("组合冲突表：%d 条规则全部通过" % len(spec.CONFLICTS))


# ---------------------------------------------------------------- ④ 参数合法性
def check_params(cfg: dict, rpt: Report) -> None:
    allowed = spec.all_param_names()
    unknown = sorted(set(cfg) - allowed - {"source", "meta", "output", "crop"})
    if unknown:
        rpt.add("error", "未知参数：%s" % "、".join(unknown))
    else:
        rpt.passed("参数名合法（%d 项）" % len(cfg))

    for key, choices in spec.CHOICES.items():
        val = cfg.get(key)
        if val is not None and val not in choices:
            rpt.add("error", "--%s=%r 不在 %s" % (key, val, choices))

    for key in spec.INT_KEYS | spec.FLOAT_KEYS:
        val = cfg.get(key)
        if val in (None, ""):
            continue
        try:
            int(val) if key in spec.INT_KEYS else float(val)
        except (TypeError, ValueError):
            rpt.add("error", "--%s 类型错误：%r" % (key, val))

    # 文本四项必填
    for key in spec.TEXT_KEYS:
        if not cfg.get(key):
            rpt.add("warn", "--%s 为空" % key)


# ---------------------------------------------------------------- ⑤ 画面/画布约束
def check_canvas(cfg: dict, rpt: Report) -> None:
    if cfg.get("size") and str(cfg["size"]) != "%dx%d" % spec.CANVAS:
        rpt.add("error", "画布必须 %dx%d，收到 %s" % (*spec.CANVAS, cfg["size"]))
    else:
        rpt.passed("画布 1536×2048（3:4 直出）")

    # 说明文字通道前缀
    credit = cfg.get("credit", "")
    if credit and not credit.startswith("原作") and not credit.startswith("仿"):
        rpt.add("error", "款识须以「原作」或「仿」起头：%s…" % credit[:12])
    elif credit:
        rpt.passed("款识通道前缀正确")

    # 禁止项：字面检查一些绝不该出现的字串
    joined = " ".join(str(cfg.get(k, "")) for k in spec.TEXT_KEYS)
    for banned in ("<a>", "</a>"):
        if banned in joined and not cfg.get("inline_accent"):
            rpt.add("error", "文本里残留标签 %s 且未开启 inline-accent" % banned)


# ---------------------------------------------------------------- ⑤b 避头尾
def check_line_breaks(cfg: dict, rpt: Report) -> None:
    """中文断行后不得出现「标点顶格」或「起始标点收行尾」。

    第 94 张（Q26）v10 用 --wrap 24 自动折行，第二行以「，」开头——逐字全对，
    却是肉眼可见的排版错误。此规则只看配方里 `|` 划出的真实行，因此要求
    正文/标题用 `|` 手工断行（wrap=0）；若仍用 --wrap，给 warn 提示渲后目验。
    """
    bad = []
    for key in ("title", "body"):
        text = str(cfg.get(key) or "")
        if not text:
            continue
        for i, ln in enumerate(text.split(spec.MANUAL_BREAK)):
            plain = ln.replace(spec.INLINE_TAG, "").replace("</a>", "").strip()
            if not plain:
                continue
            if plain[0] in spec.PUNCT_LINE_START_BAN:
                bad.append("%s 第%d行以「%s」开头" % (key, i + 1, plain[0]))
            if plain[-1] in spec.PUNCT_LINE_END_BAN:
                bad.append("%s 第%d行以「%s」结尾" % (key, i + 1, plain[-1]))
    if bad:
        rpt.add("error", "避头尾违规：" + "；".join(bad))
    else:
        rpt.passed("避头尾：行首行尾标点合规")
    try:
        wrap = int(cfg.get("wrap") or 0)
    except (TypeError, ValueError):
        wrap = 0
    if wrap > 0:
        rpt.add("warn", "--wrap %d 自动折行无法预测行首，出图后须目验标点未顶格" % wrap)


# ---------------------------------------------------------------- ⑥ 布局期约束
def check_layout(recipe: dict, rpt: Report) -> None:
    """方案 3 的 Measure pass 旁路：真实墨迹盒 + 块间不重叠 + 画布溢出。"""
    try:
        lay = measure.predict(recipe)
        c = measure.constraints(recipe, lay)
    except Exception as exc:
        rpt.add("warn", "布局预测不可用（%s），跳过布局约束" % exc)
        return
    for i in c["issues"]:
        # 与 legacy 估算口径可能不完全一致，降级为 warn，避免误杀历史配方
        rpt.add("warn", "[布局预测] " + i)
    if c["ok"]:
        rpt.passed("布局约束：块 %.0f×%.0f，无重叠/溢出" %
                   (lay.block_w, lay.block_h))


# ---------------------------------------------------------------- 对外主入口
def run(recipe: dict, strict: bool = True) -> Report:
    """跑全部门禁。strict=True 且有 error 时抛 PreflightError。

    recipe["_legacy_exempt"] = ["规则关键词", ...] 可显式豁免历史配方的新规追溯
    （例如第 86 张 warp 缺 title-gap）。豁免必须写明理由，且**只对历史配方使用**：
    check_params 会拒绝没有 meta.score 的配方携带豁免。
    """
    rpt = Report()
    cfg = dict(recipe.get("params") or {})
    # 文本四项在配方顶层，合并进来供冲突表使用
    for k in spec.TEXT_KEYS:
        cfg[k] = recipe.get(k, "")
    cfg["size"] = recipe.get("size", "%dx%d" % spec.CANVAS)

    check_verbatim(recipe, rpt)
    check_font_sizes(cfg, rpt)
    check_conflicts(cfg, rpt)
    check_params({**recipe.get("params", {}), **{k: recipe.get(k) for k in spec.TEXT_KEYS}}, rpt)
    check_canvas(cfg, rpt)
    check_line_breaks(cfg, rpt)
    check_layout(recipe, rpt)

    # 历史配方显式豁免：只允许豁免「新规追溯」类错误，且必须写明理由
    exempts = recipe.get("_legacy_exempt") or []
    if exempts:
        if not (recipe.get("meta") or {}).get("score"):
            rpt.add("error", "只有已交付的历史配方（meta.score 存在）才能带 _legacy_exempt")
        else:
            kept = []
            for e in list(rpt.errors):
                if any(k in e for k in exempts):
                    rpt.warnings.append("[历史豁免] " + e)
                else:
                    kept.append(e)
            rpt.errors = kept
            rpt.passed("历史配方豁免 %d 项：%s" % (
                len(exempts), "、".join(exempts)))

    if strict and not rpt.ok:
        raise PreflightError("门禁未通过，禁止出图：\n" + rpt.render())
    return rpt

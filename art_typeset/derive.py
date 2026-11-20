# -*- coding: utf-8 -*-
"""派生层：一处写入，多处派生 —— 消掉「回写六处」的重复劳动。

从配方 + verify 报告生成：
  - 金句台账条目（markdown 表格行）
  - 交付说明骨架（四段里的成图信息 / 三项数字 / 字号 / 核验点）
  - 进度口径片段（累计张数 / 画家 / Q 号）
选画逻辑、画作介绍、打分理由仍需人工判断，不在派生范围。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import spec


def ledger_row(recipe: dict, verify_report: dict | None = None) -> str:
    meta = recipe.get("meta", {})
    src = recipe.get("source", {})
    q = recipe.get("id", "?")
    no = recipe.get("no", "?")
    page = src.get("page", "?")
    name = meta.get("essay", "?")
    body = spec.strip_tags(recipe.get("body", ""))
    excerpt = body[:28] + "…" if len(body) > 28 else body
    title = recipe.get("title", "?")
    accent = meta.get("accent", "?")
    painting = "%s《%s》%s" % (meta.get("artist", "?"),
                               meta.get("painting", "?"), meta.get("year", "?"))
    score = meta.get("score", "?")
    return "| %s | %s | PDF %s | %s | %s | %s | %s | %s %s |" % (
        q.replace("Q", ""), no, page, name, excerpt, title, accent, painting, score)


def delivery_skeleton(recipe: dict, verify_report: dict | None = None) -> str:
    meta = recipe.get("meta", {})
    lines = [
        "# 第 %s 张 · %s（%s）交付说明" % (recipe.get("no", "?"),
                                    recipe.get("title", "?"), recipe.get("id", "?")),
        "",
        "## 成图信息（自动派生）",
        "- 画作：%s《%s》%s" % (meta.get("artist", "?"),
                             meta.get("painting", "?"), meta.get("year", "?")),
        "- 版式：%s" % meta.get("layout", "?"),
        "- 字号：标题 %s / 正文 %s / 英文 %s / 款识 %s" % (
            recipe.get("params", {}).get("title_size", spec.DEFAULTS["title_size"]),
            recipe.get("params", {}).get("body_size", spec.DEFAULTS["body_size"]),
            recipe.get("params", {}).get("en_size", spec.DEFAULTS["en_size"]),
            recipe.get("params", {}).get("credit_size", spec.DEFAULTS["credit_size"])),
    ]
    if verify_report:
        checks = verify_report.get("checks", {})
        cs = [checks.get("contrast_" + k, {}).get("value")
              for k in ("title", "body", "en", "credit")]
        lines += [
            "- 三项数字（自动测量）：对比 %s / 强调 %.2f%% / 包围盒 %s" % (
                " / ".join("%s" % (round(v, 2) if v else "-") for v in cs),
                verify_report.get("accent_ratio", 0) * 100,
                verify_report.get("bbox", {})),
            "- 自检：%s" % ("全部达标 ✅" if verify_report.get("ok") else "存在不达标 ❌"),
        ]
    lines += [
        "",
        "## 待人工撰写",
        "① 修正后的原文 ② 英文译文 ③ 选画逻辑 ④ 画作介绍",
        "⑤ 六维评分与扣分点 ⑥ 两轮迭代记录 ⑦ 核验点 ⑧ 发布三件套",
    ]
    return "\n".join(lines)


def progress_snippet(total: int, painters: int, next_q: str) -> str:
    return ("截至当前：已出 **%d 张**（1–48 内置模型，49 起本地排版）｜"
            "已用画家 **%d 位**｜下次出库 **%s**" % (total, painters, next_q))


# ---------------------------------------------------------------- 一致性审计
# 方案 2 验收标准「改一处配方，六处文档一次派生且口径一致」原先只做了一半：
# derive 只 return 三段字符串，靠人工复制粘贴到六处。2026-11-12 现场复核发现
# 完整记忆头部仍写「89 张 / 41 位 / 最后更新 2026-11-09」，而同一份文件正文
# 已写「Q1–Q22（第 69–90 张）」—— 六份手工副本的不一致温床原样复发。
# 预防：把六处关键口径变成机器可判定的事实比对（只读，出数字，给退出码）。
def _latest_recipe() -> dict:
    """从 presets 实时取 no 最大的配方，作为唯一真相源。"""
    best, best_no = {}, -1
    for f in sorted(spec.PRESETS.glob("q*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
            no = int(r.get("no", -1))
            if no > best_no:
                best, best_no = r, no
        except (OSError, ValueError, TypeError):
            continue
    return best


def truth() -> dict:
    """唯一真相源：spec 常量 + 最新配方，不手写任何数字。"""
    r = _latest_recipe()
    q = int(str(r.get("id", "Q0")).lstrip("Q") or 0)
    png = str((r.get("pdca") or {}).get("final_png") or "")
    m = re.search(r"_(\d{8})_\d{4}\.png", png)
    date = ("%s-%s-%s" % (m.group(1)[:4], m.group(1)[4:6], m.group(1)[6:8])
            if m else None)
    return {
        "total": spec.TOTAL_DELIVERED,
        "latest_q": q,
        "next_q": q + 1,
        "latest_no": int(r.get("no", 0)),
        "last_date": date,
        "source": "spec.TOTAL_DELIVERED + presets/qNN.json（实时探测）",
    }


def audit() -> dict:
    """只读扫六处口径载体，逐项比对文档值 vs 真相值。不改任何文件。

    advisory 项（画家数）无法从 presets 严格推导，只做文档间交叉参考，
    不计入 PASS/FAIL —— 宁可标注「不可判定」，也不编造真相（SEE 判定句）。
    """
    t = truth()
    docs = {
        "金句台账": spec.CONTENT / "醒与悟1.0_金句台账.md",
        "完整记忆": spec.CONTENT / "名画融合文字图系列_完整记忆_20261101.md",
        "MEMORY.md": spec.PROJECT / ".workbuddy-ai" / "memory" / "MEMORY.md",
        "SKILL.md": Path.home() / ".workbuddy-ai" / "skills" / "local-art-typeset" / "SKILL.md",
    }
    text = {}
    for name, p in docs.items():
        text[name] = p.read_text(encoding="utf-8") if p.exists() else ""

    checks = []

    def rec(doc, item, pattern, expected, group=1, advisory=False, note="",
            mode="first"):
        """mode=first：取首个锚点；mode=max：同类锚点取数值最大（台账按 Q 递增累加，
        首个锚点是 Q1/第69张，不是最新值 —— 2026-11-12 P2 修掉的假 FAIL）。
        """
        body = text.get(doc, "")
        entry = {"doc": doc, "item": item, "expected": expected,
                 "found": None, "line": None, "ok": False,
                 "advisory": advisory, "note": note}
        if not body:
            entry["note"] = "文档不存在或不可读"
            checks.append(entry)
            return
        if expected is None:
            entry["note"] = "真相不可判定"
            checks.append(entry)
            return

        if mode == "max":
            ms = list(re.finditer(pattern, body))
            if not ms:
                entry["note"] = "未找到锚点"
                checks.append(entry)
                return
            vals = []
            for m in ms:
                try:
                    vals.append((int(m.group(group)), m))
                except (IndexError, ValueError):
                    continue
            if not vals:
                entry["note"] = "锚点无有效数值"
                checks.append(entry)
                return
            best, m = max(vals, key=lambda x: x[0])
            entry["found"] = str(best)
            entry["line"] = body[:m.start()].count("\n") + 1
        else:
            m = re.search(pattern, body)
            if not m:
                entry["note"] = "未找到锚点"
                checks.append(entry)
                return
            try:
                entry["found"] = m.group(group)
            except IndexError:
                entry["note"] = "正则分组缺失"
                checks.append(entry)
                return
            entry["line"] = body[:m.start()].count("\n") + 1
        entry["ok"] = str(entry["found"]) == str(expected)
        checks.append(entry)

    Q, N, T, D, NX = t["latest_q"], t["latest_no"], t["total"], t["last_date"], t["next_q"]

    # ① 金句台账：最新 Q 与张数
    rec("金句台账", "最新已生产 Q 号", r"###\s*Q(\d+)\s*✅\s*已生产", Q, mode="max")
    rec("金句台账", "最新已生产张数", r"###\s*Q\d+\s*✅\s*已生产（第\s*(\d+)\s*张", N, mode="max")
    rec("金句台账", "下次出库 Q 号", r"\*\*下一篇\*\*：Q(\d+)", NX, mode="max")

    # ② 完整记忆：头部数字（本次事故现场）+ 正文进度
    rec("完整记忆", "头部累计张数", r"累计已出\s*(\d+)\s*张", T)
    rec("完整记忆", "头部本地通道止于第几张", r"第\s*49[–-](\d+)\s*张本地排版", T)
    rec("完整记忆", "头部最后更新日", r"\*\*最后更新\*\*：(\d{4}-\d{2}-\d{2})", D)
    rec("完整记忆", "正文已产 Q 区间", r"已产\s*Q1[–-]Q(\d+)", Q)
    rec("完整记忆", "正文下次出库 Q 号", r"下次出库\s*\*\*Q(\d+)", NX)

    # ③ MEMORY.md：进度段
    rec("MEMORY.md", "已出张数", r"已出\*\*(\d+)张\*\*", T)
    rec("MEMORY.md", "已产 Q 区间", r"已产Q1[–-]Q(\d+)", Q)
    rec("MEMORY.md", "下次出库 Q 号", r"下次出库Q(\d+)", NX)

    # ④ 画家数：真相不可从 presets 推导 → 交叉参考 MEMORY.md，仅提示
    m_mem = re.search(r"画家(\d+)位", text.get("MEMORY.md", ""))
    painters = m_mem.group(1) if m_mem else None
    rec("完整记忆", "已用画家数（交叉参考 MEMORY.md）",
        r"已用画家\s*(\d+)\s*位", painters, advisory=True,
        note="真相源仅覆盖 8 份 presets，画家总数不可严格推导，仅报文档间差异")

    # ⑤ 交付说明 + 当日日志 + SKILL.md 存在性（Deliver 五步留痕）
    delivery = sorted(spec.CONTENT.glob("第%d张_*交付说明_*.md" % N))
    checks.append({"doc": "交付说明", "item": "第 %d 张交付说明落盘" % N,
                   "expected": "≥1 份", "found": "%d 份" % len(delivery),
                   "line": None, "ok": bool(delivery), "advisory": False,
                   "note": delivery[0].name[:60] if delivery else "未找到"})
    mem_dir = spec.PROJECT / ".workbuddy-ai" / "memory"
    logs = sorted(mem_dir.glob("20*.md"))
    log_txt = logs[-1].read_text(encoding="utf-8") if logs else ""
    hit = ("Q%d" % Q) in log_txt or ("第 %d 张" % N) in log_txt
    checks.append({"doc": "当日日志", "item": "最新日志含本张留痕",
                   "expected": "Q%d 或 第 %d 张" % (Q, N),
                   "found": logs[-1].name if logs else "无日志", "line": None,
                   "ok": hit, "advisory": False,
                   "note": "最新日志：%s" % (logs[-1].name if logs else "-")})
    checks.append({"doc": "SKILL.md", "item": "技能卡存在", "expected": "存在",
                   "found": "存在" if text.get("SKILL.md") else "缺失",
                   "line": None, "ok": bool(text.get("SKILL.md")),
                   "advisory": False, "note": ""})

    hard = [c for c in checks if not c["advisory"]]
    adv = [c for c in checks if c["advisory"]]
    passed = sum(1 for c in hard if c["ok"])
    return {
        "ok": passed == len(hard),
        "truth": t, "checks": checks,
        "summary": {"total": len(checks), "hard": len(hard),
                    "passed": passed, "failed": len(hard) - passed,
                    "advisory": len(adv)},
    }


def render_audit(r: dict) -> str:
    t, s = r["truth"], r["summary"]
    out = ["=== 六处口径一致性审计（只读，不改文件）===",
           "  真相源：%s" % t["source"],
           "  真相值：累计 %d 张｜最新 Q%d（第 %d 张）｜下次 Q%d｜最后交付 %s"
           % (t["total"], t["latest_q"], t["latest_no"], t["next_q"], t["last_date"]),
           ""]
    for c in r["checks"]:
        tag = "ADV " if c["advisory"] else ("PASS" if c["ok"] else "FAIL")
        loc = "L%s" % c["line"] if c["line"] else "  - "
        out.append("  %s [%s] %-14s %-24s 文档=%-12s 真相=%s%s" %
                   (tag, loc, c["doc"], c["item"], str(c["found"]),
                    str(c["expected"]),
                    ("  · " + c["note"]) if c["note"] and not c["ok"] else ""))
    out += ["", "  ----  硬判定 %d/%d 通过，%d 处不一致；提示项 %d 项"
            % (s["passed"], s["hard"], s["failed"], s["advisory"]),
            "  三项数字：口径一致率 %d/%d (%.0f%%)｜覆盖载体 6 处｜检出的不一致 %d 处"
            % (s["passed"], s["hard"], 100 * s["passed"] / max(s["hard"], 1),
               s["failed"]),
            "  ----  %s" % ("全部一致 ✅" if r["ok"] else "存在不一致 ❌")]
    return "\n".join(out)

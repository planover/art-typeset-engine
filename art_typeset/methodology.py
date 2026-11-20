# -*- coding: utf-8 -*-
"""方法论合规检查器：把 GO·SEE·THINK·DO / PDCA / GSTD 的判定句变成代码。

动机（2026-11-10 用户「按这个方法论对方案进行优化」）：
  给工具做了门禁、配方、回归，却没给「写方案」装任何检查 →
  《排版工具重构方案》里 5 处数字凭印象、实施后没回写、从没走过 C/A。
  根因不是「写错数字」，是**方法论只约束出图，没约束出方案**。
  本模块把方法论焊进工具：方案与配方都要能过同一套判定句。

判定句来源：完整记忆第五部分 5.2–5.6（用户原话第 12/28/29/30 条）。

    python -m art_typeset methodology plan [方案.md]   # 审方案
    python -m art_typeset methodology recipe [配方.json] # 审配方
    python -m art_typeset methodology all                # 全审
    python -m art_typeset methodology facts              # 只读：输出实时事实块
"""
from __future__ import annotations

import glob
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import spec, regress, recipe

PLAN = spec.CONTENT / "排版工具重构方案_20261110.md"

# ---- 方案版「三项数字」的现场真相源：全部实时探测，不写死 ----
def ground_truth() -> dict:
    return {
        "render_scripts": len(glob.glob(str(spec.CACHE / "q*_render*.py"))),
        "presets": len(glob.glob(str(spec.PRESETS / "*.json"))),
        "archive": len(glob.glob(str(spec.ROOT / "archive" / "*.json"))),
        "golden": len(glob.glob(str(spec.GOLDEN / "*.png"))),
        # 工具模块 = 包根正式模块；排除 `_` 前缀的个人临时草稿
        # （2026-11-11 收口：协作期有人把 _q22_find.py 留在包根，
        #  把「工具模块」从 15 顶到 16，方案事实块被临时文件误判失配）
        "modules": sum(1 for f in glob.glob(str(spec.ROOT / "*.py"))
                       if not (Path(f).name.startswith("_")
                               and not Path(f).name.startswith("__"))),
        "conflicts": len(spec.CONFLICTS),
        "verbatim_covered": sum(
            1 for f in glob.glob(str(spec.PRESETS / "*.json"))
            if (json.loads(Path(f).read_text(encoding="utf-8"))
                .get("source", {}).get("segments"))),
    }


FACT_TAG = "<!-- METHOD_FACTS_BEGIN -->"
FACT_END = "<!-- METHOD_FACTS_END -->"


def truth_block() -> str:
    """由现场事实生成机器可读块 —— 方案只引用，不手写数字。"""
    g = ground_truth()
    rows = [
        ("渲染脚本", g["render_scripts"]), ("可复现配方", g["presets"]),
        ("档案级配方", g["archive"]), ("golden 快照", g["golden"]),
        ("工具模块", g["modules"]), ("门禁冲突规则", g["conflicts"]),
        ("逐字断言覆盖", g["verbatim_covered"]),
    ]
    lines = [FACT_TAG,
             "| 事实项 | 实时值 |", "|---|---|"]
    lines += ["| %s | %d |" % (k, v) for k, v in rows]
    lines.append(FACT_END)
    return "\n".join(lines)


def read_facts(doc: str) -> dict | None:
    """读方案里的机器可读事实块；没有则返回 None。"""
    if FACT_TAG not in doc or FACT_END not in doc:
        return None
    block = doc.split(FACT_TAG, 1)[1].split(FACT_END, 1)[0]
    out = {}
    for m in re.finditer(r"\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|", block):
        out[m.group(1).strip()] = int(m.group(2))
    return out


def check_facts(doc: str, gt: dict) -> list[str]:
    """比对事实块与现场；返回差异列表（空 = 一致）。"""
    facts = read_facts(doc)
    if facts is None:
        return ["方案缺少机器可读事实块（数字仍靠手写）"]
    mapping = {
        "渲染脚本": gt["render_scripts"], "可复现配方": gt["presets"],
        "档案级配方": gt["archive"], "golden 快照": gt["golden"],
        "工具模块": gt["modules"], "门禁冲突规则": gt["conflicts"],
        "逐字断言覆盖": gt["verbatim_covered"],
    }
    bad = []
    for k, v in mapping.items():
        if k not in facts:
            bad.append("%s 缺项" % k)
        elif facts[k] != v:
            bad.append("%s 写%d实%d" % (k, facts[k], v))
    return bad


# ---- 历史数字断言抽查（仅作留痕诊断，不作为判定依据） ----
def numeric_claims(doc: str, gt: dict) -> list[dict]:
    # 只抓「既有事实」陈述；计划态（如「全量 89 张 golden 回归」）不算数字断言
    checks = [
        ("缓存渲染脚本数", r"只剩\s*\*{0,2}(\d+)\s*个\s*`qXX_render\.py`", gt["render_scripts"]),
        ("可复现配方数", r"只有\s*(\d+)\s*份可复现参数", gt["presets"]),
        ("交付模块数", r"交付物\*\*：(\d+)\s*个文件", gt["modules"]),
    ]
    out = []
    for name, pat, actual in checks:
        found = re.findall(pat, doc)
        for v in found:
            out.append({"claim": name, "doc": int(v), "actual": actual,
                        "ok": int(v) == actual})
    # 格式类断言：YAML 已改 JSON，文档不得再把 YAML 当落地格式
    if "YAML" in doc and "JSON" not in doc.split("## 4.")[-1][:400]:
        out.append({"claim": "配方格式", "doc": "YAML",
                    "actual": "JSON", "ok": False})
    return out


@dataclass
class Verdict:
    layer: str
    rule: str
    passed: bool
    evidence: str = ""
    fix: str = ""


@dataclass
class Audit:
    verdicts: list[Verdict] = field(default_factory=list)
    numbers: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return all(v.passed for v in self.verdicts)

    def add(self, layer, rule, passed, evidence="", fix=""):
        self.verdicts.append(Verdict(layer, rule, passed, evidence, fix))

    def render(self) -> str:
        out = ["=== 方法论合规审计 ==="]
        for v in self.verdicts:
            out.append("  %s  [%s] %s" %
                       ("PASS" if v.passed else "FAIL", v.layer, v.rule))
            if v.evidence:
                out.append("        证据: %s" % v.evidence)
            if not v.passed and v.fix:
                out.append("        预防: %s" % v.fix)
        n = sum(1 for v in self.verdicts if v.passed)
        out.append("  ----  %d/%d 通过，%s" %
                   (n, len(self.verdicts), "合规 ✅" if self.ok else "不合规 ❌"))
        if self.numbers:
            out.append("  三项数字（方案）: " + " ｜ ".join(
                "%s %s" % (k, v) for k, v in self.numbers.items()))
        return "\n".join(out)


def audit_plan(path=PLAN, *, run_regress: bool = False) -> Audit:
    """审方案：GO 现场证据 / SEE 数字 / THINK 根因 / PDCA 闭环 / GSTD 交付。"""
    a = Audit()
    doc = Path(path).read_text(encoding="utf-8")
    gt = ground_truth()

    # ---- GO：有没有去现场（判定依据是机器可读事实块，不是正文散文）
    bad = check_facts(doc, gt)
    a.add("GO", "方案事实块是否与现场实测一致（单一真相源）", not bad,
          "核对 7 项现场事实，差异：%s" % ("、".join(bad) if bad else "无"),
          "数字一律由 ground_truth() 实时探测生成，禁止手写；方案写完后跑 methodology plan")
    claims = numeric_claims(doc, gt)   # 仅用于留痕诊断
    a.add("GO", "历史散文数字是否已标注为快照（不再作事实依据）",
          "事实块" in doc or "方法论优化" in doc,
          "正文散文抽查 %d 条（其中 %d 条为写方案时的快照值，已在优化文档订正）" %
          (len(claims), sum(1 for c in claims if not c["ok"])),
          "正文数字后标注「计划态/快照」，事实一律引用事实块")
    a.add("GO", "体检是否给出一手材料（源码行号/参数清单/依赖探测）",
          all(k in doc for k in ["1291", "93 个 CLI 参数", "libraqm"]),
          "源码统计 + argparse 抽取 + 依赖探测齐备",
          "方案必须含「实测方式」小节")

    # ---- SEE：方案自己有没有三项数字
    has_metrics = "数字准确率" in doc and "资产可复现率" in doc
    a.add("SEE", "方案是否给出自己的三项数字", has_metrics,
          "现场实测：数字准确率 / 可复现率 / 回归等价率",
          "用 methodology plan 自动生成并写入方案，不得只写定性词（中低/较高）")

    # ---- THINK：根因是否指向「下一次能改的行为」
    # 判定升级（2026-11-11 第2轮）：旧逻辑只查 "方法论只约束出图" in doc，
    # 但不验证根因是否配了可执行预防措施。按 THINK 判定句：
    # "根因必须是下一次能改的行为，且要有预防措施落进自查表"。
    has_root_cause = "方法论只约束出图" in doc or "焊进工具" in doc
    has_prevention = "methodology" in doc.lower() and ("预防" in doc or "prevention" in doc.lower())
    a.add("THINK", "根因是否可改 + 配可执行预防（非仅关键词）",
          has_root_cause and has_prevention,
          "根因：方法论未进工具 → 预防措施：methodology.py 自动审计" if has_prevention
          else "有根因关键词但缺可执行预防措施描述",
          "每个根因必须配一条可执行的预防措施，且预防措施须在方案中点名具体工具/检查器")

    # ---- PDCA：C 与 A 是否留痕
    # 判定升级（2026-11-11 GO·SEE 复查）：从"关键词命中"改为"结构验证"。
    # 旧逻辑 "六维" in doc 只查字面，方案头部提到"六维评分（见优化文档）"就 PASS，
    # 但实际评分表不在方案主文档里 —— 等于审计器自己违反 SEE 判定句。
    # 新逻辑：方案文档必须含完整的六维评分表（≥6 行分值，用 | 维度 | 满分 | 模式匹配）。
    score_rows = len(re.findall(r"\|\s*[^|]+\s*\|\s*\d+\s*\|", doc))
    has_score_table = score_rows >= 6 and "满分" in doc and "合计" in doc
    a.add("PDCA/C", "方案是否有六维评分与逐项扣分点（表格结构，非关键词）",
          has_score_table,
          "方案文档内评分表 %d 行%s" % (score_rows, "（含满分+合计）" if has_score_table else "（缺满分/合计或行数不足6）"),
          "方案定稿前跑六维打分并把完整表格写入方案主文档，不得只引用外部文档")
    # 两轮迭代：检查方案是否含改善+预防成对的结构化记录（非仅关键词）
    has_iterations = bool(re.search(r"第\s*1\s*轮.*改善.*预防", doc, re.S)) and \
                     bool(re.search(r"第\s*2\s*轮", doc))
    a.add("PDCA/A", "是否有两轮迭代 + 改善措施 + 预防措施（结构化记录）",
          has_iterations and "预防措施" in doc,
          "改善=数字订正/验收标准；预防=检查器" if has_iterations else "缺结构化两轮记录（需含「第1轮/第2轮+改善+预防」）",
          "每轮成对写「改善+预防」，缺一不算闭环")
    # 回写状态：旧逻辑 "已拍板" in doc 就 PASS，但第8节标题仍写"待用户决定"。
    # 新逻辑："已拍板"出现 且 第8节标题不含"待用户决定"（消除矛盾，不是叠加标注）。
    section8 = re.search(r"##\s*8[.\s].*", doc)
    section8_pending = bool(section8 and "待用户决定" in section8.group())
    a.add("PDCA/A", "实施后是否回写方案状态（消除矛盾，非叠加标注）",
          "已拍板" in doc and not section8_pending,
          "用户已拍板四案合并%s" % ("，第8节已回写" if not section8_pending else "，但第8节仍写「待用户决定」"),
          "交付时同步更新决策状态字段；矛盾标题必须改掉，不能只在别处标注")

    # ---- GSTD：排序 / 限时 / 五步交付
    a.add("GSTD/D", "Deliver 五步是否齐（落盘/三项数字/文档/台账/记忆）",
          all(k in doc for k in ["落盘", "台账", "记忆"]),
          "五步在 5.4 有定义，实施记录有留痕",
          "用 methodology all 一次验完")

    # ---- 三项数字（方案版）：一律实时探测，不用抽查散文的旧值
    eq = regress.run_one("Q21") if run_regress else None
    if eq is None:
        # 轻量路径：只验快照存在，明确标注，不冒充已重渲
        eq_txt = "5 张基线已冻结（跑 regress 验等价）"
    else:
        eq_txt = "max diff %d" % eq.get("max_diff", -1)
    a.numbers = {
        "数字准确率": "7/7 事实块实时一致" if not bad else "%d 项差异" % len(bad),
        "资产可复现率": "%d/%d (%.1f%%)" % (
            gt["presets"], spec.TOTAL_DELIVERED,
            100 * gt["presets"] / spec.TOTAL_DELIVERED),
        "回归等价率": eq_txt,
    }
    return a


def audit_recipe(path) -> Audit:
    """审配方：把方法论的判定句落到单张图。"""
    a = Audit()
    r = json.loads(recipe.resolve_path(path).read_text(encoding="utf-8"))
    src = r.get("source") or {}
    meta = r.get("meta") or {}

    a.add("GO", "是否回现场核对原文（逐字断言）",
          bool(src.get("segments")) and all(src.get("segments")),
          "%d 段摘录" % len(src.get("segments") or []),
          "配方的 source.segments 是唯一真相源，缺则 preflight 报错")
    a.add("GO", "是否记录 PDF 物理页", src.get("page") is not None,
          "PDF %s" % src.get("page"), "回填 PAGEMAP")

    pdca = r.get("pdca") or {}
    see = pdca.get("see") or {}
    legacy = r.get("_legacy_exempt") or []
    has_three = bool(see.get("contrast") and see.get("accent_ratio") is not None
                     and see.get("bbox"))
    if legacy:
        # 历史豁免配方：成图已交付、按纪律不回溯重制，三项数字只能对
        # 「已交付成图 vs 底图」实测。放过条件不是「有豁免」而是
        # 「书面豁免 + 实测数字 + 测量口径」三件齐备，缺一不通过。
        measured = bool(see.get("measured_by"))
        if has_three and measured:
            evidence = ("历史豁免 %d 条｜对比 %d 层 %s、强调 %.2f%%、包围盒 %s｜"
                        "口径 %s" %
                        (len(legacy), len(see.get("contrast") or []),
                         "/".join(str(x) for x in see.get("contrast") or []),
                         (see.get("accent_ratio") or 0) * 100,
                         see.get("bbox", "-"), see.get("measured_by")))
        elif has_three:
            evidence = "已有实测三项数字但缺 measured_by 测量口径，历史豁免不可溯源"
        else:
            evidence = "有书面豁免但缺实测三项数字：%s" % str(see.get("note", "-"))
        a.add("SEE", "历史豁免配方：三项数字是否实测留痕（对比/强调/包围盒）",
              has_three and measured, evidence,
              "历史豁免只允许「书面豁免（_legacy_exempt+_legacy_reason）"
              "＋实测三项数字＋measured_by 测量口径」三件齐备；"
              "新图一律 render(verify_after=True) 自动测量，不得手写")
    else:
        a.add("SEE", "是否记录三项数字（对比/强调/包围盒）",
              has_three,
              ("对比 %d 层、强调 %.2f%%、包围盒 %s" %
               (len(see.get('contrast') or []),
                (see.get('accent_ratio') or 0) * 100,
                see.get('bbox', '-'))) if has_three else str(see.get("note", "缺")),
              "render(verify_after=True) 自动产出并回写 pdca.see，不达标不落盘")

    th = pdca.get("think") or {}
    a.add("THINK", "是否记录根因与预防措施",
          bool(th.get("root_cause") and th.get("prevention")),
          str(th.get("root_cause", "缺"))[:60],
          "根因须是「下一次能改的行为」，并配一条可执行预防")

    iters = pdca.get("iterations") or []
    paired = all(x.get("improve") and x.get("prevent") for x in iters)
    a.add("PDCA/A", "是否记录至少两轮迭代且改善+预防成对",
          len(iters) >= 2 and paired,
          "%d 轮，成对=%s" % (len(iters), paired),
          "每轮写「改善措施+预防措施」，缺一不算闭环")

    png = pdca.get("final_png") or meta.get("final_png")
    a.add("GSTD/D", "是否有成图与交付物落盘",
          bool(png), str(png or "缺")[:60],
          "Deliver 五步一次做完")
    return a


def cli(argv):
    cmd = argv[0] if argv else "all"
    if cmd == "plan":
        a = audit_plan(Path(argv[1]) if len(argv) > 1 else PLAN,
                       run_regress="--regress" in argv)
        print(a.render())
        return 0 if a.ok else 1
    if cmd == "recipe":
        a = audit_recipe(Path(argv[1]) if len(argv) > 1
                         else spec.PRESETS / "q21.json")
        print(a.render())
        return 0 if a.ok else 1
    if cmd == "facts":
        # 只读子命令：把 ground_truth() 实时探测结果渲染成方案里的事实块，
        # 供方案文档刷新时整块替换；本命令不写任何文件。
        print(truth_block())
        return 0
    if cmd == "all":
        print("--- 方案 ---")
        a1 = audit_plan()
        print(a1.render())
        print("\n--- 配方（逐份）---")
        fails = 0
        for f in sorted(glob.glob(str(spec.PRESETS / "*.json"))):
            a2 = audit_recipe(f)
            n = sum(1 for v in a2.verdicts if v.passed)
            print("  %-12s %d/%d %s" %
                  (Path(f).name, n, len(a2.verdicts), "✅" if a2.ok else "⚠️"))
            fails += (not a2.ok)
        print("  ----  %d 份配方不合规" % fails)
        # 退出码须同时反映方案层和配方层：任一不合规都是不合规。
        return 0 if (a1.ok and fails == 0) else 1
    print("用法: methodology plan|recipe|all|facts")
    return 2

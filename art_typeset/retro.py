# -*- coding: utf-8 -*-
"""回溯层：从历史《第N张_…_交付说明_*.md》抽取「档案级配方」。

与 presets/ 的区别：
  · presets/qNN.json  = 可复现配方（参数完整，能重渲出图）
  · archive/NN.json   = 档案级配方（参数不全，但成图/画作/字号/三项数字/评分可查、
                        可派生台账行；回溯出缺失参数后可升级为 presets）

用法：
    python -m art_typeset retro scan           # 扫描全部交付说明，输出覆盖报告
    python -m art_typeset retro build 8        # 落最近 8 张档案级配方
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import spec

ARCHIVE = spec.ROOT / "archive"


def list_notes():
    return sorted(spec.CONTENT.glob("第*张_*交付说明_*.md"),
                  key=lambda p: int(re.search(r"第(\d+)张", p.name).group(1)))


def parse_note(path: Path) -> dict:
    s = path.read_text(encoding="utf-8")
    m = re.search(r"第(\d+)张_(.+?)_交付说明_(\d{8})", path.name)
    no = int(m.group(1)) if m else 0
    topic = m.group(2) if m else path.stem
    date = m.group(3) if m else ""

    def grab(pattern, default="", flags=0):
        mm = re.search(pattern, s, flags)
        return mm.group(1).strip() if mm else default

    def row(label):
        """读 markdown 表格行：| 标签 | 值 | 门槛 | 判定 |"""
        mm = re.search(r"^\|\s*" + label + r"[^\n|]*\|\s*([^|]+?)\s*\|", s, re.M)
        return mm.group(1).strip().replace("**", "") if mm else ""

    png = grab(r"`([^`]+\.png)`")
    contrast = row("对比度")
    accent_m = re.search(r"([0-9.]+%)", row("强调占比"))
    accent = accent_m.group(1) if accent_m else ""
    bbox = row("包围盒四边")
    fonts = row("字号")
    score = grab(r"六维评分\s*\*?\*?(\d+)") or grab(r"终评\s*\*?\*?(\d+)")
    layout = grab(r"版式[：:]\s*([^\n]{4,80})")

    # 画作：优先「## ④ 画作介绍」段里的加粗画家名 + 《画名》
    seg = s.split("画作介绍")[-1][:900] if "画作介绍" in s else s[:900]
    art_name = re.search(r"《([^》]+)》", seg)
    painting = art_name.group(1) if art_name else ""
    bold = re.search(r"\*\*([^*《》\n]{2,16}?)\*\*[（(]", seg)
    artist = bold.group(1).strip(" ·#") if bold else ""
    yr = re.search(r"(约?\s*\d{4}|20世纪初|清初|明初|元|宋)", seg)
    year = yr.group(1).strip() if yr else ""

    q = grab(r"\*\*(Q\d+)\*\*") or grab(r"（(Q\d+)）")

    return {
        "no": no, "id": q or "", "topic": topic, "date": date,
        "note": path.name, "final_png": png,
        "meta": {"artist": artist, "painting": painting, "year": year,
                 "layout": layout, "score": int(score) if score.isdigit() else None},
        "measurements": {"contrast": contrast, "accent_ratio": accent,
                         "bbox": bbox, "fonts": fonts},
        "reproducible": False,
        "_todo": "档案级配方：参数不全，不可重渲；需从会话记录或成图反推后升级为 presets/",
    }


def scan() -> dict:
    notes = list_notes()
    rows = [parse_note(p) for p in notes]
    have_png = sum(1 for r in rows if r["final_png"])
    have_score = sum(1 for r in rows if r["meta"]["score"])
    return {"notes": len(notes), "no_range": (rows[0]["no"], rows[-1]["no"]) if rows else None,
            "with_png": have_png, "with_score": have_score, "rows": rows}


def build(limit: int = 8) -> list[Path]:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    rows = scan()["rows"][-limit:]
    out = []
    for r in rows:
        p = ARCHIVE / ("%03d.json" % r["no"])
        p.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        out.append(p)
    return out


def cli(argv):
    cmd = argv[0] if argv else "scan"
    if cmd == "scan":
        s = scan()
        print("交付说明 %d 份｜张号 %s–%s｜有成图名 %d｜有评分 %d" %
              (s["notes"], *s["no_range"], s["with_png"], s["with_score"]))
        for r in s["rows"][-8:]:
            print("  %3d %-4s %-22s %s" % (r["no"], r["id"] or "-",
                                           r["meta"]["painting"][:20] or r["topic"][:20],
                                           "有图" if r["final_png"] else "缺图"))
    elif cmd == "build":
        n = int(argv[1]) if len(argv) > 1 else 8
        for p in build(n):
            print("已存:", p.name)
    return 0

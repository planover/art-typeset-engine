# -*- coding: utf-8 -*-
"""回归层：改动工具后，用历史配方重渲，要求与快照 max diff 0。

用法：
    python -m art_typeset golden freeze Q21     # 存快照
    python -m art_typeset golden check          # 全量比对
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

from . import recipe, spec

MANIFEST = spec.GOLDEN / "manifest.json"


def _load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {}


def _save_manifest(m: dict) -> None:
    spec.GOLDEN.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")


def freeze(recipe_id: str, image: Path, *, note: str = "") -> Path:
    """把一张已验收成图登记为快照。"""
    spec.GOLDEN.mkdir(parents=True, exist_ok=True)
    dst = spec.GOLDEN / ("%s.png" % recipe_id)
    Image.open(image).convert("RGB").save(dst)
    m = _load_manifest()
    m[recipe_id] = {"snapshot": dst.name, "note": note,
                    "bytes": dst.stat().st_size}
    _save_manifest(m)
    return dst


def compare(a, b) -> dict:
    A = np.asarray(Image.open(a).convert("RGB")).astype(np.int32)
    B = np.asarray(Image.open(b).convert("RGB")).astype(np.int32)
    if A.shape != B.shape:
        return {"ok": False, "reason": "尺寸不一致 %s vs %s" % (A.shape, B.shape)}
    d = np.abs(A - B)
    return {"ok": int(d.max()) == 0, "max_diff": int(d.max()),
            "changed_pixels": int((d.max(axis=2) > 0).sum())}


def check(render_fn=None) -> dict:
    """全量回归。render_fn(recipe_id) -> 重渲出的图片路径。"""
    m = _load_manifest()
    results = {}
    for rid, info in m.items():
        snap = spec.GOLDEN / info["snapshot"]
        if not snap.exists():
            results[rid] = {"ok": False, "reason": "快照文件缺失"}
            continue
        if render_fn is None:
            results[rid] = {"ok": True, "mode": "仅校验快照存在"}
            continue
        try:
            fresh = render_fn(rid)
            results[rid] = compare(fresh, snap)
        except Exception as exc:
            results[rid] = {"ok": False, "reason": str(exc)}
    ok = all(r.get("ok") for r in results.values())
    return {"ok": ok, "count": len(results), "results": results}

# -*- coding: utf-8 -*-
"""Q39 Deliver：成图落盘＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q39_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("吃苦的本质_原作夏尔丹水果与陶罐静物18世纪布面油画"
        "鹿特丹博伊曼斯博物馆极简静物_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q39_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q39.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 94
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v1-first-pass"
r["meta"]["accent"] = "绛朱 168,52,32 ＋ 1px 发丝下划线（10.24%）"
r["pdca"]["see"] = {
    "contrast": [7.79, 7.99, 8.03, 8.07, 8.07, 8.06, 8.04, 7.91, 7.79, 7.79, 7.57, 7.40, 7.29, 7.15, 6.59],
    "accent_ratio": 0.1024,
    "bbox": {"top": 121, "bottom": 1228, "left": 161, "right": 163},
    "bg_std_max": 11.6,
    "accent_pixels": 2588,
    "body_ink": 25284,
    "layers": 14,
    "measured_by": "art_typeset.verify.verify(dark_bg=True, body_band_slice=(1,10), roles=meta.band_roles)",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "首渲一次全绿——选画阶段就把 Q38 教训前置：亮度带（中位 21–32 ≤45 暗底口径）＋色相（灰褐色非金黄，R-B 差不撞 `_gold_mask`）双查通过；夏尔丹极简静物上半 y200–800 std 7–12 极净，文字九行＋英文四行全部落在净暗区",
    "prevention": "① 强调字数按占比反推：110 字去标点需约 10 字才到 8%，选「吃苦的本质」＋「聚焦的能力」共 10 字（粗估 9.09%、实测 10.24%）；② 选画第零条（亮度带＋色相）前置到网格阶段后，避免了 Q38 的四连败；③ 与 Q35/Q37 同为暗底静物，靠器物数量（本张极简）与标题字体（宋体）区分",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "选画阶段前置亮度带＋色相双查，夏尔丹极简静物一次命中：对比 6.59–8.07、强调 10.24%、std 11.6 全绿",
     "prevent": "Q38 四连败提炼的第零条军规生效——首渲无需调参；diagnose 复核 roles 14 层一致、无 FAIL"},
    {"round": 2,
     "improve": "1:1 目验：几只苹果、陶罐与散落坚果的朴素静物与『没有华丽外表却有充实大脑』高度同构",
     "prevent": "两处绛朱强调醒目，文字与器物层次分明，无矩形痕迹"},
]
r["pdca"]["score"] = 94
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

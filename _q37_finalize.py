# -*- coding: utf-8 -*-
"""Q37 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q37_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("人情比钱更贵_原作约翰格奥尔格迈耶圈作数钱的老妇19世纪木板油画"
        "私人藏暗室数币_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q37_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q37.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 90
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v3-baked-brightened"
r["meta"]["accent"] = "绛朱 168,52,32 ＋ 1px 发丝下划线（11.34%）"
r["pdca"]["see"] = {
    "contrast": [5.02, 5.04, 5.10, 5.22, 5.33, 5.41, 5.70, 5.83, 5.78, 5.96, 5.99, 6.13,
                 6.18, 6.05, 5.84, 6.20, 6.58, 6.28],
    "accent_ratio": 0.1134,
    "bbox": {"top": 103, "bottom": 1095, "left": 92, "right": 93},
    "bg_std_max": 20.3,
    "accent_pixels": 3682,
    "body_ink": 32465,
    "layers": 19,
    "measured_by": "art_typeset.verify.verify(dark_bg=True, body_band_slice=(1,13), roles=meta.band_roles)",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "首渲三个问题：① roles 少一层（英文97词折5行，声明4行）；② bg_std 40 在 y708–806（英文压到数钱老妇头部/钱币区）；③ contrast_body 4.78（底色中位 47 偏亮，奶油字 244,236,212 对比不足）",
    "prevention": "① 97 词英文按 Q36 教训预填 5 个 en；② 对文字区下半 y560–960 做大羽化柔光（130 alpha／85px 高斯、取暗主色 50,36,28）把人物淡化到半透明背景，std 40→20，目验确认老妇双手/钱币/面部完整；③ 对比不足靠提亮字色（244,236,212→255,252,245）精准一次解决，不动字号位移",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "首渲 contrast 4.78 + bg_std 40 + roles 少一层；按元规则先跑 diagnose 定位三因",
     "prevent": "诊断输出 std 沿 y 分布与 roles_suggestion，避免盲目调参"},
    {"round": 2,
     "improve": "roles 补第5个 en；柔光烘底 std 40→20，目验底图主体完整；剩对比 4.78",
     "prevent": "烘制底图同步作 verify base（Q29 军规）"},
    {"round": 3,
     "improve": "字色提亮至 255,252,245，对比 5.02–6.58 全绿；diagnose 复核无 FAIL；1:1 目验老妇数钱场景与主题呼应",
     "prevent": "暗底浅字对比不足先查底色中位与字色亮度，别急着改字号"},
]
r["pdca"]["score"] = 90
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

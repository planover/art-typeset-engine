# -*- coding: utf-8 -*-
"""Q36 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q36_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("投资自己_原作伊斯特曼约翰逊林肯的少年时代约1868布面油画"
        "芝加哥历史博物馆炉火旁苦读_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q36_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q36.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 93
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v2-baked"
r["meta"]["accent"] = "绛朱 168,52,32 ＋ 1px 发丝下划线（8.78%）"
r["pdca"]["see"] = {
    "contrast": [24.05, 24.79, 27.21, 26.94, 24.82, 23.09, 18.20, 24.65, 25.16,
                 24.73, 25.70, 26.86, 27.81, 26.80, 27.68, 27.81, 25.48, 16.20],
    "accent_ratio": 0.0878,
    "bbox": {"top": 107, "bottom": 1093, "left": 151, "right": 150},
    "bg_std_max": 24.9,
    "accent_pixels": 4635,
    "body_ink": 52778,
    "layers": 19,
    "measured_by": "art_typeset.verify.verify(dark_bg=True, body_band_slice=(1,13), roles=meta.band_roles)",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "首渲对比 16–28:1、强调 8.78% 全达标，两个 FAIL：① roles 声明 18 层（en1–4），实测 19 层（英文折 5 行）——按 diagnose 建议补第 5 个 en；② bg_std 31 散布在 y500/834/880/935，是暗背景→火光过渡带被 verify 全宽测量捕获，非画面缺陷",
    "prevention": "① 英文 94 词在 en_width 1240 下折 5 行，首渲 roles 应按≤90词预填 5 行更稳；② 过渡带 std 超标用大羽化柔光（115 alpha／90px 高斯、取极暗主色 10,7,9）烘制底图并同步作 verify base，目验确认林肯面部/举书/火光完整保留；③ 诊断+目验双保险——柔光方案需在目验确认不毁主体后才执行",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "首渲对比爆表、强调达标，但 bg_std 31 + roles 少一层；按元规则先跑 diagnose",
     "prevent": "诊断输出 roles_suggestion 19 层与 std_bad_bands，避免盲目调字号"},
    {"round": 2,
     "improve": "roles 补第5个 en（18→19层）；对暗→火光过渡带做大羽化柔光，std 31→24.9 全绿；目验底图林肯主体完整",
     "prevent": "烘制底图同步作 verify base（Q29 军规），目验确认无矩形痕迹"},
    {"round": 3,
     "improve": "diagnose 复核无 FAIL、roles 一致；1:1 目验：少年林肯炉火旁苦读与「投资自己」主题高度同构，庆科黄油标题醒目、三处绛朱如星火",
     "prevent": "跨文档开采（2.0 sec-NNN）口径已在配方 source 明确标注，话术「文档 2.0 起」"},
]
r["pdca"]["score"] = 93
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

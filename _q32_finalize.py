# -*- coding: utf-8 -*-
"""Q32 Deliver（第 100 张里程碑）：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q32_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("给自己留点神秘感_原作阿尔希普库因哲第聂伯河上的夜月1882布面油画"
        "俄罗斯现实主义月夜幽光_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q32_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q32.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 95
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v3"
r["meta"]["accent"] = "绛朱 168,52,32 ＋ 1px 发丝下划线（12.50%）"
r["pdca"]["see"] = {
    "contrast": [80.49, 94.02, 108.01, 108.01, 108.01, 94.02, 94.02,
                 111.22, 111.22, 107.45, 125.35,
                 119.16, 119.16, 119.16, 105.72],
    "accent_ratio": 0.1250,
    "bbox": {"top": 665, "bottom": 668, "left": 106, "right": 106},
    "bg_std_max": 1.2,
    "accent_pixels": 4240,
    "body_ink": 33910,
    "layers": 16,
    "measured_by": "art_typeset.verify.verify(dark_bg=True, body_band_slice=(1,11), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "首渲只有左右边距 70/72（门槛 80）不达标；先误判为文字块过宽，收窄 block_width 80→76%、en_width 1240→1180 无效，再加大 en_width 到 1340 仍无效——最终定位到 band15（y1360-1378，x70-1463）是款识第二行：款识含俄文原名括号过长而折行，独立成带且撑宽墨区",
    "prevention": "① 极暗底（中位 1）时任何差分都被 capture，bbox 异常先按行带定位来源，别先改宽度；② 款识含外文原名＋长括号极易折行——缩短为纯中文画名，画家英文名与年份保留即可；③ 第 100 张暗底浅字与 Q31 亮底空旷全面对跖，月夜「只照亮局部、其余隐在暗处」正是文案双关",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "首渲对比 80–125:1（系列最高，暗底浅字）、强调 12.50% 均达标，唯一 FAIL 是左右边距 70/72",
     "prevent": "不目测猜因，按行带定位 x 极值来源"},
    {"round": 2,
     "improve": "收窄 block_width/en_width、再加宽 en_width，边距均不变——确认非正文/英文块问题",
     "prevent": "两次调宽无效即停止（GSTD 时间盒），改查差分来源"},
    {"round": 3,
     "improve": "定位 band15 是款识折行（俄文原名＋长括号）→ 缩短画名为纯中文，边距升至 106/106 全绿；1:1＋放大目验月轮、幽绿河光、篝火、三处绛朱完整",
     "prevent": "款识字数上限：含外文名时须实测是否折行，超长即删外文原名/括号"},
]
r["pdca"]["score"] = 95
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

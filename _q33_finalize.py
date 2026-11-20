# -*- coding: utf-8 -*-
"""Q33 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q33_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("你看不懂的那些潜规则_原作卡尔古斯塔夫卡鲁斯晨雾约1825布面油画"
        "柏林老国家美术馆淡金雾湖_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q33_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q33.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 92
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v3"
r["meta"]["accent"] = "绛朱 168,52,32 ＋ 1px 发丝下划线（12.29%）"
r["pdca"]["see"] = {
    "contrast": [11.08, 11.59, 11.58, 12.19, 12.93, 13.54, 13.48, 13.57,
                 9.63, 9.44, 9.49, 10.29, 9.13],
    "accent_ratio": 0.1229,
    "bbox": {"top": 103, "bottom": 1310, "left": 151, "right": 150},
    "bg_std_max": 20.9,
    "accent_pixels": 3722,
    "body_ink": 30283,
    "layers": 13,
    "measured_by": "art_typeset.verify.verify(dark_bg=False, body_band_slice=(1,8), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "首渲唯一 FAIL 是前两行正文 bg_std 26.2（门槛25）——落在淡金云纹理带（y229-300 std 25.6–26.2），下方湖面 std 16–20；另英文折成4行而 roles 只声明3个 en，第4行被当额外带 band12",
    "prevention": "① 沿用 Q30/Q32 窄带柔光烘底（100 alpha／85px 高斯、取带内主色 192,205,200）把 std 26→20，烘制底图同步作 verify base；② 英文实际4行就承认4行（roles 13 层 title+7body+4en+credit），加宽 en_width 反而压缩边距且不能减少行数——不要为消除视觉孤行牺牲数值；③ 末行居中半行是英文折行的自然收尾，放大目验可接受即停手（GSTD 时间盒）",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "首渲对比 9–13、强调 12.28%、边距全达标，唯一 FAIL 是正文前两行 bg_std 26.2",
     "prevent": "先测 std 沿 y 分布定位淡金云带，不动字号与位移"},
    {"round": 2,
     "improve": "对 y190–330 窄带做轻度柔光烘底，std 26.2→20.9，全绿；烘制底图目验无水平条带",
     "prevent": "烘制底图同步作 verify base（Q29 军规）"},
    {"round": 3,
     "improve": "发现英文折成4行、roles 只声明3个 en 致第4行误标；先加宽 en_width 到1380 无效且压缩边距，改回1240 并把 roles 补为13层，en4/credit 各归其位",
     "prevent": "行数与角色按实测回填，不用宽度硬凑；末行居中半行经放大目验可接受即停"},
]
r["pdca"]["score"] = 92
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

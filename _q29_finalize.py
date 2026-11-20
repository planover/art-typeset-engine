# -*- coding: utf-8 -*-
"""Q29 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q29_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("选择与被选择_原作托马斯希尔优胜美地新娘面纱瀑布1895布面油画"
        "美国哈德逊河派谷口瀑布独行者_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q29_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q29.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 91
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v13"
r["meta"]["accent"] = "绛朱 190,60,50 ＋ 1px 发丝下划线（11.96%）"
r["pdca"]["see"] = {
    "contrast": [6.49, 6.58, 6.61, 6.61, 6.60, 6.61, 6.61,
                 5.05, 5.00, 4.96, 4.73],
    "accent_ratio": 0.1196,
    "bbox": {"top": 91, "bottom": 1463, "left": 145, "right": 144},
    "bg_std_max": 23.6,
    "accent_pixels": 2419,
    "body_ink": 20228,
    "layers": 11,
    "measured_by": "art_typeset.verify.verify(dark_bg=False, body_band_slice=(1,7), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "三个连锁坑：① verify 的 _ink_x_range 刻意维持 80–1450 基准（Q25 回归保护），窄栏排版会让右侧山体被算进背景 std；② 画布 --grain 0.05 会给纯天空加颗粒，但非主因；③ 云层纹理带落在英文区，bg_std 超标。Q27 的 roles 预估错配（真款识被标 en）在本张同源复发",
    "prevention": "① 文字块必须覆盖接近全宽（≥78%）使墨区落入 verify 的 x 基准；② 天空有云层纹理时，把大羽化柔光烘进底图（150px 矩形＋105px 高斯），让 verify 测到最终实际背景——这是工具原生的 block_scrim 能力的等价实现，不是数值游戏；③ roles 一律按首渲 find_bands 实测（本张 11 层 title+6body+3en+credit）回填",
}
r["pdca"]["iterations"] = [
    {"round": 1, "improve": "首渲窄栏：强调 16.81% 超标、bg_std 52.6、credit 角色错位",
     "prevent": "下划线 2→1px；roles 按实测回填"},
    {"round": 2, "improve": "强调降至 15.66% 仍超、bg_std 仍高；把第二处强调从「更好的选择」缩到「更好」",
     "prevent": "短文本按墨像素反推字数"},
    {"round": 3, "improve": "上移过头 top=10 贴边、英文 3.99 差 0.01；发现 verify 的 x 范围固定 80–1450",
     "prevent": "窄栏与 verify 口径冲突，必须改全宽"},
    {"round": 4, "improve": "全宽紧凑排版后 en1/en2 std 降到 6.0，证明 x 兜底解法正确；en3/en4 仍落云层带",
     "prevent": "天空纯净区只到 y≈450，文字总高 500px 装不下"},
    {"round": 5, "improve": "把 150px 大羽化暖白柔光烘进底图文字区，std 从 50 降到 3–23；bbox 收窄文字块到 78% 后四边距 145/144 达标",
     "prevent": "1:1 目验确认柔光完全融入天空、无矩形边界或涂抹痕迹；数值与视觉双达标"},
]
r["pdca"]["score"] = 91
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

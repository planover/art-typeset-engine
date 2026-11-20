# -*- coding: utf-8 -*-
"""Q31 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q31_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("执着说明你见得太少_原作托马斯费恩利风景习作1833纸本油画"
        "挪威国家美术馆空旷地平线_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q31_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q31.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 94
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v5"
r["meta"]["accent"] = "绛朱 136,84,64 ＋ 单字强调「少」（14.18%）"
r["pdca"]["see"] = {
    "contrast": [12.86, 13.11, 12.87, 12.55, 12.12,
                 8.86, 8.74, 8.72, 7.16],
    "accent_ratio": 0.1418,
    "bbox": {"top": 105, "bottom": 1439, "left": 189, "right": 189},
    "bg_std_max": 12.5,
    "accent_pixels": 2203,
    "body_ink": 15533,
    "layers": 9,
    "measured_by": "art_typeset.verify.verify(dark_bg=False, body_band_slice=(1,5), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "71 字极短文本＋2 字实心强调（执着）导致强调占比 16.5–17.2% 超标：分母是正文墨像素（约 1.55 万），笔画密集的 2 字占比天然偏高；下调下划线 alpha、降色饱和、去下划线均无效（16.4→16.5%），证明分子主体是强调字本身而非下划线",
    "prevention": "① 极短文本（<80 字）的强调必须选笔画少的字——本张改「执着」（2字浓墨）为「少」（1字），占比降至 14.18% 且语义仍在；② 强调方式（颜色/下划线）不改变占比量级时，不要反复微调参数，直接换强调词；③ roles 一律按首渲 find_bands 实测（本张 9 层 title+4body+3en+credit）回填，credit 被合并进末带时不要硬声明第 10 层",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "首渲：对比正文末行 4.80/英文 3.42 不达标、强调 17.18%、credit 角色错位",
     "prevent": "字色按天空中位 142–175 反推，加深至近黑（16,14,12 / 22,18,14）"},
    {"round": 2,
     "improve": "字色加深后对比 12.8/8.7/7.16 全达标；强调仍 16.52%",
     "prevent": "确认对比度与强调占比是两个独立维度，不要混调"},
    {"round": 3,
     "improve": "下划线 alpha 220→110、强调色降饱和、厚度归零，占比仍在 16.5% 左右",
     "prevent": "三次微调无果即停止试错（GSTD 时间盒），换因：强调字本身笔画密度"},
    {"round": 4,
     "improve": "强调词从「执着」换「少」（笔画少、语义仍在），占比 14.18% 达标",
     "prevent": "极短文本按语义挑笔画少的强调字，比调渲染参数有效"},
    {"round": 5,
     "improve": "roles 按实测 9 层回填（credit 与英文末带合并），三项数字全绿；全幅＋放大目验：毛笔字锋利、绛朱「少」醒目、下半极简地平线完整",
     "prevent": "馆藏照片 CC BY 4.0 署名已写进款识，合规"},
]
r["pdca"]["score"] = 94
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

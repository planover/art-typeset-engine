# -*- coding: utf-8 -*-
"""Q27 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q27_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("过度谦虚是自降价值_原作詹姆斯惠斯勒夜曲约1875布面油画唯美主义"
        "蓝黑雾金钟塔倒影_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q27_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q27.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 93
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v4"
r["meta"]["accent"] = "灯火琥珀金 255,190,80 ＋ 2px 细下划线（10.44%）"
r["pdca"]["see"] = {
    "contrast": [6.05, 5.24, 5.38, 5.46, 5.58, 5.60, 5.94, 6.30, 6.96,
                 6.86, 7.57, 8.25, 9.09, 9.17, 11.51, 15.03, 17.56, 15.42,
                 19.53, 20.03],
    "accent_ratio": 0.1044,
    "bbox": {"top": 908, "bottom": 156, "left": 452, "right": 132},
    "bg_std_max": 12.2,
    "accent_pixels": 4246,
    "body_ink": 40666,
    "layers": 20,
    "measured_by": "art_typeset.verify.verify(dark_bg=True, body_band_slice=(1,9), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "把暗底当成整块均匀：夜曲水面越往下越暗，正文首行落在中位 41.9 的较亮上沿，4.82:1 差 0.18；又沿用上一张经验预估英文 9 行，实际折成 10 行，真款识被挤到 band19 角色错位（Q24/Q25 同源）",
    "prevention": "① 暗底长文首行所在亮度带必须单独反推字色，不许按整块中位取色；② band_roles 一律以首渲 find_bands 实测层数回填，禁止预估；③ 放大目验出现疑似伪影时先做 A/B 逐像素差定位，确认不是画面/字体叠合再动工具（避免无谓改动破坏 regress）",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "首渲 20 层实测：正文首行 4.82:1 FAIL、强调 10.77% 达标、包围盒 908/156/452/132 达标；roles 只声明 19 层，真款识落 band19",
     "prevent": "最弱层以分层实测为准；行带数按渲染结果回填而非按文案估算"},
    {"round": 2,
     "improve": "英文区放大见横向细线，先做五变体对照（去下划线/换 garamond/去 grain/去 warp），再做 A/B 逐像素差：英文区差异 0，差异只落在中文 3 处强调下划线 → 判定为水面横纹与 Playfair 基线衬线叠合的放大错觉，非删除线伪影，工具不动",
     "prevent": "目验疑点先量化归因；local_typeset.py 保持只读，避免改渲染逻辑破坏 9 张 golden 逐像素回归"},
    {"round": 3,
     "improve": "正文奶白 238,226,196 → 252,246,226、强调金 240,158,64 → 255,190,80（提亮后仍靠饱和度＋细线压过正文）、roles 改为 20 层；复测全绿 5.24–20.03 / 10.44% / 四边达标",
     "prevent": "提亮正文时必须同步提亮强调色，否则奶白会反压金色造成「数字达标但强调隐身」"},
    {"round": 4,
     "improve": "1:1 全幅＋中文区放大目验：wave 弧线可辨、金线细而不抢、正文八行无标点顶格、钟塔与金色倒影完好留在文字左侧、无边框/色块/水印",
     "prevent": "三项数字全绿仍必须过 1:1 目验；交付前跑 regress / golden / derive audit 三张安全网"},
]
r["pdca"]["score"] = 93
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

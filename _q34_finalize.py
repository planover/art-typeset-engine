# -*- coding: utf-8 -*-
"""Q34 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q34_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("想成熟从放弃做好人开始_原作伊萨克列维坦伏尔加河1889布面油画"
        "普廖斯列维坦故居博物馆孤帆河水_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q34_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q34.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 94
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v1-首渲即达标"
r["meta"]["accent"] = "绛朱 168,52,32 ＋ 1px 发丝下划线（13.84%）"
r["pdca"]["see"] = {
    "contrast": [12.28, 13.08, 13.06, 13.09, 13.13, 13.04, 12.97, 13.00, 12.78,
                 8.70, 8.64, 8.51, 8.38, 7.37],
    "accent_ratio": 0.1384,
    "bbox": {"top": 119, "bottom": 1267, "left": 154, "right": 153},
    "bg_std_max": 19.2,
    "accent_pixels": 4594,
    "body_ink": 33201,
    "layers": 14,
    "measured_by": "art_typeset.verify.verify(dark_bg=False, body_band_slice=(1,9), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "无 FAIL——检修后流程把 Q31/Q32/Q33 三次触礁的教训前置：①选画阶段按 std 沿 y 分布挑天然净天空（8–15）而非事后烘底；②首渲前按 BODY 8 行＋英文实测 4 行预填 14 层 roles；③强调按字数反推 17 字（13.84% 落中段）。首渲即全绿，且按新元规则仍跑 diagnose 确认无隐藏问题",
    "prevention": "工具化诊断已固化（art_typeset/diagnose.py + CLI diagnose）；本次是检修后第一张，验证前置预判＋诊断双保险有效——零调参、零返工",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "首渲即全绿（对比 12.28/12.78–13.13/8.38–8.70/7.37、强调 13.84%、四边 119/1267/154/153、std 19.2）；按新元规则首渲后跑 diagnose 确认 roles 建议一致、强调构成一致、无 FAIL",
     "prevent": "检修成果：选画阶段筛天然净天空＋按实测预填 roles＋按字数反推强调——三项前置取代事后调参"},
    {"round": 2,
     "improve": "1:1 全幅＋放大目验：华文中宋标题锋利、两处绛朱醒目、正文八行顶格合规、英文末行居中半行自然、款识完整；孤帆独立水面与文案气质呼应",
     "prevent": "视觉目验不接受数值达标替代，也与 Q33 淡金晨雾／黑体／中部块全面对跖"},
]
r["pdca"]["score"] = 94
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

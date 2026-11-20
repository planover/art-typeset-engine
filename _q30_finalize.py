# -*- coding: utf-8 -*-
"""Q30 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q30_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("高质量的关系_原作费迪南德霍德勒图恩湖的对称倒影1909布面油画"
        "瑞士象征主义山湖镜像_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q30_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q30.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 93
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v2"
r["meta"]["accent"] = "绛朱 178,52,32 ＋ 1px 发丝下划线（10.25%）"
r["pdca"]["see"] = {
    "contrast": [8.58, 8.99, 8.97, 8.99, 9.03, 8.94, 8.92, 8.91,
                 7.01, 6.93, 6.97, 7.44],
    "accent_ratio": 0.1025,
    "bbox": {"top": 1199, "bottom": 266, "left": 146, "right": 146},
    "bg_std_max": 20.4,
    "accent_pixels": 2122,
    "body_ink": 20712,
    "layers": 12,
    "measured_by": "art_typeset.verify.verify(dark_bg=False, body_band_slice=(1,8), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "草稿三项数字只差标题带 bg_std 26.3（门槛 25）——标题落在真实山岸与水下倒影的交界纹理带（y=1200–1281，std 26–28），下半纯水区 std 仅 7–9。直接下移文字会让底部Margin<80，故不能靠位移",
    "prevention": "沿用 Q29 军规：对窄带做轻度大羽化柔光（95 alpha／75px 高斯，取带内主色 187,207,211）烘进底图，且烘制底图必须同步作为 verify 的 base——否则 verify 测原图 std 与视觉脱节。1:1 目验确认无水平条带或矩形痕迹",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "现场已有半途补给：q30.json＋底图＋草稿齐备但 score=0。复查草稿三项数字：对比 8.4–9.0/6.9–7.0/7.44、强调 10.24%、四边合格，唯一 FAIL 是标题带 bg_std 26.3 vs 25",
     "prevent": "先测 std 沿 y 分布定位污染带（y=1200–1350 岸线/倒影交界），不盲目改字号或位移"},
    {"round": 2,
     "improve": "对标题窄带做轻度柔光烘底后重渲：bg_std 26.3→20.4，对比 8.58/8.91–9.03/6.93–7.01/7.44、强调 10.25%、四边 1199/266/146/146 全绿；全幅＋文字区放大目验确认柔光无痕、双关构图成立",
     "prevent": "与主标「对称倒影＝互惠平衡」的画意双关一并目验；不因数值达标跳过视觉检查"},
]
r["pdca"]["score"] = 93
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

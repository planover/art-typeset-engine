# -*- coding: utf-8 -*-
"""Q28 Deliver：成图落盘（系统真实时间戳）＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q28_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("没那么多三观一致_原作温斯洛霍默男孩垂钓格洛斯特港1880纸本水彩"
        "美国现实主义纸白赭石双童帆船倒影_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q28_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q28.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 92
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v2"
r["meta"]["accent"] = "赭朱 168,52,32 ＋ 1px 发丝下划线（10.33%）"
r["meta"]["layout"] = ("亮底深字＋短文本系列首次整块弓形形变（warp arc:-34 且 warp_body on）；"
                       "得意黑斜体标题＋思源宋正文五行按标点手工断行＋Inter 英文＋文楷款识四体混排；"
                       "文字压上半纸白留白，两个背向而坐的男孩、帆船与倒影完整留在下半幅；"
                       "与 Q27 暗底浅字、下半块、毛笔标题全面对跖")
r["pdca"]["see"] = {
    "contrast": [6.33, 6.30, 6.30, 6.27, 6.40, 6.62,
                 4.43, 4.48, 4.50, 4.50, 4.49, 4.48, 5.07],
    "accent_ratio": 0.1033,
    "bbox": {"top": 99, "bottom": 1234, "left": 180, "right": 401},
    "bg_std_max": 14.8,
    "accent_pixels": 2655,
    "body_ink": 25695,
    "layers": 13,
    "measured_by": "art_typeset.verify.verify(dark_bg=False, body_band_slice=(1,6), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "用户第三次点名「怎么还说 PDF」——根因是把转写文档的物理页（如 118）当页码口径，而源其实是 md 文档《醒与悟1.0.md》的锚点 s165（印刷 106）。断言脚本、配方 source、pdca.go 三处都残留物理页口径",
    "prevention": "① 原文一律从 md 文档锚点篇目正文逐字比对，不再读 txt 物理页；② 交付话术统一「文档 N 起」，禁止出现「PDF N 起」；③ band_roles 以首渲 find_bands 实测层数（此题 13 层）回填，不预估",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "断言源从转写文档物理页 118 切到 md 文档锚点 s165（印刷 106），逐字断言 6/6；配方 source 增加 doc/anchor 字段、page 改 106；pdca.go 的筛除路径改用 s148–s165 篇目锚点，清除全部「PDF」提法",
     "prevent": "短指令「下一句」默认读磁盘 md 文档版，不从用户粘贴或转写页读取；话术层彻底去 PDF 化"},
    {"round": 2,
     "improve": "首渲实测 13 层：对比 6.33/6.27–6.62/4.43–4.50/5.07（最弱 4.43 英文，超 4:1 门槛）、强调 10.33%、包围盒 99/1234/180/401、bg_std 14.8 全绿；layout 自适应把 title-gap 34→74 给弧形容错",
     "prevent": "整块弓形形变的首行须单独看其亮度带与行距，公式化 gap 不足时交给 render 自检的 layout_changes 修正"},
    {"round": 3,
     "improve": "1:1 全幅＋中文区放大目验：标题弧线自然、笔画无断裂，赭朱强调词配发丝下划线醒目不隐身，英文清晰无横穿伪影、行首无标点顶格，双童与帆船倒影完好留在下半幅，无边框/色块/水印",
     "prevent": "三项数字全绿仍必须过 1:1 目验；首次形变手法尤其要放大看笔画完整性"},
]
r["pdca"]["score"] = 92
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

# -*- coding: utf-8 -*-
"""Q25 第 93 张：落盘 + 配方回填（时间戳取系统真实时间）。"""
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
SRC = ROOT / ".workbuddy-ai" / "tmp" / "q25_v4.png"
PRESET = ROOT / "art_typeset" / "presets" / "q25.json"

ts = datetime.now().strftime("%Y%m%d_%H%M")
name = (f"别激发别人的羡慕嫉妒恨_原作乔治英尼斯月升1887布面油画"
        f"美国色调主义暗褐草地橙金月色_{ts}.png")
final = CONTENT / name
shutil.copyfile(SRC, final)
print("FINAL_PNG=" + name)
print("final_bytes=" + str(final.stat().st_size))

r = json.loads(PRESET.read_text(encoding="utf-8"))
r["meta"]["score"] = 94
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v4"
r["pdca"]["see"] = {
    "contrast": [8.57, 7.76, 7.76, 6.88, 6.58, 5.51],
    "accent_ratio": 0.1364,
    "bbox": {"top": 1399, "bottom": 236, "left": 185, "right": 184},
    "bg_std_max": 10.0,
    "accent_pixels": 1151,
    "body_ink": 8437,
    "layers": 6,
    "measured_by": "art_typeset.verify.verify(dark_bg=True, body_band_slice=(1,3), roles=meta.band_roles) · spec.ACCENT_POLICY=continuous_band_with_underline_v1",
    "measured_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["iterations"] = [
    {
        "round": 1,
        "improve": "整块 rotate -6 斜排 → 所有行带 y 范围被拉长互相覆盖，只剩 3 层，英文与款识测不到层（layers_found FAIL），门禁删图；撤回整块旋转，改标题 --warp arc 单弧形变，正文/英文/款识保持端正",
        "prevent": "形变只给标题或短句；整块旋转会让相邻行带合并，verify 分层测量失效（Q21 透视事故的变体）",
    },
    {
        "round": 2,
        "improve": "arc:24 目验几乎看不出弯；6 层行带其实全达标但 roles 硬编码 8 层导致真款识被误标 en1、contrast_credit=None 假 FAIL；给 verify.py 加 roles 参数 + 配方 meta.band_roles 显式声明，并把弧幅度 24→38",
        "prevent": "工具层：默认 8 层角色在层数多（Q24 band10）与层数少（Q25 en1）两种情况下都会错位，配方必须能声明真实行带结构；数字达标不替代 1:1 目验形变是否可辨",
    },
    {
        "round": 3,
        "improve": "角色全对、六层对比 8.57/7.76/6.58–6.88/5.51 全绿，但强调占比 17.21% 超标：42 字短文本染了 6 字；按 8437 正文墨像素反推，6 字→5 字（不是说→不是），下划线 4→2px",
        "prevent": "短文本强调字数必须由正文墨像素反推，禁止沿用长文的 20 字经验；门禁不达标不落盘",
    },
    {
        "round": 4,
        "improve": "强调 13.64% 达标，1:1 目验确认 arc:38 弧线肉眼可辨、蜜金强调与细下划线比奶油正文醒目、中英文与款识完整无截断、文字落在天然暗草地且避开月光倒影与左侧人影",
        "prevent": "出图必打三项数字 + 1:1 底部交界带目验；工具改动后跑 regress / golden check 确认历史配方不受影响",
    },
]
r["pdca"]["score"] = 94
r["pdca"]["final_png"] = name
PRESET.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("preset updated: score=94 see.ok=True iterations=4")

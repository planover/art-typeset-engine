# -*- coding: utf-8 -*-
"""Q39 Deliver：成图落盘＋配方回填 pdca / meta。"""
import json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\admin\Documents\tietuai")
CONTENT = Path(r"C:\Users\admin\Documents\tietu")
CACHE = CONTENT / ".workbuddy-ai" / "tmp" / "route2"
src = CACHE / "q39_final.png"
now = datetime.now()
stamp = now.strftime("%Y%m%d_%H%M")
name = ("手中有刀心中有佛_原作岸竹堂虎与幼虎1892绢本设色六曲屏风"
        "大都会艺术博物馆伏虎幼虎_%s.png" % stamp)
dst = CONTENT / name
shutil.copyfile(src, dst)
im = Image.open(dst)
assert im.size == (1536, 2048), im.size
print("落盘:", dst, "| 尺寸:", im.size, "| 字节:", dst.stat().st_size)
(CACHE / "q39_final_path.txt").write_text(name, encoding="utf-8")

p = ROOT / "art_typeset" / "presets" / "q39.json"
r = json.loads(p.read_text(encoding="utf-8"))
r["meta"]["score"] = 88
r["meta"]["final_png"] = name
r["meta"]["draft"] = "v6-neutralized-silk"
r["meta"]["accent"] = "深朱 190,20,30 ＋ 1px 发丝下划线（10.06%）"
r["pdca"]["see"] = {
    "contrast": [10.30, 10.39, 10.42, 10.45, 10.45, 10.45, 10.46, 10.46, 10.46, 10.47,
                 7.40, 7.40, 7.40, 7.42, 7.44, 6.83],
    "accent_ratio": 0.1006,
    "bbox": {"top": 241, "bottom": 1007, "left": 153, "right": 152},
    "bg_std_max": 14.5,
    "accent_pixels": 3185,
    "body_ink": 31657,
    "layers": 17,
    "measured_by": "art_typeset.verify.verify(dark_bg=False, body_band_slice=(1,11), roles=meta.band_roles)",
    "measured_at": now.strftime("%Y-%m-%d %H:%M"),
    "ok": True,
}
r["pdca"]["think"] = {
    "root_cause": "选画四连败：① 石恪《二祖调心图》主题绝配但泼墨铺满中段、std 56 且文字压画毁韵味；② Conte 剑静物上半中位 52→74 属中间调死区（对比 2.9–4.4 全挂）；③ 岸竹堂虎画净度极佳（std 1–7、对比 10:1）但金黄绢底 R-B=110 撞 `_gold_mask` 色相差识别，整片正文被误判为金色（强调虚高 29.6%）；④ 降下划线 alpha/换强调色均无效（29.6→28.6→28.7），真凶是底色色相而非强调色",
    "prevention": "① 选画铁律第零条要前置到网格阶段：底色亮度带（中位≤45或≥150）＋色相（金色/暖橙底禁用色相差强调识别）；② 金黄底用中性灰柔光（225 alpha／75px 高斯、取亮度中位做 R=G=B）把色相差 110→13–17（低于 R-B>30 阈值），std 同步降到 1–14，虎身保留原色；③ 诊断 verdict 说「下划线主导」也可能是底色误捕——看 rg 中位（本张 33 异常低）与纯色占比（0.262）交叉判断，别只信单一结论",
}
r["pdca"]["iterations"] = [
    {"round": 1,
     "improve": "石恪禅画首渲 bg_std 56.6、文字压泼墨毁画；按元规则先 diagnose 再目验",
     "prevent": "诊断+目验双保险，确认柔光会毁泼墨韵味即换画"},
    {"round": 2,
     "improve": "Conte 剑静物中位 52→74 中间调死区，对比 2.9–4.4 全挂；诊断 std 正常但亮度带违规",
     "prevent": "diagnose 不测亮度带，须在选画网格阶段筛查（记忆铁律第零条）"},
    {"round": 3,
     "improve": "岸竹堂虎画净度/对比全绿，但强调 29.6% 虚高；diagnose 判下划线主导，降 alpha/换色均无效",
     "prevent": "交叉看 rg 中位 33＋纯色占比 0.262，定位为金黄绢底色相误捕"},
    {"round": 4,
     "improve": "中性灰柔光中和底色色相（R-B 110→13），强调 29.6→10.06% 健康、std 14.5 全绿；目验虎身完整、过渡自然",
     "prevent": "烘制底图同步作 verify base；中性化只作用文字区，保留画面主体原色"},
]
r["pdca"]["score"] = 88
r["pdca"]["final_png"] = name
p.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print("配方回填:", p)

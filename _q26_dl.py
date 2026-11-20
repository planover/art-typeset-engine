# -*- coding: utf-8 -*-
"""Q26：串行低频下载候选原图（绕 429），带退避重试。"""
from pathlib import Path
from urllib.request import Request, urlopen
import time

CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
CACHE.mkdir(parents=True, exist_ok=True)
UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"

CANDS = {
    "qiuying": "https://upload.wikimedia.org/wikipedia/commons/6/67/Qiu_Ying_-_Saying_Farewell_at_Xunyang_-_Google_Art_Project.jpg",
    "lane": "https://upload.wikimedia.org/wikipedia/commons/e/e1/A_Calm_Sea%2C_by_Fitz_Henry_Lane%2C_c._1860%2C_oil_on_canvas_-_Cape_Ann_Museum_-_Gloucester%2C_MA_-_DSC01126.jpg",
}

for name, url in CANDS.items():
    p = CACHE / f"q26_{name}.jpg"
    if p.exists() and p.stat().st_size > 200_000:
        print("cached", name, p.stat().st_size)
        continue
    for attempt in range(5):
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": "image/jpeg,image/*"})
            with urlopen(req, timeout=180) as r:
                data = r.read()
            p.write_bytes(data)
            print("ok", name, len(data), "bytes")
            break
        except Exception as e:
            wait = 8 * (attempt + 1)
            print(f"  429/fail {name} attempt{attempt+1}: {e} -> sleep {wait}s")
            time.sleep(wait)
    time.sleep(6)

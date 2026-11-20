# -*- coding: utf-8 -*-
"""Q26：经 API 取合法 thumburl（thumb.wikimedia.org），串行下载两幅终选。
A = Fitz Henry Lane《A Calm Sea》c.1860
B = 沈周《Landscape with Pavilion and Willows》(Met)
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json, time

UA = "WorkBuddyArtTypeset/1.0 (local research; contact: local)"
API = "https://commons.wikimedia.org/w/api.php"
CACHE = Path(r"C:\Users\admin\Documents\tietu\.workbuddy-ai\tmp\route2")
CACHE.mkdir(parents=True, exist_ok=True)

FILES = {
    "lane": ("File:A Calm Sea, by Fitz Henry Lane, c. 1860, oil on canvas - Cape Ann Museum - Gloucester, MA - DSC01126.jpg", 3000),
    "shenzhou": ("File:Shen Zhou - Landscape with Pavilion and Willows - 69.131.10 - Metropolitan Museum of Art.jpg", 3000),
}


def api(p):
    p = dict(p); p["format"] = "json"
    r = Request(API + "?" + urlencode(p), headers={"User-Agent": UA})
    return json.loads(urlopen(r, timeout=40).read().decode("utf-8"))


for name, (title, wpx) in FILES.items():
    d = api({"action": "query", "titles": title, "prop": "imageinfo",
             "iiprop": "url|size", "iiurlwidth": wpx})
    page = list(d["query"]["pages"].values())[0]
    if "imageinfo" not in page:
        print("MISS", name, page.keys()); continue
    ii = page["imageinfo"][0]
    print(name, ii["width"], "x", ii["height"], "-> thumb", ii["thumbwidth"], "x", ii["thumbheight"])
    url = ii["thumburl"].split("?")[0]
    p = CACHE / f"q26_{name}.jpg"
    if p.exists() and p.stat().st_size > 300_000:
        print("  cached", p.stat().st_size); continue
    for attempt in range(4):
        try:
            r = Request(url, headers={"User-Agent": UA})
            data = urlopen(r, timeout=180).read()
            p.write_bytes(data)
            print("  ok", len(data), "bytes ->", p)
            break
        except Exception as e:
            print("  fail", attempt + 1, e)
            time.sleep(10 * (attempt + 1))
    time.sleep(5)

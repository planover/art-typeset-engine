# -*- coding: utf-8 -*-
"""冻结 Q25 golden 快照（中文长文件名不经过 bash 传参）。"""
from pathlib import Path
from art_typeset import golden

CONTENT = Path(r"C:\Users\admin\Documents\tietu")
hits = sorted(CONTENT.glob("别激发别人的羡慕嫉妒恨_*_20261112_1405.png"))
assert len(hits) == 1, hits
p = golden.freeze("Q25", hits[0], note="第93张 Q25 · 暗底浅字 · 标题 arc:38 · 94分")
print("frozen:", p)

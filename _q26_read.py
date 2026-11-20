import pymupdf, sys

PDF = r"C:\Users\admin\Documents\tietu\醒与悟1.0.pdf"
doc = pymupdf.open(PDF)
print("total pages:", doc.page_count)
for p in range(92, 102):           # 0-based 92 == 物理页 93
    page = doc[p]
    t = page.get_text("text")
    print("=" * 70)
    print(f"### 物理页 {p+1} （0-based {p}） chars={len(t)}")
    print(t.strip()[:2600])

import os
import pymupdf as fitz

pdf_path = "powerbi/powerbi.pdf"
output_dir = "app/images"

os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_path)
for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(dpi=150)
    pix.save(f"{output_dir}/page_{i}.png")
    print(f"Saved page_{i}.png")
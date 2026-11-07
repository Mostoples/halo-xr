"""Ekspor PPTX → PDF + PNG per slide lewat PowerPoint COM (Windows). python deck/export.py output/X.pptx"""
import sys, pathlib, win32com.client
src = pathlib.Path(sys.argv[1]).resolve()
png_dir = src.parent / (src.stem + "_png"); png_dir.mkdir(exist_ok=True)
app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(str(src), WithWindow=False)
pres.SaveAs(str(src.with_suffix(".pdf")), 32)
for i, sl in enumerate(pres.Slides, 1):
    sl.Export(str(png_dir / f"slide{i:02d}.png"), "PNG", 1600, 900)
pres.Close()
print("ok", src.with_suffix(".pdf"))

"""Render PDF pages to image files using PyMuPDF.

Call ``run(pdf_file, output_dir, zoom=1.33333333)``. Requires PyMuPDF.
Legacy source: ``ws/pdf2img.py``.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class RenderResult: pages:int; outputs:tuple[Path,...]
def run(pdf_file:Path,output_dir:Path,*,zoom:float=1.33333333,image_extension:str="png")->RenderResult:
    import fitz
    if not pdf_file.is_file():raise FileNotFoundError(f"PDF not found: {pdf_file}")
    if zoom<=0:raise ValueError("zoom must be positive")
    output_dir.mkdir(parents=True,exist_ok=True);outputs=[]
    with fitz.open(pdf_file) as document:
        for index,page in enumerate(document):
            pixmap=page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),alpha=False)
            destination=output_dir/f"{pdf_file.stem}_{index:04d}.{image_extension.lstrip('.')}";pixmap.save(destination);outputs.append(destination)
    return RenderResult(len(outputs),tuple(outputs))
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("pdf_file",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--zoom",type=float,default=1.33333333);ap.add_argument("--extension",default="png");a=ap.parse_args(argv)
    try:r=run(a.pdf_file,a.output_dir,zoom=a.zoom,image_extension=a.extension)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(f"pages={r.pages} output={a.output_dir}");return 0
if __name__=="__main__":raise SystemExit(main())

"""Move XML documents and image files into separate directories.

Call ``run(source_dir, image_dir, xml_dir, execute=False)``. Preview is the
default. Legacy source: ``important/move_img&xml_to_new.py``.
"""
from __future__ import annotations
import argparse, shutil
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS={".jpg",".jpeg",".png",".webp",".bmp",".gif",".tif",".tiff"}
@dataclass(frozen=True, slots=True)
class OrganizeResult: images:int; xml:int; ignored:int; moved:int

def run(source_dir:Path,image_dir:Path,xml_dir:Path,*,recursive:bool=False,execute:bool=False)->OrganizeResult:
    if not source_dir.is_dir(): raise FileNotFoundError(f"Source not found: {source_dir}")
    files=sorted(source_dir.glob("**/*" if recursive else "*")); images=xml=ignored=moved=0
    for p in files:
        if not p.is_file(): continue
        if p.suffix.casefold()==".xml": destination=xml_dir/p.name; xml+=1
        elif p.suffix.casefold() in IMAGE_EXTENSIONS: destination=image_dir/p.name; images+=1
        else: ignored+=1; continue
        if execute:
            destination.parent.mkdir(parents=True,exist_ok=True); shutil.move(str(p),str(destination)); moved+=1
    return OrganizeResult(images,xml,ignored,moved)

def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]); ap.add_argument("source_dir",type=Path); ap.add_argument("image_dir",type=Path); ap.add_argument("xml_dir",type=Path); ap.add_argument("--recursive",action="store_true"); ap.add_argument("--execute",action="store_true"); a=ap.parse_args(argv)
    try:r=run(a.source_dir,a.image_dir,a.xml_dir,recursive=a.recursive,execute=a.execute)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(f"images={r.images} xml={r.xml} ignored={r.ignored} moved={r.moved}");return 0
if __name__=="__main__":raise SystemExit(main())

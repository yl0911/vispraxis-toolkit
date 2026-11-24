"""Create empty YOLO TXT labels for images without XML annotations.

Call ``run(image_dir, output_dir, xml_dir=None)``. Existing TXT files are not
overwritten. Legacy source: ``important/makeYolo_no_lable.py``.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True, slots=True)
class CreateResult: images:int; created:int; skipped_annotated:int; skipped_existing:int
def run(image_dir:Path,output_dir:Path,*,xml_dir:Path|None=None,recursive:bool=True)->CreateResult:
    if not image_dir.is_dir():raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if xml_dir is not None and not xml_dir.is_dir():raise FileNotFoundError(f"XML directory not found: {xml_dir}")
    images=sorted(p for p in image_dir.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in {".jpg",".jpeg",".png",".webp"})
    xml_stems={p.stem.casefold() for p in xml_dir.glob("*.xml")} if xml_dir else set();created=annotated=existing=0
    output_dir.mkdir(parents=True,exist_ok=True)
    for image in images:
        if image.stem.casefold() in xml_stems:annotated+=1;continue
        destination=output_dir/f"{image.stem}.txt"
        if destination.exists():existing+=1;continue
        destination.touch();created+=1
    return CreateResult(len(images),created,annotated,existing)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("image_dir",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--xml-dir",type=Path);ap.add_argument("--no-recursive",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.image_dir,a.output_dir,xml_dir=a.xml_dir,recursive=not a.no_recursive)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(f"images={r.images} created={r.created} annotated={r.skipped_annotated} existing={r.skipped_existing}");return 0
if __name__=="__main__":raise SystemExit(main())

"""Copy one XML template beside each image using the image stem.

Call ``run(image_dir, template, output_dir=None, execute=False)``. Preview is
the default. Legacy source: ``dingstock/xml_copy.py``.
"""
from __future__ import annotations
import argparse,shutil
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class CopyResult: images:int; planned:int; copied:int; skipped:int
def run(image_dir:Path,template:Path,output_dir:Path|None=None,*,recursive:bool=True,overwrite:bool=False,execute:bool=False)->CopyResult:
    if not image_dir.is_dir():raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not template.is_file():raise FileNotFoundError(f"Template not found: {template}")
    output_dir=output_dir or image_dir;images=sorted(p for p in image_dir.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in {".png",".jpg",".jpeg",".webp"});planned=copied=skipped=0
    for image in images:
        relative=image.relative_to(image_dir).with_suffix(".xml");destination=output_dir/relative
        if destination.exists() and not overwrite:skipped+=1;continue
        planned+=1
        if execute:destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(template,destination);copied+=1
    return CopyResult(len(images),planned,copied,skipped)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("image_dir",type=Path);ap.add_argument("template",type=Path);ap.add_argument("--output-dir",type=Path);ap.add_argument("--overwrite",action="store_true");ap.add_argument("--no-recursive",action="store_true");ap.add_argument("--execute",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.image_dir,a.template,a.output_dir,recursive=not a.no_recursive,overwrite=a.overwrite,execute=a.execute)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(r);print(f"mode={'execute' if a.execute else 'preview'}");return 0
if __name__=="__main__":raise SystemExit(main())

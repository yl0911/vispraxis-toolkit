"""Copy exact dHash groups into separate directories.

Call ``run(image_dir, output_dir, hash_size=16)``. Requires Pillow and dhash.
Legacy source: ``dingstock/select_similar_DH.py``.
"""
from __future__ import annotations
import argparse,shutil
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class GroupResult: images:int; duplicate_groups:int; copied:int
def run(image_dir:Path,output_dir:Path,*,hash_size:int=16,recursive:bool=True)->GroupResult:
    import dhash
    from PIL import Image
    if not image_dir.is_dir():raise FileNotFoundError(f"Image directory not found: {image_dir}")
    files=sorted(p for p in image_dir.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in {".jpg",".jpeg",".png",".webp"});groups={}
    for path in files:
        with Image.open(path) as image:row,col=dhash.dhash_row_col(image,size=hash_size)
        groups.setdefault(dhash.format_hex(row,col),[]).append(path)
    duplicates={key:paths for key,paths in groups.items() if len(paths)>1};copied=0
    for key,paths in duplicates.items():
        target=output_dir/key;target.mkdir(parents=True,exist_ok=True)
        for index,path in enumerate(paths):shutil.copyfile(path,target/f"{index}_{path.name}");copied+=1
    return GroupResult(len(files),len(duplicates),copied)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("image_dir",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--hash-size",type=int,default=16);ap.add_argument("--no-recursive",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.image_dir,a.output_dir,hash_size=a.hash_size,recursive=not a.no_recursive)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

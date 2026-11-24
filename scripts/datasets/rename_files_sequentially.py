"""Rename selected files using a label and sequential number.

Call ``run(directory, label, execute=False)``. Preview is the default. Legacy
source: ``bty/Batch_Rename.py``.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True, slots=True)
class RenameResult: matched:int; renamed:int; conflicts:int
def run(directory:Path,label:str,*,start:int=0,extensions:tuple[str,...]=(".jpg",".jpeg",".png",".txt"),output_extension:str|None=None,recursive:bool=False,execute:bool=False)->RenameResult:
    if not directory.is_dir():raise FileNotFoundError(f"Directory not found: {directory}")
    files=sorted(p for p in directory.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in extensions)
    planned=[]
    for index,path in enumerate(files,start):
        suffix=("."+output_extension.lstrip(".")) if output_extension else path.suffix
        planned.append((path,directory/f"{label}_{index:06d}{suffix}"))
    conflicts=sum(1 for old,new in planned if new.exists() and new!=old)
    renamed=0
    if execute and not conflicts:
        temporary=[]
        for index,(old,new) in enumerate(planned):
            temp=old.with_name(f".__rename_{index}_{old.name}");old.rename(temp);temporary.append((temp,new))
        for temp,new in temporary:temp.rename(new);renamed+=1
    return RenameResult(len(files),renamed,conflicts)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("directory",type=Path);ap.add_argument("label");ap.add_argument("--start",type=int,default=0);ap.add_argument("--output-extension");ap.add_argument("--recursive",action="store_true");ap.add_argument("--execute",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.directory,a.label,start=a.start,output_extension=a.output_extension,recursive=a.recursive,execute=a.execute)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(f"matched={r.matched} renamed={r.renamed} conflicts={r.conflicts}");return 0 if not r.conflicts else 1
if __name__=="__main__":raise SystemExit(main())

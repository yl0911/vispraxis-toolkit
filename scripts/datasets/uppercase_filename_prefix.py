"""Uppercase the filename segment before the first underscore.

Call ``run(directory, execute=False)``. Preview is the default. Legacy source:
``dingstock/imgN_lower2upper.py``.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class RenameResult: matched:int; planned:int; renamed:int; conflicts:int
def run(directory:Path,*,recursive:bool=True,execute:bool=False)->RenameResult:
    if not directory.is_dir():raise FileNotFoundError(f"Directory not found: {directory}")
    images=sorted(p for p in directory.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in {".png",".jpg",".jpeg"});planned=[]
    for path in images:
        prefix,separator,remainder=path.name.partition("_");new_name=prefix.upper()+separator+remainder
        if new_name!=path.name:planned.append((path,path.with_name(new_name)))
    conflicts=sum(1 for old,new in planned if new.exists() and new!=old);renamed=0
    if execute and not conflicts:
        for old,new in planned:old.rename(new);renamed+=1
    return RenameResult(len(images),len(planned),renamed,conflicts)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("directory",type=Path);ap.add_argument("--no-recursive",action="store_true");ap.add_argument("--execute",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.directory,recursive=not a.no_recursive,execute=a.execute)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(r);print(f"mode={'execute' if a.execute else 'preview'}");return 0 if not r.conflicts else 1
if __name__=="__main__":raise SystemExit(main())

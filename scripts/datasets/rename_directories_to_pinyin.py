"""Rename immediate child directories from Chinese characters to pinyin.

Call ``run(directory, execute=False)``. Requires pypinyin. Preview is default.
Legacy source: ``imgdeal/name_pinyin.py``.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class RenameResult: directories:int; planned:int; renamed:int; conflicts:int
def run(directory:Path,*,separator:str="",execute:bool=False)->RenameResult:
    from pypinyin import lazy_pinyin
    if not directory.is_dir():raise FileNotFoundError(f"Directory not found: {directory}")
    children=sorted(p for p in directory.iterdir() if p.is_dir());plans=[]
    for path in children:
        name=separator.join(lazy_pinyin(path.name)).replace("·","")
        if name and name!=path.name:plans.append((path,path.with_name(name)))
    conflicts=sum(1 for old,new in plans if new.exists() and new!=old);renamed=0
    if execute and not conflicts:
        for old,new in plans:old.rename(new);renamed+=1
    return RenameResult(len(children),len(plans),renamed,conflicts)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("directory",type=Path);ap.add_argument("--separator",default="");ap.add_argument("--execute",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.directory,separator=a.separator,execute=a.execute)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(r);print(f"mode={'execute' if a.execute else 'preview'}");return 0 if not r.conflicts else 1
if __name__=="__main__":raise SystemExit(main())

"""Write one VOC XML per configured label group for every source document.

Call ``run(xml_dir, output_dir, groups)``. Merged sources: duplicate
`xml_getlabel_to_new.py` files. Source XML files are unchanged.
"""
from __future__ import annotations
import argparse,copy,json,xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class SplitResult: documents:int; outputs:int
def run(xml_dir:Path,output_dir:Path,groups:dict[str,set[str]],*,recursive:bool=True)->SplitResult:
    if not xml_dir.is_dir():raise FileNotFoundError(f"XML directory not found: {xml_dir}")
    files=sorted(xml_dir.glob("**/*.xml" if recursive else "*.xml"));written=0
    for source in files:
        root=ET.parse(source).getroot();objects=root.findall("object")
        for group,names in groups.items():
            selected=[obj for obj in objects if (obj.findtext("name") or "").strip() in names]
            if not selected:continue
            new_root=copy.deepcopy(root)
            for obj in new_root.findall("object"):new_root.remove(obj)
            for obj in selected:new_root.append(copy.deepcopy(obj))
            destination=output_dir/group/source.name;destination.parent.mkdir(parents=True,exist_ok=True);ET.ElementTree(new_root).write(destination,encoding="utf-8",xml_declaration=True);written+=1
    return SplitResult(len(files),written)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("xml_dir",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("groups_json",type=Path);ap.add_argument("--no-recursive",action="store_true");a=ap.parse_args(argv)
    try:groups={k:set(v) for k,v in json.loads(a.groups_json.read_text(encoding="utf-8")).items()};r=run(a.xml_dir,a.output_dir,groups,recursive=not a.no_recursive)
    except (OSError,ValueError,ET.ParseError,json.JSONDecodeError) as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

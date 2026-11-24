"""Select paired images and VOC XML files by included/excluded labels.

Call ``run(image_dir, xml_dir, output_dir, include, exclude=())``. Files are
copied, not moved. Merged sources: duplicate `select_cats_img_xml.py` files.
"""
from __future__ import annotations
import argparse,shutil,xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class SelectResult: documents:int; selected:int; missing_images:int
def run(image_dir:Path,xml_dir:Path,output_dir:Path,*,include:set[str],exclude:set[str]|None=None,recursive:bool=True)->SelectResult:
    if not image_dir.is_dir() or not xml_dir.is_dir():raise FileNotFoundError("Image or XML directory not found")
    exclude=exclude or set();xml_files=sorted(xml_dir.glob("**/*.xml" if recursive else "*.xml"));selected=missing=0
    image_index={p.stem.casefold():p for p in image_dir.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in {".jpg",".jpeg",".png",".webp"}}
    for xml in xml_files:
        labels={n.text.strip() for n in ET.parse(xml).getroot().findall("object/name") if n.text}
        if not labels.intersection(include) or labels.intersection(exclude):continue
        image=image_index.get(xml.stem.casefold())
        if image is None:missing+=1;continue
        (output_dir/"images").mkdir(parents=True,exist_ok=True);(output_dir/"labels").mkdir(parents=True,exist_ok=True)
        shutil.copy2(image,output_dir/"images"/image.name);shutil.copy2(xml,output_dir/"labels"/xml.name);selected+=1
    return SelectResult(len(xml_files),selected,missing)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("image_dir",type=Path);ap.add_argument("xml_dir",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--include",action="append",required=True);ap.add_argument("--exclude",action="append",default=[]);ap.add_argument("--no-recursive",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.image_dir,a.xml_dir,a.output_dir,include=set(a.include),exclude=set(a.exclude),recursive=not a.no_recursive)
    except (OSError,ValueError,ET.ParseError) as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

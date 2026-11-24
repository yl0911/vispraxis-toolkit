"""Crop every image using named boxes from one VOC XML template.

Call ``run(image_dir, template_xml, output_dir)``. Requires OpenCV.
Legacy source: ``dingstock/img_cut_xmlTemp.py``.
"""
from __future__ import annotations
import argparse,xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class CropResult: images:int; boxes:int; crops:int; outputs:tuple[Path,...]
def load_boxes(path:Path)->dict[str,tuple[int,int,int,int]]:
    root=ET.parse(path).getroot();boxes={}
    for obj in root.findall("object"):
        name=obj.findtext("name");box=obj.find("bndbox")
        if name and box is not None:boxes[name]=(int(box.findtext("xmin")),int(box.findtext("ymin")),int(box.findtext("xmax")),int(box.findtext("ymax")))
    return boxes
def run(image_dir:Path,template_xml:Path,output_dir:Path,*,recursive:bool=True)->CropResult:
    import cv2
    if not image_dir.is_dir():raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not template_xml.is_file():raise FileNotFoundError(f"Template not found: {template_xml}")
    boxes=load_boxes(template_xml);images=sorted(p for p in image_dir.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in {".png",".jpg",".jpeg"});outputs=[]
    for path in images:
        image=cv2.imread(str(path))
        if image is None:continue
        h,w=image.shape[:2]
        for name,(x1,y1,x2,y2) in boxes.items():
            x1,y1,x2,y2=max(0,x1),max(0,y1),min(w,x2),min(h,y2)
            if x2<=x1 or y2<=y1:continue
            destination=output_dir/f"{path.stem}_{name}{path.suffix}";destination.parent.mkdir(parents=True,exist_ok=True)
            if cv2.imwrite(str(destination),image[y1:y2,x1:x2]):outputs.append(destination)
    return CropResult(len(images),len(boxes),len(outputs),tuple(outputs))
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("image_dir",type=Path);ap.add_argument("template_xml",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--no-recursive",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.image_dir,a.template_xml,a.output_dir,recursive=not a.no_recursive)
    except (ImportError,OSError,ValueError,ET.ParseError) as e:print(f"ERROR: {e}");return 1
    print(f"images={r.images} boxes={r.boxes} crops={r.crops}");return 0
if __name__=="__main__":raise SystemExit(main())

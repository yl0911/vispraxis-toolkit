"""Inpaint pixels in a region selected by an HSV color range.

Call ``run(source, output_dir, roi, lower_hsv, upper_hsv)``. Requires OpenCV.
Merged sources: ``imgdeal/Inpaint.py`` and ``imgdeal/Inpaint_one.py``.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class InpaintResult: images:int; written:int; failed:tuple[str,...]
def run(source:Path,output_dir:Path,*,roi:tuple[int,int,int,int],lower_hsv:tuple[int,int,int],upper_hsv:tuple[int,int,int],radius:float=5,recursive:bool=True)->InpaintResult:
    import cv2,numpy as np
    if source.is_file():files=[source]
    elif source.is_dir():files=sorted(p for p in source.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in {".png",".jpg",".jpeg"})
    else:raise FileNotFoundError(f"Source not found: {source}")
    x1,y1,x2,y2=roi;written=0;failed=[]
    for path in files:
        image=cv2.imread(str(path))
        if image is None or x2<=x1 or y2<=y1 or x2>image.shape[1] or y2>image.shape[0]:failed.append(str(path));continue
        area=image[y1:y2,x1:x2];hsv=cv2.cvtColor(area,cv2.COLOR_BGR2HSV);mask=cv2.inRange(hsv,np.array(lower_hsv),np.array(upper_hsv));mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((3,3),np.uint8));image[y1:y2,x1:x2]=cv2.inpaint(area,mask,radius,cv2.INPAINT_NS)
        destination=output_dir/path.name;destination.parent.mkdir(parents=True,exist_ok=True)
        if cv2.imwrite(str(destination),image):written+=1
        else:failed.append(str(path))
    return InpaintResult(len(files),written,tuple(failed))
def _ints(value:str,count:int)->tuple[int,...]:
    result=tuple(int(v) for v in value.split(","))
    if len(result)!=count:raise argparse.ArgumentTypeError(f"expected {count} comma-separated integers")
    return result
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("source",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--roi",required=True);ap.add_argument("--lower-hsv",required=True);ap.add_argument("--upper-hsv",required=True);ap.add_argument("--radius",type=float,default=5);a=ap.parse_args(argv)
    try:r=run(a.source,a.output_dir,roi=_ints(a.roi,4),lower_hsv=_ints(a.lower_hsv,3),upper_hsv=_ints(a.upper_hsv,3),radius=a.radius)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(f"images={r.images} written={r.written} failed={len(r.failed)}");return 0 if not r.failed else 1
if __name__=="__main__":raise SystemExit(main())

"""Copy paired images and labels into train, validation, and test subsets.

Call ``run(image_dir, label_dir, output_dir, ratios=(.9,.1,0), seed=None)``.
Legacy source: ``important/data_divided.py``.
"""
from __future__ import annotations
import argparse,random,shutil
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class SplitResult: paired:int; train:int; validation:int; test:int; missing_labels:int
def run(image_dir:Path,label_dir:Path,output_dir:Path,*,ratios:tuple[float,float,float]=(.9,.1,0),seed:int|None=None,label_extension:str=".txt")->SplitResult:
    if not image_dir.is_dir() or not label_dir.is_dir():raise FileNotFoundError("Image or label directory not found")
    if any(v<0 for v in ratios) or abs(sum(ratios)-1)>1e-9:raise ValueError("ratios must be non-negative and sum to 1")
    images=sorted(p for p in image_dir.iterdir() if p.is_file());pairs=[];missing=0
    for image in images:
        label=label_dir/f"{image.stem}{label_extension}"
        if label.is_file():pairs.append((image,label))
        else:missing+=1
    random.Random(seed).shuffle(pairs);n=len(pairs);train_n=round(n*ratios[0]);val_n=round(n*ratios[1]);parts=(('train',pairs[:train_n]),('val',pairs[train_n:train_n+val_n]),('test',pairs[train_n+val_n:]))
    for name,items in parts:
        for image,label in items:
            img_out=output_dir/name/"images"/image.name;label_out=output_dir/name/"labels"/label.name;img_out.parent.mkdir(parents=True,exist_ok=True);label_out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(image,img_out);shutil.copy2(label,label_out)
    return SplitResult(n,len(parts[0][1]),len(parts[1][1]),len(parts[2][1]),missing)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("image_dir",type=Path);ap.add_argument("label_dir",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--ratios",default="0.9,0.1,0");ap.add_argument("--seed",type=int);ap.add_argument("--label-extension",default=".txt");a=ap.parse_args(argv)
    try:ratios=tuple(float(v) for v in a.ratios.split(","));assert len(ratios)==3;r=run(a.image_dir,a.label_dir,a.output_dir,ratios=ratios,seed=a.seed,label_extension=a.label_extension)
    except (AssertionError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

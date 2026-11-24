"""Extract selected GIF frames into PNG files.

Call ``run(source, output_dir, step=1, partitions=1)``. Requires Pillow.
Legacy source: ``dingstock/gif_editor.py``.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True,slots=True)
class ExtractResult: gifs:int; frames:int; outputs:tuple[Path,...]
def run(source:Path,output_dir:Path,*,step:int=1,partitions:int=1,recursive:bool=True)->ExtractResult:
    from PIL import Image
    if step<1 or partitions<1:raise ValueError("step and partitions must be positive")
    if source.is_file():files=[source]
    elif source.is_dir():files=sorted(source.glob("**/*.gif" if recursive else "*.gif"))
    else:raise FileNotFoundError(f"Source not found: {source}")
    outputs=[]
    for gif in files:
        with Image.open(gif) as image:
            total=getattr(image,"n_frames",1)
            for index in range(total):
                part=min(partitions-1,(index*partitions)//total)
                part_start=(part*total)//partitions
                if (index-part_start)%step:continue
                image.seek(index);destination=output_dir/gif.stem/f"{gif.stem}_{part}_{index:06d}.png"
                destination.parent.mkdir(parents=True,exist_ok=True);image.convert("RGBA").save(destination);outputs.append(destination)
    return ExtractResult(len(files),len(outputs),tuple(outputs))
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("source",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--step",type=int,default=1);ap.add_argument("--partitions",type=int,default=1);ap.add_argument("--no-recursive",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.source,a.output_dir,step=a.step,partitions=a.partitions,recursive=not a.no_recursive)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(f"gifs={r.gifs} frames={r.frames}");return 0
if __name__=="__main__":raise SystemExit(main())

"""Extract video frames at a frame or time interval.

Call ``run(source, output_dir, interval=2, interval_seconds=True)`` or use the
CLI. Requires OpenCV. Legacy source: ``important/video_cut.py``.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path

VIDEO_EXTENSIONS={".mp4",".webm",".avi",".mov",".mkv",".flv",".wmv",".m4v",".mpg",".mpeg"}
@dataclass(frozen=True,slots=True)
class ExtractResult: videos:int; frames:int; failed:tuple[str,...]; outputs:tuple[Path,...]

def run(source:Path,output_dir:Path,*,interval:float=1,interval_seconds:bool=False,image_extension:str="jpg",recursive:bool=True)->ExtractResult:
    import cv2
    if interval<=0:raise ValueError("interval must be positive")
    if source.is_file():videos=[source]
    elif source.is_dir():videos=sorted(p for p in source.glob("**/*" if recursive else "*") if p.is_file() and p.suffix.casefold() in VIDEO_EXTENSIONS)
    else:raise FileNotFoundError(f"Source not found: {source}")
    outputs=[];failed=[]
    for video in videos:
        capture=cv2.VideoCapture(str(video))
        if not capture.isOpened():failed.append(f"Cannot open: {video}");continue
        fps=capture.get(cv2.CAP_PROP_FPS) or 0
        stride=max(1,round(interval*fps)) if interval_seconds else max(1,round(interval))
        target=output_dir/video.stem;target.mkdir(parents=True,exist_ok=True);index=saved=0
        try:
            while True:
                ok,frame=capture.read()
                if not ok:break
                if index%stride==0:
                    path=target/f"{video.stem}_{saved:06d}.{image_extension.lstrip('.')}"
                    if not cv2.imwrite(str(path),frame):failed.append(f"Cannot write: {path}");break
                    outputs.append(path);saved+=1
                index+=1
        finally:capture.release()
    return ExtractResult(len(videos),len(outputs),tuple(failed),tuple(outputs))
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("source",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--interval",type=float,default=1);ap.add_argument("--seconds",action="store_true");ap.add_argument("--extension",default="jpg");ap.add_argument("--no-recursive",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.source,a.output_dir,interval=a.interval,interval_seconds=a.seconds,image_extension=a.extension,recursive=not a.no_recursive)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(f"videos={r.videos} frames={r.frames} failed={len(r.failed)}");[print(f"ERROR: {e}") for e in r.failed];return 0 if not r.failed else 1
if __name__=="__main__":raise SystemExit(main())

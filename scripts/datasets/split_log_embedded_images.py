"""Split icon/background log groups and decode embedded data-URI images.

Call ``run(log_file, output_dir)``. Requires Pillow for format validation.
Legacy source: ``split_log_data_images.py``.
"""
from __future__ import annotations
import argparse,base64,binascii,io,re
from dataclasses import dataclass
from pathlib import Path
PATTERN=re.compile(r"(?P<key>icon|background)\s*:\s*data:image/[\w.+-]+;base64,(?P<payload>[A-Za-z0-9+/=]+)");KEYS=("icon","background")
@dataclass(frozen=True,slots=True)
class SplitResult: groups:int; incomplete:int; images:int
def decode(payload:str)->tuple[bytes,str]:
    from PIL import Image
    try:data=base64.b64decode(payload+"="*(-len(payload)%4),validate=True)
    except binascii.Error as e:raise ValueError(f"Invalid base64: {e}") from e
    with Image.open(io.BytesIO(data)) as image:image.load();extension=(image.format or "bin").lower()
    return data,"jpg" if extension=="jpeg" else extension
def groups(path:Path):
    pending={}
    for line in path.open("r",encoding="utf-8",errors="replace"):
        match=PATTERN.search(line)
        if not match:continue
        key=match.group("key")
        if key in pending:yield pending;pending={}
        pending[key]=(line.rstrip(),match.group("payload"))
        if all(k in pending for k in KEYS):yield pending;pending={}
    if pending:yield pending
def run(log_file:Path,output_dir:Path,*,start_index:int=0,limit:int|None=None,write_images:bool=True)->SplitResult:
    if not log_file.is_file():raise FileNotFoundError(f"Log not found: {log_file}")
    output_dir.mkdir(parents=True,exist_ok=True);count=incomplete=images=0
    for offset,group in enumerate(groups(log_file)):
        if limit is not None and count>=limit:break
        index=start_index+offset;(output_dir/f"{index}.log").write_text("\n".join(group[k][0] for k in KEYS if k in group)+"\n",encoding="utf-8")
        if len(group)!=len(KEYS):incomplete+=1
        if write_images:
            for key in KEYS:
                if key in group:data,ext=decode(group[key][1]);(output_dir/f"{index}_{key}.{ext}").write_bytes(data);images+=1
        count+=1
    return SplitResult(count,incomplete,images)
def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]);ap.add_argument("log_file",type=Path);ap.add_argument("output_dir",type=Path);ap.add_argument("--start-index",type=int,default=0);ap.add_argument("--limit",type=int);ap.add_argument("--no-images",action="store_true");a=ap.parse_args(argv)
    try:r=run(a.log_file,a.output_dir,start_index=a.start_index,limit=a.limit,write_images=not a.no_images)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

"""Preview sequential rename of the historical flowers image directory."""
from pathlib import Path
from scripts.datasets.rename_files_sequentially import run
DIRECTORY=Path(r"E:\desktop\test\xwfk\flowers");LABEL="flowers";START=0;EXECUTE=False
def main()->int:
    try:r=run(DIRECTORY,LABEL,start=START,output_extension="jpg",execute=EXECUTE)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(r);print(f"mode={'execute' if EXECUTE else 'preview'}");return 0
if __name__=="__main__":raise SystemExit(main())

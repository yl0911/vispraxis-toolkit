"""Preview uppercasing filename prefixes in the image2text queue."""
from pathlib import Path
from scripts.datasets.uppercase_filename_prefix import run
DIRECTORY=Path(r"D:\yl\desktop\test\image2text\queue_it");EXECUTE=False
def main()->int:
    try:r=run(DIRECTORY,execute=EXECUTE)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(r);print(f"mode={'execute' if EXECUTE else 'preview'}");return 0
if __name__=="__main__":raise SystemExit(main())

"""Preview converting immediate child directory names under ./new to pinyin."""
from pathlib import Path
from scripts.datasets.rename_directories_to_pinyin import run
DIRECTORY=Path("./new");EXECUTE=False
def main()->int:
    try:r=run(DIRECTORY,execute=EXECUTE)
    except Exception as e:print(f"ERROR: {e}");return 1
    print(r);print(f"mode={'execute' if EXECUTE else 'preview'}");return 0
if __name__=="__main__":raise SystemExit(main())

"""Split embedded icon/background images from the historical service log."""
from pathlib import Path
from scripts.datasets.split_log_embedded_images import run
LOG_FILE=Path(r"D:\yl\desktop\test\visionengine\vg_botdeflector\test\20260831\out.log")
OUTPUT_DIR=LOG_FILE.parent/"split"
def main()->int:
    try:r=run(LOG_FILE,OUTPUT_DIR)
    except Exception as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

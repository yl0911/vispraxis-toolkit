"""Generate Geetest train/validation image lists with the historical ratio."""
from pathlib import Path
from scripts.datasets.split_image_list import run
ROOT=Path(r"D:\yl\desktop\test\geetest_image\geetest_v4_all\ml-png\icon_mask\save_compose")
TRAIN_RATIO=.9
SEED=None
def main()->int:
    try:r=run(ROOT/"images",ROOT,train_ratio=TRAIN_RATIO,seed=SEED)
    except (OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(f"train={r.train} validation={r.validation}");return 0
if __name__=="__main__":raise SystemExit(main())

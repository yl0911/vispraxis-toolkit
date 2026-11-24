"""Split the historical notouchshape paired image/TXT dataset."""
from pathlib import Path
from scripts.datasets.split_paired_dataset import run
BASE=Path(r"D:\yl\data\notouchshape\train");OUTPUT=BASE/"divided";RATIOS=(.9,.1,0);SEED=None
def main()->int:
    try:r=run(BASE/"images",BASE/"txt",OUTPUT,ratios=RATIOS,seed=SEED)
    except Exception as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

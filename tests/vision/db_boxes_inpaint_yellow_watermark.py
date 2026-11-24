"""Remove the historical yellow watermark inside its configured ROI."""
from pathlib import Path
from scripts.vision.inpaint_color_region import run
SOURCE=Path("./test/db_boxs");OUTPUT=Path("./result/db_boxs");ROI=(9,39,220,310);LOWER=(26,43,46);UPPER=(72,255,255)
def main()->int:
    try:r=run(SOURCE,OUTPUT,roi=ROI,lower_hsv=LOWER,upper_hsv=UPPER)
    except Exception as e:print(f"ERROR: {e}");return 1
    print(r);return 0 if not r.failed else 1
if __name__=="__main__":raise SystemExit(main())

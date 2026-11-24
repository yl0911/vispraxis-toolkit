"""Crop the historical nine images using temp.xml boxes."""
from pathlib import Path
from scripts.vision.crop_images_by_voc_template import run
IMAGES=Path(r"D:\yl\desktop\test\nine\nine");TEMPLATE=Path(r"D:\yl\desktop\test\nine\temp.xml");OUTPUT=Path(r"D:\yl\desktop\test\nine\img_cut")
def main()->int:
    try:r=run(IMAGES,TEMPLATE,OUTPUT)
    except Exception as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

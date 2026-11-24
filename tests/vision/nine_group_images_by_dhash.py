"""Group historical nine crops by exact 16-bit-size dHash output."""
from pathlib import Path
from scripts.vision.group_images_by_dhash import run
IMAGES=Path(r"D:\yl\desktop\test\nine\img_cut");OUTPUT=Path(r"D:\yl\desktop\test\nine\save4");HASH_SIZE=16
def main()->int:
    try:r=run(IMAGES,OUTPUT,hash_size=HASH_SIZE)
    except Exception as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

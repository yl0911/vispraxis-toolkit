"""Preview organizing the historical street dataset into images and labels."""
from pathlib import Path
from scripts.datasets.organize_images_and_xml import run
SOURCE=Path(r"E:\yl\data\streetAI\Universal_object_manual_labeling\AI_street\v20230412\all")
IMAGE_DIR=SOURCE.parent/"images";XML_DIR=SOURCE.parent/"labels";EXECUTE=False
def main()->int:
    try:r=run(SOURCE,IMAGE_DIR,XML_DIR,execute=EXECUTE)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(r);print(f"mode={'execute' if EXECUTE else 'preview'}");return 0
if __name__=="__main__":raise SystemExit(main())

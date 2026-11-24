"""Preview copying the nine-image XML template beside every image."""
from pathlib import Path
from scripts.documents.copy_xml_template_for_images import run
IMAGE_DIR=Path(r"D:\yl\desktop\test\nine\nine");TEMPLATE=Path(r"D:\yl\desktop\test\nine\temp.xml");EXECUTE=False
def main()->int:
    try:r=run(IMAGE_DIR,TEMPLATE,execute=EXECUTE)
    except OSError as e:print(f"ERROR: {e}");return 1
    print(r);print(f"mode={'execute' if EXECUTE else 'preview'}");return 0
if __name__=="__main__":raise SystemExit(main())

"""Create empty labels for unannotated images in Road puddle subdatasets."""
from pathlib import Path
from scripts.documents.create_empty_yolo_labels import run
BASE_DIR=Path(r"E:\yl\data\Road_puddle\2amok_cut")
def main()->int:
    if not BASE_DIR.is_dir():print(f"ERROR: Directory not found: {BASE_DIR}");return 1
    for dataset in sorted(p for p in BASE_DIR.iterdir() if p.is_dir()):
        try:r=run(dataset/"images",dataset/"txt",xml_dir=dataset/"labels")
        except OSError as e:print(f"ERROR: {dataset}: {e}");continue
        print(dataset.name,r)
    return 0
if __name__=="__main__":raise SystemExit(main())

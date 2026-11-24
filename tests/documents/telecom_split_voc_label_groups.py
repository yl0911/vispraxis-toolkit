"""Split historical telecom VOC objects into key, point, and logo groups."""
from pathlib import Path
from scripts.documents.split_voc_by_label_groups import run
XML_DIR=Path(r"F:\localcode\test\xml_img");OUTPUT=XML_DIR.parent/"xml_save"
GROUPS={"key_classes":{"zx","qly","ysx","wx","ptn","ly","onu"},"four_points":{"top_right","top_left","bottom_right","bottom_left"},"logo":{"logo"}}
def main()->int:
    try:r=run(XML_DIR,OUTPUT,GROUPS)
    except Exception as e:print(f"ERROR: {e}");return 1
    print(r);return 0
if __name__=="__main__":raise SystemExit(main())

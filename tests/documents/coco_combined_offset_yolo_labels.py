"""Preview the historical COCO/VOC combined YOLO class-ID adjustment."""

from pathlib import Path

from scripts.documents.offset_yolo_class_ids import run

LABEL_DIR = Path(r"F:\data\all\coco_and_voc\combine\cocoTrain_vocAll_expand\txt")
OFFSET = -1
NAME_LENGTH = 8
EXECUTE = False


def main() -> int:
    try:
        result = run(LABEL_DIR, offset=OFFSET, name_length=NAME_LENGTH, execute=EXECUTE)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"matched={result.matched_files} files={result.changed_files} rows={result.changed_rows}")
    print(f"mode={'execute' if EXECUTE else 'preview'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

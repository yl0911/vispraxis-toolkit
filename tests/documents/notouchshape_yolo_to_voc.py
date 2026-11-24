"""Business call for converting notouchshape YOLO labels to VOC XML.

    python -m tests.documents.notouchshape_yolo_to_voc --class shape
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.documents.yolo_to_voc import run

# Business parameter preset migrated from important/txt2xml.py.
DEFAULT_BASE_DIR = Path(r"D:\yl\data\notouchshape\train")
DEFAULT_IMAGE_NAME = "images"
DEFAULT_LABEL_NAME = "txt"
DEFAULT_OUTPUT_NAME = "labels"
DEFAULT_CLASSES = ("0",)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--image-name", default=DEFAULT_IMAGE_NAME)
    parser.add_argument("--label-name", default=DEFAULT_LABEL_NAME)
    parser.add_argument("--output-name", default=DEFAULT_OUTPUT_NAME)
    parser.add_argument("--class", dest="classes", action="append")
    parser.add_argument("--recursive", action="store_true")
    args = parser.parse_args(argv)
    classes = tuple(args.classes) if args.classes else DEFAULT_CLASSES
    image_dir = args.base_dir / args.image_name
    label_dir = args.base_dir / args.label_name
    output_dir = args.base_dir / args.output_name
    print(f"image_dir:  {image_dir}")
    print(f"label_dir:  {label_dir}")
    print(f"output_dir: {output_dir}")
    print(f"classes:    {classes}")
    try:
        result = run(
            image_dir,
            label_dir,
            output_dir,
            classes=classes,
            recursive=args.recursive,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"converted={result.documents_converted}/{result.labels_found} "
        f"objects={result.objects_written}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

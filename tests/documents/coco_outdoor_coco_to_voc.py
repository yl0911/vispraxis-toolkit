"""COCO outdoor business call for exporting selected classes to VOC.

    python -m tests.documents.coco_outdoor_coco_to_voc
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.documents.coco_to_voc import run

DEFAULT_BASE_DIR = Path(r"F:\data\coco\coco2017\coco")
DEFAULT_DATASET = "val2017"
DEFAULT_CLASSES = ("person", "car", "bus", "truck")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--class", dest="classes", action="append")
    parser.add_argument("--copy-images", action="store_true")
    args = parser.parse_args(argv)
    classes = tuple(args.classes or DEFAULT_CLASSES)
    coco_file = args.base_dir / "annotations" / f"instances_{args.dataset}.json"
    image_dir = args.base_dir / args.dataset
    output_dir = args.base_dir / f"{args.dataset}_voc" / "Annotations"
    image_output_dir = args.base_dir / f"{args.dataset}_voc" / "JPEGImages"
    print(f"coco_file:  {coco_file}")
    print(f"output_dir: {output_dir}")
    print(f"classes:    {classes}")
    try:
        result = run(
            coco_file,
            output_dir,
            classes=classes,
            image_dir=image_dir if args.copy_images else None,
            image_output_dir=image_output_dir if args.copy_images else None,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"documents={result.documents_written}/{result.images_found} "
        f"objects={result.objects_written} copied={result.images_copied} "
        f"errors={len(result.errors)}"
    )
    return 0 if not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

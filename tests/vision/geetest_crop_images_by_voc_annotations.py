"""Geetest V4 call for cropping labeled icons from paired VOC annotations.

    python -m tests.vision.geetest_crop_images_by_voc_annotations
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.vision.crop_images_by_voc_annotations import run

DEFAULT_BASE_DIR = Path(
    r"D:\yl\desktop\test\OSS\geetest\geetestclick_v4\20250704"
)
DEFAULT_IMAGE_NAME = "images_all"
DEFAULT_VOC_NAME = "xml"
DEFAULT_OUTPUT_NAME = "images_save"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--image-name", default=DEFAULT_IMAGE_NAME)
    parser.add_argument("--voc-name", default=DEFAULT_VOC_NAME)
    parser.add_argument("--output-name", default=DEFAULT_OUTPUT_NAME)
    parser.add_argument("--class", dest="classes", action="append")
    parser.add_argument("--no-recursive", action="store_true")
    args = parser.parse_args(argv)
    image_dir = args.base_dir / args.image_name
    voc_dir = args.base_dir / args.voc_name
    output_dir = args.base_dir / args.output_name
    print(f"image_dir:  {image_dir}")
    print(f"voc_dir:    {voc_dir}")
    print(f"output_dir: {output_dir}")
    try:
        result = run(
            image_dir,
            voc_dir,
            output_dir,
            classes=tuple(args.classes or ()),
            recursive=not args.no_recursive,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"processed={result.images_processed}/{result.images_found} "
        f"objects={result.objects_found} crops={result.crops_written} "
        f"errors={len(result.errors)}"
    )
    return 0 if not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

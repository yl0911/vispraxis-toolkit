"""Geetest business call for moving images that have matching XML files.

This is a business test, not an automated unit test. It stores the parameters
used by the Geetest dataset task so the call can be reused in another checkout
or development environment.

Default behavior is preview-only. Review or override the paths before running:

    python -m tests.datasets.geetest_move_images_matching_xml
    python -m tests.datasets.geetest_move_images_matching_xml \
        --annotation-dir D:\\data\\cut --image-dir D:\\data\\images --execute
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.datasets.move_images_matching_xml import run

# Business parameter preset. Update this section when the task changes.
DEFAULT_ANNOTATION_DIR = Path(
    r"D:\yl\desktop\test\geetest_image\geetestclick_v4_botdeflector\20260721\cut"
)
DEFAULT_IMAGE_DIR = Path(
    r"D:\yl\desktop\test\geetest_image\geetestclick_v4_botdeflector\20260721\images"
)
DEFAULT_RECURSIVE = False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--annotation-dir", type=Path, default=DEFAULT_ANNOTATION_DIR)
    parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMAGE_DIR)
    parser.add_argument("--recursive", action="store_true", default=DEFAULT_RECURSIVE)
    parser.add_argument("--execute", action="store_true", help="Move files after previewing")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"annotation_dir: {args.annotation_dir}")
    print(f"image_dir:      {args.image_dir}")
    print(f"mode:           {'execute' if args.execute else 'preview'}")
    try:
        result = run(
            args.annotation_dir,
            args.image_dir,
            execute=args.execute,
            overwrite=args.overwrite,
            recursive=args.recursive,
        )
    except (FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(
        f"matched={result.matched} planned={result.planned} "
        f"moved={result.moved} skipped={result.skipped}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

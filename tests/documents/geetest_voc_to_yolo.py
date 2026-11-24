"""Geetest business call for converting VOC annotations to YOLO labels.

This file intentionally keeps business paths and class parameters separate
from the generic converter. Update the preset or override it from the command
line when using the repository in another environment:

    python -m tests.documents.geetest_voc_to_yolo
    python -m tests.documents.geetest_voc_to_yolo \
        --base-dir D:\\data\\save_compose --class 0
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.documents.voc_to_yolo import run

# Business parameter preset. Update this section when the task changes.
DEFAULT_BASE_DIR = Path(
    r"D:\yl\desktop\test\geetest_image\geetest_v4_all\ml-png\icon_mask\save_compose"
)
DEFAULT_SOURCE_NAME = "Annotations"
DEFAULT_OUTPUT_NAME = "labels"
DEFAULT_CLASSES = ("0",)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--source-name", default=DEFAULT_SOURCE_NAME)
    parser.add_argument("--output-name", default=DEFAULT_OUTPUT_NAME)
    parser.add_argument("--class", dest="classes", action="append")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--fail-on-unknown-class", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    classes = tuple(args.classes) if args.classes else DEFAULT_CLASSES
    source_dir = args.base_dir / args.source_name
    output_dir = args.base_dir / args.output_name

    print(f"source_dir: {source_dir}")
    print(f"output_dir: {output_dir}")
    print(f"classes:    {classes}")
    try:
        result = run(
            source_dir,
            output_dir,
            classes=classes,
            recursive=args.recursive,
            fail_on_unknown_class=args.fail_on_unknown_class,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(
        f"converted={result.documents_converted}/{result.documents_found} "
        f"objects={result.objects_written} skipped={result.objects_skipped}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

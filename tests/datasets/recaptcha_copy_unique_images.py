"""Recaptcha business call for building a hash-deduplicated image directory.

Preview first, then add ``--execute`` after checking the paths:

    python -m tests.datasets.recaptcha_copy_unique_images
    python -m tests.datasets.recaptcha_copy_unique_images --execute
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.datasets.copy_unique_images_by_hash import run

# Business parameter preset migrated from dingstock/rename_remove_duplicates.py.
DEFAULT_BASE_DIR = Path(
    r"D:\yl\desktop\test\geetest_image\geetestclick_common\20261124"
)
DEFAULT_SOURCE_NAME = "icon"
DEFAULT_OUTPUT_NAME = "unique"
DEFAULT_METHOD = "md5"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--source-name", default=DEFAULT_SOURCE_NAME)
    parser.add_argument("--output-name", default=DEFAULT_OUTPUT_NAME)
    parser.add_argument("--method", choices=("md5", "ahash", "dhash", "phash"), default=DEFAULT_METHOD)
    parser.add_argument("--hash-size", type=int, default=8)
    parser.add_argument("--keep-original-name", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    source_dir = args.base_dir / args.source_name
    output_dir = args.base_dir / args.output_name
    print(f"source_dir: {source_dir}")
    print(f"output_dir: {output_dir}")
    print(f"method:     {args.method}")
    print(f"mode:       {'execute' if args.execute else 'preview'}")
    try:
        result = run(
            source_dir,
            output_dir,
            method=args.method,
            hash_size=args.hash_size,
            keep_original_name=args.keep_original_name,
            execute=args.execute,
        )
    except (FileNotFoundError, FileExistsError, ImportError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"images={result.images_found} unique={result.unique_images} "
        f"duplicates={result.duplicate_images} failed={result.failed_images} "
        f"copied={result.copied}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.failed_images == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

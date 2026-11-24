"""Street dataset call for synchronizing VOC sizes with source images.

    python -m tests.documents.street_sync_voc_image_sizes
    python -m tests.documents.street_sync_voc_image_sizes --execute
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.documents.sync_voc_image_sizes import run

DEFAULT_BASE_DIR = Path(r"E:\yl\data\streetAI\train_model\all_data")
DEFAULT_IMAGE_NAME = "images"
DEFAULT_VOC_NAME = "labels"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--image-name", default=DEFAULT_IMAGE_NAME)
    parser.add_argument("--voc-name", default=DEFAULT_VOC_NAME)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    image_dir = args.base_dir / args.image_name
    voc_dir = args.base_dir / args.voc_name
    print(f"image_dir: {image_dir}")
    print(f"voc_dir:   {voc_dir}")
    print(f"mode:      {'execute' if args.execute else 'preview'}")
    try:
        result = run(
            image_dir,
            voc_dir,
            recursive=args.recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"documents={result.documents_found} changed={result.documents_changed} "
        f"failed={result.documents_failed} updated={result.updated}"
    )
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

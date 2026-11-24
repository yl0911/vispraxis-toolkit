"""Street dataset call for isolating images and labels without a counterpart.

Preview the operation first:

    python -m tests.datasets.street_quarantine_unpaired_files

Move the reported files only after reviewing the paths:

    python -m tests.datasets.street_quarantine_unpaired_files --execute
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.datasets.quarantine_unpaired_files import run

# Business parameter preset migrated from important/del_imgxml.py.
DEFAULT_BASE_DIR = Path(r"E:\yl\data\streetAI")
DEFAULT_IMAGE_NAME = "images"
DEFAULT_LABEL_NAME = "labels"
DEFAULT_QUARANTINE_NAME = "remove"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--image-name", default=DEFAULT_IMAGE_NAME)
    parser.add_argument("--label-name", default=DEFAULT_LABEL_NAME)
    parser.add_argument("--quarantine-name", default=DEFAULT_QUARANTINE_NAME)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    image_dir = args.base_dir / args.image_name
    label_dir = args.base_dir / args.label_name
    quarantine_dir = args.base_dir / args.quarantine_name
    print(f"image_dir:      {image_dir}")
    print(f"label_dir:      {label_dir}")
    print(f"quarantine_dir: {quarantine_dir}")
    print(f"mode:           {'execute' if args.execute else 'preview'}")
    try:
        result = run(
            image_dir,
            label_dir,
            quarantine_dir,
            recursive=args.recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, FileExistsError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"images={result.image_files} labels={result.label_files} "
        f"unpaired_images={result.unpaired_images} "
        f"unpaired_labels={result.unpaired_labels} moved={result.moved}"
    )
    for item in result.planned:
        print(f"{item.kind}: {item.source} -> {item.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

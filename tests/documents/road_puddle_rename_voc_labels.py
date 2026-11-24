"""Road-puddle business call for correcting historical VOC class names.

    python -m tests.documents.road_puddle_rename_voc_labels
    python -m tests.documents.road_puddle_rename_voc_labels --execute
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.documents.rename_voc_labels import run

DEFAULT_SOURCE_DIR = Path(r"E:\yl\data\Road_puddle\2amok_cut\videoText_99358\labels")
DEFAULT_MAPPING = {"ccement_cart": "cement_cart"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    print(f"source_dir: {args.source_dir}")
    print(f"mapping:    {DEFAULT_MAPPING}")
    print(f"mode:       {'execute' if args.execute else 'preview'}")
    try:
        result = run(
            args.source_dir,
            DEFAULT_MAPPING,
            recursive=args.recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"documents={result.documents_found} changed={result.documents_changed} "
        f"labels={result.labels_changed} failed={result.documents_failed}"
    )
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

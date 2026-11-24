"""Business call for exporting historical COCO-person VOC labels to COCO JSON.

    python -m tests.documents.coco_person_voc_to_coco
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.documents.voc_to_coco import run

# Business parameter preset migrated from imgdeal/voc_to_coco_old.py.
DEFAULT_SOURCE_DIR = Path(r"G:\dataset\COCO\person\coco_val2014\annotations")
DEFAULT_OUTPUT_FILE = Path(r"G:\dataset\COCO\person\coco_val2014\instances_val2014.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--recursive", action="store_true")
    args = parser.parse_args(argv)
    print(f"source_dir:  {args.source_dir}")
    print(f"output_file: {args.output_file}")
    try:
        result = run(args.source_dir, args.output_file, recursive=args.recursive)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"converted={result.documents_converted}/{result.documents_found} "
        f"objects={result.objects_written}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

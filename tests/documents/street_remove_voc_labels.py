"""Street dataset business call for removing obsolete VOC object classes.

    python -m tests.documents.street_remove_voc_labels
    python -m tests.documents.street_remove_voc_labels --execute
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.documents.remove_voc_labels import run

DEFAULT_SOURCE_DIR = Path(
    r"E:\yl\data\streetAI\Universal_object_manual_labeling\AI_street\labels"
)
DEFAULT_LABELS = ("trash can",)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--label", dest="labels", action="append")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    labels = tuple(args.labels or DEFAULT_LABELS)
    print(f"source_dir: {args.source_dir}")
    print(f"labels:     {labels}")
    print(f"mode:       {'execute' if args.execute else 'preview'}")
    try:
        result = run(
            args.source_dir,
            labels=labels,
            recursive=args.recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"documents={result.documents_found} changed={result.documents_changed} "
        f"objects={result.objects_removed} failed={result.documents_failed}"
    )
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

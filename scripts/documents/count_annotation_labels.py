"""Count class labels in YOLO TXT and Pascal VOC XML documents.

Python call:
    ``run(label_dir, labels=None, recursive=False)``

CLI call:
    ``python scripts/documents/count_annotation_labels.py LABEL_DIR``

Merged duplicate sources:
    ``D:\\yl\\localcode\\bty\\statistics_yolo_label.py``
    ``D:\\yl\\localcode\\imgdeal\\statistics_yolo_label.py``
    ``D:\\yl\\localcode\\important\\statistics_yolo_label.py``
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


def run(
    label_dir: Path,
    *,
    labels: set[str] | None = None,
    recursive: bool = False,
) -> dict[str, int]:
    """Return label counts from TXT and XML files in a directory."""
    if not label_dir.is_dir():
        raise FileNotFoundError(f"Label directory not found: {label_dir}")
    pattern = "**/*" if recursive else "*"
    counts: Counter[str] = Counter()
    for path in sorted(label_dir.glob(pattern)):
        if not path.is_file():
            continue
        if path.suffix.casefold() == ".txt":
            names = [line.split()[0] for line in path.read_text(encoding="utf-8").splitlines() if line.split()]
        elif path.suffix.casefold() == ".xml":
            names = [node.text.strip() for node in ET.parse(path).getroot().findall("object/name") if node.text]
        else:
            continue
        counts.update(name for name in names if labels is None or name in labels)
    return dict(sorted(counts.items()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("label_dir", type=Path)
    parser.add_argument("--label", dest="labels", action="append")
    parser.add_argument("--recursive", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        counts = run(args.label_dir, labels=set(args.labels) if args.labels else None, recursive=args.recursive)
    except (ET.ParseError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    for index, (label, count) in enumerate(counts.items()):
        print(f"{index} {label} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

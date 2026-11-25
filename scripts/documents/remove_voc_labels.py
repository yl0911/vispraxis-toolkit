"""Remove selected object labels from Pascal VOC XML documents.

Function:
    Find VOC objects whose class name is in a configured set and preview or
    remove those object nodes from the XML documents.

Python call:
    ``run(voc_dir, labels=("trash can",), execute=False)``

CLI call:
    ``python scripts/documents/remove_voc_labels.py VOC_DIR --label unwanted``

Side effects:
    Preview-only by default. Pass ``execute=True`` or ``--execute`` to update XML.

Merged legacy sources:
    ``D:\\yl\\localcode\\bty\\xmlTool.py``
    ``D:\\yl\\localcode\\imgdeal\\xmlTool.py``
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RemovalResult:
    documents_found: int
    documents_changed: int
    documents_failed: int
    objects_removed: int
    labels_removed: dict[str, int]
    errors: tuple[str, ...]


def run(
    source_dir: Path,
    *,
    labels: tuple[str, ...],
    recursive: bool = False,
    execute: bool = False,
) -> RemovalResult:
    """Preview or remove selected VOC object nodes."""
    if not source_dir.is_dir():
        raise FileNotFoundError(f"VOC directory not found: {source_dir}")
    selected = {label.strip() for label in labels if label.strip()}
    if not selected:
        raise ValueError("At least one label is required")
    sources = sorted(source_dir.glob("**/*.xml" if recursive else "*.xml"))
    counts: Counter[str] = Counter()
    errors: list[str] = []
    changed = 0
    for source in sources:
        try:
            tree = ET.parse(source)
            root = tree.getroot()
            matches = []
            for obj in root.findall("object"):
                name = obj.findtext("name", "").strip()
                if name in selected:
                    matches.append((obj, name))
            if not matches:
                continue
            changed += 1
            for obj, name in matches:
                counts[name] += 1
                if execute:
                    root.remove(obj)
            if execute:
                ET.indent(tree, space="  ")
                tree.write(source, encoding="utf-8", xml_declaration=True)
        except (ET.ParseError, OSError, ValueError) as exc:
            errors.append(f"{source}: {exc}")
    return RemovalResult(
        documents_found=len(sources),
        documents_changed=changed,
        documents_failed=len(errors),
        objects_removed=sum(counts.values()),
        labels_removed=dict(counts),
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--label", dest="labels", action="append", required=True)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.source_dir,
            labels=tuple(args.labels),
            recursive=args.recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"documents={result.documents_found} changed={result.documents_changed} "
        f"objects={result.objects_removed} failed={result.documents_failed} "
        f"mode={'execute' if args.execute else 'preview'}"
    )
    for label, count in sorted(result.labels_removed.items()):
        print(f"{label}: {count}")
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

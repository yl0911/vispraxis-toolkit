"""Rename object class labels in Pascal VOC XML documents.

Function:
    Apply an explicit old-to-new class mapping to VOC annotations. XML files
    are modified in place only when execution is explicitly enabled.

Python call:
    ``run(voc_dir, {"old_name": "new_name"}, execute=False)``

CLI call:
    ``python scripts/documents/rename_voc_labels.py VOC_DIR --map old=new``

Side effects:
    Preview-only by default. Pass ``execute=True`` or ``--execute`` to update XML.

Legacy source:
    ``D:\\yl\\localcode\\important\\Pictools.py``
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RenameResult:
    documents_found: int
    documents_changed: int
    documents_failed: int
    labels_changed: int
    replacements: dict[tuple[str, str], int]
    errors: tuple[str, ...]


def run(
    source_dir: Path,
    mapping: dict[str, str],
    *,
    recursive: bool = False,
    execute: bool = False,
) -> RenameResult:
    """Preview or apply class-name replacements to VOC XML files."""
    if not source_dir.is_dir():
        raise FileNotFoundError(f"VOC directory not found: {source_dir}")
    if not mapping:
        raise ValueError("At least one label mapping is required")
    if any(not old or not new for old, new in mapping.items()):
        raise ValueError("Label mapping names must not be empty")

    sources = sorted(source_dir.glob("**/*.xml" if recursive else "*.xml"))
    replacements: Counter[tuple[str, str]] = Counter()
    errors: list[str] = []
    changed_documents = 0
    for source in sources:
        try:
            tree = ET.parse(source)
            root = tree.getroot()
            changed = 0
            for obj in root.findall("object"):
                name = obj.find("name")
                if name is None or name.text is None:
                    continue
                old_name = name.text.strip()
                new_name = mapping.get(old_name)
                if new_name is None or new_name == old_name:
                    continue
                name.text = new_name
                replacements[(old_name, new_name)] += 1
                changed += 1
            if changed:
                changed_documents += 1
                if execute:
                    ET.indent(tree, space="  ")
                    tree.write(source, encoding="utf-8", xml_declaration=True)
        except (ET.ParseError, OSError, ValueError) as exc:
            errors.append(f"{source}: {exc}")

    return RenameResult(
        documents_found=len(sources),
        documents_changed=changed_documents,
        documents_failed=len(errors),
        labels_changed=sum(replacements.values()),
        replacements=dict(replacements),
        errors=tuple(errors),
    )


def _mapping(value: str) -> tuple[str, str]:
    old, separator, new = value.partition("=")
    if not separator or not old.strip() or not new.strip():
        raise argparse.ArgumentTypeError("Mappings must use OLD=NEW")
    return old.strip(), new.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--map", dest="mappings", action="append", type=_mapping, required=True)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.source_dir,
            dict(args.mappings),
            recursive=args.recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"documents={result.documents_found} changed={result.documents_changed} "
        f"labels={result.labels_changed} failed={result.documents_failed} "
        f"mode={'execute' if args.execute else 'preview'}"
    )
    for (old, new), count in sorted(result.replacements.items()):
        print(f"{old} -> {new}: {count}")
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

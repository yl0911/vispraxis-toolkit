"""Synchronize Pascal VOC size fields with their matching image files.

Function:
    Match XML and image files by relative path and stem, read actual dimensions,
    and preview or update the VOC width, height, and depth fields.

Python call:
    ``run(image_dir, voc_dir, execute=False)``

CLI call:
    ``python scripts/documents/sync_voc_image_sizes.py IMAGES VOC``

Side effects:
    Preview-only by default. Invalid inputs are reported and never deleted.

Legacy source:
    ``D:\\yl\\localcode\\important\\Pictools.py``
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")


@dataclass(frozen=True, slots=True)
class SizeChange:
    xml: Path
    image: Path
    old_size: tuple[int | None, int | None, int | None]
    new_size: tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class SyncResult:
    documents_found: int
    documents_changed: int
    documents_failed: int
    updated: int
    changes: tuple[SizeChange, ...]
    errors: tuple[str, ...]


def _find_image(image_dir: Path, relative_xml: Path) -> Path:
    base = image_dir / relative_xml.with_suffix("")
    for suffix in IMAGE_SUFFIXES:
        candidate = base.with_suffix(suffix)
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"No image matches annotation: {relative_xml}")


def _optional_int(parent: ET.Element, name: str) -> int | None:
    node = parent.find(name)
    if node is None or node.text is None:
        return None
    try:
        return int(node.text.strip())
    except ValueError:
        return None


def run(
    image_dir: Path,
    voc_dir: Path,
    *,
    recursive: bool = False,
    execute: bool = False,
) -> SyncResult:
    """Preview or update VOC image dimensions from matching image files."""
    if not image_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not voc_dir.is_dir():
        raise FileNotFoundError(f"VOC directory not found: {voc_dir}")

    sources = sorted(voc_dir.glob("**/*.xml" if recursive else "*.xml"))
    changes: list[SizeChange] = []
    errors: list[str] = []
    updated = 0
    for source in sources:
        relative = source.relative_to(voc_dir)
        try:
            image_path = _find_image(image_dir, relative)
            with Image.open(image_path) as image:
                width, height = image.size
                depth = len(image.getbands())
            tree = ET.parse(source)
            root = tree.getroot()
            size = root.find("size")
            if size is None:
                size = ET.SubElement(root, "size")
            old_size = tuple(_optional_int(size, name) for name in ("width", "height", "depth"))
            new_size = (width, height, depth)
            if old_size == new_size:
                continue
            for name, value in zip(("width", "height", "depth"), new_size):
                node = size.find(name)
                if node is None:
                    node = ET.SubElement(size, name)
                node.text = str(value)
            changes.append(SizeChange(source, image_path, old_size, new_size))
            if execute:
                ET.indent(tree, space="  ")
                tree.write(source, encoding="utf-8", xml_declaration=True)
                updated += 1
        except (ET.ParseError, FileNotFoundError, OSError, ValueError) as exc:
            errors.append(f"{source}: {exc}")

    return SyncResult(
        documents_found=len(sources),
        documents_changed=len(changes),
        documents_failed=len(errors),
        updated=updated,
        changes=tuple(changes),
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("image_dir", type=Path)
    parser.add_argument("voc_dir", type=Path)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.image_dir,
            args.voc_dir,
            recursive=args.recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"documents={result.documents_found} changed={result.documents_changed} "
        f"failed={result.documents_failed} updated={result.updated} "
        f"mode={'execute' if args.execute else 'preview'}"
    )
    for change in result.changes:
        print(f"{change.xml}: {change.old_size} -> {change.new_size}")
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

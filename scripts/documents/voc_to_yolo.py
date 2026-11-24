"""Convert Pascal VOC XML bounding boxes to YOLO TXT labels.

Function:
    Read VOC XML documents, select configured classes, normalize bounding boxes,
    and write one YOLO TXT document per XML file. Source files are not modified.

Python call:
    ``run(source_dir, output_dir, classes=("cat", "dog"))``

CLI call:
    ``python scripts/documents/voc_to_yolo.py VOC_DIR YOLO_DIR --class cat``

Merged legacy sources:
    ``D:\\yl\\localcode\\important\\voc_to_yolo.py``
    ``D:\\yl\\localcode\\bty\\voc_to_yolo.py``

The project-specific oriented-point export from the newer source is not folded
into this generic bounding-box converter and remains pending review.
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ConversionResult:
    """Summary of a directory conversion."""

    documents_found: int
    documents_converted: int
    documents_failed: int
    objects_written: int
    objects_skipped: int
    outputs: tuple[Path, ...]
    errors: tuple[str, ...]


def normalize_box(
    image_width: int,
    image_height: int,
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
) -> tuple[float, float, float, float]:
    """Convert absolute VOC corners to normalized YOLO center coordinates."""
    if image_width <= 0 or image_height <= 0:
        raise ValueError("VOC image width and height must be positive")
    if xmax < xmin or ymax < ymin:
        raise ValueError("Bounding box maximum must not be smaller than minimum")
    width = xmax - xmin
    height = ymax - ymin
    return (
        round((xmin + width / 2.0) / image_width, 6),
        round((ymin + height / 2.0) / image_height, 6),
        round(width / image_width, 6),
        round(height / image_height, 6),
    )


def _required_text(parent: ET.Element, name: str, source: Path) -> str:
    node = parent.find(name)
    if node is None or node.text is None:
        raise ValueError(f"Missing {name!r} in {source}")
    return node.text.strip()


def convert_file(
    source: Path,
    destination: Path,
    class_ids: dict[str, int],
    *,
    fail_on_unknown_class: bool = False,
) -> tuple[int, int]:
    """Convert one VOC XML file and return (written, skipped) object counts."""
    root = ET.parse(source).getroot()
    size = root.find("size")
    if size is None:
        raise ValueError(f"Missing 'size' in {source}")
    image_width = int(_required_text(size, "width", source))
    image_height = int(_required_text(size, "height", source))

    rows: list[str] = []
    skipped = 0
    for obj in root.findall("object"):
        class_name = _required_text(obj, "name", source)
        if class_name not in class_ids:
            if fail_on_unknown_class:
                raise ValueError(f"Unknown class {class_name!r} in {source}")
            skipped += 1
            continue
        box = obj.find("bndbox")
        if box is None:
            raise ValueError(f"Missing 'bndbox' for {class_name!r} in {source}")
        normalized = normalize_box(
            image_width,
            image_height,
            float(_required_text(box, "xmin", source)),
            float(_required_text(box, "ymin", source)),
            float(_required_text(box, "xmax", source)),
            float(_required_text(box, "ymax", source)),
        )
        rows.append(f"{class_ids[class_name]} " + " ".join(map(str, normalized)))

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    return len(rows), skipped


def run(
    source_dir: Path,
    output_dir: Path,
    *,
    classes: tuple[str, ...],
    class_mapping: dict[str, int] | None = None,
    recursive: bool = False,
    fail_on_unknown_class: bool = False,
) -> ConversionResult:
    """Convert VOC XML files in one directory to YOLO TXT files."""
    if not source_dir.is_dir():
        raise FileNotFoundError(f"VOC source directory not found: {source_dir}")
    if not classes:
        raise ValueError("At least one class is required")

    class_ids = class_mapping or {name: index for index, name in enumerate(classes)}
    missing = set(classes) - set(class_ids)
    if missing:
        raise ValueError(f"Class mapping is missing: {sorted(missing)}")

    pattern = "**/*.xml" if recursive else "*.xml"
    sources = sorted(source_dir.glob(pattern))
    outputs: list[Path] = []
    errors: list[str] = []
    converted = written = skipped = 0

    for source in sources:
        destination = output_dir / source.relative_to(source_dir).with_suffix(".txt")
        try:
            file_written, file_skipped = convert_file(
                source,
                destination,
                class_ids,
                fail_on_unknown_class=fail_on_unknown_class,
            )
        except (ET.ParseError, OSError, ValueError) as exc:
            errors.append(f"{source}: {exc}")
            continue
        converted += 1
        written += file_written
        skipped += file_skipped
        outputs.append(destination)

    return ConversionResult(
        documents_found=len(sources),
        documents_converted=converted,
        documents_failed=len(errors),
        objects_written=written,
        objects_skipped=skipped,
        outputs=tuple(outputs),
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source_dir", type=Path, help="Directory containing VOC XML files")
    parser.add_argument("output_dir", type=Path, help="Directory for YOLO TXT files")
    parser.add_argument("--class", dest="classes", action="append", required=True)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--fail-on-unknown-class", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.source_dir,
            args.output_dir,
            classes=tuple(args.classes),
            recursive=args.recursive,
            fail_on_unknown_class=args.fail_on_unknown_class,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"converted={result.documents_converted}/{result.documents_found} "
        f"objects={result.objects_written} skipped={result.objects_skipped}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

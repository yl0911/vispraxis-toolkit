"""Convert normalized YOLO TXT labels to Pascal VOC XML annotations.

Function:
    Match labels to images by relative path and stem, read actual image sizes,
    and write one VOC XML document per matched label. Inputs are unchanged.

Python call:
    ``run(image_dir, label_dir, output_dir, classes=("cat", "dog"))``

CLI call:
    ``python scripts/documents/yolo_to_voc.py IMAGES LABELS VOC --class cat``

Legacy source:
    ``D:\\yl\\localcode\\important\\txt2xml.py``
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


@dataclass(frozen=True, slots=True)
class ConversionResult:
    labels_found: int
    documents_converted: int
    documents_failed: int
    objects_written: int
    outputs: tuple[Path, ...]
    errors: tuple[str, ...]


def _find_image(image_dir: Path, relative_label: Path) -> Path:
    base = image_dir / relative_label.with_suffix("")
    for suffix in IMAGE_SUFFIXES:
        candidate = base.with_suffix(suffix)
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"No image matches label: {relative_label}")


def _parse_rows(source: Path, classes: tuple[str, ...]) -> list[tuple[str, float, float, float, float]]:
    rows: list[tuple[str, float, float, float, float]] = []
    for line_number, raw_line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("%"):
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f"Expected 5 columns at {source}:{line_number}")
        class_id = int(parts[0])
        if class_id < 0 or class_id >= len(classes):
            raise ValueError(f"Unknown class id {class_id} at {source}:{line_number}")
        x_center, y_center, width, height = map(float, parts[1:])
        if width < 0 or height < 0:
            raise ValueError(f"Negative box size at {source}:{line_number}")
        rows.append((classes[class_id], x_center, y_center, width, height))
    return rows


def _write_voc(
    destination: Path,
    image: Path,
    image_size: tuple[int, int],
    objects: list[tuple[str, float, float, float, float]],
) -> int:
    image_width, image_height = image_size
    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = image.parent.name
    ET.SubElement(root, "filename").text = image.name
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(image_width)
    ET.SubElement(size, "height").text = str(image_height)
    ET.SubElement(size, "depth").text = "3"
    ET.SubElement(root, "segmented").text = "0"
    for name, x_center, y_center, width, height in objects:
        xmin = max(0, round((x_center - width / 2) * image_width))
        ymin = max(0, round((y_center - height / 2) * image_height))
        xmax = min(image_width, round((x_center + width / 2) * image_width))
        ymax = min(image_height, round((y_center + height / 2) * image_height))
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = name
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "0"
        ET.SubElement(obj, "difficult").text = "0"
        box = ET.SubElement(obj, "bndbox")
        for key, value in (("xmin", xmin), ("ymin", ymin), ("xmax", xmax), ("ymax", ymax)):
            ET.SubElement(box, key).text = str(value)
    ET.indent(root, space="  ")
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)
    return len(objects)


def run(
    image_dir: Path,
    label_dir: Path,
    output_dir: Path,
    *,
    classes: tuple[str, ...],
    recursive: bool = False,
) -> ConversionResult:
    """Convert matched YOLO labels and images to VOC XML files."""
    if not image_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not label_dir.is_dir():
        raise FileNotFoundError(f"Label directory not found: {label_dir}")
    if not classes:
        raise ValueError("At least one class is required")

    labels = sorted(label_dir.glob("**/*.txt" if recursive else "*.txt"))
    outputs: list[Path] = []
    errors: list[str] = []
    object_count = 0
    for label in labels:
        relative = label.relative_to(label_dir)
        destination = output_dir / relative.with_suffix(".xml")
        try:
            image = _find_image(image_dir, relative)
            rows = _parse_rows(label, classes)
            with Image.open(image) as opened:
                image_size = opened.size
            object_count += _write_voc(destination, image, image_size, rows)
            outputs.append(destination)
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: {exc}")
    return ConversionResult(
        labels_found=len(labels),
        documents_converted=len(outputs),
        documents_failed=len(errors),
        objects_written=object_count,
        outputs=tuple(outputs),
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("image_dir", type=Path)
    parser.add_argument("label_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--class", dest="classes", action="append", required=True)
    parser.add_argument("--recursive", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.image_dir,
            args.label_dir,
            args.output_dir,
            classes=tuple(args.classes),
            recursive=args.recursive,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"converted={result.documents_converted}/{result.labels_found} "
        f"objects={result.objects_written}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

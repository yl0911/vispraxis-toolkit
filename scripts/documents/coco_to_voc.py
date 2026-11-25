"""Convert COCO detection annotations to Pascal VOC XML documents.

Function:
    Read one COCO JSON file, optionally select classes, and write one VOC XML
    document for each image that has a selected bounding-box annotation.

Python call:
    ``run(coco_file, output_dir, classes=("person",), image_dir=...)``

CLI call:
    ``python scripts/documents/coco_to_voc.py instances.json VOC --class person``

Side effects:
    Writes XML documents. Source JSON and images are not modified. Images are
    copied only when both ``image_dir`` and ``image_output_dir`` are supplied.

Merged legacy sources:
    ``D:\\yl\\localcode\\imgdeal\\coco_to_voc.py``
    ``D:\\yl\\localcode\\imgdeal\\COCOtoVOC.py``
"""

from __future__ import annotations

import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ConversionResult:
    images_found: int
    documents_written: int
    objects_written: int
    images_copied: int
    skipped_annotations: int
    errors: tuple[str, ...]
    outputs: tuple[Path, ...]


def _number(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    return float(value)


def _write_voc(
    destination: Path,
    image: dict[str, Any],
    objects: list[tuple[str, list[float]]],
) -> None:
    filename = str(image.get("file_name", "")).strip()
    if not filename:
        raise ValueError("COCO image is missing file_name")
    width = int(_number(image.get("width"), "image width"))
    height = int(_number(image.get("height"), "image height"))
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image size for {filename}")

    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = "VOC"
    ET.SubElement(root, "filename").text = filename
    source = ET.SubElement(root, "source")
    ET.SubElement(source, "database").text = "COCO"
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = "3"
    ET.SubElement(root, "segmented").text = "0"
    for class_name, bbox in objects:
        x, y, box_width, box_height = bbox
        xmin = max(0, round(x))
        ymin = max(0, round(y))
        xmax = min(width, round(x + box_width))
        ymax = min(height, round(y + box_height))
        if xmax <= xmin or ymax <= ymin:
            continue
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = class_name
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "0"
        ET.SubElement(obj, "difficult").text = "0"
        box = ET.SubElement(obj, "bndbox")
        for name, value in (("xmin", xmin), ("ymin", ymin), ("xmax", xmax), ("ymax", ymax)):
            ET.SubElement(box, name).text = str(value)
    ET.indent(root, space="  ")
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)


def run(
    coco_file: Path,
    output_dir: Path,
    *,
    classes: tuple[str, ...] = (),
    image_dir: Path | None = None,
    image_output_dir: Path | None = None,
) -> ConversionResult:
    """Convert selected COCO bounding boxes into VOC XML documents."""
    if not coco_file.is_file():
        raise FileNotFoundError(f"COCO JSON not found: {coco_file}")
    if (image_dir is None) != (image_output_dir is None):
        raise ValueError("image_dir and image_output_dir must be supplied together")
    if image_dir is not None and not image_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    data = json.loads(coco_file.read_text(encoding="utf-8"))
    images = data.get("images", [])
    annotations = data.get("annotations", [])
    categories = data.get("categories", [])
    if not all(isinstance(value, list) for value in (images, annotations, categories)):
        raise ValueError("COCO images, annotations, and categories must be lists")

    category_names = {
        category["id"]: str(category["name"])
        for category in categories
        if isinstance(category, dict) and "id" in category and "name" in category
    }
    selected = set(classes) if classes else set(category_names.values())
    by_image: dict[Any, list[tuple[str, list[float]]]] = defaultdict(list)
    skipped = 0
    for annotation in annotations:
        if not isinstance(annotation, dict):
            skipped += 1
            continue
        class_name = category_names.get(annotation.get("category_id"))
        bbox = annotation.get("bbox")
        if class_name not in selected or not isinstance(bbox, list) or len(bbox) != 4:
            skipped += 1
            continue
        try:
            parsed_bbox = [_number(value, "bbox value") for value in bbox]
        except ValueError:
            skipped += 1
            continue
        if parsed_bbox[2] <= 0 or parsed_bbox[3] <= 0:
            skipped += 1
            continue
        by_image[annotation.get("image_id")].append((class_name, parsed_bbox))

    outputs: list[Path] = []
    errors: list[str] = []
    copied = objects_written = 0
    for image in images:
        if not isinstance(image, dict) or image.get("id") not in by_image:
            continue
        filename = str(image.get("file_name", ""))
        destination = output_dir / Path(filename).with_suffix(".xml").name
        try:
            objects = by_image[image["id"]]
            _write_voc(destination, image, objects)
            outputs.append(destination)
            objects_written += len(objects)
            if image_dir is not None and image_output_dir is not None:
                source_image = image_dir / filename
                if not source_image.is_file():
                    raise FileNotFoundError(f"Image not found: {source_image}")
                target_image = image_output_dir / filename
                target_image.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_image, target_image)
                copied += 1
        except (OSError, ValueError) as exc:
            errors.append(f"{filename or image.get('id')}: {exc}")
    return ConversionResult(
        images_found=len(images),
        documents_written=len(outputs),
        objects_written=objects_written,
        images_copied=copied,
        skipped_annotations=skipped,
        errors=tuple(errors),
        outputs=tuple(outputs),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("coco_file", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--class", dest="classes", action="append")
    parser.add_argument("--image-dir", type=Path)
    parser.add_argument("--image-output-dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.coco_file,
            args.output_dir,
            classes=tuple(args.classes or ()),
            image_dir=args.image_dir,
            image_output_dir=args.image_output_dir,
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"documents={result.documents_written}/{result.images_found} "
        f"objects={result.objects_written} copied={result.images_copied} "
        f"skipped_annotations={result.skipped_annotations} errors={len(result.errors)}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

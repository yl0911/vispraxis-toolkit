"""Convert Pascal VOC XML annotations to one COCO JSON document.

Function:
    Read VOC XML files, collect image metadata and bounding boxes, and write a
    COCO instances JSON file. Source annotations are not modified.

Python call:
    ``run(voc_dir, output_file, recursive=True)``

CLI call:
    ``python scripts/documents/voc_to_coco.py VOC_DIR instances.json``

Legacy source:
    ``D:\\yl\\localcode\\imgdeal\\voc_to_coco_old.py``
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ConversionResult:
    documents_found: int
    documents_converted: int
    documents_failed: int
    objects_written: int
    output: Path
    errors: tuple[str, ...]


def _required_text(parent: ET.Element, name: str, source: Path) -> str:
    node = parent.find(name)
    if node is None or node.text is None or not node.text.strip():
        raise ValueError(f"Missing {name!r} in {source}")
    return node.text.strip()


def _parse_document(source: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    root = ET.parse(source).getroot()
    size = root.find("size")
    if size is None:
        raise ValueError(f"Missing 'size' in {source}")
    image = {
        "file_name": _required_text(root, "filename", source),
        "width": int(_required_text(size, "width", source)),
        "height": int(_required_text(size, "height", source)),
    }
    objects: list[dict[str, object]] = []
    for obj in root.findall("object"):
        name = _required_text(obj, "name", source)
        box = obj.find("bndbox")
        if box is None:
            raise ValueError(f"Missing 'bndbox' for {name!r} in {source}")
        xmin = float(_required_text(box, "xmin", source))
        ymin = float(_required_text(box, "ymin", source))
        xmax = float(_required_text(box, "xmax", source))
        ymax = float(_required_text(box, "ymax", source))
        if xmax < xmin or ymax < ymin:
            raise ValueError(f"Invalid bounding box for {name!r} in {source}")
        objects.append({"name": name, "bbox": [xmin, ymin, xmax - xmin, ymax - ymin]})
    return image, objects


def run(source_dir: Path, output_file: Path, *, recursive: bool = False) -> ConversionResult:
    """Convert a directory of VOC XML files into one COCO instances file."""
    if not source_dir.is_dir():
        raise FileNotFoundError(f"VOC source directory not found: {source_dir}")

    sources = sorted(source_dir.glob("**/*.xml" if recursive else "*.xml"))
    parsed: list[tuple[dict[str, object], list[dict[str, object]]]] = []
    errors: list[str] = []
    for source in sources:
        try:
            parsed.append(_parse_document(source))
        except (ET.ParseError, OSError, ValueError) as exc:
            errors.append(f"{source}: {exc}")

    class_names = sorted({str(obj["name"]) for _, objects in parsed for obj in objects})
    category_ids = {name: index for index, name in enumerate(class_names, start=1)}
    categories = [
        {"id": category_id, "name": name, "supercategory": "none"}
        for name, category_id in category_ids.items()
    ]
    images: list[dict[str, object]] = []
    annotations: list[dict[str, object]] = []
    annotation_id = 1
    for image_id, (image, objects) in enumerate(parsed, start=1):
        images.append({"id": image_id, **image})
        for obj in objects:
            bbox = list(obj["bbox"])
            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": category_ids[str(obj["name"])],
                    "bbox": bbox,
                    "area": bbox[2] * bbox[3],
                    "segmentation": [],
                    "iscrowd": 0,
                }
            )
            annotation_id += 1

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(
            {"images": images, "annotations": annotations, "categories": categories},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return ConversionResult(
        documents_found=len(sources),
        documents_converted=len(parsed),
        documents_failed=len(errors),
        objects_written=len(annotations),
        output=output_file,
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output_file", type=Path)
    parser.add_argument("--recursive", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(args.source_dir, args.output_file, recursive=args.recursive)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"converted={result.documents_converted}/{result.documents_found} "
        f"objects={result.objects_written} output={result.output}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.documents_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

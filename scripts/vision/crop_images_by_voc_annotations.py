"""Crop objects from images using each image's matching VOC annotation.

Function:
    Match images and VOC XML documents by relative path and stem, clip every
    bounding box to the image, and save each object crop under its class name.

Python call:
    ``run(image_dir, voc_dir, output_dir, classes=("icon",))``

CLI call:
    ``python scripts/vision/crop_images_by_voc_annotations.py IMAGES VOC OUTPUT``

Side effects:
    Writes new crop images. Source images and annotations are not modified.

Legacy source:
    ``D:\\yl\\localcode\\dingstock\\geetest_v4_datasets.py``
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True, slots=True)
class CropResult:
    images_found: int
    annotations_found: int
    images_processed: int
    objects_found: int
    crops_written: int
    objects_skipped: int
    classes: dict[str, int]
    outputs: tuple[Path, ...]
    errors: tuple[str, ...]


def _required_int(parent: ET.Element, name: str, source: Path) -> int:
    text = parent.findtext(name)
    if text is None:
        raise ValueError(f"Missing {name!r} in {source}")
    return round(float(text.strip()))


def _safe_class_name(name: str) -> str:
    cleaned = name.strip().replace("/", "_").replace("\\", "_")
    if not cleaned or cleaned in {".", ".."}:
        raise ValueError(f"Unsafe class name: {name!r}")
    return cleaned


def _load_objects(source: Path) -> list[tuple[str, tuple[int, int, int, int]]]:
    root = ET.parse(source).getroot()
    objects: list[tuple[str, tuple[int, int, int, int]]] = []
    for obj in root.findall("object"):
        name = obj.findtext("name", "").strip()
        box = obj.find("bndbox")
        if not name or box is None:
            continue
        objects.append(
            (
                name,
                (
                    _required_int(box, "xmin", source),
                    _required_int(box, "ymin", source),
                    _required_int(box, "xmax", source),
                    _required_int(box, "ymax", source),
                ),
            )
        )
    return objects


def run(
    image_dir: Path,
    voc_dir: Path,
    output_dir: Path,
    *,
    classes: tuple[str, ...] = (),
    recursive: bool = True,
    output_suffix: str = ".png",
) -> CropResult:
    """Crop all selected VOC objects from paired images."""
    if not image_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not voc_dir.is_dir():
        raise FileNotFoundError(f"VOC directory not found: {voc_dir}")
    if not output_suffix.startswith("."):
        output_suffix = "." + output_suffix
    selected = set(classes)
    pattern = "**/*" if recursive else "*"
    images = sorted(
        path
        for path in image_dir.glob(pattern)
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )
    annotations = sorted(voc_dir.glob("**/*.xml" if recursive else "*.xml"))
    annotation_map = {
        path.relative_to(voc_dir).with_suffix("").as_posix().casefold(): path
        for path in annotations
    }
    outputs: list[Path] = []
    errors: list[str] = []
    class_counts: Counter[str] = Counter()
    processed = objects_found = skipped = 0
    for image_path in images:
        relative = image_path.relative_to(image_dir)
        key = relative.with_suffix("").as_posix().casefold()
        annotation = annotation_map.get(key)
        if annotation is None:
            errors.append(f"{image_path}: matching VOC XML not found")
            continue
        try:
            image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("image decode failed")
            height, width = image.shape[:2]
            objects = _load_objects(annotation)
            processed += 1
            objects_found += len(objects)
            per_class: Counter[str] = Counter()
            for class_name, (xmin, ymin, xmax, ymax) in objects:
                if selected and class_name not in selected:
                    skipped += 1
                    continue
                safe_name = _safe_class_name(class_name)
                xmin, xmax = sorted(
                    (min(max(0, xmin), width), min(max(0, xmax), width))
                )
                ymin, ymax = sorted(
                    (min(max(0, ymin), height), min(max(0, ymax), height))
                )
                if xmax <= xmin or ymax <= ymin:
                    skipped += 1
                    continue
                index = per_class[safe_name]
                per_class[safe_name] += 1
                destination = (
                    output_dir
                    / safe_name
                    / relative.parent
                    / f"{image_path.stem}_{index:03d}{output_suffix}"
                )
                destination.parent.mkdir(parents=True, exist_ok=True)
                ok, encoded = cv2.imencode(output_suffix, image[ymin:ymax, xmin:xmax])
                if not ok:
                    raise OSError(f"Failed to encode crop: {destination}")
                destination.write_bytes(encoded.tobytes())
                outputs.append(destination)
                class_counts[class_name] += 1
        except (ET.ParseError, OSError, ValueError) as exc:
            errors.append(f"{image_path}: {exc}")
    return CropResult(
        images_found=len(images),
        annotations_found=len(annotations),
        images_processed=processed,
        objects_found=objects_found,
        crops_written=len(outputs),
        objects_skipped=skipped,
        classes=dict(class_counts),
        outputs=tuple(outputs),
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("image_dir", type=Path)
    parser.add_argument("voc_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--class", dest="classes", action="append")
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--output-suffix", default=".png")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.image_dir,
            args.voc_dir,
            args.output_dir,
            classes=tuple(args.classes or ()),
            recursive=not args.no_recursive,
            output_suffix=args.output_suffix,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"processed={result.images_processed}/{result.images_found} "
        f"objects={result.objects_found} crops={result.crops_written} "
        f"skipped={result.objects_skipped} errors={len(result.errors)}"
    )
    for name, count in sorted(result.classes.items()):
        print(f"{name}: {count}")
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

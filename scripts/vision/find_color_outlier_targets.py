"""Find visually different targets using rotation-insensitive color features.

Function:
    Crop targets from detection boxes, compare Lab color histograms, and rank
    targets by their median distance to the other targets. Detection boxes
    should fit their targets closely so shared background does not dominate.

Python call:
    ``run(image_path, boxes, n_outliers=1)``

CLI call:
    ``python scripts/vision/find_color_outlier_targets.py IMAGE BOXES``

The box source may be Pascal VOC XML, a JSON file, or a JSON array. Optional
visualization writes a marked image without modifying the input.

Legacy source:
    ``D:\\yl\\localcode\\find_odd_target.py``
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np


Box = Sequence[float | int]


@dataclass(frozen=True, slots=True)
class TargetScore:
    index: int
    box: tuple[int, int, int, int]
    class_id: int
    confidence: float
    outlier_score: float
    contrast: float
    is_outlier: bool


@dataclass(frozen=True, slots=True)
class OutlierResult:
    image: Path
    outlier_indices: tuple[int, ...]
    margin: float
    targets: tuple[TargetScore, ...]
    distance_matrix: np.ndarray
    visualization: Path | None


def read_image(path: Path) -> np.ndarray:
    """Read an image through bytes so Windows paths are handled consistently."""
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unsupported or damaged image: {path}")
    return image


def load_boxes(value: str | Path) -> list[list[float | int]]:
    """Load boxes from VOC XML, JSON file, or an inline JSON array."""
    path = Path(value)
    if path.is_file() and path.suffix.casefold() == ".xml":
        boxes: list[list[float | int]] = []
        root = ET.parse(path).getroot()
        for item in root.findall("object"):
            bounds = item.find("bndbox")
            if bounds is None:
                continue
            coordinates = [
                int(float(bounds.findtext(name, "0")))
                for name in ("xmin", "ymin", "xmax", "ymax")
            ]
            label = item.findtext("name", "")
            boxes.append(coordinates + [int(label) if label.isdigit() else -1, 1.0])
        return boxes
    if path.is_file():
        with path.open(encoding="utf-8") as stream:
            data = json.load(stream)
    else:
        try:
            data = json.loads(str(value))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Boxes must be an existing XML/JSON file or JSON array: {value}") from exc
    if not isinstance(data, list) or any(not isinstance(item, list) for item in data):
        raise ValueError("Box JSON must be an array of arrays")
    return data


def _crop_targets(
    image: np.ndarray, boxes: Sequence[Box], min_confidence: float
) -> tuple[list[np.ndarray], list[tuple[int, tuple[int, int, int, int], int, float]]]:
    height, width = image.shape[:2]
    crops: list[np.ndarray] = []
    metadata: list[tuple[int, tuple[int, int, int, int], int, float]] = []
    for index, raw_box in enumerate(boxes):
        if len(raw_box) < 4:
            raise ValueError(f"Box {index} must contain at least four coordinates")
        x1, y1, x2, y2 = (int(round(float(value))) for value in raw_box[:4])
        class_id = int(raw_box[4]) if len(raw_box) > 4 else -1
        confidence = float(raw_box[5]) if len(raw_box) > 5 else 1.0
        if confidence < min_confidence:
            continue
        x1, x2 = sorted((max(0, min(x1, width)), max(0, min(x2, width))))
        y1, y2 = sorted((max(0, min(y1, height)), max(0, min(y2, height))))
        if x2 - x1 < 4 or y2 - y1 < 4:
            continue
        crops.append(image[y1:y2, x1:x2])
        metadata.append((index, (x1, y1, x2, y2), class_id, confidence))
    return crops, metadata


def _describe_target(
    crop: np.ndarray, ab_bins: int, lightness_bins: int, inner_scale: float
) -> tuple[np.ndarray, np.ndarray, float]:
    height, width = crop.shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.ellipse(
        mask,
        (width // 2, height // 2),
        (max(1, int(width * inner_scale / 2)), max(1, int(height * inner_scale / 2))),
        0,
        0,
        360,
        255,
        -1,
    )
    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
    ab_histogram = cv2.calcHist(
        [lab], [1, 2], mask, [ab_bins, ab_bins], [0, 256, 0, 256]
    )
    ab_histogram = (ab_histogram / max(float(ab_histogram.sum()), 1e-6)).ravel()

    selected = mask > 0
    lightness = lab[..., 0].astype(np.float32)[selected]
    normalized = (lightness - lightness.mean()) / (lightness.std() + 1e-6)
    lightness_histogram, _ = np.histogram(
        normalized, bins=lightness_bins, range=(-2.5, 2.5)
    )
    lightness_histogram = lightness_histogram.astype(np.float32)
    lightness_histogram /= max(float(lightness_histogram.sum()), 1e-6)
    lab_float = lab.astype(np.float32)
    contrast = float(sum(lab_float[..., channel][selected].std() for channel in range(3)))
    return ab_histogram.astype(np.float32), lightness_histogram, contrast


def _bhattacharyya(left: np.ndarray, right: np.ndarray) -> float:
    coefficient = float(np.sum(np.sqrt(left * right)))
    return float(np.sqrt(max(0.0, 1.0 - coefficient)))


def _draw_result(image: np.ndarray, targets: Sequence[TargetScore]) -> np.ndarray:
    visualization = image.copy()
    for target in targets:
        x1, y1, x2, y2 = target.box
        color = (0, 0, 255) if target.is_outlier else (0, 180, 0)
        cv2.rectangle(visualization, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            visualization,
            f"{target.index}: {target.outlier_score:.3f}",
            (x1 + 2, max(15, y1 + 16)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )
    return visualization


def run(
    image_path: Path,
    boxes: Sequence[Box],
    *,
    n_outliers: int = 1,
    ab_bins: int = 16,
    lightness_bins: int = 16,
    inner_scale: float = 0.9,
    lightness_weight: float = 0.5,
    min_confidence: float = 0.0,
    visualization_path: Path | None = None,
) -> OutlierResult:
    """Rank the color outliers among targets in one image."""
    if ab_bins < 2 or lightness_bins < 2:
        raise ValueError("Histogram bin counts must be at least 2")
    if not 0 < inner_scale <= 1:
        raise ValueError("inner_scale must be greater than 0 and at most 1")
    if lightness_weight < 0:
        raise ValueError("lightness_weight must not be negative")
    image = read_image(image_path)
    crops, metadata = _crop_targets(image, boxes, min_confidence)
    count = len(crops)
    if count < 3:
        raise ValueError("At least three valid targets are required to identify an outlier")
    if not 0 <= n_outliers <= count - 2:
        raise ValueError("n_outliers must leave at least two targets in the majority")

    features = [
        _describe_target(crop, ab_bins, lightness_bins, inner_scale) for crop in crops
    ]
    distances = np.zeros((count, count), dtype=np.float32)
    for left in range(count):
        for right in range(left + 1, count):
            distance = _bhattacharyya(features[left][0], features[right][0])
            distance += lightness_weight * _bhattacharyya(
                features[left][1], features[right][1]
            )
            distances[left, right] = distances[right, left] = distance

    scores = np.array(
        [np.median(np.delete(distances[index], index)) for index in range(count)]
    )
    order = np.argsort(-scores)
    selected = set(int(index) for index in order[:n_outliers])
    remaining = np.delete(scores, list(selected)) if selected else scores
    margin = (
        float(scores[order[0]] / (np.median(remaining) + 1e-6)) if selected else 0.0
    )
    targets = tuple(
        TargetScore(
            index=meta[0],
            box=meta[1],
            class_id=meta[2],
            confidence=meta[3],
            outlier_score=float(scores[position]),
            contrast=float(features[position][2]),
            is_outlier=position in selected,
        )
        for position, meta in enumerate(metadata)
    )
    if visualization_path is not None:
        visualization_path.parent.mkdir(parents=True, exist_ok=True)
        suffix = visualization_path.suffix or ".png"
        success, encoded = cv2.imencode(suffix, _draw_result(image, targets))
        if not success:
            raise OSError(f"Cannot encode visualization as {suffix}")
        encoded.tofile(visualization_path)
    return OutlierResult(
        image_path,
        tuple(targets[index].index for index in order[:n_outliers]),
        margin,
        targets,
        distances,
        visualization_path,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("image", type=Path)
    parser.add_argument("boxes", help="VOC XML, JSON file, or inline JSON array")
    parser.add_argument("--n-outliers", type=int, default=1)
    parser.add_argument("--ab-bins", type=int, default=16)
    parser.add_argument("--lightness-bins", type=int, default=16)
    parser.add_argument("--inner-scale", type=float, default=0.9)
    parser.add_argument("--lightness-weight", type=float, default=0.5)
    parser.add_argument("--min-confidence", type=float, default=0.0)
    parser.add_argument("--visualization", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.image,
            load_boxes(args.boxes),
            n_outliers=args.n_outliers,
            ab_bins=args.ab_bins,
            lightness_bins=args.lightness_bins,
            inner_scale=args.inner_scale,
            lightness_weight=args.lightness_weight,
            min_confidence=args.min_confidence,
            visualization_path=args.visualization,
        )
    except (FileNotFoundError, OSError, ET.ParseError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"targets={len(result.targets)} outliers={list(result.outlier_indices)} "
        f"margin={result.margin:.3f}"
    )
    for target in sorted(result.targets, key=lambda item: -item.outlier_score):
        marker = " outlier" if target.is_outlier else ""
        print(
            f"#{target.index} box={target.box} score={target.outlier_score:.4f} "
            f"contrast={target.contrast:.2f}{marker}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

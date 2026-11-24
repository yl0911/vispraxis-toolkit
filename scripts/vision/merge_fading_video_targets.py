"""Merge targets visible at different times in a mostly static video.

Function:
    Sample video frames, estimate a clean temporal background, detect changing
    regions, select each region's clearest frame, and composite all targets.

Python call:
    ``run(source, output_dir, step=15, threshold=10.0)``

CLI call:
    ``python scripts/vision/merge_fading_video_targets.py VIDEO_OR_DIR OUTPUT``

Side effects:
    Writes one merged image per successfully processed video. Source videos are
    never modified. Debug mode additionally writes background and mask images.

Legacy source:
    ``D:\\yl\\localcode\\merge_frames_targets.py``
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


VIDEO_SUFFIXES = {
    ".webm", ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".m4v",
    ".mpg", ".mpeg", ".ts",
}


@dataclass(frozen=True, slots=True)
class VideoMerge:
    source: Path
    output: Path | None
    frames_sampled: int
    targets_merged: int
    error: str | None = None


@dataclass(frozen=True, slots=True)
class MergeResult:
    videos_found: int
    videos_processed: int
    videos_failed: int
    outputs: tuple[Path, ...]
    videos: tuple[VideoMerge, ...]


def extract_frames(video_path: Path, *, step: int = 15, max_frames: int = 0) -> list[np.ndarray]:
    """Sequentially decode and sample frames without unreliable frame seeking."""
    if step < 1:
        raise ValueError("step must be at least 1")
    if max_frames < 0:
        raise ValueError("max_frames must be zero or positive")
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise OSError(f"Cannot open video: {video_path}")
    frames: list[np.ndarray] = []
    index = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if index % step == 0:
                frames.append(frame)
                if max_frames and len(frames) >= max_frames:
                    break
            index += 1
    finally:
        capture.release()
    return frames


def _odd_kernel(value: int, name: str, *, allow_disabled: bool = True) -> int:
    if allow_disabled and value < 3:
        return value
    if value < 3 or value % 2 == 0:
        raise ValueError(f"{name} must be an odd integer of at least 3")
    return value


def _split_region(
    region: np.ndarray,
    differences: np.ndarray,
    min_area: int,
    smooth: int,
    seed_fraction: float,
    min_gain: float,
) -> list[tuple[np.ndarray, int]]:
    """Split touching targets when their pixels peak in different frames."""
    frame_count = differences.shape[0]
    best_frame = np.argmax(differences, axis=0).astype(np.uint8)
    if smooth >= 3:
        best_frame = cv2.medianBlur(best_frame, smooth)
    seed_floor = max(min_area, int(region.sum() * seed_fraction))
    seeds: list[tuple[np.ndarray, int]] = []
    for frame_index in range(frame_count):
        count, labels, stats, _ = cv2.connectedComponentsWithStats(
            ((best_frame == frame_index) & region).astype(np.uint8), 8
        )
        seeds.extend(
            (labels == label, frame_index)
            for label in range(1, count)
            if stats[label, cv2.CC_STAT_AREA] >= seed_floor
        )

    whole_best = int(
        np.argmax([differences[index][region].sum() for index in range(frame_count)])
    )
    if len(seeds) <= 1:
        return [(region, whole_best)]
    seed_frames = [frame_index for _, frame_index in seeds]
    gain = max(
        differences[frame_index][seed].mean()
        / max(differences[whole_best][seed].mean(), 1e-6)
        for seed, frame_index in seeds
    )
    if max(seed_frames) - min(seed_frames) < 2 and gain < min_gain:
        return [(region, whole_best)]

    distances = np.stack(
        [
            cv2.distanceTransform((~seed).astype(np.uint8), cv2.DIST_L2, 3)
            for seed, _ in seeds
        ]
    )
    owners = np.argmin(distances, axis=0)
    return [
        (region & (owners == index), frame_index)
        for index, (_, frame_index) in enumerate(seeds)
    ]


def merge_frames(
    frames: list[np.ndarray],
    *,
    threshold: float = 10.0,
    min_area: int = 150,
    feather: int = 9,
    dilate: int = 7,
    split_smooth: int = 9,
    seed_fraction: float = 0.2,
    min_gain: float = 1.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[tuple[int, int, int]]]:
    """Merge sampled frames and return output, background, mask, and picks."""
    if not frames:
        raise ValueError("At least one frame is required")
    if any(frame is None for frame in frames):
        raise ValueError("Frames must not contain None")
    reference = frames[0]
    if any(frame.shape != reference.shape for frame in frames):
        raise ValueError("All frames must have the same shape")
    if threshold < 0 or min_area < 1 or dilate < 0:
        raise ValueError("threshold, min_area, and dilate must be non-negative")
    _odd_kernel(feather, "feather")
    _odd_kernel(split_smooth, "split_smooth")
    if not 0 < seed_fraction <= 1 or min_gain <= 0:
        raise ValueError("seed_fraction must be in (0, 1] and min_gain must be positive")
    if len(frames) == 1:
        blank = np.zeros(reference.shape[:2], dtype=np.uint8)
        return reference.copy(), reference.copy(), blank, []

    stack = np.stack(frames).astype(np.float32)
    if stack.ndim == 3:
        stack = stack[..., None]
    grayscale = reference.ndim == 2
    rough_background = np.median(stack, axis=0)
    differences = np.abs(stack - rough_background[None]).sum(axis=3)
    differences = np.stack(
        [cv2.GaussianBlur(difference, (5, 5), 0) for difference in differences]
    )
    background_indices = np.argmin(differences, axis=0)
    background = np.take_along_axis(
        stack, background_indices[None, :, :, None], axis=0
    )[0]

    mask = (differences.max(axis=0) > threshold).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    if dilate:
        mask = cv2.dilate(mask, np.ones((dilate, dilate), np.uint8))
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    output = background.copy()
    picks: list[tuple[int, int, int]] = []
    for component in range(1, component_count):
        if stats[component, cv2.CC_STAT_AREA] < min_area:
            continue
        for subregion, best in _split_region(
            labels == component,
            differences,
            min_area,
            split_smooth,
            seed_fraction,
            min_gain,
        ):
            area = int(subregion.sum())
            if area < min_area:
                continue
            picks.append((component, best, area))
            alpha = subregion.astype(np.float32)
            if feather >= 3:
                alpha = cv2.GaussianBlur(alpha, (feather, feather), 0)
            alpha = alpha[..., None]
            output = stack[best] * alpha + output * (1.0 - alpha)

    output = np.clip(output, 0, 255).astype(np.uint8)
    background = np.clip(background, 0, 255).astype(np.uint8)
    if grayscale:
        output, background = output[..., 0], background[..., 0]
    return output, background, mask * 255, picks


def _write_image(path: Path, image: np.ndarray, jpeg_quality: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parameters = (
        [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
        if path.suffix.casefold() in {".jpg", ".jpeg"}
        else []
    )
    ok, encoded = cv2.imencode(path.suffix or ".png", image, parameters)
    if not ok:
        raise OSError(f"Failed to encode image: {path}")
    path.write_bytes(encoded.tobytes())


def run(
    source: Path,
    output_dir: Path,
    *,
    step: int = 15,
    max_frames: int = 0,
    output_suffix: str = ".jpg",
    jpeg_quality: int = 95,
    threshold: float = 10.0,
    min_area: int = 150,
    feather: int = 9,
    dilate: int = 7,
    split_smooth: int = 9,
    seed_fraction: float = 0.2,
    min_gain: float = 1.2,
    debug: bool = False,
) -> MergeResult:
    """Process one video or all supported videos in a directory."""
    if source.is_file():
        videos = [source]
    elif source.is_dir():
        videos = sorted(
            path for path in source.iterdir()
            if path.is_file() and path.suffix.casefold() in VIDEO_SUFFIXES
        )
    else:
        raise FileNotFoundError(f"Video source not found: {source}")
    if not output_suffix.startswith("."):
        output_suffix = "." + output_suffix
    if not 1 <= jpeg_quality <= 100:
        raise ValueError("jpeg_quality must be between 1 and 100")

    results: list[VideoMerge] = []
    outputs: list[Path] = []
    for video in videos:
        frames: list[np.ndarray] = []
        destination = output_dir / f"{video.stem}{output_suffix}"
        try:
            frames = extract_frames(video, step=step, max_frames=max_frames)
            if len(frames) < 2:
                raise ValueError("Fewer than two frames were sampled")
            output, background, mask, picks = merge_frames(
                frames,
                threshold=threshold,
                min_area=min_area,
                feather=feather,
                dilate=dilate,
                split_smooth=split_smooth,
                seed_fraction=seed_fraction,
                min_gain=min_gain,
            )
            _write_image(destination, output, jpeg_quality)
            if debug:
                _write_image(output_dir / f"{video.stem}_background{output_suffix}", background, jpeg_quality)
                _write_image(output_dir / f"{video.stem}_mask.png", mask, jpeg_quality)
            outputs.append(destination)
            results.append(VideoMerge(video, destination, len(frames), len(picks)))
        except (OSError, ValueError) as exc:
            results.append(VideoMerge(video, None, len(frames), 0, str(exc)))
    processed = sum(item.error is None for item in results)
    return MergeResult(len(videos), processed, len(videos) - processed, tuple(outputs), tuple(results))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--step", type=int, default=15)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--output-suffix", default=".jpg")
    parser.add_argument("--jpeg-quality", type=int, default=95)
    parser.add_argument("--threshold", type=float, default=10.0)
    parser.add_argument("--min-area", type=int, default=150)
    parser.add_argument("--feather", type=int, default=9)
    parser.add_argument("--dilate", type=int, default=7)
    parser.add_argument("--split-smooth", type=int, default=9)
    parser.add_argument("--seed-fraction", type=float, default=0.2)
    parser.add_argument("--min-gain", type=float, default=1.2)
    parser.add_argument("--debug", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.source,
            args.output_dir,
            step=args.step,
            max_frames=args.max_frames,
            output_suffix=args.output_suffix,
            jpeg_quality=args.jpeg_quality,
            threshold=args.threshold,
            min_area=args.min_area,
            feather=args.feather,
            dilate=args.dilate,
            split_smooth=args.split_smooth,
            seed_fraction=args.seed_fraction,
            min_gain=args.min_gain,
            debug=args.debug,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"processed={result.videos_processed}/{result.videos_found} "
        f"failed={result.videos_failed}"
    )
    for item in result.videos:
        if item.error:
            print(f"ERROR: {item.source}: {item.error}")
        else:
            print(
                f"{item.source} -> {item.output} "
                f"frames={item.frames_sampled} targets={item.targets_merged}"
            )
    return 0 if result.videos_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

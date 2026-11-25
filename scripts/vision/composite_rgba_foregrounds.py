"""Generate images by rotating and compositing RGBA foregrounds on backgrounds.

Function:
    Randomly select foreground and background images, rotate and scale the
    foreground, adjust its opacity, and place it fully inside the background.

Python call:
    ``run(foreground_dir, background_dir, output_dir, count=100, seed=42)``

CLI call:
    ``python scripts/vision/composite_rgba_foregrounds.py FOREGROUNDS BACKGROUNDS OUTPUT``

Side effects:
    Writes generated images and does not modify source assets.

Merged legacy sources:
    ``D:\\yl\\localcode\\get_mask_final.py``
    ``D:\\yl\\localcode\\get_mask_final_baseimg.py``
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


@dataclass(frozen=True, slots=True)
class CompositeItem:
    foreground: Path
    background: Path
    output: Path
    angle: float
    opacity: float
    scale: float
    position: tuple[int, int]


@dataclass(frozen=True, slots=True)
class CompositeResult:
    foregrounds_found: int
    backgrounds_found: int
    images_written: int
    items: tuple[CompositeItem, ...]


def _images(directory: Path, recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    return sorted(
        path
        for path in directory.glob(pattern)
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )


def _range(values: tuple[float, float], name: str, *, minimum: float | None = None) -> None:
    low, high = values
    if low > high:
        raise ValueError(f"{name} minimum must not exceed maximum")
    if minimum is not None and low < minimum:
        raise ValueError(f"{name} must be at least {minimum}")


def _prepare_foreground(
    source: Path,
    *,
    angle: float,
    opacity: float,
    scale: float,
) -> Image.Image:
    with Image.open(source) as opened:
        foreground = opened.convert("RGBA")
    width = max(1, round(foreground.width * scale))
    height = max(1, round(foreground.height * scale))
    foreground = foreground.resize((width, height), Image.Resampling.LANCZOS)
    foreground = foreground.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    if opacity < 1:
        alpha = foreground.getchannel("A").point(lambda value: round(value * opacity))
        foreground.putalpha(alpha)
    return foreground


def run(
    foreground_dir: Path,
    background_dir: Path,
    output_dir: Path,
    *,
    count: int = 100,
    seed: int | None = None,
    angle_range: tuple[float, float] = (-180.0, 180.0),
    opacity_range: tuple[float, float] = (0.7, 1.0),
    scale_range: tuple[float, float] = (1.0, 1.0),
    recursive: bool = False,
    output_suffix: str = ".png",
) -> CompositeResult:
    """Generate random foreground/background composites."""
    if not foreground_dir.is_dir():
        raise FileNotFoundError(f"Foreground directory not found: {foreground_dir}")
    if not background_dir.is_dir():
        raise FileNotFoundError(f"Background directory not found: {background_dir}")
    if count < 1:
        raise ValueError("count must be at least 1")
    _range(angle_range, "angle_range")
    _range(opacity_range, "opacity_range", minimum=0.0)
    _range(scale_range, "scale_range", minimum=0.01)
    if opacity_range[1] > 1:
        raise ValueError("opacity must not exceed 1")
    if not output_suffix.startswith("."):
        output_suffix = "." + output_suffix

    foregrounds = _images(foreground_dir, recursive)
    backgrounds = _images(background_dir, recursive)
    if not foregrounds:
        raise FileNotFoundError(f"No foreground images found: {foreground_dir}")
    if not backgrounds:
        raise FileNotFoundError(f"No background images found: {background_dir}")
    rng = random.Random(seed)
    items: list[CompositeItem] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        foreground_path = rng.choice(foregrounds)
        background_path = rng.choice(backgrounds)
        angle = rng.uniform(*angle_range)
        opacity = rng.uniform(*opacity_range)
        scale = rng.uniform(*scale_range)
        foreground = _prepare_foreground(
            foreground_path, angle=angle, opacity=opacity, scale=scale
        )
        with Image.open(background_path) as opened:
            background = opened.convert("RGBA")
        if foreground.width > background.width or foreground.height > background.height:
            fit = min(
                background.width / foreground.width,
                background.height / foreground.height,
            )
            foreground = foreground.resize(
                (
                    max(1, round(foreground.width * fit)),
                    max(1, round(foreground.height * fit)),
                ),
                Image.Resampling.LANCZOS,
            )
        x = rng.randint(0, background.width - foreground.width)
        y = rng.randint(0, background.height - foreground.height)
        background.alpha_composite(foreground, (x, y))
        destination = output_dir / f"composite_{index:06d}{output_suffix}"
        if output_suffix.casefold() in {".jpg", ".jpeg"}:
            background.convert("RGB").save(destination, quality=95)
        else:
            background.save(destination)
        items.append(
            CompositeItem(
                foreground_path,
                background_path,
                destination,
                angle,
                opacity,
                scale,
                (x, y),
            )
        )
    return CompositeResult(len(foregrounds), len(backgrounds), len(items), tuple(items))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("foreground_dir", type=Path)
    parser.add_argument("background_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--angle-min", type=float, default=-180.0)
    parser.add_argument("--angle-max", type=float, default=180.0)
    parser.add_argument("--opacity-min", type=float, default=0.7)
    parser.add_argument("--opacity-max", type=float, default=1.0)
    parser.add_argument("--scale-min", type=float, default=1.0)
    parser.add_argument("--scale-max", type=float, default=1.0)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--output-suffix", default=".png")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.foreground_dir,
            args.background_dir,
            args.output_dir,
            count=args.count,
            seed=args.seed,
            angle_range=(args.angle_min, args.angle_max),
            opacity_range=(args.opacity_min, args.opacity_max),
            scale_range=(args.scale_min, args.scale_max),
            recursive=args.recursive,
            output_suffix=args.output_suffix,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"foregrounds={result.foregrounds_found} "
        f"backgrounds={result.backgrounds_found} written={result.images_written}"
    )
    for item in result.items:
        print(
            f"{item.output}: foreground={item.foreground.name} "
            f"background={item.background.name} angle={item.angle:.2f} "
            f"opacity={item.opacity:.3f} scale={item.scale:.3f} position={item.position}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

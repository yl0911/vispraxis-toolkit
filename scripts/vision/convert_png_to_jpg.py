"""Convert PNG images to JPEG without deleting the source files.

Python call:
    ``run(source, output_dir=None, quality=90, recursive=False)``

CLI call:
    ``python scripts/vision/convert_png_to_jpg.py SOURCE [--output-dir DIR]``

Transparent pixels are composited onto a configurable RGB background. Existing
JPEG files are skipped unless ``overwrite`` is enabled.

Legacy source:
    ``D:\\yl\\localcode\\imgdeal\\png_to_jpg.py``
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ConversionResult:
    converted: int
    skipped: int
    outputs: tuple[Path, ...]


def _png_files(source: Path, recursive: bool) -> list[Path]:
    if source.is_file():
        return [source] if source.suffix.casefold() == ".png" else []
    if not source.is_dir():
        raise FileNotFoundError(f"Source not found: {source}")
    return sorted(source.glob("**/*.png" if recursive else "*.png"))


def run(
    source: Path,
    output_dir: Path | None = None,
    *,
    quality: int = 90,
    background: tuple[int, int, int] = (255, 255, 255),
    recursive: bool = False,
    overwrite: bool = False,
) -> ConversionResult:
    """Convert a PNG file or directory of PNG files to JPEG."""
    from PIL import Image

    if not 1 <= quality <= 100:
        raise ValueError("quality must be between 1 and 100")
    files = _png_files(source, recursive)
    base = source if source.is_dir() else source.parent
    converted = skipped = 0
    outputs: list[Path] = []

    for png_path in files:
        relative = png_path.relative_to(base).with_suffix(".jpg")
        destination = (output_dir / relative) if output_dir else png_path.with_suffix(".jpg")
        if destination.exists() and not overwrite:
            skipped += 1
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(png_path) as image:
            rgba = image.convert("RGBA")
            canvas = Image.new("RGBA", rgba.size, background + (255,))
            canvas.alpha_composite(rgba)
            canvas.convert("RGB").save(destination, format="JPEG", quality=quality)
        converted += 1
        outputs.append(destination)
    return ConversionResult(converted, skipped, tuple(outputs))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument("--background", default="255,255,255", help="RGB values")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        background = tuple(int(value) for value in args.background.split(","))
        if len(background) != 3 or any(not 0 <= value <= 255 for value in background):
            raise ValueError("background must contain three RGB values from 0 to 255")
        result = run(
            args.source,
            args.output_dir,
            quality=args.quality,
            background=background,
            recursive=args.recursive,
            overwrite=args.overwrite,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"converted={result.converted} skipped={result.skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

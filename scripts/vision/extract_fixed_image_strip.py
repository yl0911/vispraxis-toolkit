"""Extract fixed-width cells from a horizontal image strip.

Function:
    For each source image, optionally save the area above a strip and extract a
    configured number of fixed-width cells from the strip.

Python call:
    ``run(input_dir, output_dir, strip_y=344, cell_width=28, cell_count=3)``

CLI call:
    ``python scripts/vision/extract_fixed_image_strip.py INPUT OUTPUT --strip-y 344``

Side effects:
    Writes crops below the output directory. Source files are not modified.
    Deduplication is intentionally left to ``copy_unique_images_by_hash.py``.

Legacy source:
    ``D:\\yl\\localcode\\dingstock\\shein_and_gtv3.py``
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


@dataclass(frozen=True, slots=True)
class ExtractedImageStrip:
    source: Path
    source_digest: str
    top_output: Path | None
    cell_outputs: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class StripExtractionResult:
    images_found: int
    images_processed: int
    top_regions_written: int
    cells_written: int
    items: tuple[ExtractedImageStrip, ...]
    errors: tuple[str, ...]


def _source_images(input_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    return sorted(
        path
        for path in input_dir.glob(pattern)
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )


def _digest(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_image(path: Path, channel_mode: str) -> Image.Image:
    with Image.open(path) as opened:
        if channel_mode == "color":
            return opened.convert("RGBA" if "A" in opened.getbands() else "RGB")
        if "A" not in opened.getbands():
            raise ValueError("inverted_alpha requires an image with an alpha channel")
        return ImageOps.invert(opened.getchannel("A")).convert("RGB")


def run(
    input_dir: Path,
    output_dir: Path,
    *,
    strip_y: int,
    cell_width: int,
    cell_count: int,
    strip_y_offset: int = 0,
    cell_x: int = 0,
    cell_gap: int = 0,
    save_top: bool = True,
    channel_mode: str = "color",
    recursive: bool = True,
) -> StripExtractionResult:
    """Extract a top region and fixed horizontal strip cells from each image."""
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    source_root = input_dir.resolve()
    output_root = output_dir.resolve()
    if output_root == source_root or source_root in output_root.parents:
        raise ValueError("Output directory must not be inside the input directory")
    if strip_y < 0 or strip_y_offset < 0 or cell_x < 0 or cell_gap < 0:
        raise ValueError("Coordinates and gaps must not be negative")
    if cell_width < 1 or cell_count < 1:
        raise ValueError("cell_width and cell_count must be positive")
    if channel_mode not in {"color", "inverted_alpha"}:
        raise ValueError("channel_mode must be 'color' or 'inverted_alpha'")

    sources = _source_images(input_dir, recursive)
    items: list[ExtractedImageStrip] = []
    errors: list[str] = []
    top_count = cell_total = 0
    for source in sources:
        try:
            image = _load_image(source, channel_mode)
            cell_y = strip_y + strip_y_offset
            required_width = cell_x + cell_count * cell_width + (cell_count - 1) * cell_gap
            if strip_y > image.height:
                raise ValueError(f"strip_y {strip_y} exceeds image height {image.height}")
            if cell_y >= image.height:
                raise ValueError(f"cell row starts outside image at y={cell_y}")
            if required_width > image.width:
                raise ValueError(
                    f"configured cells require width {required_width}, image width is {image.width}"
                )
            digest = _digest(source)
            top_output = None
            if save_top and strip_y > 0:
                top_output = output_dir / "top" / f"{digest}.jpg"
                top_output.parent.mkdir(parents=True, exist_ok=True)
                image.crop((0, 0, image.width, strip_y)).convert("RGB").save(
                    top_output, quality=95
                )
                top_count += 1
            cell_outputs: list[Path] = []
            for index in range(cell_count):
                left = cell_x + index * (cell_width + cell_gap)
                cell = image.crop((left, cell_y, left + cell_width, image.height))
                destination = output_dir / "cells" / f"{digest}_{index:02d}.png"
                destination.parent.mkdir(parents=True, exist_ok=True)
                cell.save(destination)
                cell_outputs.append(destination)
                cell_total += 1
            items.append(
                ExtractedImageStrip(source, digest, top_output, tuple(cell_outputs))
            )
        except (OSError, SyntaxError, ValueError) as exc:
            errors.append(f"{source}: {exc}")
    return StripExtractionResult(
        len(sources),
        len(items),
        top_count,
        cell_total,
        tuple(items),
        tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--strip-y", type=int, required=True)
    parser.add_argument("--strip-y-offset", type=int, default=0)
    parser.add_argument("--cell-width", type=int, required=True)
    parser.add_argument("--cell-count", type=int, required=True)
    parser.add_argument("--cell-x", type=int, default=0)
    parser.add_argument("--cell-gap", type=int, default=0)
    parser.add_argument("--no-save-top", action="store_true")
    parser.add_argument(
        "--channel-mode", choices=("color", "inverted_alpha"), default="color"
    )
    parser.add_argument("--no-recursive", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.input_dir,
            args.output_dir,
            strip_y=args.strip_y,
            strip_y_offset=args.strip_y_offset,
            cell_width=args.cell_width,
            cell_count=args.cell_count,
            cell_x=args.cell_x,
            cell_gap=args.cell_gap,
            save_top=not args.no_save_top,
            channel_mode=args.channel_mode,
            recursive=not args.no_recursive,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"images={result.images_found} processed={result.images_processed} "
        f"top={result.top_regions_written} cells={result.cells_written} "
        f"failed={len(result.errors)}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if not result.errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

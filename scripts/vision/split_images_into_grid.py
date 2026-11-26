"""Split images into a configurable row-by-column grid.

Function:
    Divide one image or a directory of images into grid cells. Proportional
    boundaries preserve all edge pixels when dimensions are not evenly divisible.

Python call:
    ``run(input_path, output_dir, rows=3, columns=3)``

CLI call:
    ``python scripts/vision/split_images_into_grid.py INPUT OUTPUT --rows 3 --columns 3``

Side effects:
    Writes grid cells below the output directory without changing source files.

Legacy source:
    ``D:\\yl\\localcode\\dingstock\\captcha_test.py``
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


@dataclass(frozen=True, slots=True)
class GridCell:
    row: int
    column: int
    box: tuple[int, int, int, int]
    output: Path


@dataclass(frozen=True, slots=True)
class SplitImage:
    source: Path
    width: int
    height: int
    cells: tuple[GridCell, ...]


@dataclass(frozen=True, slots=True)
class GridSplitResult:
    images_found: int
    images_processed: int
    cells_written: int
    items: tuple[SplitImage, ...]
    errors: tuple[str, ...]


def _sources(input_path: Path, recursive: bool) -> tuple[Path, list[Path]]:
    if input_path.is_file():
        if input_path.suffix.casefold() not in IMAGE_SUFFIXES:
            raise ValueError(f"Unsupported image type: {input_path}")
        return input_path.parent, [input_path]
    if not input_path.is_dir():
        raise FileNotFoundError(f"Image input not found: {input_path}")
    pattern = "**/*" if recursive else "*"
    return input_path, sorted(
        path
        for path in input_path.glob(pattern)
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )


def run(
    input_path: Path,
    output_dir: Path,
    *,
    rows: int = 3,
    columns: int = 3,
    recursive: bool = False,
    output_suffix: str = ".png",
) -> GridSplitResult:
    """Split every selected image into grid cells."""
    if rows < 1 or columns < 1:
        raise ValueError("rows and columns must be positive")
    if not output_suffix.startswith("."):
        output_suffix = "." + output_suffix
    if output_suffix.casefold() not in IMAGE_SUFFIXES:
        raise ValueError(f"Unsupported output image type: {output_suffix}")
    source_root, sources = _sources(input_path, recursive)
    if input_path.is_dir():
        resolved_source = source_root.resolve()
        resolved_output = output_dir.resolve()
        if resolved_output == resolved_source or resolved_source in resolved_output.parents:
            raise ValueError("Output directory must not be inside the input directory")

    items: list[SplitImage] = []
    errors: list[str] = []
    cells_written = 0
    for source in sources:
        try:
            with Image.open(source) as opened:
                image = opened.convert("RGBA" if "A" in opened.getbands() else "RGB")
            if image.width < columns or image.height < rows:
                raise ValueError(
                    f"image {image.width}x{image.height} is smaller than grid {columns}x{rows}"
                )
            relative_parent = source.parent.relative_to(source_root)
            cell_items: list[GridCell] = []
            for row in range(rows):
                top = row * image.height // rows
                bottom = (row + 1) * image.height // rows
                for column in range(columns):
                    left = column * image.width // columns
                    right = (column + 1) * image.width // columns
                    destination = (
                        output_dir
                        / relative_parent
                        / source.stem
                        / f"r{row:02d}_c{column:02d}{output_suffix}"
                    )
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    cell = image.crop((left, top, right, bottom))
                    if output_suffix.casefold() in {".jpg", ".jpeg"}:
                        cell.convert("RGB").save(destination, quality=95)
                    else:
                        cell.save(destination)
                    cell_items.append(
                        GridCell(row, column, (left, top, right, bottom), destination)
                    )
                    cells_written += 1
            items.append(SplitImage(source, image.width, image.height, tuple(cell_items)))
        except (OSError, SyntaxError, ValueError) as exc:
            errors.append(f"{source}: {exc}")
    return GridSplitResult(
        len(sources), len(items), cells_written, tuple(items), tuple(errors)
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("input_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--output-suffix", default=".png")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.input_path,
            args.output_dir,
            rows=args.rows,
            columns=args.columns,
            recursive=args.recursive,
            output_suffix=args.output_suffix,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"images={result.images_found} processed={result.images_processed} "
        f"cells={result.cells_written} failed={len(result.errors)}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if not result.errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

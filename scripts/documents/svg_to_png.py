"""Render SVG documents as PNG images.

Python call:
    ``run(source, output_dir, width=150, height=50, recursive=True)``

CLI call:
    ``python scripts/documents/svg_to_png.py SOURCE OUTPUT --width 150 --height 50``

Requires the optional ``cairosvg`` package.

Legacy sources:
    ``D:\\yl\\localcode\\svg2img.py``
    ``D:\\yl\\localcode\\svg_to_img.go`` (same purpose; Python retained)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RenderResult:
    rendered: int
    skipped: int
    outputs: tuple[Path, ...]


def run(
    source: Path,
    output_dir: Path,
    *,
    width: int | None = None,
    height: int | None = None,
    recursive: bool = True,
    overwrite: bool = False,
) -> RenderResult:
    """Render one SVG or a directory tree while preserving relative paths."""
    import cairosvg

    if source.is_file():
        files, base = [source], source.parent
    elif source.is_dir():
        files = sorted(source.glob("**/*.svg" if recursive else "*.svg"))
        base = source
    else:
        raise FileNotFoundError(f"Source not found: {source}")
    if width is not None and width <= 0 or height is not None and height <= 0:
        raise ValueError("width and height must be positive")

    rendered = skipped = 0
    outputs: list[Path] = []
    for svg_path in files:
        destination = output_dir / svg_path.relative_to(base).with_suffix(".png")
        if destination.exists() and not overwrite:
            skipped += 1
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(destination),
            output_width=width,
            output_height=height,
        )
        rendered += 1
        outputs.append(destination)
    return RenderResult(rendered, skipped, tuple(outputs))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.source,
            args.output_dir,
            width=args.width,
            height=args.height,
            recursive=not args.no_recursive,
            overwrite=args.overwrite,
        )
    except (ImportError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"rendered={result.rendered} skipped={result.skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Business call for extracting three VisionEngine icon-strip cells."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.vision.extract_fixed_image_strip import run


DEFAULT_INPUT_DIR = Path(
    r"D:\yl\desktop\test\visionengine\vg_botdeflector\20261103\icon"
)
DEFAULT_OUTPUT_DIR = Path(
    r"D:\yl\desktop\test\visionengine\vg_botdeflector\20261103\icon_save"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--strip-y", type=int, default=0)
    parser.add_argument("--cell-width", type=int, default=28)
    parser.add_argument("--cell-count", type=int, default=3)
    parser.add_argument("--cell-x", type=int, default=0)
    parser.add_argument("--cell-gap", type=int, default=1)
    args = parser.parse_args(argv)
    print(f"input_dir:  {args.input_dir}")
    print(f"output_dir: {args.output_dir}")
    try:
        result = run(
            args.input_dir,
            args.output_dir,
            strip_y=args.strip_y,
            cell_width=args.cell_width,
            cell_count=args.cell_count,
            cell_x=args.cell_x,
            cell_gap=args.cell_gap,
            save_top=False,
            channel_mode="inverted_alpha",
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"processed={result.images_processed} cells={result.cells_written} "
        f"failed={len(result.errors)}"
    )
    return 0 if not result.errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

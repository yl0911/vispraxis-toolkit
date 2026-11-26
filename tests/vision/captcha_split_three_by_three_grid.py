"""Business call for splitting captcha images into a three-by-three grid."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.vision.split_images_into_grid import run


DEFAULT_INPUT = Path(
    r"D:\yl\desktop\test\geetest_image\geetestclick_common\test\1_comb"
)
DEFAULT_OUTPUT = Path(
    r"D:\yl\desktop\test\geetest_image\geetestclick_common\test\1_grid"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--recursive", action="store_true")
    args = parser.parse_args(argv)
    print(f"input:  {args.input}")
    print(f"output: {args.output}")
    try:
        result = run(
            args.input,
            args.output,
            rows=args.rows,
            columns=args.columns,
            recursive=args.recursive,
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

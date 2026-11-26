"""Business call for stitching Geetest v4 base images and indexed icons."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.vision.stitch_base_with_indexed_images import run


DEFAULT_INPUT_DIR = Path(r"D:\yl\desktop\test\geetest_image\geetestclick_v4_hoyoverse\test")
DEFAULT_OUTPUT_DIR = Path(
    r"D:\yl\desktop\test\geetest_image\geetestclick_v4_hoyoverse\test_comb"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--size", type=int, default=50)
    parser.add_argument("--small-count", type=int, default=3)
    parser.add_argument("--index-start", type=int, default=0)
    parser.add_argument("--fill-missing", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args(argv)
    print(f"input_dir:  {args.input_dir}")
    print(f"output_dir: {args.output_dir}")
    try:
        result = run(
            args.input_dir,
            args.output_dir,
            small_size=(args.size, args.size),
            max_small_images=args.small_count,
            fill_missing=args.fill_missing,
            index_start=args.index_start,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"groups={result.groups_found} written={result.images_written} "
        f"without_base={len(result.groups_without_base)} failed={len(result.failed_groups)}"
    )
    return 0 if not result.failed_groups else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Business call for generating rotated icon/background composite images.

    python -m tests.vision.icon_composite_augmentation --count 100
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.vision.composite_rgba_foregrounds import run

DEFAULT_FOREGROUND_DIR = Path(r"C:\Users\Administrator\Desktop\base_icon")
DEFAULT_BACKGROUND_DIR = Path(r"C:\Users\Administrator\Desktop\background")
DEFAULT_OUTPUT_DIR = Path(r"C:\Users\Administrator\Desktop\test\saves")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--foreground-dir", type=Path, default=DEFAULT_FOREGROUND_DIR)
    parser.add_argument("--background-dir", type=Path, default=DEFAULT_BACKGROUND_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--angle-min", type=float, default=-180.0)
    parser.add_argument("--angle-max", type=float, default=180.0)
    parser.add_argument("--opacity-min", type=float, default=0.7)
    parser.add_argument("--opacity-max", type=float, default=1.0)
    args = parser.parse_args(argv)
    print(f"foreground_dir: {args.foreground_dir}")
    print(f"background_dir: {args.background_dir}")
    print(f"output_dir:     {args.output_dir}")
    try:
        result = run(
            args.foreground_dir,
            args.background_dir,
            args.output_dir,
            count=args.count,
            seed=args.seed,
            angle_range=(args.angle_min, args.angle_max),
            opacity_range=(args.opacity_min, args.opacity_max),
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"written={result.images_written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

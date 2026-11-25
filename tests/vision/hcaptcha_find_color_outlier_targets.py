"""Business call for finding the color outlier in merged HCaptcha targets.

    python -m tests.vision.hcaptcha_find_color_outlier_targets
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.vision.find_color_outlier_targets import load_boxes, run


DEFAULT_IMAGE = Path(r"C:\Users\Administrator\Desktop\hc_video_save\merged.png")
DEFAULT_BOXES = Path(r"C:\Users\Administrator\Desktop\hc_video_save\merged.xml")
DEFAULT_VISUALIZATION = Path(
    r"C:\Users\Administrator\Desktop\hc_video_save_draw\merged.png"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--boxes", type=Path, default=DEFAULT_BOXES)
    parser.add_argument("--visualization", type=Path, default=DEFAULT_VISUALIZATION)
    parser.add_argument("--n-outliers", type=int, default=1)
    parser.add_argument("--ab-bins", type=int, default=16)
    parser.add_argument("--lightness-bins", type=int, default=16)
    parser.add_argument("--inner-scale", type=float, default=0.9)
    parser.add_argument("--lightness-weight", type=float, default=0.5)
    args = parser.parse_args(argv)
    print(f"image:         {args.image}")
    print(f"boxes:         {args.boxes}")
    print(f"visualization: {args.visualization}")
    try:
        result = run(
            args.image,
            load_boxes(args.boxes),
            n_outliers=args.n_outliers,
            ab_bins=args.ab_bins,
            lightness_bins=args.lightness_bins,
            inner_scale=args.inner_scale,
            lightness_weight=args.lightness_weight,
            visualization_path=args.visualization,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"outliers={list(result.outlier_indices)} margin={result.margin:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

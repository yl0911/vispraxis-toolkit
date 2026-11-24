"""HCaptcha business call for merging targets from static-background videos.

    python -m tests.vision.hcaptcha_merge_fading_video_targets
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.vision.merge_fading_video_targets import run

# Business parameter preset migrated from merge_frames_targets.py.
DEFAULT_SOURCE = Path(r"C:\Users\Administrator\Desktop\hc_video")
DEFAULT_OUTPUT_DIR = Path(r"C:\Users\Administrator\Desktop\hc_video_save")
DEFAULT_STEP = 15


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--step", type=int, default=DEFAULT_STEP)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=10.0)
    parser.add_argument("--min-area", type=int, default=150)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    print(f"source:     {args.source}")
    print(f"output_dir: {args.output_dir}")
    try:
        result = run(
            args.source,
            args.output_dir,
            step=args.step,
            max_frames=args.max_frames,
            threshold=args.threshold,
            min_area=args.min_area,
            debug=args.debug,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"processed={result.videos_processed}/{result.videos_found} failed={result.videos_failed}")
    for item in result.videos:
        print(f"{item.source}: output={item.output} error={item.error}")
    return 0 if result.videos_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

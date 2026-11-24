"""HCaptcha business call for downloading one historical OSS object prefix.

Set credentials in the environment, preview, then explicitly execute:

    $env:OSS_ACCESS_KEY_ID = "..."
    $env:OSS_ACCESS_KEY_SECRET = "..."
    python -m tests.datasets.hcaptcha_download_oss_prefix
    python -m tests.datasets.hcaptcha_download_oss_prefix --execute
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from scripts.datasets.download_oss_prefix import run

# Non-secret business parameter preset migrated from dingstock/oss_download.py.
DEFAULT_ENDPOINT = "https://oss-accelerate.aliyuncs.com"
DEFAULT_BUCKET = "captchaai-collector"
DEFAULT_PREFIX = (
    "2025-11-46/MLProjectHCaptcha/2025-11-12/unsolved/"
    "drag_drop-please_drag_the_segment_on_the_right_to_complete_the_line/"
)
DEFAULT_OUTPUT_DIR = Path(
    r"D:\yl\desktop\test\hc_drag_piece_complete\20251203\images"
)
DEFAULT_MAX_FILES = 1000


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    print(f"endpoint:   {args.endpoint}")
    print(f"bucket:     {args.bucket}")
    print(f"prefix:     {args.prefix}")
    print(f"output_dir: {args.output_dir}")
    print(f"mode:       {'execute' if args.execute else 'preview'}")
    try:
        result = run(
            args.endpoint,
            args.bucket,
            args.prefix,
            args.output_dir,
            access_key_id=os.getenv("OSS_ACCESS_KEY_ID", ""),
            access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET", ""),
            max_files=args.max_files,
            workers=args.workers,
            overwrite=args.overwrite,
            execute=args.execute,
        )
    except (FileExistsError, ImportError, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"objects={result.objects_found} planned={result.planned} "
        f"downloaded={result.downloaded} skipped={result.skipped_existing} "
        f"failed={result.failed}"
    )
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

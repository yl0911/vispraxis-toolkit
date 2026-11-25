"""Business call for evaluating the local ocr.common2 service.

Preview the selected dataset by default; add ``--execute`` to send requests.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.automation.evaluate_image_text_service import run


DEFAULT_IMAGE_DIR = Path(r"D:\yl\desktop\test\image2text\queue_it\test")
DEFAULT_ENDPOINT = "http://127.0.0.1:3000/mlinvoke"
DEFAULT_SERVICE = "ocr.common2"
DEFAULT_REPORT_DIR = Path(r"D:\yl\desktop\test\image2text\queue_it\reports")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMAGE_DIR)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--min-accuracy", type=float, default=0.99)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    print(f"image_dir: {args.image_dir}")
    print(f"endpoint:  {args.endpoint}")
    print(f"mode:      {'execute' if args.execute else 'preview'}")
    try:
        result = run(
            args.image_dir,
            args.endpoint,
            service=DEFAULT_SERVICE,
            batch_size=args.batch_size,
            timeout=args.timeout,
            limit=args.limit,
            json_report=args.report_dir / "ocr_common2.json",
            csv_report=args.report_dir / "ocr_common2.csv",
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"samples={result.samples_collected} skipped={len(result.skipped_files)}")
    if result.summary is None:
        return 0
    print(f"accuracy={result.summary.accuracy:.4f}")
    return 0 if result.summary.accuracy >= args.min_accuracy else 2


if __name__ == "__main__":
    raise SystemExit(main())

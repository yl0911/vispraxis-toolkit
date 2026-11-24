"""Business call for exporting icon hashes consumed by the Go service.

    python -m tests.datasets.icon_hash_export_for_go
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.datasets.export_image_md5_manifest import run

# Business preset based on the original ml_iconHash_batch.py CLI workflow.
DEFAULT_SOURCE_DIR = Path(r"D:\yl\desktop\test\geetest_image\icons")
DEFAULT_OUTPUT_FILE = DEFAULT_SOURCE_DIR.parent / "ml_iconHash_batch_out.txt"
DEFAULT_PATTERN = "*_*.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--pattern", default=DEFAULT_PATTERN)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--keep-duplicates", action="store_true")
    args = parser.parse_args(argv)
    print(f"source_dir: {args.source_dir}")
    print(f"output:     {args.output}")
    try:
        result = run(
            args.source_dir,
            args.output,
            recursive=args.recursive,
            pattern=args.pattern,
            output_format="go",
            with_names=True,
            keep_duplicates=args.keep_duplicates,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"files={result.files_found} unique={result.unique_hashes} "
        f"duplicates={result.duplicate_files}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

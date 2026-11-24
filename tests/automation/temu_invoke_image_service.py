"""Temu business call for invoking the local image service per source image.

Preview request construction by default, then explicitly execute:

    python -m tests.automation.temu_invoke_image_service
    python -m tests.automation.temu_invoke_image_service --execute
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.automation.invoke_image_json_service import IMAGE_SUFFIXES, run

# Business parameter preset migrated from request_batch.py.
DEFAULT_SOURCE_DIR = Path(r"D:\yl\desktop\test\temu_draw\downloads")
DEFAULT_RESPONSE_DIR = Path(r"D:\yl\desktop\test\temu_draw\responses")
DEFAULT_ENDPOINT = "http://127.0.0.1:3000/mlinvoke"
DEFAULT_MODULE = "temu:draw"
QUESTION_MARKER = "select-temu_Please click on the"


def _question(path: Path) -> str:
    return next((part for part in path.parts if QUESTION_MARKER in part), "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--response-dir", type=Path, default=DEFAULT_RESPONSE_DIR)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if not args.source_dir.is_dir():
        print(f"ERROR: Source directory not found: {args.source_dir}")
        return 1
    sources = sorted(
        path
        for path in args.source_dir.rglob("*")
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )
    if args.limit:
        sources = sources[: args.limit]
    print(f"source_dir: {args.source_dir}")
    print(f"endpoint:   {args.endpoint}")
    print(f"images:     {len(sources)}")
    print(f"mode:       {'execute' if args.execute else 'preview'}")
    failed = sent = 0
    for source in sources:
        relative = source.relative_to(args.source_dir)
        response_file = args.response_dir / relative.with_suffix(".json")
        try:
            result = run(
                source,
                args.endpoint,
                payload={"module": DEFAULT_MODULE, "question": _question(relative)},
                timeout=args.timeout,
                response_file=response_file,
                execute=args.execute,
            )
            sent += int(result.sent)
            print(f"{relative}: sent={result.sent} status={result.status_code}")
        except (ImportError, OSError, ValueError) as exc:
            failed += 1
            print(f"ERROR: {relative}: {exc}")
    print(f"processed={len(sources)} sent={sent} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

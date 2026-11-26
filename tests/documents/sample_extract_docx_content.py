"""Business call for extracting the historical local Word document."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.documents.extract_docx_content import run


DEFAULT_DOCX_FILE = Path("/ntt/code/word.docx")
DEFAULT_OUTPUT_DIR = Path("/ntt/code/word_content")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--docx-file", type=Path, default=DEFAULT_DOCX_FILE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--no-media", action="store_true")
    args = parser.parse_args(argv)
    print(f"docx_file:  {args.docx_file}")
    print(f"output_dir: {args.output_dir}")
    try:
        result = run(
            args.docx_file,
            args.output_dir,
            extract_media=not args.no_media,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"paragraphs={result.paragraphs_found} tables={result.tables_found} "
        f"media={result.media_written} report={result.report_file}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

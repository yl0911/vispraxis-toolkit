"""Render the historical SVG captcha directory at 150 by 50 pixels."""

from pathlib import Path

from scripts.documents.svg_to_png import run

SOURCE_DIR = Path("./svg_captcha")
OUTPUT_DIR = Path("./img_captcha")
WIDTH = 150
HEIGHT = 50


def main() -> int:
    try:
        result = run(SOURCE_DIR, OUTPUT_DIR, width=WIDTH, height=HEIGHT)
    except (ImportError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"rendered={result.rendered} skipped={result.skipped} output={OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Convert the historical car PNG dataset to JPEG files."""

from pathlib import Path

from scripts.vision.convert_png_to_jpg import run

SOURCE_DIR = Path(r"./car/allCar")
JPEG_QUALITY = 70


def main() -> int:
    try:
        result = run(SOURCE_DIR, quality=JPEG_QUALITY)
    except (ImportError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"source={SOURCE_DIR} converted={result.converted} skipped={result.skipped}")
    print("PNG source files were retained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

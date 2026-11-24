"""Preview the historical Temu draw-image exact duplicate move."""

from pathlib import Path

from scripts.datasets.move_md5_duplicates import run

SOURCE_DIR = Path(r"D:\yl\desktop\test\temu_draw\draw_img")
COMPARISON_DIR = Path(r"D:\yl\desktop\test\temu_draw\no_1")
OUTPUT_DIR = Path(r"D:\yl\desktop\test\temu_draw\no_2")
EXECUTE = False


def main() -> int:
    try:
        result = run(SOURCE_DIR, COMPARISON_DIR, OUTPUT_DIR, execute=EXECUTE)
    except (FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"compared={result.compared} matched={result.matched} moved={result.moved}")
    print(f"mode={'execute' if EXECUTE else 'preview'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

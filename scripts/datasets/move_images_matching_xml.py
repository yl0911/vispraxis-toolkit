"""Move images whose names match XML annotation names.

Function:
    Match image and XML files by case-insensitive filename stem. The default is
    preview-only; pass ``execute=True`` or CLI ``--execute`` to move files.

Python call:
    ``run(annotation_dir, image_dir, execute=False)``

CLI call:
    ``python scripts/datasets/move_images_matching_xml.py XML_DIR IMAGE_DIR``

Legacy source:
    ``D:\\yl\\localcode\\move_matching_images_to_cut.py``
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
)


@dataclass(frozen=True, slots=True)
class MoveResult:
    """Counts and output paths produced by a move operation."""

    matched: int
    moved: int
    planned: int
    skipped: int
    outputs: tuple[Path, ...]


def collect_xml_stems(annotation_dir: Path) -> set[str]:
    """Return case-insensitive stems for XML files in one directory."""
    return {
        path.stem.casefold()
        for path in annotation_dir.iterdir()
        if path.is_file() and path.suffix.casefold() == ".xml"
    }


def iter_images(image_dir: Path, recursive: bool):
    """Yield supported images in deterministic path order."""
    pattern = "**/*" if recursive else "*"
    for path in sorted(image_dir.glob(pattern)):
        if path.is_file() and path.suffix.casefold() in IMAGE_EXTENSIONS:
            yield path


def run(
    annotation_dir: Path,
    image_dir: Path,
    *,
    execute: bool = False,
    overwrite: bool = False,
    recursive: bool = False,
) -> MoveResult:
    """Preview or move images matching XML files.

    Raises ``FileNotFoundError`` for missing input directories. Existing output
    files are skipped unless ``overwrite`` is enabled.
    """
    if not annotation_dir.is_dir():
        raise FileNotFoundError(f"Annotation directory not found: {annotation_dir}")
    if not image_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")

    xml_stems = collect_xml_stems(annotation_dir)
    matched = moved = skipped = 0
    outputs: list[Path] = []

    for image_path in iter_images(image_dir, recursive):
        if image_path.stem.casefold() not in xml_stems:
            continue
        matched += 1
        destination = annotation_dir / image_path.name
        if destination.exists() and not overwrite:
            skipped += 1
            continue
        if execute:
            if destination.exists():
                destination.unlink()
            shutil.move(str(image_path), str(destination))
            moved += 1
            outputs.append(destination)

    return MoveResult(
        matched=matched,
        moved=moved,
        planned=matched - skipped,
        skipped=skipped,
        outputs=tuple(outputs),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("annotation_dir", type=Path, help="Directory containing XML files")
    parser.add_argument("image_dir", type=Path, help="Directory containing source images")
    parser.add_argument("--execute", action="store_true", help="Move files; default is preview-only")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing files")
    parser.add_argument("--recursive", action="store_true", help="Search images recursively")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.annotation_dir,
            args.image_dir,
            execute=args.execute,
            overwrite=args.overwrite,
            recursive=args.recursive,
        )
    except (FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1
    action = "moved" if args.execute else "planned"
    print(f"matched={result.matched} {action}={getattr(result, action)} skipped={result.skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

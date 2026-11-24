"""Find and optionally move unpaired image and annotation files.

Function:
    Compare files by stem across two directories. Files without a matching stem
    are reported and can be moved into separate quarantine subdirectories.

Python call:
    ``run(image_dir, label_dir, quarantine_dir, execute=False)``

CLI call:
    ``python scripts/datasets/quarantine_unpaired_files.py IMAGES LABELS QUARANTINE``

Side effects:
    Preview-only by default. Pass ``execute=True`` or ``--execute`` to move files.

Legacy source:
    ``D:\\yl\\localcode\\important\\del_imgxml.py``
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class UnpairedFile:
    source: Path
    destination: Path
    kind: str


@dataclass(frozen=True, slots=True)
class QuarantineResult:
    image_files: int
    label_files: int
    unpaired_images: int
    unpaired_labels: int
    moved: int
    planned: tuple[UnpairedFile, ...]


def _files_by_stem(directory: Path, *, recursive: bool) -> dict[str, list[Path]]:
    pattern = "**/*" if recursive else "*"
    grouped: dict[str, list[Path]] = {}
    for path in sorted(directory.glob(pattern)):
        if path.is_file():
            grouped.setdefault(path.stem.casefold(), []).append(path)
    return grouped


def run(
    image_dir: Path,
    label_dir: Path,
    quarantine_dir: Path,
    *,
    recursive: bool = False,
    execute: bool = False,
) -> QuarantineResult:
    """Plan or move files whose stem has no counterpart in the other directory."""
    if not image_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not label_dir.is_dir():
        raise FileNotFoundError(f"Label directory not found: {label_dir}")

    images = _files_by_stem(image_dir, recursive=recursive)
    labels = _files_by_stem(label_dir, recursive=recursive)
    planned: list[UnpairedFile] = []
    for kind, source_dir, grouped, other, subdir in (
        ("image", image_dir, images, labels, "images"),
        ("label", label_dir, labels, images, "labels"),
    ):
        for stem in sorted(set(grouped) - set(other)):
            for source in grouped[stem]:
                relative = source.relative_to(source_dir) if recursive else Path(source.name)
                planned.append(
                    UnpairedFile(source, quarantine_dir / subdir / relative, kind)
                )

    destinations = [item.destination.resolve() for item in planned]
    if len(destinations) != len(set(destinations)):
        raise FileExistsError("Multiple unpaired files map to the same quarantine path")
    existing = [item.destination for item in planned if item.destination.exists()]
    if existing:
        raise FileExistsError(f"Quarantine destination already exists: {existing[0]}")

    moved = 0
    if execute:
        for item in planned:
            item.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item.source), item.destination)
            moved += 1

    return QuarantineResult(
        image_files=sum(map(len, images.values())),
        label_files=sum(map(len, labels.values())),
        unpaired_images=sum(item.kind == "image" for item in planned),
        unpaired_labels=sum(item.kind == "label" for item in planned),
        moved=moved,
        planned=tuple(planned),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("image_dir", type=Path)
    parser.add_argument("label_dir", type=Path)
    parser.add_argument("quarantine_dir", type=Path)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.image_dir,
            args.label_dir,
            args.quarantine_dir,
            recursive=args.recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, FileExistsError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    action = "moved" if args.execute else "planned"
    print(
        f"images={result.image_files} labels={result.label_files} "
        f"unpaired_images={result.unpaired_images} "
        f"unpaired_labels={result.unpaired_labels} {action}={len(result.planned)}"
    )
    for item in result.planned:
        print(f"{item.kind}: {item.source} -> {item.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

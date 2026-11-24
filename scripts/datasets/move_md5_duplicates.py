"""Move source files that exactly match comparison files by name and MD5.

Python call:
    ``run(source_dir, comparison_dir, output_dir, execute=False)``

CLI call:
    ``python scripts/datasets/move_md5_duplicates.py SOURCE COMPARE OUTPUT``

Only same-name files are compared. The default is preview-only.

Legacy source:
    ``D:\\yl\\localcode\\similarity_comparison_md5.py``
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DuplicateResult:
    compared: int
    matched: int
    moved: int
    outputs: tuple[Path, ...]


def file_md5(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(
    source_dir: Path,
    comparison_dir: Path,
    output_dir: Path,
    *,
    recursive: bool = True,
    execute: bool = False,
) -> DuplicateResult:
    """Preview or move exact same-name duplicates from source to output."""
    for directory in (source_dir, comparison_dir):
        if not directory.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory}")
    files = sorted(comparison_dir.glob("**/*" if recursive else "*"))
    compared = matched = moved = 0
    outputs: list[Path] = []
    for comparison in files:
        if not comparison.is_file():
            continue
        relative = comparison.relative_to(comparison_dir)
        source = source_dir / relative
        if not source.is_file():
            continue
        compared += 1
        if file_md5(source) != file_md5(comparison):
            continue
        matched += 1
        destination = output_dir / relative
        if execute:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            moved += 1
            outputs.append(destination)
    return DuplicateResult(compared, matched, moved, tuple(outputs))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("comparison_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.source_dir,
            args.comparison_dir,
            args.output_dir,
            recursive=not args.no_recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"compared={result.compared} matched={result.matched} moved={result.moved}")
    print("mode=" + ("execute" if args.execute else "preview"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Add a fixed offset to class IDs in YOLO TXT label files.

Python call:
    ``run(label_dir, offset=-1, name_length=8, execute=False)``

CLI call:
    ``python scripts/documents/offset_yolo_class_ids.py LABEL_DIR --offset -1``

The default is preview-only because label files are modified in place.

Legacy source:
    ``D:\\yl\\localcode\\imgdeal\\change_yolo_label.py``
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class OffsetResult:
    matched_files: int
    changed_files: int
    changed_rows: int


def run(
    label_dir: Path,
    *,
    offset: int,
    name_length: int | None = None,
    recursive: bool = True,
    execute: bool = False,
) -> OffsetResult:
    """Preview or apply a class-ID offset to YOLO labels."""
    if not label_dir.is_dir():
        raise FileNotFoundError(f"Label directory not found: {label_dir}")
    files = sorted(label_dir.glob("**/*.txt" if recursive else "*.txt"))
    matched = changed_files = changed_rows = 0
    for path in files:
        if name_length is not None and len(path.stem) != name_length:
            continue
        matched += 1
        rows: list[str] = []
        file_changes = 0
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            parts = raw_line.split()
            if not parts:
                rows.append("")
                continue
            parts[0] = str(int(parts[0]) + offset)
            rows.append(" ".join(parts))
            file_changes += 1
        if file_changes:
            changed_files += 1
            changed_rows += file_changes
            if execute:
                path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return OffsetResult(matched, changed_files, changed_rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("label_dir", type=Path)
    parser.add_argument("--offset", type=int, required=True)
    parser.add_argument("--name-length", type=int)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.label_dir,
            offset=args.offset,
            name_length=args.name_length,
            recursive=not args.no_recursive,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"matched={result.matched_files} changed_files={result.changed_files} rows={result.changed_rows}")
    print("mode=" + ("execute" if args.execute else "preview"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

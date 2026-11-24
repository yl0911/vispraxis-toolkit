"""Export MD5 values compatible with services hashing decoded image bytes.

Function:
    Hash binary image files by their original bytes. Text files containing raw
    Base64 or data URLs are decoded first, matching a service that hashes bytes
    after decoding an incoming Base64 field.

Python call:
    ``run(source_dir, output_file, output_format="json")``

CLI call:
    ``python scripts/datasets/export_image_md5_manifest.py SOURCE --format go``

Side effects:
    Reads source files and optionally writes one UTF-8 manifest. Sources are
    never modified.

Legacy source:
    ``D:\\yl\\localcode\\dingstock\\ml_iconHash_batch.py``
"""

from __future__ import annotations

import argparse
import base64
import binascii
import fnmatch
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


OutputFormat = Literal["json", "go", "tsv"]
SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".txt", ".b64"}
BASE64_PATTERN = re.compile(rb"^[A-Za-z0-9+/=\r\n_-]+$")


@dataclass(frozen=True, slots=True)
class HashEntry:
    md5: str
    sources: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class ManifestResult:
    files_found: int
    unique_hashes: int
    duplicate_files: int
    entries: tuple[HashEntry, ...]
    output: Path | None
    content: str


def load_decoded_bytes(path: Path) -> bytes:
    """Read binary image bytes or decode a Base64 text representation."""
    data = path.read_bytes()
    if (
        data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:3] == b"\xff\xd8\xff"
        or data[:6] in {b"GIF87a", b"GIF89a"}
        or data[:2] == b"BM"
        or (data[:4] == b"RIFF" and data[8:12] == b"WEBP")
    ):
        return data
    text = data.strip()
    if text.startswith(b"data:") and b"," in text:
        text = text.split(b",", 1)[1]
    if text and BASE64_PATTERN.fullmatch(text):
        compact = re.sub(rb"\s+", b"", text)
        padded = compact + b"=" * (-len(compact) % 4)
        try:
            if b"-" in compact or b"_" in compact:
                return base64.urlsafe_b64decode(padded)
            return base64.b64decode(padded, validate=True)
        except (binascii.Error, ValueError):
            pass
    return data


def _render(entries: tuple[HashEntry, ...], output_format: OutputFormat, with_names: bool) -> str:
    if output_format == "json":
        values: object
        if with_names:
            values = [
                {"md5": entry.md5, "sources": [path.as_posix() for path in entry.sources]}
                for entry in entries
            ]
        else:
            values = [entry.md5 for entry in entries]
        return json.dumps(values, ensure_ascii=False, indent=2) + "\n"
    if output_format == "go":
        lines = ["[]string{"]
        for entry in entries:
            comment = f" // {', '.join(path.as_posix() for path in entry.sources)}" if with_names else ""
            lines.append(f'    "{entry.md5}",{comment}')
        lines.append("}")
        return "\n".join(lines) + "\n"
    lines = []
    for entry in entries:
        names = ",".join(path.as_posix() for path in entry.sources) if with_names else ""
        lines.append(f"{entry.md5}\t{names}".rstrip())
    return "\n".join(lines) + ("\n" if lines else "")


def run(
    source_dir: Path,
    output_file: Path | None = None,
    *,
    recursive: bool = False,
    pattern: str = "*",
    output_format: OutputFormat = "json",
    with_names: bool = False,
    keep_duplicates: bool = False,
) -> ManifestResult:
    """Build and optionally write an MD5 manifest."""
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    if output_format not in {"json", "go", "tsv"}:
        raise ValueError(f"Unsupported output format: {output_format}")
    glob_pattern = "**/*" if recursive else "*"
    files = sorted(
        path
        for path in source_dir.glob(glob_pattern)
        if path.is_file()
        and path.suffix.casefold() in SUPPORTED_SUFFIXES
        and fnmatch.fnmatch(path.name.casefold(), pattern.casefold())
    )
    grouped: dict[str, list[Path]] = {}
    order: list[tuple[str, Path]] = []
    for path in files:
        digest = hashlib.md5(load_decoded_bytes(path)).hexdigest()
        relative = path.relative_to(source_dir)
        grouped.setdefault(digest, []).append(relative)
        order.append((digest, relative))
    if keep_duplicates:
        entries = tuple(HashEntry(digest, (path,)) for digest, path in order)
    else:
        entries = tuple(
            HashEntry(digest, tuple(grouped[digest])) for digest in sorted(grouped)
        )
    content = _render(entries, output_format, with_names)
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8", newline="\n")
    return ManifestResult(
        files_found=len(files),
        unique_hashes=len(grouped),
        duplicate_files=len(files) - len(grouped),
        entries=entries,
        output=output_file,
        content=content,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--pattern", default="*")
    parser.add_argument("--format", dest="output_format", choices=("json", "go", "tsv"), default="json")
    parser.add_argument("--with-names", action="store_true")
    parser.add_argument("--keep-duplicates", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.source_dir,
            args.output,
            recursive=args.recursive,
            pattern=args.pattern,
            output_format=args.output_format,
            with_names=args.with_names,
            keep_duplicates=args.keep_duplicates,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if result.output is None:
        print(result.content, end="")
    print(
        f"files={result.files_found} unique={result.unique_hashes} "
        f"duplicates={result.duplicate_files} output={result.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

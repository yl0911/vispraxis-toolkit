"""Copy one representative of each image hash into a clean directory.

Function:
    Scan images, compute MD5 or a perceptual hash, discard repeated hashes, and
    plan or copy the unique representatives to an output directory.

Python call:
    ``run(source_dir, output_dir, method="md5", execute=False)``

CLI call:
    ``python scripts/datasets/copy_unique_images_by_hash.py SOURCE OUTPUT --method md5``

Side effects:
    Preview-only by default. Pass ``execute=True`` or ``--execute`` to copy files.

Dependencies:
    MD5 uses the Python standard library. aHash, dHash, and pHash additionally
    require Pillow and ImageHash.

Merged legacy sources:
    ``D:\\yl\\localcode\\dingstock\\remove_duplicates.py``
    ``D:\\yl\\localcode\\dingstock\\remove_duplicates2.py``
    ``D:\\yl\\localcode\\dingstock\\rename_remove_duplicates.py``
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal


HashMethod = Literal["md5", "ahash", "dhash", "phash"]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}


@dataclass(frozen=True, slots=True)
class UniqueImage:
    source: Path
    destination: Path
    hash_value: str


@dataclass(frozen=True, slots=True)
class DeduplicationResult:
    images_found: int
    unique_images: int
    duplicate_images: int
    failed_images: int
    copied: int
    planned: tuple[UniqueImage, ...]
    errors: tuple[str, ...]


def _md5(path: Path, hash_size: int) -> str:
    del hash_size
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _perceptual_hasher(method: HashMethod) -> Callable[[Path, int], str]:
    try:
        import imagehash
        from PIL import Image
    except ImportError as exc:
        raise ImportError("Pillow and ImageHash are required for perceptual hashes") from exc

    functions = {
        "ahash": imagehash.average_hash,
        "dhash": imagehash.dhash,
        "phash": imagehash.phash,
    }

    def compute(path: Path, hash_size: int) -> str:
        with Image.open(path) as image:
            return str(functions[method](image.convert("RGB"), hash_size=hash_size))

    return compute


def run(
    source_dir: Path,
    output_dir: Path,
    *,
    method: HashMethod = "md5",
    hash_size: int = 8,
    recursive: bool = True,
    keep_original_name: bool = False,
    execute: bool = False,
) -> DeduplicationResult:
    """Plan or copy one representative for each distinct image hash."""
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    if method not in {"md5", "ahash", "dhash", "phash"}:
        raise ValueError(f"Unsupported hash method: {method}")
    if hash_size < 2:
        raise ValueError("hash_size must be at least 2")
    source_root = source_dir.resolve()
    output_root = output_dir.resolve()
    if output_root == source_root or source_root in output_root.parents:
        raise ValueError("Output directory must not be inside the source directory")

    pattern = "**/*" if recursive else "*"
    sources = sorted(
        path
        for path in source_dir.glob(pattern)
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )
    compute_hash = _md5 if method == "md5" else _perceptual_hasher(method)
    seen: set[str] = set()
    planned: list[UniqueImage] = []
    errors: list[str] = []
    duplicates = 0
    for source in sources:
        try:
            hash_value = compute_hash(source, hash_size)
        except (OSError, ValueError) as exc:
            errors.append(f"{source}: {exc}")
            continue
        if hash_value in seen:
            duplicates += 1
            continue
        seen.add(hash_value)
        relative = source.relative_to(source_dir)
        destination = (
            output_dir / relative
            if keep_original_name
            else output_dir / f"{hash_value}{source.suffix.casefold()}"
        )
        planned.append(UniqueImage(source, destination, hash_value))

    destinations = [item.destination.resolve() for item in planned]
    if len(destinations) != len(set(destinations)):
        raise FileExistsError("Multiple unique images map to the same output path")
    existing = [item.destination for item in planned if item.destination.exists()]
    if existing:
        raise FileExistsError(f"Output file already exists: {existing[0]}")

    copied = 0
    if execute:
        for item in planned:
            item.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item.source, item.destination)
            copied += 1
    return DeduplicationResult(
        images_found=len(sources),
        unique_images=len(planned),
        duplicate_images=duplicates,
        failed_images=len(errors),
        copied=copied,
        planned=tuple(planned),
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--method", choices=("md5", "ahash", "dhash", "phash"), default="md5")
    parser.add_argument("--hash-size", type=int, default=8)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--keep-original-name", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.source_dir,
            args.output_dir,
            method=args.method,
            hash_size=args.hash_size,
            recursive=not args.no_recursive,
            keep_original_name=args.keep_original_name,
            execute=args.execute,
        )
    except (FileNotFoundError, FileExistsError, ImportError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"images={result.images_found} unique={result.unique_images} "
        f"duplicates={result.duplicate_images} failed={result.failed_images} "
        f"copied={result.copied} mode={'execute' if args.execute else 'preview'}"
    )
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.failed_images == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

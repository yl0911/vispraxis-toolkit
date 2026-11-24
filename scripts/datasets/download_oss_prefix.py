"""Download objects under an Aliyun OSS prefix.

Function:
    List objects below one prefix, optionally limit the result, and download
    them concurrently while preserving their relative object-key structure.

Python call:
    ``run(endpoint, bucket, prefix, output_dir, access_key_id=..., access_key_secret=...)``

CLI call:
    ``python scripts/datasets/download_oss_prefix.py ENDPOINT BUCKET PREFIX OUTPUT``

Credentials:
    CLI defaults read ``OSS_ACCESS_KEY_ID`` and ``OSS_ACCESS_KEY_SECRET``.
    Credentials must never be written into this repository.

Side effects:
    Preview-only by default. Pass ``execute=True`` or ``--execute`` to download.
    Existing files are retained unless overwrite is explicitly enabled.

Legacy source:
    ``D:\\yl\\localcode\\dingstock\\oss_download.py``
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True, slots=True)
class DownloadItem:
    object_key: str
    destination: Path
    size: int | None


@dataclass(frozen=True, slots=True)
class DownloadResult:
    objects_found: int
    planned: int
    downloaded: int
    skipped_existing: int
    failed: int
    items: tuple[DownloadItem, ...]
    errors: tuple[str, ...]


def _destination(output_dir: Path, prefix: str, object_key: str) -> Path:
    relative_text = object_key[len(prefix):].lstrip("/") if object_key.startswith(prefix) else object_key
    relative = PurePosixPath(relative_text)
    if not relative.parts or relative_text.endswith("/"):
        raise ValueError(f"Object key does not name a file: {object_key}")
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"Unsafe object key: {object_key}")
    destination = output_dir.joinpath(*relative.parts)
    output_root = output_dir.resolve()
    if output_root not in destination.resolve().parents:
        raise ValueError(f"Object key escapes output directory: {object_key}")
    return destination


def run(
    endpoint: str,
    bucket_name: str,
    prefix: str,
    output_dir: Path,
    *,
    access_key_id: str,
    access_key_secret: str,
    max_files: int = 0,
    workers: int = 8,
    overwrite: bool = False,
    execute: bool = False,
) -> DownloadResult:
    """List and optionally download OSS objects below a prefix."""
    if not endpoint or not bucket_name:
        raise ValueError("endpoint and bucket_name are required")
    if not access_key_id or not access_key_secret:
        raise ValueError("OSS access key ID and secret are required")
    if max_files < 0:
        raise ValueError("max_files must be zero or positive")
    if workers < 1:
        raise ValueError("workers must be at least 1")
    try:
        import oss2
    except ImportError as exc:
        raise ImportError("Install oss2 to use OSS downloads") from exc

    bucket = oss2.Bucket(
        oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name
    )
    items: list[DownloadItem] = []
    errors: list[str] = []
    objects_found = 0
    try:
        for obj in oss2.ObjectIterator(bucket, prefix=prefix):
            if obj.key.endswith("/"):
                continue
            if max_files and len(items) >= max_files:
                break
            objects_found += 1
            try:
                destination = _destination(output_dir, prefix, obj.key)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            items.append(DownloadItem(obj.key, destination, getattr(obj, "size", None)))
    except Exception as exc:
        raise RuntimeError(f"Failed to list OSS prefix {prefix!r}: {exc}") from exc

    destinations = [item.destination.resolve() for item in items]
    if len(destinations) != len(set(destinations)):
        raise FileExistsError("Multiple OSS objects map to the same local path")

    pending = [item for item in items if overwrite or not item.destination.exists()]
    skipped = len(items) - len(pending)
    downloaded = 0
    if execute:
        for item in pending:
            item.destination.parent.mkdir(parents=True, exist_ok=True)

        def download(item: DownloadItem) -> DownloadItem:
            bucket.get_object_to_file(item.object_key, str(item.destination))
            return item

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(download, item): item for item in pending}
            for future in as_completed(futures):
                item = futures[future]
                try:
                    future.result()
                    downloaded += 1
                except Exception as exc:
                    errors.append(f"{item.object_key}: {exc}")

    return DownloadResult(
        objects_found=objects_found,
        planned=len(pending),
        downloaded=downloaded,
        skipped_existing=skipped,
        failed=len(errors),
        items=tuple(items),
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("endpoint")
    parser.add_argument("bucket")
    parser.add_argument("prefix")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--access-key-id", default=os.getenv("OSS_ACCESS_KEY_ID"))
    parser.add_argument("--access-key-secret", default=os.getenv("OSS_ACCESS_KEY_SECRET"))
    parser.add_argument("--max-files", type=int, default=0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.endpoint,
            args.bucket,
            args.prefix,
            args.output_dir,
            access_key_id=args.access_key_id or "",
            access_key_secret=args.access_key_secret or "",
            max_files=args.max_files,
            workers=args.workers,
            overwrite=args.overwrite,
            execute=args.execute,
        )
    except (FileExistsError, ImportError, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"objects={result.objects_found} planned={result.planned} "
        f"downloaded={result.downloaded} skipped={result.skipped_existing} "
        f"failed={result.failed} mode={'execute' if args.execute else 'preview'}"
    )
    for item in result.items:
        print(f"{item.object_key} -> {item.destination}")
    for error in result.errors:
        print(f"ERROR: {error}")
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

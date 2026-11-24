"""Invoke an HTTP JSON service with Base64-encoded images.

Function:
    Read one image or a directory of images, key them by MD5, insert the Base64
    map into a configurable JSON field, and optionally POST the payload.

Python call:
    ``run(input_path, endpoint, payload={"module": "demo"}, execute=False)``

CLI call:
    ``python scripts/automation/invoke_image_json_service.py INPUT ENDPOINT --field module=demo``

Side effects:
    Preview-only by default. Pass ``execute=True`` or ``--execute`` to send the
    request. An optional response file is written only after a successful call.

Legacy source:
    ``D:\\yl\\localcode\\request_batch.py``
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}


@dataclass(frozen=True, slots=True)
class InvocationResult:
    images_found: int
    images_encoded: int
    duplicate_images: int
    sent: bool
    status_code: int | None
    response: Any
    response_file: Path | None


def _collect_images(input_path: Path, *, recursive: bool, max_images: int) -> list[Path]:
    if input_path.is_file():
        if input_path.suffix.casefold() not in IMAGE_SUFFIXES:
            raise ValueError(f"Unsupported image type: {input_path}")
        return [input_path]
    if not input_path.is_dir():
        raise FileNotFoundError(f"Image input not found: {input_path}")
    pattern = "**/*" if recursive else "*"
    images = sorted(
        path
        for path in input_path.glob(pattern)
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )
    return images[:max_images] if max_images else images


def encode_images(paths: list[Path]) -> tuple[dict[str, str], int]:
    """Return an MD5-to-Base64 image map and the duplicate count."""
    encoded: dict[str, str] = {}
    duplicates = 0
    for path in paths:
        content = path.read_bytes()
        digest = hashlib.md5(content).hexdigest()
        if digest in encoded:
            duplicates += 1
            continue
        encoded[digest] = base64.b64encode(content).decode("ascii")
    return encoded, duplicates


def run(
    input_path: Path,
    endpoint: str,
    *,
    payload: dict[str, Any] | None = None,
    image_field: str = "images",
    headers: dict[str, str] | None = None,
    recursive: bool = False,
    max_images: int = 9,
    timeout: float = 60.0,
    response_file: Path | None = None,
    execute: bool = False,
) -> InvocationResult:
    """Build and optionally send one image-service JSON request."""
    if not endpoint:
        raise ValueError("endpoint is required")
    if not image_field:
        raise ValueError("image_field is required")
    if max_images < 0:
        raise ValueError("max_images must be zero or positive")
    if timeout <= 0:
        raise ValueError("timeout must be positive")

    paths = _collect_images(input_path, recursive=recursive, max_images=max_images)
    images, duplicates = encode_images(paths)
    request_payload = dict(payload or {})
    if image_field in request_payload:
        raise ValueError(f"Payload already contains image field {image_field!r}")
    request_payload[image_field] = images
    if not execute:
        return InvocationResult(
            len(paths), len(images), duplicates, False, None, None, None
        )

    try:
        import requests
    except ImportError as exc:
        raise ImportError("Install requests to invoke HTTP services") from exc
    response = requests.post(
        endpoint,
        json=request_payload,
        headers=headers or None,
        timeout=timeout,
    )
    response.raise_for_status()
    try:
        response_data: Any = response.json()
    except ValueError:
        response_data = response.text
    written_file = None
    if response_file is not None:
        response_file.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(response_data, str):
            response_file.write_text(response_data, encoding="utf-8")
        else:
            response_file.write_text(
                json.dumps(response_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        written_file = response_file
    return InvocationResult(
        len(paths),
        len(images),
        duplicates,
        True,
        response.status_code,
        response_data,
        written_file,
    )


def _key_value(value: str) -> tuple[str, str]:
    key, separator, item = value.partition("=")
    if not separator or not key.strip():
        raise argparse.ArgumentTypeError("Values must use KEY=VALUE")
    return key.strip(), item


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("input_path", type=Path)
    parser.add_argument("endpoint")
    parser.add_argument("--field", dest="fields", action="append", type=_key_value, default=[])
    parser.add_argument("--header", dest="headers", action="append", type=_key_value, default=[])
    parser.add_argument("--image-field", default="images")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--max-images", type=int, default=9)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--response-file", type=Path)
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.input_path,
            args.endpoint,
            payload=dict(args.fields),
            image_field=args.image_field,
            headers=dict(args.headers),
            recursive=args.recursive,
            max_images=args.max_images,
            timeout=args.timeout,
            response_file=args.response_file,
            execute=args.execute,
        )
    except (FileNotFoundError, ImportError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"images={result.images_found} encoded={result.images_encoded} "
        f"duplicates={result.duplicate_images} sent={result.sent} "
        f"status={result.status_code} mode={'execute' if args.execute else 'preview'}"
    )
    if result.response is not None:
        print(json.dumps(result.response, ensure_ascii=False) if not isinstance(result.response, str) else result.response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

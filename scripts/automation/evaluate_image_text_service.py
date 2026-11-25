"""Evaluate an HTTP image-to-text service against answers encoded in filenames.

Function:
    Read ``ANSWER_suffix.ext`` images, send MD5-keyed Base64 batches to an HTTP
    JSON service, compare returned text, and optionally write JSON/CSV reports.

Python call:
    ``run(image_input, endpoint, service="ocr", execute=False)``

CLI call:
    ``python scripts/automation/evaluate_image_text_service.py IMAGES ENDPOINT --service ocr``

Side effects:
    Preview-only by default. ``execute=True`` or ``--execute`` sends requests.
    Report files are written only during execution.

Legacy source:
    ``D:\\yl\\localcode\\dingstock\\ocr_common2_eval.py``
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


@dataclass(frozen=True, slots=True)
class ImageSample:
    path: Path
    expected: str


@dataclass(frozen=True, slots=True)
class EvaluationItem:
    file_name: str
    path: str
    request_id: str
    expected: str
    predicted: str
    correct: bool
    success: bool | None
    score: float | None
    error: str = ""


@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    total: int
    correct: int
    wrong: int
    errored: int
    skipped: int
    accuracy: float
    elapsed_seconds: float


@dataclass(frozen=True, slots=True)
class EvaluationRun:
    images_found: int
    samples_collected: int
    skipped_files: tuple[str, ...]
    executed: bool
    items: tuple[EvaluationItem, ...]
    summary: EvaluationSummary | None
    json_report: Path | None
    csv_report: Path | None


PostJson = Callable[[str, dict[str, Any], float], dict[str, Any]]


def normalize_text(value: Any) -> str:
    """Normalize case and whitespace without conflating similar characters."""
    return "".join(str(value or "").split()).casefold()


def _image_paths(image_input: Path, recursive: bool) -> list[Path]:
    if image_input.is_file():
        if image_input.suffix.casefold() not in IMAGE_SUFFIXES:
            raise ValueError(f"Unsupported image type: {image_input}")
        return [image_input]
    if not image_input.is_dir():
        raise FileNotFoundError(f"Image input not found: {image_input}")
    pattern = "**/*" if recursive else "*"
    return sorted(
        path
        for path in image_input.glob(pattern)
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )


def collect_samples(
    image_input: Path,
    *,
    answer_separator: str = "_",
    recursive: bool = False,
    limit: int = 0,
) -> tuple[list[ImageSample], list[str], int]:
    """Collect samples whose filename begins with the expected text."""
    if not answer_separator:
        raise ValueError("answer_separator is required")
    if limit < 0:
        raise ValueError("limit must not be negative")
    paths = _image_paths(image_input, recursive)
    samples: list[ImageSample] = []
    skipped: list[str] = []
    for path in paths:
        expected, separator, _ = path.stem.partition(answer_separator)
        if not separator or not expected:
            skipped.append(str(path))
            continue
        samples.append(ImageSample(path, expected))
        if limit and len(samples) >= limit:
            break
    return samples, skipped, len(paths)


def _chunks(items: Sequence[ImageSample], size: int) -> Iterable[Sequence[ImageSample]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


def _post_json(endpoint: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not isinstance(result, dict):
        raise ValueError("Service response must be a JSON object")
    return result


def _error_item(sample: ImageSample, request_id: str, error: str) -> EvaluationItem:
    return EvaluationItem(
        sample.path.name,
        str(sample.path),
        request_id,
        sample.expected,
        "",
        False,
        False,
        None,
        error,
    )


def _evaluate_batch(
    samples: Sequence[ImageSample],
    endpoint: str,
    service: str,
    metadata: dict[str, Any],
    timeout: float,
    post_json: PostJson,
    *,
    text_field: str,
    score_field: str,
    success_field: str,
) -> list[EvaluationItem]:
    images: dict[str, str] = {}
    grouped: dict[str, list[ImageSample]] = {}
    results: list[EvaluationItem] = []
    for sample in samples:
        try:
            content = sample.path.read_bytes()
        except OSError as exc:
            results.append(_error_item(sample, "", f"read failed: {exc}"))
            continue
        request_id = hashlib.md5(content).hexdigest()
        images.setdefault(request_id, base64.b64encode(content).decode("ascii"))
        grouped.setdefault(request_id, []).append(sample)
    if not images:
        return results

    try:
        response = post_json(
            endpoint,
            {"images": images, "service": service, "metadata": metadata},
            timeout,
        )
        response_code = response.get("code", 200)
        if response_code != 200:
            raise ValueError(
                f"service code {response_code}: {response.get('message', '')}"
            )
        response_data = response.get("data", {})
        if not isinstance(response_data, dict):
            raise ValueError("Response data must be an object keyed by image MD5")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        for request_id, request_samples in grouped.items():
            for sample in request_samples:
                results.append(_error_item(sample, request_id, f"request failed: {exc}"))
        return results

    for request_id, request_samples in grouped.items():
        item_data = response_data.get(request_id)
        if not isinstance(item_data, dict):
            for sample in request_samples:
                results.append(_error_item(sample, request_id, "missing response item"))
            continue
        predicted = str(item_data.get(text_field) or "")
        raw_score = item_data.get(score_field)
        raw_success = item_data.get(success_field)
        for sample in request_samples:
            results.append(
                EvaluationItem(
                    sample.path.name,
                    str(sample.path),
                    request_id,
                    sample.expected,
                    predicted,
                    normalize_text(sample.expected) == normalize_text(predicted),
                    raw_success if isinstance(raw_success, bool) else None,
                    float(raw_score) if isinstance(raw_score, (int, float)) else None,
                )
            )
    return results


def _summary(
    items: Sequence[EvaluationItem], skipped: int, elapsed: float
) -> EvaluationSummary:
    total = len(items)
    correct = sum(item.correct for item in items)
    errored = sum(bool(item.error) for item in items)
    return EvaluationSummary(
        total,
        correct,
        total - correct,
        errored,
        skipped,
        correct / total if total else 0.0,
        elapsed,
    )


def _write_json(
    path: Path,
    summary: EvaluationSummary,
    items: Sequence[EvaluationItem],
    skipped: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "summary": asdict(summary),
                "items": [asdict(item) for item in items],
                "skipped_files": list(skipped),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, items: Sequence[EvaluationItem]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [field.name for field in EvaluationItem.__dataclass_fields__.values()]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(asdict(item) for item in items)


def run(
    image_input: Path,
    endpoint: str,
    *,
    service: str,
    metadata: dict[str, Any] | None = None,
    answer_separator: str = "_",
    batch_size: int = 32,
    timeout: float = 30.0,
    recursive: bool = False,
    limit: int = 0,
    text_field: str = "text",
    score_field: str = "score",
    success_field: str = "success",
    json_report: Path | None = None,
    csv_report: Path | None = None,
    execute: bool = False,
    post_json: PostJson | None = None,
) -> EvaluationRun:
    """Preview or execute an image-to-text service evaluation."""
    if not endpoint or not service:
        raise ValueError("endpoint and service are required")
    if batch_size < 1 or timeout <= 0:
        raise ValueError("batch_size and timeout must be positive")
    samples, skipped, images_found = collect_samples(
        image_input,
        answer_separator=answer_separator,
        recursive=recursive,
        limit=limit,
    )
    if not samples:
        raise ValueError("No images with answers encoded in their filenames were found")
    if not execute:
        return EvaluationRun(
            images_found, len(samples), tuple(skipped), False, (), None, None, None
        )

    start = time.perf_counter()
    items: list[EvaluationItem] = []
    sender = post_json or _post_json
    for batch in _chunks(samples, batch_size):
        items.extend(
            _evaluate_batch(
                batch,
                endpoint,
                service,
                dict(metadata or {}),
                timeout,
                sender,
                text_field=text_field,
                score_field=score_field,
                success_field=success_field,
            )
        )
    summary = _summary(items, len(skipped), time.perf_counter() - start)
    if json_report is not None:
        _write_json(json_report, summary, items, skipped)
    if csv_report is not None:
        _write_csv(csv_report, items)
    return EvaluationRun(
        images_found,
        len(samples),
        tuple(skipped),
        True,
        tuple(items),
        summary,
        json_report,
        csv_report,
    )


def _json_object(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"Invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("Value must be a JSON object")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("image_input", type=Path)
    parser.add_argument("endpoint")
    parser.add_argument("--service", required=True)
    parser.add_argument("--metadata-json", type=_json_object, default={})
    parser.add_argument("--answer-separator", default="_")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--score-field", default="score")
    parser.add_argument("--success-field", default="success")
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--csv-report", type=Path)
    parser.add_argument("--min-accuracy", type=float)
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.image_input,
            args.endpoint,
            service=args.service,
            metadata=args.metadata_json,
            answer_separator=args.answer_separator,
            batch_size=args.batch_size,
            timeout=args.timeout,
            recursive=args.recursive,
            limit=args.limit,
            text_field=args.text_field,
            score_field=args.score_field,
            success_field=args.success_field,
            json_report=args.json_report,
            csv_report=args.csv_report,
            execute=args.execute,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"images={result.images_found} samples={result.samples_collected} "
        f"skipped={len(result.skipped_files)} mode={'execute' if result.executed else 'preview'}"
    )
    if result.summary is not None:
        print(
            f"correct={result.summary.correct}/{result.summary.total} "
            f"accuracy={result.summary.accuracy:.4f} errors={result.summary.errored} "
            f"elapsed={result.summary.elapsed_seconds:.2f}s"
        )
        if args.min_accuracy is not None and result.summary.accuracy < args.min_accuracy:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

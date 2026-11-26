"""Stitch indexed small images below their matching base image.

Function:
    Match ``NAME.ext`` with ``NAME_1.png``, ``NAME_2.png``, and similar files,
    resize the indexed images, and place them in one row below the base image.

Python call:
    ``run(input_dir, output_dir, small_size=(50, 50), max_small_images=3)``

CLI call:
    ``python scripts/vision/stitch_base_with_indexed_images.py INPUT OUTPUT``

Side effects:
    Writes stitched images under the output directory and preserves relative
    subdirectories. Source images are not modified.

Merged legacy sources:
    ``D:\\yl\\localcode\\dingstock\\geetest_v4_making_req_data.py``
    ``D:\\yl\\localcode\\dingstock\\geetestv4_making_test.py``
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
BASE_SUFFIX_PRIORITY = {".jpg": 0, ".jpeg": 1, ".png": 2, ".webp": 3, ".bmp": 4}


@dataclass(frozen=True, slots=True)
class StitchItem:
    base: Path
    small_images: tuple[Path | None, ...]
    output: Path


@dataclass(frozen=True, slots=True)
class StitchResult:
    groups_found: int
    images_written: int
    groups_without_base: tuple[str, ...]
    failed_groups: tuple[str, ...]
    items: tuple[StitchItem, ...]


def _indexed_name(path: Path) -> tuple[str, int] | None:
    prefix, separator, index = path.stem.rpartition("_")
    if not separator or not prefix or not index.isdigit():
        return None
    return prefix, int(index)


def _to_rgb(image: Image.Image, background: str) -> Image.Image:
    if image.mode == "RGB":
        return image.copy()
    if image.mode in {"RGBA", "LA"} or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")
        canvas = Image.new("RGB", rgba.size, background)
        canvas.paste(rgba, mask=rgba.getchannel("A"))
        return canvas
    return image.convert("RGB")


def _choose_base(candidates: list[Path]) -> Path:
    return min(
        candidates,
        key=lambda path: (
            BASE_SUFFIX_PRIORITY.get(path.suffix.casefold(), 99),
            path.name.casefold(),
        ),
    )


def _fallback_base(prefix: str, candidates: list[Path]) -> Path | None:
    """Match ``123_icon_1`` to an unambiguous base such as ``123_bg.jpg``."""
    current = prefix
    while "_" in current:
        current = current.rsplit("_", 1)[0]
        matches = [
            path
            for path in candidates
            if path.stem == current or path.stem.startswith(current + "_")
        ]
        distinct_stems = {path.stem for path in matches}
        if len(distinct_stems) == 1:
            return _choose_base(matches)
        if len(distinct_stems) > 1:
            return None
    return None


def _collect_groups(
    input_dir: Path, recursive: bool
) -> tuple[
    list[tuple[Path, Path, list[tuple[int, Path]]]],
    list[str],
]:
    pattern = "**/*" if recursive else "*"
    images = sorted(
        path
        for path in input_dir.glob(pattern)
        if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
    )
    bases: dict[tuple[Path, str], list[Path]] = {}
    indexed: dict[tuple[Path, str], list[tuple[int, Path]]] = {}
    loose_bases: dict[Path, list[Path]] = {}
    for path in images:
        relative_parent = path.parent.relative_to(input_dir)
        parsed = _indexed_name(path)
        if parsed is None:
            bases.setdefault((relative_parent, path.stem), []).append(path)
            loose_bases.setdefault(relative_parent, []).append(path)
        else:
            indexed.setdefault((relative_parent, parsed[0]), []).append((parsed[1], path))

    groups: list[tuple[Path, Path, list[tuple[int, Path]]]] = []
    missing: list[str] = []
    for (relative_parent, prefix), small_images in sorted(
        indexed.items(), key=lambda item: (str(item[0][0]), item[0][1])
    ):
        exact = bases.get((relative_parent, prefix), [])
        base = _choose_base(exact) if exact else _fallback_base(
            prefix, loose_bases.get(relative_parent, [])
        )
        if base is None:
            missing.append(str(relative_parent / prefix))
            continue
        groups.append(
            (
                relative_parent,
                base,
                sorted(small_images, key=lambda item: (item[0], item[1].name.casefold())),
            )
        )
    return groups, missing


def _select_small_images(
    indexed: list[tuple[int, Path]],
    *,
    max_small_images: int,
    fill_missing: bool,
    index_start: int,
) -> list[Path | None]:
    if not fill_missing:
        selected = [path for _, path in indexed]
        return selected[:max_small_images] if max_small_images else selected
    if max_small_images < 1:
        raise ValueError("max_small_images must be positive when fill_missing is enabled")
    by_index = {index: path for index, path in indexed}
    return [by_index.get(index) for index in range(index_start, index_start + max_small_images)]


def _stitch(
    base_path: Path,
    small_paths: list[Path | None],
    output_path: Path,
    *,
    small_size: tuple[int, int],
    background: str,
    align: str,
) -> None:
    with Image.open(base_path) as opened:
        base = _to_rgb(opened, background)
    small_images: list[Image.Image] = []
    for path in small_paths:
        if path is None:
            small_images.append(Image.new("RGB", small_size, background))
            continue
        with Image.open(path) as opened:
            small_images.append(
                _to_rgb(opened, background).resize(small_size, Image.Resampling.LANCZOS)
            )
    if not small_images:
        raise ValueError("No indexed images selected")
    row_width = small_size[0] * len(small_images)
    width = max(base.width, row_width)
    output = Image.new("RGB", (width, base.height + small_size[1]), background)
    base_x = 0 if align == "left" else (width - base.width) // 2
    row_x = 0 if align == "left" else (width - row_width) // 2
    output.paste(base, (base_x, 0))
    for index, image in enumerate(small_images):
        output.paste(image, (row_x + index * small_size[0], base.height))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_options = {"quality": 95} if output_path.suffix.casefold() in {".jpg", ".jpeg"} else {}
    output.save(output_path, **save_options)


def run(
    input_dir: Path,
    output_dir: Path,
    *,
    small_size: tuple[int, int] = (50, 50),
    max_small_images: int = 3,
    fill_missing: bool = False,
    index_start: int = 1,
    background: str = "white",
    align: str = "left",
    recursive: bool = True,
) -> StitchResult:
    """Stitch every detected base/indexed-image group."""
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    if input_dir.resolve() == output_dir.resolve():
        raise ValueError("output_dir must differ from input_dir")
    if small_size[0] < 1 or small_size[1] < 1:
        raise ValueError("small_size dimensions must be positive")
    if max_small_images < 0:
        raise ValueError("max_small_images must not be negative")
    if index_start < 0:
        raise ValueError("index_start must not be negative")
    if align not in {"left", "center"}:
        raise ValueError("align must be 'left' or 'center'")

    groups, missing = _collect_groups(input_dir, recursive)
    items: list[StitchItem] = []
    failed: list[str] = []
    for relative_parent, base, indexed in groups:
        selected = _select_small_images(
            indexed,
            max_small_images=max_small_images,
            fill_missing=fill_missing,
            index_start=index_start,
        )
        destination = output_dir / relative_parent / base.name
        try:
            _stitch(
                base,
                selected,
                destination,
                small_size=small_size,
                background=background,
                align=align,
            )
        except (OSError, SyntaxError, ValueError) as exc:
            failed.append(f"{base}: {exc}")
            continue
        items.append(StitchItem(base, tuple(selected), destination))
    return StitchResult(len(groups), len(items), tuple(missing), tuple(failed), tuple(items))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--small-width", type=int, default=50)
    parser.add_argument("--small-height", type=int, default=50)
    parser.add_argument("--max-small-images", type=int, default=3)
    parser.add_argument("--fill-missing", action="store_true")
    parser.add_argument("--index-start", type=int, default=1)
    parser.add_argument("--background", default="white")
    parser.add_argument("--align", choices=("left", "center"), default="left")
    parser.add_argument("--no-recursive", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.input_dir,
            args.output_dir,
            small_size=(args.small_width, args.small_height),
            max_small_images=args.max_small_images,
            fill_missing=args.fill_missing,
            index_start=args.index_start,
            background=args.background,
            align=args.align,
            recursive=not args.no_recursive,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"groups={result.groups_found} written={result.images_written} "
        f"without_base={len(result.groups_without_base)} failed={len(result.failed_groups)}"
    )
    for item in result.items:
        print(f"{item.output}: base={item.base.name} small={len(item.small_images)}")
    return 0 if not result.failed_groups else 2


if __name__ == "__main__":
    raise SystemExit(main())

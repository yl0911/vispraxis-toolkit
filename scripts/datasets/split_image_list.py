"""Randomly split image paths into train and validation list files.

Call ``run(image_dir, output_dir, train_ratio=0.9, seed=None)`` or run this
file as a CLI. Legacy source: ``important/v_yolo_data_split.py``.
"""
from __future__ import annotations
import argparse, random
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True, slots=True)
class SplitResult:
    train: int
    validation: int
    train_file: Path
    validation_file: Path

def run(image_dir: Path, output_dir: Path, *, train_ratio: float = .9, seed: int | None = None,
        extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")) -> SplitResult:
    if not image_dir.is_dir(): raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not 0 <= train_ratio <= 1: raise ValueError("train_ratio must be between 0 and 1")
    rng = random.Random(seed)
    images = sorted(p.resolve() for p in image_dir.iterdir() if p.is_file() and p.suffix.casefold() in extensions)
    rng.shuffle(images)
    cutoff = round(len(images) * train_ratio)
    train, validation = images[:cutoff], images[cutoff:]
    output_dir.mkdir(parents=True, exist_ok=True)
    train_file, validation_file = output_dir / "train.txt", output_dir / "val.txt"
    train_file.write_text("".join(f"{p}\n" for p in train), encoding="utf-8")
    validation_file.write_text("".join(f"{p}\n" for p in validation), encoding="utf-8")
    return SplitResult(len(train), len(validation), train_file, validation_file)

def main(argv: list[str] | None = None) -> int:
    ap=argparse.ArgumentParser(description=__doc__.split("\n",1)[0]); ap.add_argument("image_dir",type=Path); ap.add_argument("output_dir",type=Path); ap.add_argument("--train-ratio",type=float,default=.9); ap.add_argument("--seed",type=int)
    a=ap.parse_args(argv)
    try: r=run(a.image_dir,a.output_dir,train_ratio=a.train_ratio,seed=a.seed)
    except (OSError,ValueError) as e: print(f"ERROR: {e}"); return 1
    print(f"train={r.train} validation={r.validation}"); return 0
if __name__ == "__main__": raise SystemExit(main())

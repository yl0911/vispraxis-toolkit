"""Count labels for the historical fire/smoke validation dataset."""

from pathlib import Path

from scripts.documents.count_annotation_labels import run

LABEL_DIR = Path(r"E:\yl\data\fireworks\aistudio\118365\fire_smoke\divided\labels\val")
LABELS: set[str] | None = None


def main() -> int:
    try:
        counts = run(LABEL_DIR, labels=LABELS)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    for index, (label, count) in enumerate(counts.items()):
        print(f"{index} {label} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

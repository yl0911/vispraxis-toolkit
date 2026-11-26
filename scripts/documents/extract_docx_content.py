"""Extract paragraphs, tables, and embedded media from a DOCX file.

Function:
    Read the standard ZIP/XML structure of a DOCX file, collect paragraph text
    and table cells, extract embedded media, and write a JSON content report.

Python call:
    ``run(docx_file, output_dir, extract_media=True)``

CLI call:
    ``python scripts/documents/extract_docx_content.py FILE.docx OUTPUT``

Side effects:
    Writes ``content.json`` and, unless disabled, files under ``media/``. The
    source document is not modified.

Legacy source:
    ``D:\\yl\\localcode\\ws\\word.ipynb``
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath


WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{WORD_NAMESPACE}}}"


@dataclass(frozen=True, slots=True)
class DocxContent:
    source: str
    paragraphs: tuple[str, ...]
    tables: tuple[tuple[tuple[str, ...], ...], ...]
    media_files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DocxExtractionResult:
    paragraphs_found: int
    tables_found: int
    media_found: int
    media_written: int
    report_file: Path
    media_outputs: tuple[Path, ...]
    content: DocxContent


def _text(element: ET.Element) -> str:
    """Join Word text runs while respecting tabs and explicit line breaks."""
    parts: list[str] = []
    for node in element.iter():
        if node.tag == f"{W}t":
            parts.append(node.text or "")
        elif node.tag == f"{W}tab":
            parts.append("\t")
        elif node.tag in {f"{W}br", f"{W}cr"}:
            parts.append("\n")
    return "".join(parts)


def _document_content(root: ET.Element) -> tuple[list[str], list[list[list[str]]]]:
    body = root.find(f"{W}body")
    if body is None:
        raise ValueError("DOCX document.xml does not contain a Word body")
    paragraphs: list[str] = []
    tables: list[list[list[str]]] = []
    for child in body:
        if child.tag == f"{W}p":
            paragraphs.append(_text(child))
        elif child.tag == f"{W}tbl":
            rows: list[list[str]] = []
            for row in child.findall(f"{W}tr"):
                rows.append([_text(cell) for cell in row.findall(f"{W}tc")])
            tables.append(rows)
    return paragraphs, tables


def _media_members(archive: zipfile.ZipFile) -> list[str]:
    return sorted(
        name
        for name in archive.namelist()
        if name.startswith("word/media/") and not name.endswith("/")
    )


def run(
    docx_file: Path,
    output_dir: Path,
    *,
    extract_media: bool = True,
    include_empty_paragraphs: bool = False,
    report_name: str = "content.json",
) -> DocxExtractionResult:
    """Extract structured text and embedded media from one DOCX document."""
    if not docx_file.is_file():
        raise FileNotFoundError(f"DOCX file not found: {docx_file}")
    if docx_file.suffix.casefold() != ".docx":
        raise ValueError("Input file must use the .docx extension")
    if not report_name or Path(report_name).name != report_name:
        raise ValueError("report_name must be a file name without directories")
    try:
        archive = zipfile.ZipFile(docx_file)
    except zipfile.BadZipFile as exc:
        raise ValueError(f"Invalid DOCX ZIP container: {docx_file}") from exc

    with archive:
        try:
            document_xml = archive.read("word/document.xml")
        except KeyError as exc:
            raise ValueError("DOCX does not contain word/document.xml") from exc
        try:
            root = ET.fromstring(document_xml)
        except ET.ParseError as exc:
            raise ValueError("DOCX document.xml is invalid") from exc
        paragraphs, raw_tables = _document_content(root)
        if not include_empty_paragraphs:
            paragraphs = [paragraph for paragraph in paragraphs if paragraph]
        media_members = _media_members(archive)
        media_outputs: list[Path] = []
        if extract_media:
            used_names: set[str] = set()
            for member in media_members:
                original_name = PurePosixPath(member).name
                candidate = original_name
                index = 1
                while candidate.casefold() in used_names:
                    path = Path(original_name)
                    candidate = f"{path.stem}_{index}{path.suffix}"
                    index += 1
                used_names.add(candidate.casefold())
                destination = output_dir / "media" / candidate
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(member))
                media_outputs.append(destination)

    content = DocxContent(
        str(docx_file),
        tuple(paragraphs),
        tuple(tuple(tuple(cell for cell in row) for row in table) for table in raw_tables),
        tuple(PurePosixPath(member).name for member in media_members),
    )
    report_file = output_dir / report_name
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(
        json.dumps(asdict(content), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return DocxExtractionResult(
        len(content.paragraphs),
        len(content.tables),
        len(media_members),
        len(media_outputs),
        report_file,
        tuple(media_outputs),
        content,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("docx_file", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--no-media", action="store_true")
    parser.add_argument("--include-empty-paragraphs", action="store_true")
    parser.add_argument("--report-name", default="content.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run(
            args.docx_file,
            args.output_dir,
            extract_media=not args.no_media,
            include_empty_paragraphs=args.include_empty_paragraphs,
            report_name=args.report_name,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"paragraphs={result.paragraphs_found} tables={result.tables_found} "
        f"media={result.media_found} extracted={result.media_written} "
        f"report={result.report_file}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

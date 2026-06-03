#!/usr/bin/env python3
"""Render selected PDF pages to PNG for visual inspection."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def parse_pages(spec: str) -> list[int]:
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise ValueError(f"Invalid page range: {part}")
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    if not pages:
        raise ValueError("No pages selected.")
    return sorted(pages)


def pages_from_report(report_path: Path, flags: set[str], max_pages: int | None) -> list[int]:
    data = json.loads(report_path.read_text(encoding="utf-8"))
    pages = []
    for page in data.get("pages", []):
        page_flags = set(page.get("flags", []))
        if not flags or page_flags.intersection(flags):
            pages.append(int(page["page"]))
    pages = sorted(dict.fromkeys(pages))
    if max_pages is not None:
        pages = pages[:max_pages]
    if not pages:
        raise ValueError("No pages matched the requested report flags.")
    return pages


def render_with_pymupdf(pdf: Path, out_dir: Path, pages: list[int], dpi: int) -> list[Path]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is not installed.") from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    document = fitz.open(str(pdf))
    try:
        page_count = document.page_count
        for page_number in pages:
            if page_number < 1 or page_number > page_count:
                raise ValueError(f"Page {page_number} out of range 1-{page_count}.")
            page = document.load_page(page_number - 1)
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            output = out_dir / f"page-{page_number:03d}.png"
            pixmap.save(str(output))
            outputs.append(output)
    finally:
        document.close()
    return outputs


def render_with_pdftoppm(pdf: Path, out_dir: Path, pages: list[int], dpi: int) -> list[Path]:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("pdftoppm is not installed.")

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for page_number in pages:
        prefix = out_dir / f"page-{page_number:03d}"
        subprocess.run(
            [
                pdftoppm,
                "-png",
                "-r",
                str(dpi),
                "-f",
                str(page_number),
                "-l",
                str(page_number),
                "-singlefile",
                str(pdf),
                str(prefix),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        output = prefix.with_suffix(".png")
        if not output.exists():
            raise RuntimeError(f"pdftoppm did not create {output}")
        outputs.append(output)
    return outputs


def choose_pages(args: argparse.Namespace) -> list[int]:
    pages = []
    if args.pages:
        pages.extend(parse_pages(args.pages))
    if args.from_report:
        pages.extend(pages_from_report(args.from_report, set(args.flag), args.max_pages))
    if not pages:
        pages = [1]
    pages = sorted(dict.fromkeys(pages))
    if args.max_pages is not None:
        pages = pages[: args.max_pages]
    return pages


def write_manifest(path: Path | None, pdf: Path, pages: list[int], outputs: list[Path], engine: str, dpi: int) -> None:
    if not path:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {
        "source": str(pdf),
        "engine": engine,
        "dpi": dpi,
        "pages": pages,
        "outputs": [str(output) for output in outputs],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="PDF file to render")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory for rendered PNG pages")
    parser.add_argument("--pages", help="Pages to render, e.g. 1,3,8-10")
    parser.add_argument("--from-report", type=Path, help="JSON report from inspect_pdf_source.py")
    parser.add_argument("--flag", action="append", default=[], help="Report flag to render, repeatable")
    parser.add_argument("--max-pages", type=int, help="Maximum pages to render")
    parser.add_argument("--dpi", type=int, default=160, help="Render DPI")
    parser.add_argument("--manifest-out", type=Path, help="Write render manifest JSON")
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")

    pages = choose_pages(args)

    try:
        outputs = render_with_pymupdf(args.pdf, args.out_dir, pages, args.dpi)
        engine = "pymupdf"
    except Exception as pymupdf_error:
        try:
            outputs = render_with_pdftoppm(args.pdf, args.out_dir, pages, args.dpi)
            engine = "pdftoppm"
        except Exception as poppler_error:
            raise SystemExit(
                "No PDF rendering backend is available. Install PyMuPDF with "
                "`python -m pip install pymupdf` or install Poppler (`pdftoppm`). "
                f"PyMuPDF error: {pymupdf_error}; pdftoppm error: {poppler_error}"
            ) from poppler_error

    write_manifest(args.manifest_out, args.pdf, pages, outputs, engine, args.dpi)
    print(f"Rendered {len(outputs)} page(s) with {engine}:")
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

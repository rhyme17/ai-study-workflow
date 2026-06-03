#!/usr/bin/env python3
"""Inspect a course PDF before using it in an AI study workflow."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


LOGIC_SYMBOLS = {
    "\uf0d9": "private-use logical-and candidate",
    "\uf0da": "private-use logical-or candidate",
    "\uf0ae": "private-use arrow candidate",
    "\uf0de": "private-use implication candidate",
    "": "logical-and glyph",
    "": "logical-or glyph",
    "": "right-arrow glyph",
    "": "double-arrow glyph",
    "": "negation glyph",
}


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def count_private_use(text: str) -> int:
    return sum(1 for ch in text if "\ue000" <= ch <= "\uf8ff")


def page_image_count(page: Any) -> int:
    try:
        resources = page.get("/Resources") or {}
        xobjects = resources.get("/XObject") or {}
        count = 0
        for obj in xobjects.values():
            resolved = obj.get_object()
            if resolved.get("/Subtype") == "/Image":
                count += 1
        return count
    except Exception:
        return 0


def inspect_pdf(path: Path, sparse_threshold: int) -> dict[str, Any]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise SystemExit("Missing dependency: install pypdf to inspect PDFs.") from exc

    reader = PdfReader(str(path))
    pages: list[dict[str, Any]] = []
    text_blocks: list[str] = []

    for index, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        text = normalize_ws(raw_text)
        private_count = count_private_use(raw_text)
        symbols = sorted({symbol for symbol in LOGIC_SYMBOLS if symbol in raw_text})
        image_count = page_image_count(page)
        flags = []
        if not text:
            flags.append("empty_text")
        if len(text) < sparse_threshold:
            flags.append("sparse_text")
        if private_count:
            flags.append("private_use_symbols")
        if symbols:
            flags.append("symbol_glyphs")
        if image_count and len(text) < sparse_threshold:
            flags.append("image_dependent")

        pages.append(
            {
                "page": index,
                "char_count": len(text),
                "image_count": image_count,
                "private_use_count": private_count,
                "symbol_glyphs": symbols,
                "flags": flags,
                "snippet": text[:240],
            }
        )
        text_blocks.append(f"--- PAGE {index:03d} chars={len(text)} images={image_count} ---\n{text}\n")

    empty_pages = [p["page"] for p in pages if "empty_text" in p["flags"]]
    sparse_pages = [p["page"] for p in pages if "sparse_text" in p["flags"]]
    private_pages = [p["page"] for p in pages if "private_use_symbols" in p["flags"]]
    image_dependent_pages = [p["page"] for p in pages if "image_dependent" in p["flags"]]

    return {
        "source": str(path),
        "page_count": len(pages),
        "sparse_threshold": sparse_threshold,
        "poppler": {
            "pdfinfo": bool(shutil.which("pdfinfo")),
            "pdftotext": bool(shutil.which("pdftotext")),
            "pdftoppm": bool(shutil.which("pdftoppm")),
        },
        "empty_page_count": len(empty_pages),
        "sparse_page_count": len(sparse_pages),
        "private_use_page_count": len(private_pages),
        "image_dependent_page_count": len(image_dependent_pages),
        "empty_pages": empty_pages,
        "sparse_pages": sparse_pages,
        "private_use_pages": private_pages,
        "image_dependent_pages": image_dependent_pages,
        "pages": pages,
        "extracted_text": "\n".join(text_blocks),
    }


def ranges(numbers: list[int]) -> str:
    if not numbers:
        return "none"
    groups: list[str] = []
    start = prev = numbers[0]
    for n in numbers[1:]:
        if n == prev + 1:
            prev = n
            continue
        groups.append(f"{start}" if start == prev else f"{start}-{prev}")
        start = prev = n
    groups.append(f"{start}" if start == prev else f"{start}-{prev}")
    return ", ".join(groups)


def render_markdown(data: dict[str, Any], max_list: int) -> str:
    poppler = data["poppler"]
    lines = [
        "# PDF Source Inspection",
        "",
        f"Source: `{data['source']}`",
        "",
        "## Summary",
        "",
        f"- Pages: {data['page_count']}",
        f"- Empty text pages: {data['empty_page_count']}",
        f"- Sparse text pages (< {data['sparse_threshold']} chars): {data['sparse_page_count']}",
        f"- Private-use / suspect symbol pages: {data['private_use_page_count']}",
        f"- Image-dependent sparse pages: {data['image_dependent_page_count']}",
        f"- Poppler available: pdfinfo={poppler['pdfinfo']}, pdftotext={poppler['pdftotext']}, pdftoppm={poppler['pdftoppm']}",
        "",
        "## Needs Human Check",
        "",
    ]
    if data["empty_pages"] or data["sparse_pages"] or data["private_use_pages"] or data["image_dependent_pages"]:
        lines.extend(
            [
                "- Some pages are `needs human check` before final answers, formula derivations, or Anki card backs.",
                f"- Empty text pages: {ranges(data['empty_pages'])}",
                f"- Sparse text pages: {ranges(data['sparse_pages'])}",
                f"- Suspect symbol pages: {ranges(data['private_use_pages'])}",
                f"- Image-dependent sparse pages: {ranges(data['image_dependent_pages'])}",
            ]
        )
    else:
        lines.append("- No extraction quality flags were detected.")

    lines.extend(
        [
            "",
            "## Page Samples",
            "",
            "| Page | Chars | Images | Flags | Snippet |",
            "| ---: | ---: | ---: | --- | --- |",
        ]
    )
    flagged = [page for page in data["pages"] if page["flags"]]
    sample_pages = flagged[:max_list] if flagged else data["pages"][:max_list]
    for page in sample_pages:
        snippet = page["snippet"].replace("|", "\\|")
        flags = ", ".join(page["flags"]) or "none"
        lines.append(f"| {page['page']} | {page['char_count']} | {page['image_count']} | {flags} | {snippet} |")
    return "\n".join(lines) + "\n"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {k: v for k, v in data.items() if k != "extracted_text"}
    path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="PDF file to inspect")
    parser.add_argument("--json-out", type=Path, help="Write structured inspection JSON")
    parser.add_argument("--markdown-out", type=Path, help="Write human-readable Markdown report")
    parser.add_argument("--text-out", type=Path, help="Write extracted per-page text")
    parser.add_argument("--sparse-threshold", type=int, default=80, help="Character count below which a page is sparse")
    parser.add_argument("--max-list", type=int, default=40, help="Maximum flagged page samples in Markdown")
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")

    data = inspect_pdf(args.pdf, args.sparse_threshold)

    if args.json_out:
        write_json(args.json_out, data)
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(render_markdown(data, args.max_list), encoding="utf-8")
    if args.text_out:
        args.text_out.parent.mkdir(parents=True, exist_ok=True)
        args.text_out.write_text(data["extracted_text"], encoding="utf-8")

    print(render_markdown(data, min(args.max_list, 20)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

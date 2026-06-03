#!/usr/bin/env python3
"""Render selected PPTX slides to PNG for visual inspection."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def parse_slides(spec: str) -> list[int]:
    slides: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise ValueError(f"Invalid slide range: {part}")
            slides.update(range(start, end + 1))
        else:
            slides.add(int(part))
    if not slides:
        raise ValueError("No slides selected.")
    return sorted(slides)


def slides_from_report(report_path: Path, flags: set[str], max_slides: int | None) -> list[int]:
    data = json.loads(report_path.read_text(encoding="utf-8"))
    slides = []
    for slide in data.get("slides", []):
        slide_flags = set(slide.get("flags", []))
        if not flags or slide_flags.intersection(flags):
            slides.append(int(slide["slide"]))
    slides = sorted(dict.fromkeys(slides))
    if max_slides is not None:
        slides = slides[:max_slides]
    if not slides:
        raise ValueError("No slides matched the requested report flags.")
    return slides


def choose_slides(args: argparse.Namespace) -> list[int]:
    slides = []
    if args.slides:
        slides.extend(parse_slides(args.slides))
    if args.from_report:
        slides.extend(slides_from_report(args.from_report, set(args.flag), args.max_slides))
    if not slides:
        slides = [1]
    slides = sorted(dict.fromkeys(slides))
    if args.max_slides is not None:
        slides = slides[: args.max_slides]
    return slides


def render_with_powerpoint(pptx: Path, out_dir: Path, slides: list[int], width: int, height: int) -> list[Path]:
    if platform.system() != "Windows":
        raise RuntimeError("PowerPoint COM rendering is only available on Windows.")

    out_dir.mkdir(parents=True, exist_ok=True)
    commands = [
        "$ErrorActionPreference = 'Stop'",
        f"$pptx = {json.dumps(str(pptx.resolve()))}",
        f"$outDir = {json.dumps(str(out_dir.resolve()))}",
        f"$slides = @({','.join(str(s) for s in slides)})",
        f"$width = {width}",
        f"$height = {height}",
        "$app = New-Object -ComObject PowerPoint.Application",
        "$presentation = $null",
        "try {",
        "  $presentation = $app.Presentations.Open($pptx, $true, $true, $false)",
        "  foreach ($slideNum in $slides) {",
        "    if ($slideNum -lt 1 -or $slideNum -gt $presentation.Slides.Count) { throw \"Slide $slideNum out of range\" }",
        "    $output = Join-Path $outDir ('slide-{0:D3}.png' -f $slideNum)",
        "    $presentation.Slides.Item($slideNum).Export($output, 'PNG', $width, $height)",
        "  }",
        "} finally {",
        "  if ($presentation -ne $null) { $presentation.Close() }",
        "  $app.Quit()",
        "}",
    ]
    script = "; ".join(commands)
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=True,
        capture_output=True,
        text=True,
    )
    outputs = [out_dir / f"slide-{slide:03d}.png" for slide in slides]
    missing = [str(path) for path in outputs if not path.exists()]
    if missing:
        raise RuntimeError(f"PowerPoint did not create: {', '.join(missing)}")
    return outputs


def render_with_libreoffice(pptx: Path, out_dir: Path, slides: list[int], dpi: int) -> list[Path]:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("LibreOffice is not installed.")
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for LibreOffice PDF rendering.") from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pptx-render-") as tmp:
        tmp_dir = Path(tmp)
        subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(tmp_dir),
                str(pptx),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        pdfs = sorted(tmp_dir.glob("*.pdf"))
        if not pdfs:
            raise RuntimeError("LibreOffice did not create a PDF.")
        document = fitz.open(str(pdfs[0]))
        outputs = []
        try:
            for slide in slides:
                if slide < 1 or slide > document.page_count:
                    raise ValueError(f"Slide {slide} out of range 1-{document.page_count}.")
                page = document.load_page(slide - 1)
                pixmap = page.get_pixmap(dpi=dpi, alpha=False)
                output = out_dir / f"slide-{slide:03d}.png"
                pixmap.save(str(output))
                outputs.append(output)
        finally:
            document.close()
    return outputs


def write_manifest(manifest_out: Path, pptx: Path, backend: str, outputs: list[Path]) -> None:
    manifest = {
        "source": str(pptx),
        "backend": backend,
        "slides": [{"slide": int(path.stem.split("-")[-1]), "path": str(path)} for path in outputs],
    }
    manifest_out.parent.mkdir(parents=True, exist_ok=True)
    manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--slides", help="Slide list such as 1,3,5-7.")
    parser.add_argument("--from-report", type=Path)
    parser.add_argument("--flag", action="append", default=[], help="Flag from inspect_pptx_source.py JSON.")
    parser.add_argument("--max-slides", type=int)
    parser.add_argument("--out-dir", type=Path, default=Path("rendered-slides"))
    parser.add_argument("--manifest-out", type=Path)
    parser.add_argument("--backend", choices=["auto", "powerpoint", "libreoffice"], default="auto")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()

    if not args.pptx.exists():
        raise SystemExit(f"File not found: {args.pptx}")
    if args.pptx.suffix.lower() != ".pptx":
        raise SystemExit("Expected a .pptx file.")

    slides = choose_slides(args)
    errors = []

    if args.backend in {"auto", "powerpoint"}:
        try:
            outputs = render_with_powerpoint(args.pptx, args.out_dir, slides, args.width, args.height)
            backend = "powerpoint"
        except Exception as exc:
            if args.backend == "powerpoint":
                raise
            errors.append(f"powerpoint: {exc}")
        else:
            if args.manifest_out:
                write_manifest(args.manifest_out, args.pptx, backend, outputs)
            print(json.dumps({"backend": backend, "outputs": [str(p) for p in outputs]}, ensure_ascii=False, indent=2))
            return

    if args.backend in {"auto", "libreoffice"}:
        try:
            outputs = render_with_libreoffice(args.pptx, args.out_dir, slides, args.dpi)
            backend = "libreoffice"
        except Exception as exc:
            if args.backend == "libreoffice":
                raise
            errors.append(f"libreoffice: {exc}")
        else:
            if args.manifest_out:
                write_manifest(args.manifest_out, args.pptx, backend, outputs)
            print(json.dumps({"backend": backend, "outputs": [str(p) for p in outputs]}, ensure_ascii=False, indent=2))
            return

    raise SystemExit("No PPTX rendering backend succeeded: " + "; ".join(errors))


if __name__ == "__main__":
    main()

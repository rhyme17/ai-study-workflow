#!/usr/bin/env python3
"""Inspect a course PPTX before using it in an AI study workflow."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


TEXT_NS = ".//{http://schemas.openxmlformats.org/drawingml/2006/main}t"
PIC_NS = ".//{http://schemas.openxmlformats.org/presentationml/2006/main}pic"
GRAPHIC_FRAME_NS = ".//{http://schemas.openxmlformats.org/presentationml/2006/main}graphicFrame"
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
GLYPH_FIXES = {
    "※": '"',
    "§": '"',
    "＊": "'",
    "＃": "",
}


def normalize_ws(text: str) -> str:
    for old, new in GLYPH_FIXES.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip()


def natural_slide_key(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def extract_text(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ""
    chunks = [node.text or "" for node in root.findall(TEXT_NS)]
    return normalize_ws(" ".join(chunks))


def count_nodes(xml_bytes: bytes, pattern: str) -> int:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return 0
    return len(root.findall(pattern))


def relationship_targets(zf: zipfile.ZipFile, slide_number: int) -> list[str]:
    rel_path = f"ppt/slides/_rels/slide{slide_number}.xml.rels"
    if rel_path not in zf.namelist():
        return []
    try:
        root = ET.fromstring(zf.read(rel_path))
    except ET.ParseError:
        return []
    targets = []
    for rel in root.findall(REL_NS):
        target = rel.attrib.get("Target", "")
        rel_type = rel.attrib.get("Type", "")
        if "image" in rel_type or "media" in rel_type or "video" in rel_type:
            targets.append(target)
    return targets


def note_text(zf: zipfile.ZipFile, slide_number: int) -> str:
    note_path = f"ppt/notesSlides/notesSlide{slide_number}.xml"
    if note_path not in zf.namelist():
        return ""
    return extract_text(zf.read(note_path))


def topic_guess(text: str, max_len: int) -> str:
    text = normalize_ws(text)
    if not text:
        return ""
    stop_prefixes = ("Chapter", "Computer Networking", "A note on the use")
    sentences = re.split(r"(?<=[.!?])\s+|\s{2,}", text)
    for sentence in sentences:
        sentence = sentence.strip(" -:\t")
        if sentence and not sentence.startswith(stop_prefixes):
            return sentence[:max_len]
    return text[:max_len]


def inspect_pptx(path: Path, sparse_threshold: int, media_threshold: int, topic_len: int) -> dict[str, Any]:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        slide_names = sorted(
            [name for name in names if re.match(r"ppt/slides/slide\d+\.xml$", name)],
            key=natural_slide_key,
        )
        media_names = [name for name in names if name.startswith("ppt/media/")]
        notes_names = [name for name in names if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", name)]

        slides: list[dict[str, Any]] = []
        text_blocks: list[str] = []

        for slide_name in slide_names:
            slide_number = natural_slide_key(slide_name)
            xml_bytes = zf.read(slide_name)
            text = extract_text(xml_bytes)
            notes = note_text(zf, slide_number)
            pic_count = count_nodes(xml_bytes, PIC_NS)
            graphic_count = count_nodes(xml_bytes, GRAPHIC_FRAME_NS)
            media_targets = relationship_targets(zf, slide_number)
            char_count = len(text)
            notes_char_count = len(notes)

            flags = []
            if not text:
                flags.append("empty_text")
            if char_count < sparse_threshold:
                flags.append("sparse_text")
            has_visual = bool(pic_count or media_targets or graphic_count)
            if pic_count >= media_threshold or len(media_targets) >= media_threshold:
                flags.append("image_heavy")
            elif char_count < sparse_threshold and has_visual:
                flags.append("image_heavy")
            if graphic_count:
                flags.append("graphic_content")
            if notes and notes_char_count > char_count:
                flags.append("notes_important")

            slides.append(
                {
                    "slide": slide_number,
                    "char_count": char_count,
                    "notes_char_count": notes_char_count,
                    "picture_count": pic_count,
                    "media_target_count": len(media_targets),
                    "graphic_count": graphic_count,
                    "flags": flags,
                    "topic": topic_guess(text, topic_len),
                    "snippet": text[:240],
                    "notes_snippet": notes[:240],
                }
            )
            text_blocks.append(
                "\n".join(
                    [
                        f"--- SLIDE {slide_number:03d} chars={char_count} notes={notes_char_count} pictures={pic_count} media={len(media_targets)} graphics={graphic_count} ---",
                        text,
                        f"NOTES: {notes}" if notes else "NOTES:",
                        "",
                    ]
                )
            )

    sparse_slides = [s["slide"] for s in slides if "sparse_text" in s["flags"]]
    image_heavy_slides = [s["slide"] for s in slides if "image_heavy" in s["flags"]]
    graphic_slides = [s["slide"] for s in slides if "graphic_content" in s["flags"]]
    notes_important_slides = [s["slide"] for s in slides if "notes_important" in s["flags"]]

    return {
        "source": str(path),
        "slide_count": len(slides),
        "notes_count": len(notes_names),
        "media_count": len(media_names),
        "sparse_threshold": sparse_threshold,
        "media_threshold": media_threshold,
        "sparse_slide_count": len(sparse_slides),
        "image_heavy_slide_count": len(image_heavy_slides),
        "graphic_slide_count": len(graphic_slides),
        "notes_important_slide_count": len(notes_important_slides),
        "sparse_slides": sparse_slides,
        "image_heavy_slides": image_heavy_slides,
        "graphic_slides": graphic_slides,
        "notes_important_slides": notes_important_slides,
        "slides": slides,
        "extracted_text": "\n".join(text_blocks),
    }


def ranges(numbers: list[int]) -> str:
    if not numbers:
        return "none"
    out = []
    start = prev = numbers[0]
    for number in numbers[1:]:
        if number == prev + 1:
            prev = number
            continue
        out.append(f"{start}-{prev}" if start != prev else str(start))
        start = prev = number
    out.append(f"{start}-{prev}" if start != prev else str(start))
    return ", ".join(out)


def markdown_report(data: dict[str, Any]) -> str:
    topic_lines = []
    for slide in data["slides"]:
        if slide["topic"]:
            topic_lines.append(f"- slide {slide['slide']}: {slide['topic']}")
    topic_preview = "\n".join(topic_lines[:40]) or "- no text topics detected"

    return f"""# PPTX Source Inspection

Source: `{data['source']}`

## Summary

- slides: {data['slide_count']}
- notes slides: {data['notes_count']}
- media files: {data['media_count']}
- sparse text slides: {data['sparse_slide_count']} ({ranges(data['sparse_slides'])})
- image-heavy slides: {data['image_heavy_slide_count']} ({ranges(data['image_heavy_slides'])})
- graphic-content slides: {data['graphic_slide_count']} ({ranges(data['graphic_slides'])})
- notes-important slides: {data['notes_important_slide_count']} ({ranges(data['notes_important_slides'])})

## Topic Preview

{topic_preview}

## Workflow Notes

- Treat sparse, image-heavy, and graphic-content slides as `needs human check` until rendered or visually inspected.
- Use speaker notes when `notes_important` is flagged; notes may contain instructor emphasis not visible on the slide.
- For exam review, confirm whether appendix/additional slides are in scope before prioritizing them.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--sparse-threshold", type=int, default=80)
    parser.add_argument("--media-threshold", type=int, default=4)
    parser.add_argument("--topic-len", type=int, default=120)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--text-out", type=Path)
    args = parser.parse_args()

    if not args.pptx.exists():
        raise SystemExit(f"File not found: {args.pptx}")
    if args.pptx.suffix.lower() != ".pptx":
        raise SystemExit("Expected a .pptx file.")

    data = inspect_pptx(args.pptx, args.sparse_threshold, args.media_threshold, args.topic_len)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown_report(data), encoding="utf-8")
    if args.text_out:
        args.text_out.parent.mkdir(parents=True, exist_ok=True)
        args.text_out.write_text(data["extracted_text"], encoding="utf-8")

    print(markdown_report(data))


if __name__ == "__main__":
    main()

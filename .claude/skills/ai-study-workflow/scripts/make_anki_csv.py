#!/usr/bin/env python3
"""Convert JSON or JSONL study cards into an Anki-ready CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


FIELDS = ["Deck", "Tags", "Type", "Front", "Back", "Source"]


def load_cards(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    data = json.loads(text)
    if isinstance(data, dict) and "cards" in data:
        data = data["cards"]
    if not isinstance(data, list):
        raise ValueError("Input must be a JSON list, a {'cards': [...]} object, or JSONL.")
    return data


def normalize_card(card: dict[str, Any], default_deck: str) -> dict[str, str]:
    front = str(card.get("front", "")).strip()
    back = str(card.get("back", "")).strip()
    if not front or not back:
        raise ValueError("Each card must include non-empty 'front' and 'back' fields.")

    tags = card.get("tags", "")
    if isinstance(tags, list):
        tags = " ".join(str(tag).strip().replace(" ", "_") for tag in tags if str(tag).strip())

    return {
        "Deck": str(card.get("deck") or default_deck),
        "Tags": str(tags),
        "Type": str(card.get("type") or "basic"),
        "Front": front,
        "Back": back,
        "Source": str(card.get("source", "")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON or JSONL card file")
    parser.add_argument("--out", type=Path, required=True, help="Output CSV path")
    parser.add_argument("--deck", default="Course::Study", help="Default Anki deck name")
    args = parser.parse_args()

    cards = [normalize_card(card, args.deck) for card in load_cards(args.input)]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(cards)

    print(f"Wrote {len(cards)} cards to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

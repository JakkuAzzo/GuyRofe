#!/usr/bin/env python3
"""
Extract readable prose from a Wix page JSON dump.

Usage:
  python scripts/extract_wix_prose.py \
      --input guy/page-data/121-collective-community-brain.json \
      --output guy/page-data/121-collective-community-brain.prose.md

Heuristic approach: recursively traverse the JSON, collect human-readable strings
while filtering out URLs, image keys, css-like values, ids, and very short tokens.
Preserves first-seen order and de-duplicates exact matches.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any, Iterable, Set, List


URL_RE = re.compile(r"^https?://", re.I)
CSS_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{3,8}$")
MIME_LIKE_RE = re.compile(r"^[a-z]+/[a-z0-9+.-]+$", re.I)
ID_LIKE_RE = re.compile(r"^[A-Za-z0-9_-]{6,}$")
MOSTLY_NON_ALPHA_RE = re.compile(r"^[^A-Za-z]{0,}$")

EXCLUDE_KEYS = {
    # Obviously non-prose keys.
    "url", "href", "src", "image", "images", "video", "media",
    "style", "styles", "css", "className", "class", "id", "compId",
    "pageId", "applicationId", "appDefinitionId", "componentType",
    "responsive", "theme", "fonts", "colors", "hex", "alpha",
}

MIN_LEN = 20  # heuristic minimum length to consider a string as prose


def is_prose(s: str) -> bool:
    s_strip = s.strip()
    if len(s_strip) < MIN_LEN:
        return False
    if URL_RE.search(s_strip):
        return False
    if CSS_HEX_RE.match(s_strip):
        return False
    if MIME_LIKE_RE.match(s_strip):
        return False
    # Skip strings that are mostly non-letters (e.g., ids, hashes)
    alpha_ratio = sum(c.isalpha() for c in s_strip) / max(1, len(s_strip))
    if alpha_ratio < 0.4:
        return False
    return True


def walk(node: Any, out: List[str], seen: Set[str], parent_key: str | None = None) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            # Skip large non-prose branches by key
            if isinstance(k, str) and k in EXCLUDE_KEYS:
                continue
            walk(v, out, seen, k)
    elif isinstance(node, list):
        for v in node:
            walk(v, out, seen, parent_key)
    elif isinstance(node, str):
        if is_prose(node) and node not in seen:
            seen.add(node)
            out.append(node)
    # else: ignore numbers, booleans, None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to Wix page JSON file")
    ap.add_argument("--output", required=True, help="Path to write extracted prose (Markdown)")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    out: List[str] = []
    seen: Set[str] = set()
    walk(data, out, seen)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for para in out:
            f.write(para.strip())
            f.write("\n\n")

    print(f"Extracted {len(out)} paragraph(s) to {args.output}")


if __name__ == "__main__":
    main()

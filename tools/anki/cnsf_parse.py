#!/usr/bin/env python3
"""
CNSF v0 parser

Parses a single CNSF note markdown file:
- YAML front matter (required)
- two required sections: "# front_md" and "# back_md"
Returns:
- meta: dict
- front_md: str
- back_md: str
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import re

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: PyYAML. Install with: pip install pyyaml"
    ) from e


_FRONT_RE = re.compile(r"(?mi)^\s*#\s*front_md\s*$")
_BACK_RE = re.compile(r"(?mi)^\s*#\s*back_md\s*$")


@dataclass(frozen=True)
class CNSFNote:
    path: Path
    meta: dict[str, Any]
    front_md: str
    back_md: str


def _split_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    if not text.lstrip().startswith("---"):
        raise ValueError(f"{path}: missing YAML front matter (expected starting '---').")

    # front matter must be the first block: --- ... ---
    m = re.match(r"(?s)^\s*---\s*\n(.*?)\n---\s*\n(.*)$", text)
    if not m:
        raise ValueError(f"{path}: malformed YAML front matter block.")

    yml, rest = m.group(1), m.group(2)
    meta = yaml.safe_load(yml) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: YAML front matter must be a mapping/object.")
    return meta, rest


def _split_sections(body: str, path: Path) -> tuple[str, str]:
    m_front = _FRONT_RE.search(body)
    m_back = _BACK_RE.search(body)

    if not m_front or not m_back:
        raise ValueError(f"{path}: must contain both '# front_md' and '# back_md' sections.")
    if m_back.start() < m_front.start():
        raise ValueError(f"{path}: '# back_md' must come after '# front_md'.")

    front_start = m_front.end()
    back_start = m_back.end()

    front_md = body[front_start:m_back.start()].strip("\n")
    back_md = body[back_start:].strip("\n")

    if not front_md.strip():
        raise ValueError(f"{path}: front_md section is empty.")
    if not back_md.strip():
        raise ValueError(f"{path}: back_md section is empty.")

    return front_md.strip() + "\n", back_md.strip() + "\n"


def load_cnsf_note(path: str | Path) -> CNSFNote:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    meta, body = _split_frontmatter(text, p)
    front_md, back_md = _split_sections(body, p)

    # Minimum required keys (schema-level)
    schema = (meta.get("schema") or "").strip()
    if schema != "cnsf/v0":
        raise ValueError(f"{p}: schema must be 'cnsf/v0' (found: {schema!r}).")

    note_id = (meta.get("note_id") or "").strip()
    if not note_id:
        raise ValueError(f"{p}: YAML must include note_id.")
    if "-" in note_id:
        raise ValueError(f"{p}: note_id must use underscores only (no hyphens): {note_id!r}")

    return CNSFNote(path=p, meta=meta, front_md=front_md, back_md=back_md)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Parse a CNSF note and print basic info.")
    ap.add_argument("path", help="Path to CNSF note markdown file")
    args = ap.parse_args()

    note = load_cnsf_note(args.path)
    print(f"OK: {note.path}")
    print(f"note_id: {note.meta.get('note_id')}")
    print(f"anki.model: {((note.meta.get('anki') or {}).get('model') if isinstance(note.meta.get('anki'), dict) else None)}")
    print(f"front_md chars: {len(note.front_md)}")
    print(f"back_md  chars: {len(note.back_md)}")


if __name__ == "__main__":
    main()

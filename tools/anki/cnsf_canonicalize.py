#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


CANON_TOP_KEYS = [
    "schema",
    "domain",
    "note_type",
    "note_id",
    "anki",
    "tags",
    "fields",
]

CANON_ANKI_KEYS = ["model", "deck"]


@dataclass(frozen=True)
class SplitFM:
    yaml_text: str
    body_text: str


def split_frontmatter(text: str, path: Path) -> SplitFM:
    """
    Expect file to start with:
      ---
      <yaml>
      ---
    """
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing YAML front matter (expected leading ---).")

    # find second '---' line (front matter end)
    # Accept --- on its own line; keep everything after as body.
    m = re.search(r"(?m)^\s*---\s*$", text)
    if not m:
        raise ValueError(f"{path}: missing YAML start delimiter '---'.")

    # find end delimiter after start
    m2 = re.search(r"(?m)^\s*---\s*$", text[m.end() :])
    if not m2:
        raise ValueError(f"{path}: missing YAML end delimiter '---'.")

    start = m.end()
    end = m.end() + m2.start()
    yaml_text = text[start:end].strip("\n")
    body_text = text[m.end() + m2.end() :].lstrip("\n")
    return SplitFM(yaml_text=yaml_text, body_text=body_text)


def _top_level_key_order(yaml_text: str) -> list[str]:
    """
    Best-effort top-level key order parser (only keys at column 0).
    """
    keys: list[str] = []
    for line in yaml_text.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue
        if line.startswith(" "):
            continue
        # key:
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", line)
        if m:
            keys.append(m.group(1))
    return keys


def _normalize_meta(meta: dict[str, Any], path: Path) -> dict[str, Any]:
    """
    Normalize known CNSF keys and coerce obvious legacy variants.
    """
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: YAML must be a mapping/object at top level.")

    # Legacy/accidental variants we’ve already seen:
    # - max8 file had stray 'source:' mapping; we fold it into fields.Source Document when possible.
    if "source" in meta and isinstance(meta.get("source"), dict):
        src = meta["source"]
        # If source.document exists and fields doesn't already provide Source Document, set it.
        doc = src.get("document")
        if doc:
            fields = meta.get("fields")
            if fields is None or not isinstance(fields, dict):
                fields = {}
                meta["fields"] = fields
            fields.setdefault("Source Document", doc)
        # remove legacy 'source'
        meta.pop("source", None)

    # Ensure schema is present and correct (do not “fix” silently)
    schema = (meta.get("schema") or "").strip()
    if schema != "cnsf/v0":
        raise ValueError(f"{path}: schema must be 'cnsf/v0' (found: {schema!r}).")

    # Enforce underscore note_id grammar
    note_id = (meta.get("note_id") or "").strip()
    if not note_id:
        raise ValueError(f"{path}: YAML must include note_id.")
    if "-" in note_id:
        raise ValueError(f"{path}: note_id must use underscores only (no hyphens): {note_id!r}")

    # Normalize anki mapping
    anki = meta.get("anki")
    if anki is None:
        raise ValueError(f"{path}: YAML missing required key: anki")
    if not isinstance(anki, dict):
        raise ValueError(f"{path}: YAML key 'anki' must be a mapping/object.")
    # Require model and deck keys (again: don’t auto-invent)
    if not (anki.get("model") and anki.get("deck")):
        raise ValueError(f"{path}: anki must include 'model' and 'deck'.")

    # Normalize tags to list[str]
    tags = meta.get("tags")
    if tags is None:
        raise ValueError(f"{path}: YAML missing required key: tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        raise ValueError(f"{path}: tags must be a list of strings.")

    # Normalize fields to mapping (optional but recommended; we treat as required in CNSF v0)
    fields = meta.get("fields")
    if fields is None:
        raise ValueError(f"{path}: YAML missing required key: fields")
    if not isinstance(fields, dict):
        raise ValueError(f"{path}: fields must be a mapping/object.")
    # Optional: ensure the known field names exist (allow extensions)
    fields.setdefault("Verification Notes", "")

    return meta


def canonicalize_meta(meta: dict[str, Any], path: Path) -> dict[str, Any]:
    """
    Produce a new dict with canonical key order and canonical sub-order.
    """
    meta = _normalize_meta(dict(meta), path)

    # Canonicalize nested anki order
    anki = meta.get("anki")
    assert isinstance(anki, dict)
    anki_canon: dict[str, Any] = {}
    for k in CANON_ANKI_KEYS:
        if k in anki:
            anki_canon[k] = anki[k]
    # preserve any extra anki keys after the canonical ones
    for k in anki.keys():
        if k not in anki_canon:
            anki_canon[k] = anki[k]
    meta["anki"] = anki_canon

    # Canonicalize top-level order
    out: dict[str, Any] = {}
    for k in CANON_TOP_KEYS:
        if k in meta:
            out[k] = meta[k]
    # Preserve any extension keys after canonical ones
    for k in meta.keys():
        if k not in out:
            out[k] = meta[k]

    return out


def dump_yaml(meta: dict[str, Any]) -> str:
    """
    Deterministic-ish YAML dump (order preserved, no sort_keys).
    """
    return yaml.safe_dump(
        meta,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=88,
    ).strip("\n")


def canonicalized_file_text(path: Path) -> tuple[str, dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    fm = split_frontmatter(text, path)
    meta = yaml.safe_load(fm.yaml_text) or {}
    meta_c = canonicalize_meta(meta, path)
    y = dump_yaml(meta_c)
    new_text = f"---\n{y}\n---\n\n{fm.body_text}"
    return new_text, meta_c


def cmd_check(paths: list[Path]) -> int:
    bad = 0
    for p in paths:
        new_text, _ = canonicalized_file_text(p)
        old_text = p.read_text(encoding="utf-8")
        if new_text != old_text:
            # specifically detect “order drift” at top-level
            fm = split_frontmatter(old_text, p)
            old_order = _top_level_key_order(fm.yaml_text)
            if old_order != [k for k in CANON_TOP_KEYS if k in old_order]:
                print(f"FAIL (YAML order drift): {p}")
            else:
                print(f"FAIL (canonicalization drift): {p}")
            bad += 1
    return 1 if bad else 0


def cmd_write(paths: list[Path]) -> int:
    changed = 0
    for p in paths:
        new_text, _ = canonicalized_file_text(p)
        old_text = p.read_text(encoding="utf-8")
        if new_text != old_text:
            p.write_text(new_text, encoding="utf-8")
            print(f"FIXED: {p}")
            changed += 1
        else:
            print(f"OK: {p}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Canonicalize CNSF v0 YAML front matter (order + normalization).")
    ap.add_argument("paths", nargs="+", help="One or more CNSF .md note files")
    ap.add_argument("--check", action="store_true", help="Fail if any file would change")
    ap.add_argument("--write", action="store_true", help="Rewrite files in-place")
    args = ap.parse_args()

    if args.check == args.write:
        raise SystemExit("Choose exactly one of --check or --write.")

    paths = [Path(p) for p in args.paths]
    for p in paths:
        if not p.exists():
            raise SystemExit(f"Not found: {p}")

    rc = cmd_check(paths) if args.check else cmd_write(paths)
    raise SystemExit(rc)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
L3 -> L4: Import TSV (HTML payload) -> Anki via AnkiConnect.

This script is intentionally minimal-first:
- Reads a TSV produced by tools/anki/export/cnsf_to_import_tsv.py
- For each row:
  - If noteId present: update existing note fields + tags
  - Else: create note and (optionally) append note_id<->noteId mapping

Later we will add:
- Strict schema validation against model field order
- Tag policy (add/remove) with idempotence
- Mapping file auto-detection per domain/note_type
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ANKI_CONNECT_URL_DEFAULT = "http://127.0.0.1:8765"


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def anki_request(action: str, params: Optional[dict] = None, url: str = ANKI_CONNECT_URL_DEFAULT) -> Any:
    payload = {"action": action, "version": 6, "params": params or {}}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect error for {action}: {data['error']}")
    return data.get("result")


@dataclass
class TsvRow:
    note_id: str
    noteId: str
    model: str
    deck: str
    tags: List[str]
    front_html: str
    back_html: str
    extra_fields: Dict[str, str]


def parse_tsv(path: Path) -> Tuple[List[str], List[TsvRow]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        header = list(reader.fieldnames or [])
        required = {"note_id", "noteId", "model", "deck", "tags", "front_html", "back_html"}
        missing = required - set(header)
        if missing:
            raise ValueError(f"Missing required TSV columns: {sorted(missing)}")

        rows: List[TsvRow] = []
        for r in reader:
            note_id = (r.get("note_id") or "").strip()
            if not note_id:
                continue

            tags_raw = (r.get("tags") or "").strip()
            tags = [t for t in tags_raw.split() if t]

            extra = {k: (r.get(k) or "") for k in header if k not in required}

            rows.append(
                TsvRow(
                    note_id=note_id,
                    noteId=(r.get("noteId") or "").strip(),
                    model=(r.get("model") or "").strip(),
                    deck=(r.get("deck") or "").strip(),
                    tags=tags,
                    front_html=(r.get("front_html") or ""),
                    back_html=(r.get("back_html") or ""),
                    extra_fields=extra,
                )
            )

    return header, rows


def build_fields_payload(row: TsvRow) -> Dict[str, str]:
    # For our current B737_Structured model, we assume:
    # NoteID, Front, Back are the canonical base fields.
    # Extra fields map by header name (e.g., Source Document).
    fields: Dict[str, str] = {
        "NoteID": row.note_id,
        "Front": row.front_html,
        "Back": row.back_html,
    }
    for k, v in row.extra_fields.items():
        # Keep exact Anki field names as columns.
        fields[k] = v
    return fields


def model_field_names(model_name: str, url: str) -> List[str]:
    # AnkiConnect: returns list of field names for a given model.
    return anki_request("modelFieldNames", {"modelName": model_name}, url=url) or []


def validate_fields_against_model(row: TsvRow, model_fields: List[str]) -> None:
    payload_fields = build_fields_payload(row)
    unknown = sorted([k for k in payload_fields.keys() if k not in set(model_fields)])
    if unknown:
        raise SystemExit(
            "FAIL: TSV contains field(s) not present in Anki model\n"
            f"  note_id: {row.note_id}\n"
            f"  model  : {row.model}\n"
            f"  unknown: {', '.join(unknown)}\n"
            "Hint: rename TSV columns to match Anki field names, or update the model in Anki."
        )


def update_note(row: TsvRow, url: str) -> None:
    note_id_num = int(row.noteId)
    fields = build_fields_payload(row)

    anki_request("updateNoteFields", {"note": {"id": note_id_num, "fields": fields}}, url=url)

    # For now: replace tags by clearing then adding (simple + deterministic).
    # (We can implement a smarter diff later.)
    current = anki_request("getNoteTags", {"note": note_id_num}, url=url) or []
    if current:
        anki_request("removeTags", {"notes": [note_id_num], "tags": " ".join(current)}, url=url)
    if row.tags:
        anki_request("addTags", {"notes": [note_id_num], "tags": " ".join(row.tags)}, url=url)


def create_note(row: TsvRow, url: str) -> int:
    fields = build_fields_payload(row)
    note = {
        "deckName": row.deck,
        "modelName": row.model,
        "fields": fields,
        "tags": row.tags,
        "options": {"allowDuplicate": False, "duplicateScope": "deck"},
    }
    new_id = anki_request("addNote", {"note": note}, url=url)
    return int(new_id)


def append_mapping(map_path: Path, note_id: str, noteId: int) -> None:
    map_path.parent.mkdir(parents=True, exist_ok=True)
    exists = map_path.exists()
    with map_path.open("a", encoding="utf-8", newline="") as f:
        if not exists:
            f.write("note_id\tnoteId\n")
        f.write(f"{note_id}\t{noteId}\n")


def read_noteid_map(map_path: Path) -> Dict[str, str]:
    """Read a mapping TSV with header: note_id \t noteId"""
    m: Dict[str, str] = {}
    if not map_path.exists():
        return m
    with map_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            nid = (row.get("note_id") or "").strip()
            aid = (row.get("noteId") or "").strip()
            if nid and aid:
                m[nid] = aid
    return m


def apply_noteid_map(rows: List[TsvRow], mapping: Dict[str, str]) -> int:
    """Fill row.noteId from mapping for any row missing noteId. Returns count applied."""
    applied = 0
    if not mapping:
        return applied
    for r in rows:
        if not r.noteId:
            hit = (mapping.get(r.note_id) or "").strip()
            if hit:
                r.noteId = hit
                applied += 1
    return applied
    for r in rows:
        # Validate field names against the target Anki model (cached per model).
        if r.model not in model_fields_cache:
            model_fields_cache[r.model] = model_field_names(r.model, url=args.anki_url)
        validate_fields_against_model(r, model_fields_cache[r.model])
        if not r.noteId:
            hit = mapping.get(r.note_id, "").strip()
            if hit:
                r.noteId = hit
                applied += 1
    return applied



def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", required=True, help="Path to L3 import TSV (HTML payload)")
    ap.add_argument("--anki-url", default=ANKI_CONNECT_URL_DEFAULT)
    ap.add_argument("--map-out", default="", help="Optional mapping TSV to append to on CREATE flows")
    ap.add_argument("--map-in", default="", help="Optional mapping TSV (note_id->noteId) to apply before sync")
    ap.add_argument("--dry-run", action="store_true", help="Parse + validate only; do not call AnkiConnect")
    ap.add_argument("--check", action="store_true", help="Validate TSV; fail if any row would CREATE (missing noteId); no AnkiConnect calls")
    args = ap.parse_args()

    tsv_path = Path(args.tsv)
    if not tsv_path.exists():
        eprint(f"TSV not found: {tsv_path}")
        return 2

    _, rows = parse_tsv(tsv_path)
    if not rows:
        eprint("No rows found.")
        return 2

    # Optional: fill missing noteId values from a mapping TSV (note_id -> noteId)
    if args.map_in:
        mapping = read_noteid_map(Path(args.map_in))
        applied = apply_noteid_map(rows, mapping)
        if applied:
            print(f"OK: map-in applied noteId for rows={applied}")

    if args.dry_run:
        print(f"OK: parsed rows={len(rows)} (dry-run)")
        return 0

    if args.check:
        missing = [r.note_id for r in rows if not r.noteId]
        if missing:
            eprint("FAIL: --check would CREATE (missing noteId) for:")
            for nid in missing:
                eprint(f"  - {nid}")
            return 1
        print(f"OK: check passed rows={len(rows)} (no creates)")
        return 0

    # Basic connectivity check
    anki_request("version", {}, url=args.anki_url)


    # Validate TSV field names against the target Anki model field names.
    # This requires AnkiConnect, so we do it only in the real sync path.
    model_fields_cache: Dict[str, List[str]] = {}
    for r in rows:
        if not r.model:
            raise SystemExit(f"Missing model for note_id={r.note_id}")
        if r.model not in model_fields_cache:
            model_fields_cache[r.model] = model_field_names(r.model, url=args.anki_url)
        validate_fields_against_model(r, model_fields_cache[r.model])


    model_fields_cache: Dict[str, List[str]] = {}
    created = 0
    updated = 0
    for r in rows:
        if r.noteId:
            update_note(r, url=args.anki_url)
            updated += 1
            print(f"OK: updated noteId {r.noteId} ({r.note_id})")
            continue

        # No noteId provided → attempt create; if duplicate, adopt existing by NoteID and update.
        try:
            nid = create_note(r, url=args.anki_url)
            created += 1
            print(f"OK: created noteId {nid} ({r.note_id})")
            if args.map_out:
                append_mapping(Path(args.map_out), r.note_id, nid)
        except RuntimeError as e:
            msg = str(e).lower()
            if "duplicate" not in msg:
                raise

            # Try to find an existing note by the stable CNSF note_id stored in the NoteID field.
            # Scope to model+deck to reduce false matches.
            query = f'note:"{r.model}" deck:"{r.deck}" NoteID:"{r.note_id}"'
            hits = anki_request("findNotes", {"query": query}, url=args.anki_url) or []

            if not hits:
                # Fall back to field-only search (in case deck/model naming differs).
                query2 = f'NoteID:"{r.note_id}"'
                hits = anki_request("findNotes", {"query": query2}, url=args.anki_url) or []

            if not hits:
                raise RuntimeError(
                    f"Duplicate on create for {r.note_id}, but could not find an existing note via NoteID search."
                ) from e

            adopted = int(hits[0])
            r.noteId = str(adopted)
            update_note(r, url=args.anki_url)
            updated += 1
            print(f"OK: adopted+updated existing noteId {adopted} ({r.note_id})")

            if args.map_out:
                append_mapping(Path(args.map_out), r.note_id, adopted)

    print(f"Done. updated={updated} created={created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

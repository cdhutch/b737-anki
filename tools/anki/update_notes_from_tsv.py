#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import urllib.request


DEFAULT_ANKI_URL = "http://127.0.0.1:8765"


CANDIDATE_ANSWER_FIELDS = [
    # most common
    "Answer",
    "Back",
    "answer",
    "back",
    # your repo-ish variants seen earlier
    "answer_md",
    "answer_html",
    "Answer_md",
    "Answer_html",
    "Back_md",
    "Back_html",
]


def anki_request(action: str, params: dict[str, Any] | None = None, url: str = DEFAULT_ANKI_URL) -> dict[str, Any]:
    payload = {"action": action, "version": 6}
    if params is not None:
        payload["params"] = params

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    out = json.loads(raw)

    # AnkiConnect convention: {"result": ..., "error": ...}
    if "error" not in out or "result" not in out:
        raise RuntimeError(f"Unexpected AnkiConnect response: {out}")
    if out["error"] is not None:
        raise RuntimeError(f"AnkiConnect error for action={action}: {out['error']}")
    return out


def read_import_html_tsv(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        required = {"note_id", "noteId", "prompt", "answer_html"}
        missing = required - set(rdr.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required TSV columns: {sorted(missing)} in {path}")
        for r in rdr:
            # skip blank lines
            if not any((v or "").strip() for v in r.values()):
                continue
            rows.append({k: (v or "") for k, v in r.items()})
    return rows


def choose_answer_field(note_fields: dict[str, Any], preferred: str | None) -> str:
    keys = list(note_fields.keys())

    if preferred:
        if preferred in note_fields:
            return preferred
        raise ValueError(f"--field {preferred!r} not present on note. Available: {keys}")

    for cand in CANDIDATE_ANSWER_FIELDS:
        if cand in note_fields:
            return cand

    # Fallback heuristic: if exactly 2 fields, pick the second as "answer/back"
    if len(keys) == 2:
        return keys[1]

    raise ValueError(
        "Could not auto-detect answer field. "
        f"Available fields: {keys}. "
        "Pass --field explicitly."
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Update Anki notes from a TSV containing noteId and answer_html.")
    ap.add_argument("--in", dest="inp", required=True, help="Input TSV (e.g. __import_html.tsv)")
    ap.add_argument("--anki-url", default=DEFAULT_ANKI_URL, help=f"AnkiConnect URL (default: {DEFAULT_ANKI_URL})")
    ap.add_argument("--field", default=None, help="Target Anki field name to update (default: auto-detect)")
    ap.add_argument("--dry-run", action="store_true", help="Do not write changes; just show what would happen")
    ap.add_argument("--limit", type=int, default=0, help="Only process first N rows (0 = all)")
    args = ap.parse_args()

    tsv_path = Path(args.inp)
    if not tsv_path.exists():
        raise FileNotFoundError(tsv_path)

    rows = read_import_html_tsv(tsv_path)
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    # Ensure AnkiConnect reachable
    try:
        ver = anki_request("version", url=args.anki_url)["result"]
    except Exception as e:
        print(f"ERROR: Unable to reach AnkiConnect at {args.anki_url}: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"AnkiConnect version: {ver}")
    print(f"Rows to process: {len(rows)}")

    # Fetch note info in one call
    note_ids = []
    for r in rows:
        nid = (r.get("noteId") or "").strip()
        if nid:
            note_ids.append(int(nid))
    info = anki_request("notesInfo", {"notes": note_ids}, url=args.anki_url)["result"]

    # Map noteId -> info
    info_map: dict[int, dict[str, Any]] = {int(n["noteId"]): n for n in info if n and "noteId" in n}

    updates: list[dict[str, Any]] = []
    skipped = 0

    for r in rows:
        # note_id = (r.get("note_id") or "").strip()
        # noteId_s = (r.get("noteId") or "").strip()
        # ans = r.get("answer_html", "")
        note_id = (r.get("note_id") or "").strip()
        noteId_s = (r.get("noteId") or "").strip()
        ans = (r.get("answer_html", "") or "").replace("\\n", "\n")


        if not noteId_s:
            print(f"SKIP (no noteId): {note_id}")
            skipped += 1
            continue

        noteId = int(noteId_s)
        ninfo = info_map.get(noteId)
        if not ninfo:
            print(f"SKIP (noteId not found in Anki): {note_id} ({noteId})")
            skipped += 1
            continue

        fields = ninfo.get("fields", {}) or {}
        try:
            target_field = choose_answer_field(fields, args.field)
        except Exception as e:
            print(f"SKIP (field detect error): {note_id} ({noteId}) -> {e}")
            skipped += 1
            continue

        # AnkiConnect expects dict of field -> string; HTML is fine.
        updates.append({"id": noteId, "fields": {target_field: ans}})

    print(f"Prepared updates: {len(updates)}")
    print(f"Skipped: {skipped}")

    if args.dry_run:
        # Show a small preview
        for u in updates[:3]:
            fid = u["id"]
            field_name = list(u["fields"].keys())[0]
            snippet = (u["fields"][field_name] or "")[:120].replace("\n", "\\n")
            print(f"DRY RUN: noteId={fid} field={field_name} value[:120]={snippet}")
        print("Dry-run complete (no changes sent).")
        return

    if not updates:
        print("Nothing to update.")
        return

    # Batch update
    # anki_request("updateNoteFields", {"note": updates}, url=args.anki_url)
    for note in updates:
        anki_request("updateNoteFields", {"note": note}, url=args.anki_url)
    print("✅ updateNoteFields complete (no error).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

HDR_RE = re.compile(r"^##\s+(\S+)\s*$")          # e.g., "## sys-elec-psc-010"
AFTER_RE = re.compile(r"^###\s+AFTER\s*$")       # "### AFTER"
SEP_RE = re.compile(r"^---\s*$")                 # note separator

def parse_notes(md_text: str) -> list[tuple[str, str]]:
    lines = md_text.splitlines()
    out: list[tuple[str, str]] = []

    cur_id: str | None = None
    in_after = False
    buf: list[str] = []

    def flush():
        nonlocal buf, cur_id
        if cur_id is None:
            return
        # Trim leading/trailing blank lines
        while buf and buf[0].strip() == "":
            buf.pop(0)
        while buf and buf[-1].strip() == "":
            buf.pop()
        # after = "\n".join(buf)
        # out.append((cur_id, after))
        # buf = []
        after = "\n".join(buf)
        if after.strip() != "":
            out.append((cur_id, after))
        buf = []

    i = 0
    while i < len(lines):
        line = lines[i]

        m = HDR_RE.match(line)
        # if m:
        #     # starting a new note
        #     if cur_id is not None:
        #         # flush previous note if we were collecting AFTER
        #         flush()
        #     cur_id = m.group(1)
        #     in_after = False
        #     buf = []
        #     i += 1
        #     continue

        if m:
            # starting a new note
            if cur_id is not None and in_after:
                flush()
            cur_id = m.group(1)
            in_after = False
            buf = []
            i += 1
            continue

        if AFTER_RE.match(line):
            in_after = True
            buf = []
            i += 1
            continue

        if SEP_RE.match(line):
            if cur_id is not None and in_after:
                flush()
            in_after = False
            i += 1
            continue

        if in_after:
            buf.append(line)

        i += 1

    # EOF flush
    if cur_id is not None and in_after:
        flush()

    return out

def tsv_escape_cell(s: str) -> str:
    # Keep it TSV-safe for robust editors/importers:
    # - replace tabs with spaces
    # - replace newlines with literal "\n" so each record stays on one row
    return s.replace("\t", " ").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input canonical markdown file")
    ap.add_argument("--out", dest="outp", required=True, help="Output TSV file")
    args = ap.parse_args()

    md_path = Path(args.inp)
    out_path = Path(args.outp)

    md_text = md_path.read_text(encoding="utf-8")
    notes = parse_notes(md_text)

    # Header + rows
    lines = ["note_id\tafter_md"]
    for note_id, after_md in notes:
        lines.append(f"{tsv_escape_cell(note_id)}\t{tsv_escape_cell(after_md)}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Rows: {len(notes)}")
    print(f"Output: {out_path}")

if __name__ == "__main__":
    main()

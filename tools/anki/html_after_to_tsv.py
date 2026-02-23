#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

# Matches: <h2 id="sys-elec-psc-010">sys-elec-psc-010</h2>
H2_RE = re.compile(r"<h2\b[^>]*>(?P<text>.*?)</h2>", re.IGNORECASE)

# AFTER header: <h3 id="after">AFTER</h3> (MultiMarkdown lowercases id)
AFTER_H3_RE = re.compile(r"<h3\b[^>]*>\s*AFTER\s*</h3>", re.IGNORECASE)

# Stop collecting at next <hr />, or next <h2>, or end
STOP_RE = re.compile(r"(<hr\s*/?>|<h2\b)", re.IGNORECASE)

def tsv_escape_cell(s: str) -> str:
    # keep one-row-per-record TSV
    s = s.replace("\t", " ")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\n", "\\n")
    return s

def strip_outer_ws(s: str) -> str:
    # preserve internal newlines; trim ends
    return s.strip()

def find_notes(html_text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    # Find all <h2> sections and slice between them
    matches = list(H2_RE.finditer(html_text))
    for idx, m in enumerate(matches):
        note_id = html.unescape(m.group("text")).strip()
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(html_text)
        section = html_text[start:end]

        # Find AFTER marker
        m_after = AFTER_H3_RE.search(section)
        if not m_after:
            continue

        after_start = m_after.end()
        after_region = section[after_start:]

        # Stop at <hr> or next <h2> if present inside slice
        m_stop = STOP_RE.search(after_region)
        if m_stop:
            after_region = after_region[: m_stop.start()]

        after_html = strip_outer_ws(after_region)
        if after_html:
            out.append((note_id, after_html))

    return out

def main() -> None:
    ap = argparse.ArgumentParser(description="Extract AFTER sections from canonical HTML to TSV.")
    ap.add_argument("--in", dest="inp", required=True, help="Input HTML file (generated from canonical MD)")
    ap.add_argument("--out", dest="outp", required=True, help="Output TSV file")
    args = ap.parse_args()

    inp = Path(args.inp)
    outp = Path(args.outp)

    html_text = inp.read_text(encoding="utf-8")
    notes = find_notes(html_text)

    lines = ["note_id\tafter_html"]
    for note_id, after_html in notes:
        lines.append(f"{tsv_escape_cell(note_id)}\t{tsv_escape_cell(after_html)}")

    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Rows: {len(notes)}")
    print(f"Output: {outp}")

if __name__ == "__main__":
    main()

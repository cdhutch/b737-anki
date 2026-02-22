#!/usr/bin/env python3
"""
Convert reviewed MultiMarkdown formatting file → Anki import TSV.

Produces:
- Single-line-safe TSV (Markdown lists preserved via literal \\n)
- Columns: note_id, prompt, answer
"""

from pathlib import Path
import re

# ----------- CONFIG (edit if needed) -----------

INPUT = Path("domains/b737/anki/sources/systems-electrical__canonical.md")
OUTPUT = Path("domains/b737/anki/exports/systems-electrical__canonical__import.tsv")# -----------------------------------------------

text = INPUT.read_text(encoding="utf-8")

pattern = re.compile(
    r"^####\s+(?P<note_id>\S+)\s*\n"
    r".*?^AFTER:\s*\n(?P<after>.*?)(?=^\s*####\s+|\Z)",
    re.S | re.M
)

rows = []

for m in pattern.finditer(text):
    note_id = m.group("note_id").strip()
    after = m.group("after").strip()

    match = re.search(
        r"^Prompt:\s*\n(?P<prompt>.*?)(?:\n{2,}|\n)Answer:\s*\n(?P<answer>.*)\Z",
        after,
        re.S | re.M,
    )

    if not match:
        raise SystemExit(f"Could not parse Prompt/Answer for {note_id}")

    prompt = match.group("prompt").strip()
    answer = match.group("answer").strip()

    def singleline(s: str) -> str:
        s = s.replace("\r\n", "\n").replace("\r", "\n")
        s = s.replace("\t", "    ")
        s = s.replace("\n", r"\n")
        return s

    rows.append((note_id, singleline(prompt), singleline(answer)))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8", newline="\n") as f:
    f.write("note_id\tprompt\tanswer\n")
    for r in rows:
        f.write("\t".join(r) + "\n")

print("✔ Done")
print("Rows:", len(rows))
print("Output:", OUTPUT)
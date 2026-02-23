#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"Empty TSV: {path}")
    header = lines[0].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        # pad short rows
        if len(parts) < len(header):
            parts += [""] * (len(header) - len(parts))
        rows.append({header[i]: parts[i] for i in range(len(header))})
    return header, rows

def write_tsv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    out_lines = ["\t".join(header)]
    for r in rows:
        out_lines.append("\t".join(r.get(h, "") for h in header))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

def main() -> None:
    ap = argparse.ArgumentParser(description="Merge base.tsv with after_html.tsv by note_id.")
    ap.add_argument("--base", required=True, help="Base TSV with note_id, noteId, prompt")
    ap.add_argument("--after", required=True, help="After TSV with note_id, after_html")
    ap.add_argument("--out", required=True, help="Output TSV")
    args = ap.parse_args()

    base_p = Path(args.base)
    after_p = Path(args.after)
    out_p = Path(args.out)

    _, base_rows = read_tsv(base_p)
    _, after_rows = read_tsv(after_p)

    after_map: dict[str, str] = {}
    for r in after_rows:
        nid = r.get("note_id", "").strip()
        if not nid:
            continue
        after_map[nid] = r.get("after_html", "")

    merged: list[dict[str, str]] = []
    missing_after: list[str] = []
    for r in base_rows:
        nid = r.get("note_id", "").strip()
        r2 = dict(r)
        r2["answer_html"] = after_map.get(nid, "")
        if not r2["answer_html"]:
            missing_after.append(nid)
        merged.append(r2)

    header = ["note_id", "noteId", "prompt", "answer_html"]
    write_tsv(out_p, header, merged)

    print(f"Base rows: {len(base_rows)}")
    print(f"After rows: {len(after_rows)}")
    print(f"Output rows: {len(merged)}")
    print(f"Missing AFTER: {len(missing_after)}")
    if missing_after:
        print("Missing IDs:")
        for x in missing_after[:20]:
            print(f"  - {x}")
        if len(missing_after) > 20:
            print("  ...")
    print(f"Output: {out_p}")

if __name__ == "__main__":
    main()

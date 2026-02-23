#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


HDR_RE = re.compile(r"^##\s+(\S+)\s*$")          # note header (## sys-...)
AFTER_RE = re.compile(r"^###\s+AFTER\s*$")       # AFTER block start
SEP_RE = re.compile(r"^---\s*$")                 # note separator

# Detect common "looks like a list but isn't markdown" bullets
BAD_BULLET_RE = re.compile(r"^\s*[•·‣◦▪▫]\s+")
# Detect markdown list items
MD_BULLET_RE = re.compile(r"^\s*-\s+\S")


@dataclass
class Issue:
    path: Path
    line_no: int
    code: str
    msg: str
    context: str


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Validate canonical MD formatting (AFTER blocks): bullet markers, blank lines before lists, etc."
    )
    ap.add_argument("--in", dest="inp", required=True, help="Input canonical markdown file")
    ap.add_argument(
        "--fix",
        action="store_true",
        help="Apply SAFE autofixes in-place (currently: convert Unicode bullets to '- ')",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero if any issues found (default: warn but exit 0)",
    )
    ap.add_argument(
        "--after-only",
        action="store_true",
        help="Only check inside ### AFTER blocks (default: true behavior; this just makes it explicit)",
    )
    return ap.parse_args()


def validate(md_text: str, path: Path) -> tuple[list[Issue], str]:
    """
    Returns (issues, possibly_modified_text).
    If no --fix, modified_text == original.
    """
    lines = md_text.splitlines()
    issues: list[Issue] = []

    in_after = False
    cur_note: str | None = None

    # We'll build a possibly modified copy if we do fixes
    out_lines = lines[:]

    def add_issue(i: int, code: str, msg: str):
        ctx = lines[i].rstrip("\n")
        note = f" [{cur_note}]" if cur_note else ""
        issues.append(Issue(path=path, line_no=i + 1, code=code, msg=f"{msg}{note}", context=ctx))

    for i, line in enumerate(lines):
        m = HDR_RE.match(line)
        if m:
            cur_note = m.group(1)
            in_after = False
            continue

        if AFTER_RE.match(line):
            in_after = True
            continue

        if SEP_RE.match(line):
            in_after = False
            continue

        if not in_after:
            continue

        # 1) Unicode bullets in AFTER blocks
        if BAD_BULLET_RE.match(line):
            add_issue(i, "BAD_BULLET", "Non-Markdown bullet character found in AFTER block; use '- '")
            continue

        # 2) Missing blank line before a markdown list
        # Only check at the START of a list run (i.e., previous line is not also a list item).
        if MD_BULLET_RE.match(line):
            if i > 0:
                prev = lines[i - 1]

                prev_is_list = bool(MD_BULLET_RE.match(prev))
                prev_is_heading = bool(HDR_RE.match(prev) or AFTER_RE.match(prev))

                # If this is the first bullet in a list (prev is not a bullet),
                # then require either a blank line or a heading immediately above.
                if not prev_is_list and prev.strip() != "" and not prev_is_heading:
                    add_issue(
                        i,
                        "NO_BLANK_BEFORE_LIST",
                        "Markdown list should be preceded by a blank line in AFTER block",
                    )
            continue


    return issues, "\n".join(out_lines) + ("\n" if md_text.endswith("\n") else "")


def apply_fixes(md_text: str) -> str:
    """
    SAFE fix only:
    - Convert common Unicode bullets at line start into '- '.
    We do NOT attempt to insert blank lines automatically because that can be context-sensitive.
    """
    lines = md_text.splitlines(keepends=False)
    fixed: list[str] = []
    in_after = False

    for line in lines:
        if AFTER_RE.match(line):
            in_after = True
            fixed.append(line)
            continue
        if SEP_RE.match(line):
            in_after = False
            fixed.append(line)
            continue

        if in_after and BAD_BULLET_RE.match(line):
            # Replace leading bullet glyph with markdown "- "
            # Preserve indentation if any.
            m = re.match(r"^(\s*)[•·‣◦▪▫]\s+(.*)$", line)
            if m:
                indent, rest = m.group(1), m.group(2)
                fixed.append(f"{indent}- {rest}")
                continue

        fixed.append(line)

    out = "\n".join(fixed)
    if md_text.endswith("\n"):
        out += "\n"
    return out


def main() -> None:
    args = parse_args()
    path = Path(args.inp)

    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    md_text = path.read_text(encoding="utf-8")

    if args.fix:
        fixed = apply_fixes(md_text)
        if fixed != md_text:
            path.write_text(fixed, encoding="utf-8")
            md_text = fixed
            print(f"OK: applied safe fixes to {path}")
        else:
            print("OK: no changes needed for safe fixes")

    issues, _ = validate(md_text, path)

    if issues:
        print(f"Found {len(issues)} issue(s):")
        for it in issues:
            print(f"{it.path}:{it.line_no}:{it.code}: {it.msg}")
            print(f"    {it.context}")
        if args.strict:
            sys.exit(1)
    else:
        print("OK: no issues found")

    sys.exit(0)


if __name__ == "__main__":
    main()

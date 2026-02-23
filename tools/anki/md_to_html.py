#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr)
        raise SystemExit(p.returncode)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Convert a Markdown/MultiMarkdown file to HTML using MultiMarkdown or Pandoc."
    )
    ap.add_argument("--in", dest="inp", required=True, help="Input .md/.mmd file")
    ap.add_argument("--out", dest="outp", required=True, help="Output .html file")
    ap.add_argument(
        "--engine",
        choices=["multimarkdown", "pandoc"],
        default="multimarkdown",
        help="Conversion engine (default: multimarkdown)",
    )
    args = ap.parse_args()

    inp = Path(args.inp)
    outp = Path(args.outp)
    outp.parent.mkdir(parents=True, exist_ok=True)

    if not inp.exists():
        raise SystemExit(f"Input file not found: {inp}")

    if args.engine == "multimarkdown":
        exe = shutil.which("multimarkdown")
        if not exe:
            raise SystemExit("multimarkdown not found on PATH. Install MultiMarkdown 6 or use --engine pandoc.")
        # MultiMarkdown writes HTML to stdout
        p = subprocess.run([exe, str(inp)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode != 0:
            sys.stderr.write(p.stderr)
            raise SystemExit(p.returncode)
        outp.write_text(p.stdout, encoding="utf-8")

    else:  # pandoc
        exe = shutil.which("pandoc")
        if not exe:
            raise SystemExit("pandoc not found on PATH. Install pandoc or use --engine multimarkdown.")
        # Pandoc writes to file via -o
        run([exe, str(inp), "-f", "markdown", "-t", "html", "-o", str(outp)])

    print(f"OK: wrote {outp}")


if __name__ == "__main__":
    main()

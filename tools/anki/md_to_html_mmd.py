#!/usr/bin/env python3
"""
L1 -> L2: CNSF Markdown -> HTML fragments

- Reads a CNSF note .md (YAML + # front_md / # back_md)
- Renders front_md and back_md to HTML using MultiMarkdown if available
  (prefers: multimarkdown, then mmd)
- Writes:
    domains/<domain>/anki/generated/<note_id>__front.html
    domains/<domain>/anki/generated/<note_id>__back.html

Also embeds an HTML comment with renderer provenance.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from tools.anki.cnsf_parse import load_cnsf_note


def _run(cmd: list[str], inp: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        input=inp,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _find_mmd() -> list[str] | None:
    for exe in ("multimarkdown", "mmd"):
        p = shutil.which(exe)
        if p:
            return [p]
    return None


def _mmd_version(mmd_cmd: list[str]) -> str:
    # MultiMarkdown prints version text; keep just first line-ish
    cp = _run(mmd_cmd + ["--version"])
    out = (cp.stdout or cp.stderr).strip()
    if not out:
        return "multimarkdown (unknown version)"
    return out.splitlines()[0].strip()


def _render_with_mmd(mmd_cmd: list[str], md: str) -> tuple[str, str]:
    """
    Returns (html, provenance_comment).
    We pass markdown via stdin.
    """
    cp = _run(mmd_cmd, inp=md)
    if cp.returncode != 0:
        raise RuntimeError(f"MultiMarkdown failed: {cp.stderr.strip() or cp.stdout.strip()}")
    ver = _mmd_version(mmd_cmd)
    prov = f"<!-- renderer: {ver} -->\n"
    return prov + cp.stdout, prov.strip()


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Render CNSF front_md/back_md to HTML using MultiMarkdown.")
    ap.add_argument("--note", required=True, help="Path to CNSF note markdown file (L1)")
    ap.add_argument(
        "--out-dir",
        default="",
        help="Override output dir (default: domains/<domain>/anki/generated)",
    )
    args = ap.parse_args()

    note = load_cnsf_note(args.note)

    domain = (note.meta.get("domain") or "").strip()
    if not domain:
        raise SystemExit(f"{note.path}: YAML missing domain")
    note_id = (note.meta.get("note_id") or "").strip()

    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        out_dir = Path("domains") / domain / "anki" / "generated"

    out_dir.mkdir(parents=True, exist_ok=True)

    out_front = out_dir / f"{note_id}__front.html"
    out_back = out_dir / f"{note_id}__back.html"

    mmd_cmd = _find_mmd()
    if not mmd_cmd:
        raise SystemExit(
            "Could not find MultiMarkdown executable. Expected 'multimarkdown' or 'mmd' on PATH."
        )

    front_html, front_prov = _render_with_mmd(mmd_cmd, note.front_md)
    back_html, back_prov = _render_with_mmd(mmd_cmd, note.back_md)

    out_front.write_text(front_html, encoding="utf-8")
    out_back.write_text(back_html, encoding="utf-8")

    print(f"OK: wrote {out_front}")
    print(f"OK: wrote {out_back}")
    print(f"provenance(front): {front_prov}")
    print(f"provenance(back) : {back_prov}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT_MARKERS = {".git", "README.md", "domains", "tools"}


def find_repo_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for cur in [p, *p.parents]:
        hits = sum(1 for m in REPO_ROOT_MARKERS if (cur / m).exists())
        if hits >= 2 and (cur / ".git").exists():
            return cur
    raise RuntimeError("Could not locate repo root (expected .git and common top-level dirs).")


def run(cmd: list[str], *, cwd: Path) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


@dataclass(frozen=True)
class PipelinePaths:
    sources_dir: Path
    exports_dir: Path
    generated_dir: Path

    canonical_md: Path
    canonical_html: Path

    base_tsv: Path
    after_md_tsv: Path
    after_html_tsv: Path

    import_md_tsv: Path
    import_html_tsv: Path


def build_paths(repo: Path, *, rel_sources: str, rel_exports: str, rel_generated: str, slug: str) -> PipelinePaths:
    sources_dir = (repo / rel_sources).resolve()
    exports_dir = (repo / rel_exports).resolve()
    generated_dir = (repo / rel_generated).resolve()

    # slug is the dataset slug, e.g. "systems-electrical"
    canonical_stem = f"{slug}__canonical"

    canonical_md = sources_dir / f"{canonical_stem}.md"
    canonical_html = generated_dir / f"{canonical_stem}.html"

    base_tsv = exports_dir / f"{canonical_stem}__base.tsv"
    after_md_tsv = exports_dir / f"{canonical_stem}__after.tsv"
    after_html_tsv = exports_dir / f"{canonical_stem}__after_html.tsv"

    import_md_tsv = exports_dir / f"{canonical_stem}__import.tsv"
    import_html_tsv = exports_dir / f"{canonical_stem}__import_html.tsv"

    return PipelinePaths(
        sources_dir=sources_dir,
        exports_dir=exports_dir,
        generated_dir=generated_dir,
        canonical_md=canonical_md,
        canonical_html=canonical_html,
        base_tsv=base_tsv,
        after_md_tsv=after_md_tsv,
        after_html_tsv=after_html_tsv,
        import_md_tsv=import_md_tsv,
        import_html_tsv=import_html_tsv,
    )

def cmd_md_to_html(repo: Path, inp: Path, outp: Path, engine: str) -> list[str]:
    return [
        sys.executable,
        str(repo / "tools/anki/md_to_html.py"),
        "--in",
        str(inp),
        "--out",
        str(outp),
        "--engine",
        engine,
    ]


def cmd_html_after_to_tsv(repo: Path, inp_html: Path, out_tsv: Path) -> list[str]:
    return [
        sys.executable,
        str(repo / "tools/anki/html_after_to_tsv.py"),
        "--in",
        str(inp_html),
        "--out",
        str(out_tsv),
    ]


def cmd_merge_base_and_after(repo: Path, base_tsv: Path, after_tsv: Path, out_tsv: Path) -> list[str]:
    # merge_base_and_after.py supports --after-col (answer_html vs after_md etc.)
    return [
        sys.executable, str(repo / "tools/anki/merge_base_and_after.py"),
        "--base", str(base_tsv),
        "--after", str(after_tsv),
        "--out", str(out_tsv),
        ]


def cmd_update_notes(repo: Path, inp_tsv: Path, field: str | None, dry_run: bool, anki_url: str) -> list[str]:
    cmd = [
        sys.executable,
        str(repo / "tools/anki/update_notes_from_tsv.py"),
        "--in",
        str(inp_tsv),
        "--anki-url",
        anki_url,
    ]
    if field:
        cmd += ["--field", field]
    if dry_run:
        cmd += ["--dry-run"]
    return cmd


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generalized Anki pipeline orchestrator (canonical MD -> HTML -> TSV -> Anki updates)."
    )
    ap.add_argument("--slug", required=True, help="Dataset slug (e.g., systems-electrical)")
    ap.add_argument(
        "--sources",
        default="domains/b737/anki/sources",
        help="Sources dir (relative to repo root)",
    )
    ap.add_argument(
        "--exports",
        default="domains/b737/anki/exports",
        help="Exports dir (relative to repo root)",
    )
    ap.add_argument(
        "--generated",
        default="domains/b737/anki/generated",
        help="Generated dir (relative to repo root)",
    )

    sub = ap.add_subparsers(dest="cmd", required=True)

    p_html = sub.add_parser("html", help="canonical.md -> canonical.html")
    p_html.add_argument("--engine", choices=["multimarkdown", "pandoc"], default="multimarkdown")

    p_after_html = sub.add_parser("after-html", help="canonical.html -> after_html.tsv")
    # (no args yet)

    p_merge_html = sub.add_parser("merge-html", help="base.tsv + after_html.tsv -> import_html.tsv")
    # (no args yet)

    p_update_html = sub.add_parser("update-html", help="import_html.tsv -> update notes in Anki")
    p_update_html.add_argument("--anki-url", default="http://127.0.0.1:8765")
    p_update_html.add_argument("--field", default=None, help="Explicit Anki field name to update (else auto-detect)")
    p_update_html.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()

    repo = find_repo_root()
    paths = build_paths(repo, rel_sources=args.sources, rel_exports=args.exports, rel_generated=args.generated, slug=args.slug)

    # Ensure output dirs exist
    paths.sources_dir.mkdir(parents=True, exist_ok=True)
    paths.exports_dir.mkdir(parents=True, exist_ok=True)
    paths.generated_dir.mkdir(parents=True, exist_ok=True)

    if args.cmd == "html":
        if not paths.canonical_md.exists():
            raise FileNotFoundError(f"Missing canonical MD: {paths.canonical_md}")
        run(cmd_md_to_html(repo, paths.canonical_md, paths.canonical_html, args.engine), cwd=repo)
        return

    if args.cmd == "after-html":
        if not paths.canonical_html.exists():
            raise FileNotFoundError(f"Missing canonical HTML: {paths.canonical_html}")
        run(cmd_html_after_to_tsv(repo, paths.canonical_html, paths.after_html_tsv), cwd=repo)
        return

    if args.cmd == "merge-html":
        if not paths.base_tsv.exists():
            raise FileNotFoundError(f"Missing base TSV: {paths.base_tsv}")
        if not paths.after_html_tsv.exists():
            raise FileNotFoundError(f"Missing after_html TSV: {paths.after_html_tsv}")
        # run(cmd_merge_base_and_after(repo, paths.base_tsv, paths.after_html_tsv, paths.import_html_tsv, "answer_html"), cwd=repo)
        run(
            cmd_merge_base_and_after(
                repo,
                paths.base_tsv,
                paths.after_html_tsv,
                paths.import_html_tsv,
            ), cwd=repo,
        )
        return

    if args.cmd == "update-html":
        if not paths.import_html_tsv.exists():
            raise FileNotFoundError(f"Missing import_html TSV: {paths.import_html_tsv}")
        run(cmd_update_notes(repo, paths.import_html_tsv, args.field, args.dry_run, args.anki_url), cwd=repo)
        return


if __name__ == "__main__":
    main()

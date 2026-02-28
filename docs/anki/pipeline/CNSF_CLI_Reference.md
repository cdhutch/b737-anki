# CNSF CLI Reference (Authoritative)

This file is intentionally generated from the current `--help` output of
the CNSF pipeline scripts. It should be updated whenever CLI switches
change.

------------------------------------------------------------------------

## tools/anki/cnsf_canonicalize.py

usage: cnsf_canonicalize.py \[-h\] \[--check\] \[--write\] paths \[paths
...\]

Canonicalize CNSF v0 YAML front matter (order + normalization).

positional arguments: paths One or more CNSF .md note files

options: -h, --help show this help message and exit --check Fail if any
file would change --write Rewrite files in-place

------------------------------------------------------------------------

## tools/anki/md_to_html_mmd.py

usage: md_to_html_mmd.py \[-h\] --note NOTE \[--out-dir OUT_DIR\]

Render CNSF front_md/back_md to HTML using MultiMarkdown.

options: -h, --help show this help message and exit --note NOTE Path to
CNSF note markdown file (L1) --out-dir OUT_DIR Override output dir
(default: domains/`<domain>`{=html}/anki/generated)

------------------------------------------------------------------------

## tools/anki/export/cnsf_to_import_tsv.py

usage: cnsf_to_import_tsv.py \[-h\] --in INPUTS \[INPUTS ...\] --out OUT
\[--map MAP\] \[--overwrite\] \[--limit LIMIT\]

options: -h, --help show this help message and exit --in INPUTS \[INPUTS
...\] --out OUT --map MAP --overwrite --limit LIMIT

------------------------------------------------------------------------

## tools/anki/sync/tsv_to_anki.py

usage: tsv_to_anki.py \[-h\] --tsv TSV \[--anki-url ANKI_URL\]
\[--map-out MAP_OUT\] \[--map-in MAP_IN\] \[--dry-run\] \[--check\]

options: -h, --help show this help message and exit --tsv TSV Path to L3
import TSV (HTML payload) --anki-url ANKI_URL --map-out MAP_OUT Optional
mapping TSV to append to on CREATE flows --map-in MAP_IN Optional
mapping TSV (note_id-\>noteId) to apply before sync --dry-run Parse +
validate only; do not call AnkiConnect --check Validate TSV; fail if any
row would CREATE (missing noteId); no AnkiConnect calls

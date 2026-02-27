# Anki pipeline (4-level model)

This repo uses a **4-level pipeline** to transform Git-controlled note sources into Anki notes (and optionally back out again).

The goal is simple:

- **L1 is canonical** (human-editable, reviewable, diffable)
- Everything else is **generated** or **synced** from L1
- We keep transformations **adjacent**, testable, and deterministic

---

## The 4-level pipeline

```
          (Git / repo)                                   (Anki)

L1: CNSF note markdown
    domains/<domain>/anki/notes/<note_type>/<note_id>.md
        |  (render: Markdown -> HTML, prefer MultiMarkdown)
        v
L2: rendered HTML fragments (front/back)
    (cacheable) domains/<domain>/anki/generated/<note_id>.html
        |  (package: HTML + metadata -> TSV rows)
        v
L3: import TSV (HTML payload, merge-eligible shape)
    domains/<domain>/anki/exports/<note_type>__import_html.tsv
        |  (sync: AnkiConnect create/update + tags + mapping)
        v
L4: Anki
    - notes updated/created
    - tags managed
    - noteId mapping maintained
```

---

## Level definitions

### L1 — CNSF note markdown (canonical source)
**One file = one Anki note (1:1).**

Contains:
- YAML front matter (domain, note_type, note_id, anki model/deck, tags, extra fields)
- `front_md` and `back_md` sections

Why L1:
- best for Git review
- easiest to author
- stable canonical representation for both B737 + UA

### L2 — rendered HTML fragments
The HTML that will actually be written into Anki fields.

Output conceptually:
- `front_html`
- `back_html`

Renderer policy:
- Prefer **Fletcher Penney MultiMarkdown** (`multimarkdown` or `mmd`) when available
- Otherwise fall back to a secondary renderer (and record provenance)

L2 is where formatting issues are diagnosed:
- tables
- bold/italics
- line breaks
- escaping behavior

### L3 — import TSV (HTML payload)
A machine-friendly representation used for sync operations.

Typical required columns:
- `note_id` (string)
- `noteId` (Anki internal numeric id; blank for create flows)
- `model`, `deck`
- `tags` (space-separated)
- `front_html`, `back_html`
- plus any model-specific fields (e.g., Source Document, Source Location, Verification Notes)

L3 is “merge-eligible output” — it should be deterministic given L1 + renderer.

### L4 — Anki (via AnkiConnect)
The live system.

Operations:
- create notes (when `noteId` missing)
- update notes (when `noteId` present)
- set/normalize tags (repo policy)
- write all fields (including Front/Back)

---

## Reverse direction (optional)
Reverse sync is useful for legacy migration, but should be treated as **import for review**, not auto-overwrite:

```
Anki (L4) -> TSV export -> generated CNSF candidates -> human review -> commit to L1
```

---

## Practical mental model

- If content is “wrong in Anki”: check **L3 → L4** sync
- If formatting is “weird in Anki”: check **L1 → L2** renderer
- If a note is missing / duplicated: check **mapping** (`note_id` ↔ `noteId`) and create-vs-update rules
- If tags drift: check **tag policy** (canonical tags in L1, computed/managed tags written to Anki)

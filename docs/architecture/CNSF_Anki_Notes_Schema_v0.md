# Canonical Note Source Format (CNSF) v0

## Anki Git-Backed Notes Architecture Specification

------------------------------------------------------------------------

# 1. Purpose

CNSF v0 defines a single canonical, configuration-controlled format for
representing Anki notes inside a Git repository.

It supports:

-   B737 Structured notes
-   UA_Lexeme notes
-   UA_Grammar notes
-   Future extensible note types
-   Bidirectional transformation between:
    -   Markdown source
    -   Rendered HTML
    -   TSV payload
    -   Anki (via AnkiConnect)

The system is designed for:

-   1:1 correspondence (one file per note)
-   Deterministic rendering
-   Explicit field mapping
-   Domain-agnostic extensibility
-   Automation-friendly transformation stages

------------------------------------------------------------------------

# 2. Architecture Overview

We define four transformation layers:

(1) Canonical Markdown (CNSF) ↓
(2) Rendered HTML fragments ↓
(3) TSV payload for AnkiConnect ↓
(4) Anki note database

Reverse bootstrap is also supported:

Anki → TSV export → HTML reconstruction → CNSF Markdown

------------------------------------------------------------------------

# 3. One Note = One File

All notes exist as individual Markdown files:

domains/`<domain>`{=html}/anki/notes/`<note_id>`{=html}.md

Example:

domains/b737/anki/notes/b737-limits-weight-800.md
domains/ua/anki/notes/ua-lex-000123.md

This eliminates section parsing ambiguity and simplifies mapping.

------------------------------------------------------------------------

# 4. File Structure

Each note file contains:

1.  YAML front matter
2.  Named Markdown blocks

## 4.1 YAML Front Matter

``` yaml
---
cnsf: 0
note_id: b737-limits-weight-800
domain: b737

anki:
  model: "B737 Structured"
  deck: "B737::Limits"

  fields:
    NoteID: "{{note_id}}"
    Source Document: "B737 AOM Rev 9.0"
    Source Location: "Ch 18 §18.2.3 Weight Limits"

  tags:
    - domain:b737
    - topic:limits
    - subtopic:weight
    - model:800
    - source:aom
    - status:unverified

render:
  targets:
    - field: "Front"
      from_block: "front"
      format: "markdown"
    - field: "Back"
      from_block: "back"
      format: "markdown"

validation:
  required_blocks: [front, back]
  required_fields: [NoteID, Source Document, Source Location]
---
```

------------------------------------------------------------------------

# 5. Named Blocks

Long-form content is stored in named blocks:

```{=html}
<!-- BLOCK: front -->
```
... markdown ... `<!-- /BLOCK: front -->`{=html}

```{=html}
<!-- BLOCK: back -->
```
... markdown ... `<!-- /BLOCK: back -->`{=html}

Blocks are explicitly delimited to avoid ambiguity.

Additional blocks are allowed:

-   morphology_note
-   conjugation_table
-   ua_example
-   en_example
-   mnemonic
-   notes

------------------------------------------------------------------------

# 6. Field-First Philosophy

Canonical truth resides in:

-   YAML fields (short values)
-   Named blocks (long content)

Front/Back are optional presentation targets.

This balances:

-   Extensibility
-   Tooling simplicity
-   Multi-model support

------------------------------------------------------------------------

# 7. Tag Standardization

Tags must use prefixed format:

-   domain:\*
-   topic:\*
-   subtopic:\*
-   status:verified\|unverified
-   textbook:\*
-   ch:\*
-   model:\*
-   source:\*

Tags are defined in YAML and rendered to Anki.

------------------------------------------------------------------------

# 8. Mapping Strategy

We DO NOT store Anki numeric noteId in canonical files.

Instead, we generate a mapping file:

domains/`<domain>`{=html}/anki/generated/note_id_map.tsv

Columns:

note_id noteId model deck

This file may be regenerated from AnkiConnect.

------------------------------------------------------------------------

# 9. Transformation Stages

## 9.1 Stage 1 --- CNSF → HTML

Operations:

-   Parse YAML
-   Extract blocks
-   Render Markdown → HTML
-   Resolve template placeholders:
    -   {{note_id}}
    -   {{block:blockname}}
    -   {{render:FieldName}}

Output: - HTML fragments per field

## 9.2 Stage 2 --- HTML → TSV

Generate TSV columns:

-   note_id
-   noteId (from mapping file)
-   field_name
-   field_html
-   tags

Output file example:

domains/`<domain>`{=html}/anki/exports/
```{=html}
<note>
```
\_\_import.tsv

## 9.3 Stage 3 --- TSV → Anki

Use AnkiConnect:

-   updateNoteFields
-   updateNoteTags

## 9.4 Stage 4 --- Bootstrap (Anki → CNSF)

Optional reverse pipeline:

-   Export notes via AnkiConnect
-   Normalize fields
-   Regenerate CNSF Markdown files

------------------------------------------------------------------------

# 10. Validation Rules

Each note may define:

validation: required_fields: \[\] required_blocks: \[\]
allowed_tag_prefixes: \[\]

The validation engine must:

-   Confirm required blocks exist
-   Confirm required fields are populated
-   Confirm tag prefixes match policy

------------------------------------------------------------------------

# 11. Model Configuration Files

Per model configuration stored at:

domains/`<domain>`{=html}/anki/note-types/`<ModelName>`{=html}.yaml

Example:

model: "B737 Structured" required_fields: - NoteID - Front - Back
large_fields: - Front - Back

This keeps the core pipeline domain-agnostic.

------------------------------------------------------------------------

# 12. Extensibility

To add a new note type:

1.  Create a model config YAML
2.  Define required fields
3.  Define required blocks (if any)
4.  No core pipeline changes required

------------------------------------------------------------------------

# 13. Design Principles

-   One canonical source of truth
-   Explicit field mapping
-   No implicit parsing rules
-   Deterministic rendering
-   Configurable per model
-   Git-first architecture
-   No reliance on Anki as primary storage

------------------------------------------------------------------------

# 14. Future Enhancements

-   YAML schema validation (JSON Schema)
-   Strict block ordering enforcement
-   Auto-verification tagging
-   Cloze-style render targets
-   PDF preview rendering
-   Round-trip diff integrity checks

------------------------------------------------------------------------

# END OF CNSF v0 SPECIFICATION

# CNSF Spec v0 (Canonical Note Source Format)

This document defines the **canonical, repo-owned note file format** used to generate, validate, and sync Anki notes for **all domains** (e.g., `b737`, `ua`).

- Schema identifier remains: `schema: cnsf/v0`
- This spec **tightens rules** (naming + delimiters + validation) without introducing a new schema version.

---

## Goals

1) **1:1 mapping** — one file corresponds to one Anki note.  
2) **Deterministic transforms** — same input yields same outputs (HTML/TSV).  
3) **Domain-agnostic** — works for B737 and Ukrainian note types.  
4) **Repo is source of truth** — tags, sources, and field payloads live in the repo.

---

## File location and 1:1 mapping

Each note is a single Markdown file:

```
domains/<domain>/anki/notes/<note_type>/<note_id>.md
```

- `<domain>` is a short identifier (e.g., `b737`, `ua`)
- `<note_type>` is the **CNSF note type** identifier (underscores only)
- `<note_id>` is the **canonical note ID** (underscores only)

**1 file = 1 Anki note**.

---

## Required structure

A CNSF note file has:

1) YAML front matter (metadata + non-front/back fields)
2) A `# front_md` section
3) A `# back_md` section

Example skeleton:

```yaml
---
schema: cnsf/v0
domain: b737
note_type: limits_weight_model
note_id: b737_limits_weight_800

anki:
  model: B737_Structured
  deck: "B737::Limits"

tags:
  - domain:b737
  - model:800
  - topic:limits
  - subtopic:weight
  - source:aom
  - status:unverified

fields:
  Source Document: "B737 AOM Rev 9.0"
  Source Location: "Ch 18 §18.2.3 Weight Limits (Certificated Limits table)"
  Verification Notes: ""

aliases:
  - b737-limits-weight-800   # optional (legacy)
---
# front_md
...markdown...

# back_md
...markdown...
```

### Required YAML keys

- `schema` (must equal `cnsf/v0`)
- `domain`
- `note_type`
- `note_id`
- `anki.model`
- `anki.deck`
- `tags` (list; may be empty but should exist)
- `fields` (object/map; may be empty but should exist)

### Required body sections

- Exactly one `# front_md`
- Exactly one `# back_md`
- Everything between these headings belongs to that section.
- Additional headings inside each section are allowed.

---

## Canonical naming grammar (underscores)

### Repo identifiers MUST use underscores

For the following **repo identifiers**, underscores are mandatory:

- `note_type`
- `note_id`
- CNSF filenames (`<note_id>.md`)
- folder names under `notes/` (`<note_type>/`)

### Allowed character set

For `domain`, `note_type`, and `note_id`:

- lowercase letters, digits, underscores only: `^[a-z0-9_]+$`
- no spaces
- no hyphens

Examples:

✅ `b737_limits_weight_800`  
✅ `ua_lexeme`  
❌ `b737-limits-weight-800` (hyphens)  
❌ `B737_Limits` (uppercase)  
❌ `limits weight` (space)

---

## Aliases (legacy compatibility)

`aliases` is optional, and exists to bridge legacy Anki note IDs that used hyphens.

- `aliases` is a YAML list of strings
- Aliases MAY contain hyphens
- Aliases MUST NOT be used for filenames or note folders
- Preferred usage: keep existing Anki notes addressable while canonical IDs move to underscores

Recommended policy:

- `note_id` is canonical (underscores)
- existing Anki NoteID field may still contain a legacy value
- mapping TSV resolves canonical ↔ Anki IDs

---

## Tags policy (canonical in repo)

### Source of truth

- `tags:` in CNSF is **canonical**.
- Anki tags are managed from CNSF via sync scripts (not ad-hoc).

### Tag grammar

Use normalized, machine-friendly tags:

- Prefer namespaced tags: `key:value`
- Use lowercase
- Use underscores if you need a delimiter inside values

Examples:

- `domain:b737`
- `domain:ua`
- `topic:limits`
- `subtopic:weight`
- `model:max8`
- `source:aom`
- `status:unverified` / `status:verified`

### Verification status

Standardize across all domains:

- `status:unverified` — default for new notes
- `status:verified` — once confirmed against the source

(Optionally add a workflow tag, but keep the above as the canonical pair.)

---

## Fields policy (non-front/back)

`fields:` is a YAML map for model-specific fields **other than** front/back.

- Keys must match Anki field names exactly (case-sensitive)
- Values are strings (empty string allowed)

Examples:
- B737: `Source Document`, `Source Location`, `Verification Notes`
- UA: `Tags_Ch` may remain as an Anki field, but canonical tags should be in `tags:`

---

## Front/back ownership

- `# front_md` and `# back_md` are the canonical **content source** for the Front/Back fields.
- They are rendered to HTML by the renderer step (MultiMarkdown preferred).

**Card templates (Anki side) remain responsible** for adding static chrome (e.g., Source footer).  
Content fields should stay “clean” and not duplicate template chrome.

---

## Renderer requirement (prove MultiMarkdown usage)

### Preferred renderer

If available on PATH, the system MUST use **Fletcher Penney MultiMarkdown**:

- `multimarkdown` OR `mmd`

The renderer step should write provenance to logs and/or output metadata, e.g.:

- `renderer: multimarkdown`
- `renderer_version: <version output>`

### Fallback renderer

If MultiMarkdown is not present, fallback is allowed, but MUST:

- emit a warning
- annotate outputs as fallback-generated (comment marker)
- remain deterministic

---

## Validation rules

A CNSF validator MUST fail the note if:

1) YAML front matter is missing or invalid
2) required YAML keys are missing
3) `domain`, `note_type`, or `note_id` violates the underscore grammar
4) `# front_md` or `# back_md` is missing or duplicated
5) file path does not match YAML:
   - path domain matches `domain:`
   - folder `notes/<note_type>/` matches `note_type:`
   - filename matches `note_id`

Recommended (warning-only) checks:

- tags contain `domain:<domain>`
- tags contain exactly one of `status:verified` or `status:unverified`

---

## Mapping to Anki (summary)

- Canonical identifier: `note_id` (underscores)
- Anki linkage:
  - prefer a dedicated Anki field: `NoteID` (string)
  - mapping TSV: `note_id` ↔ `noteId` (numeric Anki internal ID)

For legacy notes that still have hyphen `NoteID` values:
- use `aliases` + mapping to locate and migrate

---

## Notes on model naming (underscores)

You want Anki model names to use underscores (e.g., `B737_Structured`, `UA_Lexeme`, `UA_Grammar`).

Recommendation:
- Do not rename in-place until you have migration scripts and a backup.
- Create new models with underscore names and migrate notes by TSV when ready.

---

## Versioning

This spec is **CNSF v0**. Tightening rules does not require bumping the schema identifier, as long as:

- existing notes remain representable (via `aliases`)
- transform contracts remain compatible

If a future change breaks representability, then bump to `cnsf/v1`.

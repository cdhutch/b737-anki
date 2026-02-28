# CNSF L1 → L4 Operational Playbook

## Purpose

This document defines the authoritative operational workflow for the CNSF
(Canonical Note Source Format) Git-backed Anki system.

It is intended for:
- Future maintainers
- Future ChatGPT sessions
- Machine bootstrap scenarios
- Audit / migration workflows

---

# Pipeline Overview

L1: Canonical CNSF Markdown (.md)
L2: Rendered HTML fragments (MultiMarkdown)
L3: Stable TSV export (HTML payload)
L4: AnkiConnect sync (create/update)

Steady state behavior:
- L1 is the single source of truth.
- L3 TSV contains `noteId` once mapping exists.
- L4 becomes update-only and idempotent.

---

# Dependencies

Required:

- Python 3.13+
- PyYAML (see requirements.txt)
- MultiMarkdown 6 (CLI available as `mmd` or `multimarkdown`)
- Anki Desktop running
- AnkiConnect installed

Install Python deps:

    pip install -r requirements.txt

---

# Mapping Lifecycle

On first sync:
- If noteId missing:
  - Try to adopt existing note by NoteID field.
  - If not found → create new.
  - Optionally append to mapping TSV.

Mapping TSV schema:

    note_id    noteId

Mapping is then fed back into L3 exporter using `--map`.

After that:
- TSV contains noteId.
- L4 performs update-only operations.
- System becomes deterministic and idempotent.

---

# Duplicate Handling Strategy

When creating:
- allowDuplicate=False
- duplicateScope="deck"

If duplicate detected:
- Search by NoteID:"<note_id>"
- Adopt existing noteId
- Update fields + tags
- Append mapping if requested

This guarantees:
- No accidental duplication
- Safe migration of legacy notes

---

# Field Ownership Model

L1 YAML controls:
- Front
- Back
- Source metadata fields
- Tags

Anki is not considered authoritative.

Future direction:
- Implement reverse sync (Anki → CNSF) for audit intake only.

---

# Safety Properties Verified

✔ L1 → L4 end-to-end
✔ Duplicate adoption works
✔ Mapping round-trip works
✔ Steady-state update-only confirmed
✔ HTML payload validated (tables render)
✔ Renderer provenance embedded

---

# Future Work (Ordered)

1. L4 --check mode (no-op diff)
2. L4 --map-in support
3. Reverse exporter (Anki → CNSF unverified)
4. Bidirectional sync governance rules


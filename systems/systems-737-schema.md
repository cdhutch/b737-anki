# 737 Systems TSV Schema (v1)

This schema is designed to be:
- **Atomic** (no redundant columns),
- **Git-friendly** (stable column order),
- **Anki-friendly** for TSV import and **AnkiConnect** automation.

---

## Tag delimiter (Anki / AnkiConnect)

**Use space-separated tags** in the `tags` column.

Why:
- Anki’s tag model treats **spaces as separators**.
- This is the most reliable format for direct TSV import and for AnkiConnect note creation.

**Rules**
- Tags **must not contain spaces**.
- Prefer `kebab-case`, `snake_case`, or `namespace:tag` patterns (e.g., `systems`, `format_bullets`, `lights-switches`, `subsys:ac-power`).

Examples:
- `common systems format_bullets`
- `common systems lights-switches verbatim`
- `systems electrical subsys:ac-power format_bullets`

---

## List delimiter (non-tag list fields)

For list-like data fields (NOT tags), use:

- **`; `** (semicolon + space)

Applies to:
- `affects_bus`
- `powered_by`
- `interacts_with`

Example:
- `affects_bus = AC TRANSFER BUS 1; AC TRANSFER BUS 2`

---

## Status vocabulary

`status` is a controlled field:

- `draft` *(default; not yet validated against source)*
- `verified`
- `needs_review` *(known issue / revisit soon)*

> Note: We are **not** duplicating verification state in `tags`. Use `status` as the single source of truth.

---

## Canonical column order (exact)

1. `note_id`  
2. `system`  
3. `subsystem`  
4. `panel_group`  
5. `panel_name`  
6. `function_type`  
7. `prompt`  
8. `answer`  
9. `normal_state`  
10. `failure_logic`  
11. `affects_bus`  
12. `powered_by`  
13. `interacts_with`  
14. `source`  
15. `ref_section`  
16. `tags`  
17. `status`  
18. `notes`

---

## Field notes

### `note_id` (required)
Recommended pattern:

`sys-<system>-<class>-<nnn>`

Where `<class>` is one of:
- `psc` = principles / concepts
- `swt` = switch / control
- `ind` = indications / annunciations / metering
- `fail` = failure logic / protections / load shedding
- `proc` = procedures (optional, if added later)

Examples:
- `sys-elec-psc-001`
- `sys-elec-swt-040`
- `sys-elec-ind-133`
- `sys-elec-fail-050`

### `function_type` (required)
Controlled-ish vocabulary (keep consistent):
- `concept`
- `control`
- `indication`
- `failure-logic`
- `procedure` *(optional)*

### Panel fields
- `panel_group`: higher-level location grouping (e.g., `Overhead – Electrical`)
- `panel_name`: specific panel/switch cluster name (e.g., `BUS TRANSFER switch`)

Leave blank for pure conceptual items.

### `ref_section`
Prefer stable references (chapter/section) over page numbers, e.g.:
- `Ch 6 §6.20.3 (AC Power System)`

---

## “Atomic data” stance

We intentionally **omit `topic`** because it is encoded by:
- `note_id` class prefix (e.g., `psc/swt/ind/fail`)
- `function_type` (behavioral category)

This avoids duplication and drift.


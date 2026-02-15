# B737 Anki Training Deck

Structured, source-controlled Anki deck for B737 training.

---

## Philosophy

- No AI-trust.
- Every note is tagged `unverified` by default.
- Nothing is considered correct until independently verified.
- All notes must include a precise source reference (use section numbers, not page numbers).
- Git repository is the single source of truth.
- Anki is only the delivery mechanism.

---

## Repository Structure

flows/
limits/
maneuvers/
recall-items/
systems/

Each TSV file represents one logical unit (e.g., a single flow or limits subsection).

---

## TSV Column Format

All TSV files must use this exact column order:

NoteID  
Front  
Back  
Source Document  
Source Location  
Verification Notes  
Tags  

Tabs must be used as delimiters.

### NoteID Rules

- Must be globally unique.
- Must remain stable once created.
- Format convention:

<category>-<topic>-###

Examples:

lim-alt-001  
lim-spd-004  
flow-bstart-003  

---

## Tagging System

All new notes must include:

- `unverified`
- Aircraft variant tag (`b737-800` or `b737-max8`)
- Content type tag (`limits`, `flow`, `maneuver`, `recall`, `systems`, `callouts`)
- `verbatim` (for exact numeric or wording limits)
- `boldface-pending` (until manually confirmed)

### After Manual Verification

When you verify a note:

- Remove `unverified`
- Add `verified`
- Replace `boldface-pending` with:
  - `boldface` (if it is a memory item)
  - or remove it entirely if not boldface

### Optional Tags

- `max-delta` → Used for MAX‑8 differences only
- `common` → Used when a value applies to both -800 and MAX
- `company-specific` → If company AOM differs from Boeing baseline

---

## Variant Policy (737-800 vs 737 MAX 8)

Training Flow:
- 737-800 first
- MAX 8 differences later

### Rules

1. If data applies only to the 737-800:
   - Tag: `b737-800`
   - Do NOT tag as MAX

2. If data applies only to the 737 MAX 8:
   - Tag: `b737-max8`
   - Add `max-delta`

3. If data applies to both variants and is identical:
   - Tag: `b737-800 b737-max8 common`

4. If data differs numerically between variants:
   - Create separate NoteIDs
   - Tag appropriately
   - Add `max-delta` to MAX-only entry

Example:

lim-wt-001 (b737-800)  
lim-wt-001-max (b737-max8 max-delta)

---

## Verification Workflow

1. Review TSV file manually.
2. Verify values against AOM / QRH / NPC.
3. Adjust tags appropriately.
4. Commit changes to `draft`.
5. Merge into `main` only after section is fully verified.

---

## Anki Import Settings

- Note Type → B737 Structured
- Existing Notes → Update
- Match Scope → Note Type
- Separator → Tab

---

This repository is maintained as a controlled training system.

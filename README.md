# B737 Anki Training Deck

Structured, source-controlled Anki deck for B737 training.

---

## Philosophy

- No AI-trust.
- Every note begins as `unverified`.
- Nothing is trusted until manually verified.
- Section numbers (not page numbers) are used for source references.
- Git repository is the single source of truth.
- Anki is only the delivery mechanism.

---

## Repository Structure

flows/
limits/
maneuvers/
recall-items/
systems/
callouts/

Each TSV file represents one logical unit.

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
- Format:

<category>-<topic>-###

Examples:

lim-alt-001  
lim-spd-004  
flow-bstart-003  

---

# Tag Taxonomy

Tags are structured to allow filtering by:

1. Verification Status
2. Aircraft Variant (exactly one required)
3. Content Type
4. Memory Status
5. Optional Context Flags

---

## 1. Verification Status (Required)

- `unverified`
- `verified`

---

## 2. Aircraft Variant (Exactly One Required)

Each note must contain **exactly one** of the following:

- `b737-800`  → Applies only to the 737-800  
- `b737-max8` → Applies only to the 737 MAX 8  
- `common`    → Applies identically to both airframes  

### Rules

- Do NOT combine variant tags.
- Do NOT use both `b737-800` and `b737-max8` on the same note.
- If a value differs between aircraft, create separate NoteIDs.
- If a value is identical for both, use `common`.

Example:

lim-wt-001 (b737-800)  
lim-wt-001-max (b737-max8)  
lim-spd-001 (common)

---

## 3. Content Type Tags (Exactly One Required)

- `limits`
- `flow`
- `maneuver`
- `recall`
- `systems`
- `callouts`

---

## 4. Memory Classification

- `boldface-pending`
- `boldface`
- (no tag if not boldface)

---

## 5. Optional Context Tags

- `verbatim`
- `max-delta`
- `company-specific`
- `training-only`
- `performance`
- `structural`
- `rvsm`

---

# Variant Policy (Operational Approach)

Training sequence:
- 737-800 first
- MAX 8 differences later

### Policy

1. Default assumption is `common` unless a documented difference exists.
2. Differences must be explicitly documented before assigning `b737-max8` or `b737-800`.
3. MAX-only differences should also include `max-delta`.
4. Separate NoteIDs must be used for differing values.

---

# Branch Policy

- `main` = Fully verified, trusted, sim-ready content only.
- `draft` = Active development, unverified, in-progress edits.

### Workflow

1. All new TSV generation happens on `draft`.
2. Manual review and verification occur on `draft`.
3. Only fully verified sections are merged into `main`.
4. `main` should always represent clean, operationally trusted material.

---

# Verification Workflow

1. Review TSV manually.
2. Confirm values against AOM / QRH / NPC.
3. Adjust tags:
   - Remove `unverified`
   - Add `verified`
   - Resolve `boldface-pending`
4. Ensure exactly one aircraft variant tag is present.
5. Commit to `draft`.
6. Merge to `main` only when section is complete.

---

# Anki Import Settings

- Note Type → B737 Structured
- Existing Notes → Update
- Match Scope → Note Type
- Separator → Tab

---

This repository is maintained as a controlled training system.

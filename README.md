# B737 Anki Training Deck

Structured, source-controlled Anki deck for B737 training.

---

# Core Philosophy

- No AI trust.
- Every generated note begins with the tag: `unverified`.
- Manual verification happens in the TSV file.
- Only after manual review is content merged from `draft` → `main`.
- Section numbers (not page numbers) are used for source references.
- Git repository is the single source of truth.
- Anki is only the delivery mechanism.

Primary goals:
- Sim survival
- Long-term line proficiency

---

# Deck Architecture (Anki)

## One Physical Deck
B737::LIMITS

All limits notes live here.

## One Filtered Deck (Dynamic)
B737::LIMITS::BOLDFACE

Filtered search:
deck:"B737::LIMITS" tag:boldface

This deck is dynamically built in Anki.
No duplicate notes are created.

---

# Repository Structure

flows/
limits/
maneuvers/
recall-items/
systems/
callouts/

Each TSV file represents one logical unit (e.g., §18.2.1 Altitude Limits).

---

# TSV Column Format

All TSV files must use this exact column order:

NoteID  
Front  
Back  
Source Document  
Source Location  
Verification Notes  
Tags  

Tabs must be used as delimiters.

---

# NoteID Rules

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

Tags are structured in four required categories plus optional context tags.

---

## 1. Verification Status (Required)

Exactly one of:

- `unverified`
- `verified`

New notes always begin as `unverified`.

---

## 2. Aircraft Variant (Exactly One Required)

Each note must contain exactly one of:

- `b737-800`   → Applies only to the 737-800
- `b737-max8`  → Applies only to the 737 MAX 8
- `common`     → Applies identically to both airframes

Rules:

- Do NOT combine variant tags.
- If a value differs between aircraft, create separate NoteIDs.
- Default assumption is `common` unless a documented difference exists.

---

## 3. Content Type (Exactly One Required)

- `limits`
- `flow`
- `maneuver`
- `recall`
- `systems`
- `callouts`

---

## 4. Memory Classification

- `boldface-pending` (default until reviewed)
- `boldface`

Boldface-only study uses the filtered deck.
No duplicate physical deck exists.

---

# Optional Context Tags (Sim + Line Optimized)

These tags exist only if they improve filtering and operational recall.

- `verbatim` → Exact numeric/wording recall required.
- `structural` → Hard red-line airframe or engine limitations.
- `max-delta` → Differences specific to the MAX 8.
- `rvsm` → RVSM regulatory-specific limitations.
- `company-specific` → Company policy differs from Boeing baseline.

Tags that are NOT used:
- performance
- training-only

---

# Limits Workflow (Reset Model)

1. Upload PDF section.
2. ChatGPT generates a complete TSV file from that section.
3. All notes:
   - Fully populated
   - Tagged `unverified`
   - Include exactly one aircraft variant tag
4. File goes into `draft` branch.
5. Manual review + corrections happen in TSV.
6. Merge `draft` → `main`.
7. Import into Anki from `main` only.

---

# Branch Policy

- `draft` = Generated, unverified, in-progress work.
- `main`  = Fully verified, trusted, sim-ready content.

Only verified sections are merged into `main`.

---

# Anki Import Settings

- Note Type → B737 Structured
- Existing Notes → Update
- Match Scope → Note Type
- Separator → Tab

---

This repository is maintained as a controlled training system.

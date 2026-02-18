# B737 Anki Training Deck

Structured, source-controlled Anki deck for B737 training.

---

# Core Philosophy

- No AI trust.
- New AI-generated notes start with the tag: `unverified`.
- Manual verification happens **in the TSV file** (before importing into Anki).
- Only after manual review is content merged from `draft` → `main`.
- **Section numbers (not page numbers)** are used for source references.
- Git repository is the single source of truth.
- Anki is only the delivery mechanism.

Primary goals:
- Sim survival
- Long-term line proficiency

---

# Deck Architecture (Anki)

## Physical Decks (recommended)

- `B737::Limits`
- `B737::Systems`

(You can add more later, e.g., `B737::Flows`, `B737::Callouts`.)

## Filtered Decks (dynamic)

### Boldface (portfolio-wide)
Name: `B737::BOLDFACE`

Filtered search:
`tag:boldface`

### Lights & Switches (portfolio-wide)
Name: `B737::LIGHTS-SWITCHES`

Filtered search:
`tag:lights-switches`

These decks are dynamically built in Anki. No duplicate notes are created.

---

# Repository Structure

Typical folders:

- `limits/`
- `systems/`
- `flows/`
- `callouts/`
- `maneuvers/`
- `recall-items/`

Each TSV file represents one logical unit (e.g., `§18.2.1 Altitude Limits`, `Electrical System`).

---

# TSV Column Format (B737 Structured)

All TSV files must use this exact column order:

1. `NoteID`
2. `Front`
3. `Back`
4. `Source Document`
5. `Source Location`
6. `Verification Notes`
7. `Tags`

**Important:** TSV files in this repo are stored **without a header row** so they can be imported directly into Anki without accidentally creating a “header note”.

Tabs must be used as delimiters.

---

# NoteID Rules

- Must be globally unique.
- Must be stable (do not renumber once imported).
- Use human-readable prefixes by category:
  - Limits: `lim-...`
  - Systems (electrical): `sys-elec-...`

---

# Tag Taxonomy (tight)

## 1) Verification
- `unverified` — present until manually validated in TSV, then removed.

(We do **not** use a `verified` tag; “verified” is the absence of `unverified`.)

## 2) Aircraft Variant (exactly one required)
Exactly one of:
- `common`
- `b737-800`
- `b737-max8`

Rules:
- Do not combine variant tags.
- If a value differs between aircraft, create separate NoteIDs.

## 3) Content Type (at least one required)
Examples:
- `limits`
- `systems`
- `flow`
- `callouts`
- `maneuver`
- `recall`

## 4) Memory Classification (only if applicable)
- `boldface` — only if it is truly a required memory-script item.

## Optional Context Tags (use sparingly)
- `verbatim` — wording/number must be exact.
- `structural` — hard red-line / structural limitation (mostly used in limitations).
- `company-specific` — references company alerts, ops advisory pages, special company data.
- `rvsm` — RVSM-specific tolerances/logic.
- `lights-switches` — switch semantics + indications/annunciations.

---

# Systems Notes Schema

Systems cards are built to support:
A) **What powers / supplies / controls this?**
B) **If X fails, what changes / what is lost / what powers it now?**

## Card patterns

### 1) Power / Supply / Control (PSC)
Front:
- “What powers **[bus/component]** normally?”
- “What supplies **[system]** under **[condition]**?”
- “What controls **[function]**?”

Back:
- One concise relationship (optionally with a condition).

Tags:
- `systems` + variant tag + `unverified` (until validated)
- Add `verbatim` if precision matters

### 2) Failure Effects (X fails → downstream)
Front:
- “If **[source/component]** fails, what changes / what is lost?”
- “With **[condition]**, what powers **[bus]**?”

Back:
- Tight operational consequences, typically 1–3 bullets.
- Include “major loads lost” when the manual clearly lists them (avoid oral-exam essays).

Tags:
- `systems` + variant tag + `unverified`

### 3) Lights & Switches (switch semantics + annunciations)
Front:
- “What does **[switch]** do in **OFF/AUTO/ON/BAT**?”
- “When does **[light/annunciation]** illuminate (GND vs FLT)?”

Back:
- Exact behavior/logic.

Tags:
- `systems` + `lights-switches` + variant tag + `unverified`

### 4) Cluster Cards (allowed)
Use clusters when:
- The source presents a list/table **or**
- The set is logically stable and typically learned as a group.

Keep clusters small and stable.

---

# Branch Policy

- Work happens on `draft`.
- Only verified TSV content is merged to `main`.
- `main` should remain import-ready.

---

# Import Discipline (Anki)

- Always confirm the correct **Note Type** (`B737 Structured`) before import.
- Always confirm the correct **Deck** before import.
- Since TSVs have **no header row**, you do not need a “first row is headers” option.

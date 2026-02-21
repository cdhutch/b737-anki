# FSRS Configuration (Anki) — B737 Systems

**Repo:** `b737-anki`  
**Applies to:** B737 Systems note imports (e.g., `systems-737-electrical.tsv`)  
**Anki version observed:** 25.09.2 (3890e12c)  
**Purpose:** Provide a *version-controlled* reference for FSRS + study preset settings. This file is the source of truth; Anki is configured manually to match.

---

## 0) Policy and guardrails

- **Do not attempt to automate FSRS settings via AnkiConnect.** Use AnkiConnect for note import/update only.
- Keep **one preset per “study regime”** (e.g., *Training Intensive* vs *Normal Maintenance*).
- Run **FSRS Optimize** only after you have enough reviews (rule of thumb: **≥ 1,000 reviews** on the relevant material, or **2–4 weeks** of consistent use).

---

## 1) Recommended presets

Create **one** preset now:

### Preset A — `B737 Systems (FSRS)`
Use this as the default for:
- your B737 systems deck(s) (starting with the one that holds the imported electrical notes)

**FSRS**
- Scheduler: **FSRS**
- FSRS enabled: **ON**
- Desired retention: **0.88**  
  - Rationale: aggressive enough for training without exploding daily workload.

**New cards / learning**
> Labels may vary by Anki build; the intent is what matters.

- New cards/day: **20** *(adjust to taste)*
- Learning steps: **10m**
- Graduating interval: **1d**
- Easy interval: **4d**

**Reviews**
- Maximum reviews/day: **200** (or “9999” if you prefer no cap)
- Bury related cards: **ON** (same day)
- New cards ignore review limit: **OFF**

**Lapses / relearning**
- Relearning steps: **10m**
- Minimum interval: **1d**
- Leech threshold: **8**
- Leech action: **Tag only** (do not auto-suspend during training)

**Display / ordering (recommended defaults)**
- New card gather order: **Random notes**
- Review sort order: **Descending retrievability** (if available)  
  - Otherwise: **Due date, then random**.

---

## 2) Optional second preset (only if needed)

Add this only if daily load feels too high during a crush period.

### Preset B — `B737 Systems (FSRS — Intensive)`
- Desired retention: **0.92**
- New cards/day: **10**
- Reviews/day: **200–9999**
- Everything else: same as Preset A

Use it temporarily when you want fewer new cards but *tighter* retention on what you do learn.

---

## 3) How to apply (manual steps)

1. In Anki, open **Deck Options** / **Presets**.
2. Create preset named exactly:
   - `B737 Systems (FSRS)`
3. Enable **FSRS** and set **Desired retention = 0.88**.
4. Set learning/relearning steps and caps as specified above.
5. Apply the preset to the deck(s) you want.
6. Confirm:
   - Studying a review card shows FSRS-style scheduling info (e.g., retrievability) where Anki displays it.

> Note: wording/layout differs slightly across Anki builds; match *values and intent* rather than chasing identical UI.

---

## 4) Optimization workflow (later)

After you have enough reviews:

1. Open FSRS settings for the preset.
2. Click **Optimize**.
3. Save the resulting FSRS parameters (Anki will show a parameter vector).
4. Paste them here and commit.

### Optimized parameters (fill later)
- Date optimized:
- Reviews used:
- Parameter vector:
- Notes:

---

## 5) Change log

- 2026-02-21: Initial recommended FSRS preset policy + baseline settings for B737 Systems.

---

## 6) Reminder rule for this repo

Whenever we change:
- card templates (`systems/anki/templates/*.html` / `*.css`), or
- import scripts / TSV schema assumptions,

**also update this file** if the change affects study behavior, scheduling assumptions, or deck/preset mapping.

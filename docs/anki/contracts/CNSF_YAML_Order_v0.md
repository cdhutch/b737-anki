# CNSF v0 — Canonical YAML Front Matter Order

This document defines the **canonical ordering and formatting** for CNSF v0 YAML front matter.

---

## 1. Canonical Top-Level Key Order

Top-level keys MUST appear in this exact order:

1. `schema`
2. `domain`
3. `note_type`
4. `note_id`
5. `anki`
6. `tags`
7. `fields`

No additional top-level keys are allowed in CNSF v0.

---

## 2. Required Key Rules

### `schema`
- Must be exactly: `cnsf/v0`

### `note_id`
- Must use **underscores only**
- Hyphens are NOT allowed
- Example: `b737_limits_weight_800`

---

## 3. Canonical Block Formatting

### Blank Line Rules

Insert **one blank line** after:

- `note_id`
- the `anki` block
- the `tags` block

No trailing whitespace allowed.

---

## 4. `anki` Block Order

The `anki` mapping MUST contain keys in this order:

1. `model`
2. `deck`

Example:

```yaml
anki:
  model: B737_Structured
  deck: "B737::Limits"
```

No additional keys allowed in CNSF v0.

---

## 5. `tags` Block Rules

- Must be a YAML list
- Two-space indentation
- One tag per line
- Unquoted scalars (unless required)

Example:

```yaml
tags:
  - domain:b737
  - model:800
  - topic:limits
  - subtopic:weight
  - source:aom
  - status:unverified
```

---

## 6. `fields` Block Order (Model-Specific)

For `B737_Structured`, the canonical order is:

1. `Source Document`
2. `Source Location`
3. `Verification Notes`

Example:

```yaml
fields:
  Source Document: "B737 AOM Rev 9.0"
  Source Location: "Ch 18 §18.2.3 Weight Limits (Certificated Limits table)"
  Verification Notes: ""
```

---

## 7. Canonical Template

```yaml
---
schema: cnsf/v0
domain: <domain>
note_type: <note_type>
note_id: <note_id>

anki:
  model: <Model_Name>
  deck: "<Deck::Path>"

tags:
  - domain:<domain>
  - ...

fields:
  Source Document: ""
  Source Location: ""
  Verification Notes: ""
---
```

---

## 8. Enforcement

Canonical YAML ordering is enforced via:

- `cnsf_yaml_canonicalize.py`
- CI lint rule (`--check` mode)

Any drift from canonical order must fail validation.

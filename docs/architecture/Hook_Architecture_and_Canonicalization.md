# CNSF Hook Architecture & Canonicalization (Authoritative)

Last Updated: 2026-02-27  
Branch Introduced: `feature/cnsf-l1-l2`

---

## Purpose

This document explains:

1. How CNSF YAML canonicalization is enforced.
2. How pre-commit is wired using `.githooks`.
3. How L1 → L2 rendering integrates with validation.
4. How to reproduce this setup on another machine.

This file exists specifically so that:

- Future Craig understands the system quickly.
- Future ChatGPT sessions have a reliable architectural reference.
- Canonicalization and hooks are not accidentally removed.

---

## High-Level Pipeline

L1  CNSF Markdown (domains/.../anki/notes/*.md)
    ↓
Canonicalization + Lint
    tools/anki/cnsf_canonicalize.py
    (enforced via pre-commit)
    ↓
L2  HTML Rendering
    tools/anki/md_to_html_mmd.py
    ↓
Generated HTML
    domains/.../anki/generated/
    ↓
Future: L3 AnkiConnect import

---

## YAML Canonicalization

Authoritative YAML ordering is defined in:

docs/anki/contracts/CNSF_YAML_Order_v0.md

Enforcement tool:

tools/anki/cnsf_canonicalize.py

The hook runs in check mode during commit:

python -m tools.anki.cnsf_canonicalize --check

If YAML key ordering drifts:

- Commit fails
- Developer must run canonicalizer
- Drift is corrected

This guarantees deterministic diffs.

---

## Pre-Commit Architecture

We intentionally use:

core.hooksPath = .githooks

This avoids modifying `.git/hooks` and keeps hooks version-controlled.

Git config location:

.git/config

Hook entrypoint:

.githooks/pre-commit

That script executes:

pre-commit run --all-files --hook-stage commit

Pre-commit configuration:

.pre-commit-config.yaml

The CNSF hook is defined as:

- language: python
- additional_dependencies: pyyaml
- files: domains/.../anki/notes/*.md

Pre-commit manages its own virtual environment automatically.

---

## Why We Did This

We want:

- Deterministic YAML ordering
- Enforced canonical structure
- No accidental schema drift
- Stable L1 → L2 pipeline
- Predictable Git diffs
- Reproducible setup on any machine

---

## Do NOT

- Do not unset core.hooksPath
- Do not remove .githooks/pre-commit
- Do not switch hook to language: system
- Do not merge unverified TSV into main

---

## If Hooks Fail

Run:

pre-commit run --all-files

If missing dependency errors appear:

pre-commit install-hooks

---

## This Document is Authoritative

Future ChatGPT sessions should treat this file as the single source of truth for:

- Hook architecture
- YAML canonicalization enforcement
- L1 → L2 validation flow

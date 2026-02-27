# Anki CNSF Development Environment Bootstrap

This document recreates the CNSF pipeline on a new machine.

Authoritative as of 2026-02-27.

---

## 1. Install Homebrew (macOS)

If not installed:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

---

## 2. Install Required Packages

brew install pre-commit
brew install multimarkdown

Verify:

pre-commit --version
multimarkdown --version

---

## 3. Clone Repository

git clone https://github.com/cdhutch/anki.git
cd anki

---

## 4. Ensure hooksPath is configured

Check:

git config --get core.hooksPath

Expected:

.githooks

If missing:

git config core.hooksPath .githooks

---

## 5. Initialize Pre-Commit Environments

pre-commit install-hooks

Do NOT run `pre-commit install` if hooksPath is already set.

---

## 6. Verify Hook Works

pre-commit run --all-files

Expected:

CNSF canonical YAML order .... Passed

---

## 7. Verify L1 → L2 Rendering

python -m tools.anki.md_to_html_mmd domains/.../note.md

---

## 8. Environment Summary

Required tools:

- git
- pre-commit
- multimarkdown
- python 3.10+ (system or brew)

---

## Optional (Future)

When L3 is implemented:

- Install Anki
- Enable AnkiConnect

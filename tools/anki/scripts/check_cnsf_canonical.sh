#!/usr/bin/env bash
set -euo pipefail

# Check all CNSF notes are canonicalized (YAML order + normalization).
python3 -m tools.anki.cnsf_canonicalize --check domains/*/anki/notes/**/*.md 2>/dev/null \
  || python3 -m tools.anki.cnsf_canonicalize --check $(git ls-files 'domains/*/anki/notes/**/*.md')

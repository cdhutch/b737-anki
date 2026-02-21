#!/opt/homebrew/bin/bash
set -euo pipefail

# concat_tsv_lenient.sh
#
# Always builds a combined TSV, even if some lines don't have 7 columns.
# Still prints warnings and writes a report file.
#
# Usage:
#   ./concat_tsv_lenient.sh limits
#   ./concat_tsv_lenient.sh limits --dry-run
#   ./concat_tsv_lenient.sh limits --out /tmp/limits_all.tsv
#   ./concat_tsv_lenient.sh limits --no-normalize   # don't touch source files

EXPECTED_COLS=7
echo "DEBUG: EXPECTED_COLS=${EXPECTED_COLS}" >&2
SKIP_SUBSTR="proto"
DRY_RUN=0
OUT=""
NORMALIZE=1

die() { echo "ERROR: $*" >&2; exit 1; }

if [[ $# -lt 1 ]]; then
  die "Provide a folder path. Example: ./concat_tsv_lenient.sh limits"
fi

FOLDER="$1"
shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --out)
      shift
      [[ $# -gt 0 ]] || die "--out requires a path"
      OUT="$1"
      shift
      ;;
    --no-normalize) NORMALIZE=0; shift ;;
    *)
      die "Unknown arg: $1"
      ;;
  esac
done

[[ -d "$FOLDER" ]] || die "Not a directory: $FOLDER"

if [[ -z "$OUT" ]]; then
  base="$(basename "$FOLDER")"
  ts="$(date +%Y%m%d_%H%M%S)"
  OUT="/tmp/${base}_combined_${ts}.tsv"
fi

REPORT="${OUT%.tsv}.lint.txt"

mapfile -t FILES < <(
  find "$FOLDER" -maxdepth 1 -type f -name '*.tsv' \
    ! -name "*${SKIP_SUBSTR}*" \
  | LC_ALL=C sort
)

if [[ ${#FILES[@]} -eq 0 ]]; then
  die "No .tsv files found in '$FOLDER' (after skipping '*${SKIP_SUBSTR}*')."
fi

echo "Folder:         $FOLDER"
echo "Skip pattern:   *${SKIP_SUBSTR}*"
echo "Expected cols:  ${EXPECTED_COLS}"
echo "Normalize:      $([[ $NORMALIZE -eq 1 ]] && echo yes || echo no)"
echo "Output:         $OUT"
echo "Report:         $REPORT"
echo "Files:"
for f in "${FILES[@]}"; do
  echo "  - $f"
done

if [[ $DRY_RUN -eq 1 ]]; then
  echo
  echo "DRY RUN: No files will be modified and no output will be written."
  exit 0
fi

# Start fresh output + report
: > "$OUT"
: > "$REPORT"

for f in "${FILES[@]}"; do
  if [[ $NORMALIZE -eq 1 ]]; then
    # Remove CR characters (CRLF -> LF and stray CR)
    sed -i '' $'s/\r$//' "$f"

    # Ensure trailing newline
    if [[ -s "$f" ]]; then
      last_byte="$(tail -c 1 "$f" || true)"
      if [[ "$last_byte" != $'\n' ]]; then
        printf '\n' >> "$f"
      fi
    else
      printf '\n' > "$f"
    fi
  fi

  # Lint (lenient): print + log mismatches, but never fail
  # awk -F'\t' -v exp="$EXPECTED_COLS" '
  awk -F $'\t' -v expected_cols="${EXPECTED_COLS}" '
    NF==0 { next }
    NF!=expected_cols {
      msg=sprintf("TSV column count mismatch: %s:%d (got %d, expected %d)", FILENAME, NR, NF, exp)
      print msg > "/dev/stderr"
      print msg
      bad=1
    }
    END { exit(0) }
  ' "$f" >> "$REPORT" || true

  # Append to combined output regardless
  cat "$f" >> "$OUT"
done

echo
echo "OK: Wrote combined TSV:"
echo "  $OUT"
echo "OK: Wrote lint report:"
echo "  $REPORT"

# Useful post-check summaries (non-fatal)
echo
echo "Summary:"
echo "  Lines in combined TSV: $(wc -l < "$OUT" | tr -d ' ')"
echo "  Mismatch warnings:     $(grep -c '^TSV column count mismatch:' "$REPORT" || true)"
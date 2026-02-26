from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

MANAGED_PREFIXES = ("src:", "topic:", "wf:")

# Split on semicolons; allow users to type commas too, but semicolon is canonical.
_SPLIT_RE = re.compile(r"[;]+")

# Characters Anki tags don't like: spaces. We'll normalize spaces to underscores.
# Keep Unicode (e.g., яблуко) and colons (:) because those are allowed and useful.
_SPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class TagSpec:
    managed_prefixes: tuple[str, ...] = MANAGED_PREFIXES
    default_topic_prefix: str = "topic:"
    source_prefix: str = "src:"


def _normalize_tag_atom(s: str) -> str:
    """
    Normalize a single tag atom into an Anki-safe tag string.
    - trims
    - collapses internal whitespace to underscores
    - strips leading/trailing underscores
    """
    s = s.strip()
    if not s:
        return ""
    s = _SPACE_RE.sub("_", s)
    s = s.strip("_")
    return s


def parse_canonical_tags(raw: str | None) -> list[str]:
    """
    Parse canonical Tags_Ch text into a list of tokens.
    Canonical separator: semicolon.
    """
    if not raw:
        return []
    # tolerate commas by converting to semicolons (optional convenience)
    raw = raw.replace(",", ";")
    parts = [p.strip() for p in _SPLIT_RE.split(raw) if p.strip()]
    return parts


def canonical_to_managed_anki_tags(tokens: Iterable[str], spec: TagSpec = TagSpec()) -> list[str]:
    """
    Convert canonical tokens into namespaced Anki tags.
    Rules:
      - textbook:* and ch:* -> src:textbook:* / src:ch:*
      - wf:* stays wf:*
      - topic:* stays topic:*
      - src:* stays src:*
      - bare token -> topic:<token>
    """
    out: list[str] = []
    for t in tokens:
        t = t.strip()
        if not t:
            continue

        # Already namespaced?
        if t.startswith("src:") or t.startswith("topic:") or t.startswith("wf:"):
            tag = _normalize_tag_atom(t)
            if tag:
                out.append(tag)
            continue

        # Source shortcuts (canonical, no src: prefix)
        if t.startswith("textbook:") or t.startswith("ch:"):
            tag = _normalize_tag_atom(spec.source_prefix + t)
            if tag:
                out.append(tag)
            continue

        # Default: treat as topic
        tag = _normalize_tag_atom(spec.default_topic_prefix + t)
        if tag:
            out.append(tag)

    # Dedupe while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for x in out:
        if x not in seen:
            seen.add(x)
            deduped.append(x)
    return deduped


def strip_managed_tags(existing: Iterable[str], spec: TagSpec = TagSpec()) -> list[str]:
    """
    Remove tags under managed prefixes (src:/topic:/wf:), leaving manual tags.
    """
    kept: list[str] = []
    for t in existing:
        if any(t.startswith(p) for p in spec.managed_prefixes):
            continue
        kept.append(t)
    return kept

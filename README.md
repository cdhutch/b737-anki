# B737 Anki Training Deck

Structured, source-controlled Anki deck for B737 training.

------------------------------------------------------------------------

## Philosophy

-   No AI-trust.
-   Every note is tagged `unverified` by default.
-   Nothing is considered correct until independently verified.
-   All notes must include a precise source reference.
-   Git repository is the single source of truth.
-   Anki is only the delivery mechanism.

------------------------------------------------------------------------

## Repository Structure

flows/ limits/ maneuvers/ recall-items/ systems/

Each TSV file represents one logical unit (e.g., a single flow or limits
subsection).

------------------------------------------------------------------------

## TSV Column Format

All TSV files must use this exact column order:

Front\
Back\
Source Document\
Source Location\
Verification Notes\
Tags

Tabs must be used as delimiters.

------------------------------------------------------------------------

## Tagging Rules

All new notes must include:

-   `unverified`
-   Aircraft variant tag (e.g., `b737-800`)
-   Content type tag (`limits`, `flow`, `maneuver`, etc.)
-   `verbatim` when exact wording or numbers are required

Example tag string:

`unverified b737-800 limits verbatim`

------------------------------------------------------------------------

## Verification Workflow

1.  Verify against the authoritative source document (AOM, QRH, NPC).
2.  Replace any placeholder values.
3.  Remove the `unverified` tag.
4.  Add `verified`.
5.  Optionally document confirmation details in the "Verification Notes"
    field.

Nothing is assumed correct until verified.

------------------------------------------------------------------------

## Anki Import Settings

-   File → Import → TSV
-   Map columns correctly
-   Enable "Tags in last field"
-   Allow HTML (if formatting is later used)

------------------------------------------------------------------------

This repository is maintained as a controlled training system.

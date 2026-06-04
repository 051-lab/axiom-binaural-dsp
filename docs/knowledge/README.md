# Axiom Knowledge

Axiom Knowledge is the research and bibliography space for DSP, hearing,
psychoacoustics, music playback, JDSP behavior, testing methodology, and
device behavior.

It has two layers:

- repo-safe notes under `docs/knowledge/`;
- local-only source metadata under
  `~/.local/share/axiom-knowledge/source-index.json`.

This directory should contain citations, short summaries, concept maps, and
Axiom-specific research questions. It must not contain copyrighted books,
long copied excerpts, private library paths, source audio, or licensed material
that cannot be redistributed.

## Note Types

Use these lightweight note types:

- bibliography entry: source metadata and why it may matter to Axiom;
- concept note: short explanation of a concept and how it might affect tests;
- research question: a question that needs a diagnostic, fixture, or listening
  protocol;
- advisory review summary: normalized feedback from an external LLM or human
  reviewer.

## Source Rules

Allowed:

- title, author, publisher, year, edition, ISBN, DOI, or URL;
- short summaries in original wording;
- links to lawful public pages;
- notes about which Axiom test or profile the source may inform.

Forbidden:

- full book chapters;
- long copied excerpts;
- private file paths;
- paywalled text copied into the repo;
- claims that a source proves Axiom behavior without measurement.

## Local Source Index

Use the local source index for private books, PDFs, library files, or personal
research material that must not enter git. The schema is tracked at
`source-index.schema.json`, but the actual index lives outside the repository:

```text
~/.local/share/axiom-knowledge/source-index.json
```

The Codex helper can search repo-safe notes and sanitized local metadata:

```bash
python3 tools/axiom-codex/axiom_codex.py knowledge-query "psychoacoustics"
```

By default, the helper does not print private `localPath` values.

## Suggested Categories

| Category | Example Use |
| --- | --- |
| DSP fundamentals | Filters, transforms, envelopes, dynamics, nonlinear stages. |
| Psychoacoustics | Loudness, masking, spatial hearing, fatigue, bass perception. |
| Music and mixing | Translation, genre stress cases, arrangement density. |
| Audio devices | Speakers, headphones, earbuds, Bluetooth, Android routing. |
| Measurement | Repeatability, proxy metrics, listening-test design. |
| JDSP and EEL2 | Host behavior, Liveprog constraints, preset interaction. |

## Bibliography Entry Template

```markdown
# Source Title

Type: book | paper | article | documentation | video | other
Author:
Year:
Publisher or venue:
Identifier or URL:
Access notes:

## Why It Matters

Short explanation of the Axiom-relevant idea.

## Concepts

- concept:
- concept:

## Possible Axiom Follow-Up

- research question:
- diagnostic or fixture:
- affected area: Core | Labs | Knowledge | Qualification | docs

## Boundaries

Do not copy protected source text. This note is a summary, not evidence that
Axiom behaves a certain way.
```

For new notes, copy `templates/source-note.md` and keep the wording original.

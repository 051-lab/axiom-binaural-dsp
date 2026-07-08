# Axiom Knowledge Policy

Axiom Knowledge has two layers:

1. Repo-safe public notes under `docs/knowledge/`.
2. Local-only PDFs and source metadata under ignored files in
   `docs/knowledge/`.

## Repo-Safe Notes

Allowed:

- citation metadata;
- short summaries in original wording;
- concept maps;
- public URLs;
- Axiom relevance notes;
- test-design questions.

Forbidden:

- copyrighted books or chapters;
- long copied excerpts;
- private library paths;
- source audio;
- claims that research proves Axiom behavior.

## Local-Only Source Index

The local index may include paths to books, PDFs, notes, or local research
files. It lives at `docs/knowledge/source-index.local.json` for easy access
from the repository, but it is ignored by git and must never be committed.

Local PDFs belong under `docs/knowledge/pdfs/`, also ignored by git. Prefer
normalized source-ID filenames such as
`spatial-sound-principles-and-applications-xie.pdf`.

Use relative local source paths from `docs/knowledge/` when possible.

Minimum source fields:

```json
{
  "id": "unique-source-id",
  "title": "Source title",
  "authors": ["Author"],
  "year": 2026,
  "type": "book | paper | article | documentation | video | other",
  "topics": ["psychoacoustics", "DSP"],
  "local source path": "pdfs/unique-source-id.pdf",
  "publicUrl": "",
  "licenseNotes": "Do not copy source text.",
  "axiomUse": "How this may inform Axiom tests.",
  "status": "unread | reading | summarized | rejected"
}
```

## Query Rule

When returning Knowledge results, summarize concepts and cite note/source IDs.
Do not print private `localPath` values unless the user explicitly asks for a
local-only inventory audit.

## External Open-Source Code Repositories

Public source repositories such as Airwindows may be indexed only as
repo-external source material. Keep local checkouts and generated indexes
outside git. Repo-safe notes may include citation metadata, license notes,
short original summaries, concept tags, and test-design questions.

Default to clean-room concept extraction even when the upstream license permits
reuse. Do not copy source code, comments, constants, distinctive structure, or
translated implementation logic into Axiom without a separate provenance and
license review. Open-source concepts may start a Labs question; they do not
justify candidate creation or accepted-baseline changes.

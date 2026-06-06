# Axiom Knowledge Policy

Axiom Knowledge has two layers:

1. Repo-safe public notes under `docs/knowledge/`.
2. Local-only source index under
   `~/.local/share/axiom-knowledge/source-index.json`.

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

The local index may include private paths to books, PDFs, notes, or local
research files. It must never be committed.

Minimum source fields:

```json
{
  "id": "unique-source-id",
  "title": "Source title",
  "authors": ["Author"],
  "year": 2026,
  "type": "book | paper | article | documentation | video | other",
  "topics": ["psychoacoustics", "DSP"],
  "localPath": "/private/path/outside/repo",
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

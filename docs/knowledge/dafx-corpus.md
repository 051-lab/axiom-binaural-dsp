# DAFx Open-Access Corpus

The International Conference on Digital Audio Effects (DAFx) has made its
peer-reviewed papers open access from the beginning. The official site provides
one complete proceedings ZIP for every conference from 1998 through 2025.

Axiom treats these papers as a local research corpus. PDFs are not committed to
Git. The repository tracks the verified proceedings catalog and an importer that
builds the ignored local shelf and merges records into the existing local source
index.

## Import

From the repository root:

```bash
python3 scripts/import_dafx_corpus.py --dry-run
python3 scripts/import_dafx_corpus.py
```

To test or refresh one conference:

```bash
python3 scripts/import_dafx_corpus.py --year 2025
```

Use `--force` only to replace PDFs already present. Downloads are written to a
temporary directory, checked as ZIP archives, restricted to safe PDF members,
and removed after extraction.

## Outputs

- PDFs: `docs/knowledge/pdfs/dafx-<year>-<source-name>.pdf`
- local metadata: `docs/knowledge/source-index.local.json`
- tracked archive catalog: `docs/knowledge/dafx-proceedings.json`

Both the PDFs and local index remain ignored by Git according to the existing
knowledge policy.

The importer uses the same normalized filename and source-ID convention as the
existing local shelf. Re-running it preserves already indexed local records and
does not create a parallel DAFx corpus.

## Agent Use

Imported entries begin as `unread` and deliberately carry broad tags. An agent
must read the relevant paper, create an original repo-safe summary or concept
note, and connect claims to a specific Axiom research question or validation
fixture before using the paper as design evidence. Open access does not mean
that full papers should be copied into prompts, commits, or generated notes.

The catalog's `lastVerified` date records when the official links were checked.
DAFx 2026 is not included because its conference is scheduled for September
2026 and no proceedings archive was available when this catalog was created.

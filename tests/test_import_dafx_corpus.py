"""Regression tests for the local-only DAFx corpus importer."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPORTER_PATH = REPO_ROOT / "scripts" / "import_dafx_corpus.py"


def load_importer():
    spec = importlib.util.spec_from_file_location("import_dafx_corpus", IMPORTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load DAFx importer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


import_dafx_corpus = load_importer()


class DAFxCorpusImporterTests(unittest.TestCase):
    def test_output_path_matches_established_local_convention(self) -> None:
        output = import_dafx_corpus.output_path(
            Path("/tmp/shelf"), 2010, "2010_LazzariniCarty_DAFx10_P19.pdf"
        )
        self.assertEqual(output.name, "dafx-2010-2010-lazzarinicarty-dafx10-p19.pdf")

    def test_safe_pdf_members_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "unsafe.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../outside.pdf", b"not a real PDF")
            with zipfile.ZipFile(archive_path) as archive:
                with self.assertRaises(ValueError):
                    list(import_dafx_corpus.safe_pdf_members(archive))

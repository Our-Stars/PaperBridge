from __future__ import annotations

from pathlib import Path

from paperbridge.models import Document, Summary


def export_json(document: Document, path: Path) -> None:
    path.write_text(document.model_dump_json(indent=2), encoding="utf-8")


def export_summary(summary: Summary, path: Path) -> None:
    path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")


def load_document(path: Path) -> Document:
    return Document.model_validate_json(path.read_text(encoding="utf-8"))


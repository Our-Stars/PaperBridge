from __future__ import annotations

from paperbridge.models import Document, SourceInfo


def test_document_schema_round_trips():
    document = Document(source=SourceInfo(pdf_path="paper.pdf", file_name="paper.pdf", page_count=1))
    payload = document.model_dump_json()
    loaded = Document.model_validate_json(payload)

    assert loaded.schema_version == "0.1.0"
    assert loaded.source.file_name == "paper.pdf"


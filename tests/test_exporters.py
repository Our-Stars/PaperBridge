from __future__ import annotations

from paperbridge.exporters.docx_exporter import export_docx
from paperbridge.exporters.markdown_exporter import export_markdown
from paperbridge.exporters.txt_exporter import export_txt
from paperbridge.models import BodyBlock, Document, Figure, SourceInfo


def _document() -> Document:
    return Document(
        source=SourceInfo(pdf_path="paper.pdf", file_name="paper.pdf", page_count=1),
        body_blocks=[
            BodyBlock(
                id="b_0001",
                type="title",
                text="Sample Paper",
                page_start=1,
                page_end=1,
                source_block_ids=["p1_raw_001"],
                bbox=[0.1, 0.1, 0.9, 0.15],
                reading_order=1,
            ),
            BodyBlock(
                id="b_0002",
                type="caption",
                text="Figure 1. Example figure.",
                page_start=1,
                page_end=1,
                source_block_ids=["p1_raw_002"],
                bbox=[0.1, 0.5, 0.9, 0.55],
                reading_order=2,
            ),
        ],
        figures=[
            Figure(
                id="fig_001",
                label="Figure 1",
                source_page=1,
                image_path=None,
                caption="Figure 1. Example figure.",
                caption_block_id="b_0002",
            )
        ],
    )


def test_markdown_and_txt_exporters(tmp_path):
    document = _document()
    markdown_path = tmp_path / "paper.md"
    txt_path = tmp_path / "paper.txt"

    export_markdown(document, markdown_path)
    export_txt(document, txt_path)

    assert "# Sample Paper" in markdown_path.read_text(encoding="utf-8")
    assert "[FIGURE fig_001]" in txt_path.read_text(encoding="utf-8")


def test_docx_exporter(tmp_path):
    path = tmp_path / "paper.docx"
    export_docx(_document(), path, tmp_path)

    assert path.exists()
    assert path.stat().st_size > 0


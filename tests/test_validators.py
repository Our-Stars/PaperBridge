from __future__ import annotations

from paperbridge.models import Document, Figure, Page, SourceInfo
from paperbridge.validators import validate_output


def test_validator_reports_missing_image(tmp_path):
    document = Document(
        source=SourceInfo(pdf_path="paper.pdf", file_name="paper.pdf", page_count=1),
        pages=[Page(number=1, width=100, height=100, has_text_layer=True, raw_block_ids=[])],
        figures=[Figure(id="fig_001", source_page=1, image_path="assets/figures/missing.png")],
    )

    report = validate_output(document, tmp_path)

    assert report.status == "error"
    assert any(issue.code == "FIGURE_IMAGE_MISSING" for issue in report.errors)


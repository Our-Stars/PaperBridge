from __future__ import annotations

import fitz

from paperbridge.text_extractor import extract_raw_blocks
from tests.make_sample_pdf import create_sample_pdf


def test_extract_raw_blocks_normalizes_bbox(tmp_path):
    pdf_path = create_sample_pdf(tmp_path / "sample.pdf")
    with fitz.open(pdf_path) as doc:
        blocks = extract_raw_blocks(doc[0], 1)

    assert blocks
    assert any("PaperBridge Sample Paper" in block.text for block in blocks)
    for block in blocks:
        assert len(block.bbox) == 4
        assert all(0 <= value <= 1 for value in block.bbox)


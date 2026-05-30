from __future__ import annotations

import json

from paperbridge.config import ConvertOptions
from paperbridge.conversion import convert_pdf
from paperbridge.exporters.json_exporter import load_document
from tests.make_sample_pdf import create_sample_pdf


def test_convert_pdf_outputs_mvp_files(tmp_path):
    pdf_path = create_sample_pdf(tmp_path / "sample.pdf")
    out_dir = tmp_path / "out"

    result = convert_pdf(
        pdf_path,
        out_dir,
        ConvertOptions(formats={"json", "md", "txt", "docx"}, use_llm=False, debug=True, force=True),
    )

    assert result.status in {"success", "warning"}
    assert (out_dir / "paper.json").exists()
    assert (out_dir / "paper.md").exists()
    assert (out_dir / "paper.txt").exists()
    assert (out_dir / "paper.docx").exists()
    assert (out_dir / "summary.json").exists()
    assert (out_dir / "assets" / "pages" / "page_001.png").exists()
    assert (out_dir / "debug" / "raw_blocks.json").exists()

    document = load_document(out_dir / "paper.json")
    assert document.metadata.title
    assert document.figures
    assert document.tables
    assert any(block.type == "reference_item" for block in document.body_blocks)

    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["stats"]["pages"] == 1


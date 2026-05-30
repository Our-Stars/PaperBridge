from __future__ import annotations

from paperbridge.config import ConvertOptions
from paperbridge.conversion import convert_pdf
from paperbridge.llm.mock_provider import MockProvider
from paperbridge.exporters.json_exporter import load_document
from tests.make_sample_pdf import create_sample_pdf


def test_llm_failure_falls_back_to_rules(tmp_path):
    pdf_path = create_sample_pdf(tmp_path / "sample.pdf")
    out_dir = tmp_path / "out"
    provider = MockProvider(fail=True)

    result = convert_pdf(
        pdf_path,
        out_dir,
        ConvertOptions(formats={"json"}, use_llm=True, use_vlm=False, force=True),
        llm_provider=provider,
    )
    document = load_document(out_dir / "paper.json")

    assert result.status in {"warning", "success"}
    assert provider.calls >= 2
    assert any(warning.code == "LLM_PAGE_STRUCTURE_FAILED" for warning in document.warnings)
    assert document.body_blocks


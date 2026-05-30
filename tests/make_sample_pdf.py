from __future__ import annotations

from pathlib import Path

import fitz


def create_sample_pdf(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 72), "PaperBridge Sample Paper", fontsize=22, fontname="helv")
    page.insert_text((72, 112), "Abstract", fontsize=14, fontname="helv")
    page.insert_textbox(
        fitz.Rect(72, 132, 540, 188),
        "This paper demonstrates a text-layer PDF with a figure caption, a table caption, and references.",
        fontsize=11,
        fontname="helv",
    )
    page.insert_text((72, 220), "1 Introduction", fontsize=15, fontname="helv")
    page.insert_textbox(
        fitz.Rect(72, 244, 540, 318),
        "PaperBridge converts academic PDFs into JSON, Markdown, TXT, and DOCX outputs. "
        "As shown in Figure 1, the pipeline keeps assets separate from text.",
        fontsize=11,
        fontname="helv",
    )
    page.draw_rect(fitz.Rect(150, 340, 462, 455), color=(0.1, 0.2, 0.6), fill=(0.85, 0.9, 1.0))
    page.insert_text((230, 402), "Pipeline diagram", fontsize=12, fontname="helv")
    page.insert_textbox(
        fitz.Rect(72, 470, 540, 510),
        "Figure 1. Overview of the proposed PaperBridge conversion pipeline.",
        fontsize=10,
        fontname="helv",
    )
    page.insert_text((72, 545), "Table 1. Comparison of output formats.", fontsize=10, fontname="helv")
    page.insert_text((92, 578), "Format     Editable     LLM Friendly", fontsize=10, fontname="cour")
    page.insert_text((92, 598), "JSON       No           Yes", fontsize=10, fontname="cour")
    page.insert_text((92, 618), "DOCX       Yes          Partial", fontsize=10, fontname="cour")
    page.insert_text((72, 680), "References", fontsize=14, fontname="helv")
    page.insert_textbox(
        fitz.Rect(72, 704, 540, 742),
        "[1] A. Example. Structured PDF conversion for research agents. 2026.",
        fontsize=10,
        fontname="helv",
    )
    doc.save(path)
    doc.close()
    return path


if __name__ == "__main__":
    create_sample_pdf(Path(__file__).parent / "fixtures" / "sample.pdf")


from __future__ import annotations

from pathlib import Path

import fitz


def open_pdf(pdf_path: Path) -> fitz.Document:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {pdf_path}")
    return fitz.open(pdf_path)


def inspect_pdf(pdf_path: Path) -> dict[str, object]:
    with open_pdf(pdf_path) as doc:
        pages: list[dict[str, object]] = []
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            pages.append(
                {
                    "page": index,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "has_text_layer": bool(text),
                    "text_length": len(text),
                    "image_count": len(page.get_images(full=True)),
                }
            )
        return {
            "pdf_path": str(pdf_path),
            "file_name": pdf_path.name,
            "page_count": doc.page_count,
            "metadata": dict(doc.metadata or {}),
            "pages": pages,
        }


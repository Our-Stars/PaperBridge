from __future__ import annotations

from pathlib import Path

import fitz

from paperbridge.models import BodyBlock, Figure, PaperWarning
from paperbridge.page_renderer import crop_page_region
from paperbridge.utils.bbox import denormalize_bbox, normalize_bbox
from paperbridge.utils.text import caption_kind, caption_label


def detect_figures(
    pdf: fitz.Document,
    body_blocks: list[BodyBlock],
    out_dir: Path,
    dpi: int,
    warnings: list[PaperWarning],
) -> list[Figure]:
    figures: list[Figure] = []
    seen_rects: set[tuple[int, int, int, int, int]] = set()

    for page_index, page in enumerate(pdf, start=1):
        if not page.get_text("text").strip():
            continue
        page_area = page.rect.width * page.rect.height
        for image in page.get_images(full=True):
            xref = image[0]
            for rect in page.get_image_rects(xref):
                if rect.is_empty or rect.width * rect.height < page_area * 0.015:
                    continue
                rect_key = (
                    page_index,
                    round(rect.x0),
                    round(rect.y0),
                    round(rect.x1),
                    round(rect.y1),
                )
                if rect_key in seen_rects:
                    continue
                seen_rects.add(rect_key)

                figure_id = f"fig_{len(figures) + 1:03d}"
                try:
                    image_path = crop_page_region(
                        page,
                        out_dir,
                        "assets/figures",
                        f"{figure_id}_page_{page_index:03d}.png",
                        rect,
                        dpi,
                    )
                except Exception as exc:  # pragma: no cover - depends on malformed PDFs
                    warnings.append(
                        PaperWarning(
                            code="FIGURE_CROP_FAILED",
                            message=f"Failed to crop figure candidate {figure_id}: {exc}",
                            page=page_index,
                        )
                    )
                    image_path = None

                figures.append(
                    Figure(
                        id=figure_id,
                        source_page=page_index,
                        bbox=normalize_bbox((rect.x0, rect.y0, rect.x1, rect.y1), page.rect.width, page.rect.height),
                        image_path=image_path,
                    )
                )

    _add_caption_fallback_figures(pdf, body_blocks, out_dir, dpi, warnings, figures)
    return figures


def _add_caption_fallback_figures(
    pdf: fitz.Document,
    body_blocks: list[BodyBlock],
    out_dir: Path,
    dpi: int,
    warnings: list[PaperWarning],
    figures: list[Figure],
) -> None:
    caption_blocks = [block for block in body_blocks if block.type == "caption" and caption_kind(block.text) == "figure"]
    for caption in caption_blocks:
        if any(item.source_page == caption.page_start and item.caption_block_id == caption.id for item in figures):
            continue
        if any(item.source_page == caption.page_start and item.caption is None for item in figures):
            continue

        page = pdf[caption.page_start - 1]
        rect = _fallback_rect(page, caption)
        figure_id = f"fig_{len(figures) + 1:03d}"
        try:
            image_path = crop_page_region(
                page,
                out_dir,
                "assets/figures",
                f"{figure_id}_page_{caption.page_start:03d}.png",
                rect,
                dpi,
            )
        except Exception as exc:  # pragma: no cover - depends on malformed PDFs
            warnings.append(
                PaperWarning(
                    code="FIGURE_CROP_FAILED",
                    message=f"Failed to crop fallback figure {figure_id}: {exc}",
                    page=caption.page_start,
                )
            )
            image_path = None

        figures.append(
            Figure(
                id=figure_id,
                label=caption_label(caption.text),
                source_page=caption.page_start,
                bbox=normalize_bbox((rect.x0, rect.y0, rect.x1, rect.y1), page.rect.width, page.rect.height),
                image_path=image_path,
                caption=caption.text,
                caption_block_id=caption.id,
            )
        )


def _fallback_rect(page: fitz.Page, caption: BodyBlock) -> fitz.Rect:
    if caption.bbox:
        x0, y0, x1, y1 = denormalize_bbox(caption.bbox, page.rect.width, page.rect.height)
    else:
        x0, y0, x1, y1 = (page.rect.width * 0.1, page.rect.height * 0.45, page.rect.width * 0.9, page.rect.height * 0.55)
    caption_mid = (y0 + y1) / 2
    horizontal_margin = page.rect.width * 0.08
    if caption_mid > page.rect.height * 0.5:
        top = max(0, y0 - page.rect.height * 0.35)
        bottom = max(top + 24, y0 - 4)
    else:
        top = min(page.rect.height - 24, y1 + 4)
        bottom = min(page.rect.height, y1 + page.rect.height * 0.35)
    return fitz.Rect(horizontal_margin, top, page.rect.width - horizontal_margin, bottom)

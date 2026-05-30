from __future__ import annotations

import contextlib
import io
from pathlib import Path

import fitz

from paperbridge.models import BodyBlock, PaperWarning, Table
from paperbridge.page_renderer import crop_page_region
from paperbridge.utils.bbox import denormalize_bbox, normalize_bbox
from paperbridge.utils.text import caption_kind, caption_label


def detect_tables(
    pdf: fitz.Document,
    body_blocks: list[BodyBlock],
    out_dir: Path,
    dpi: int,
    warnings: list[PaperWarning],
) -> list[Table]:
    tables: list[Table] = []
    _detect_structured_tables(pdf, out_dir, dpi, warnings, tables)
    _add_caption_fallback_tables(pdf, body_blocks, out_dir, dpi, warnings, tables)
    return tables


def _detect_structured_tables(
    pdf: fitz.Document,
    out_dir: Path,
    dpi: int,
    warnings: list[PaperWarning],
    tables: list[Table],
) -> None:
    for page_index, page in enumerate(pdf, start=1):
        finder = getattr(page, "find_tables", None)
        if finder is None:
            continue
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                found = finder()
        except Exception:
            continue
        for found_table in getattr(found, "tables", []):
            rows = [[_cell_text(cell) for cell in row] for row in found_table.extract()]
            rows = [row for row in rows if any(cell for cell in row)]
            if not _is_useful_table(rows):
                continue
            table_id = f"table_{len(tables) + 1:03d}"
            rect = fitz.Rect(found_table.bbox)
            try:
                image_path = crop_page_region(
                    page,
                    out_dir,
                    "assets/tables",
                    f"{table_id}_page_{page_index:03d}.png",
                    rect,
                    dpi,
                )
            except Exception as exc:  # pragma: no cover - depends on malformed PDFs
                warnings.append(
                    PaperWarning(
                        code="TABLE_CROP_FAILED",
                        message=f"Failed to crop table candidate {table_id}: {exc}",
                        page=page_index,
                    )
                )
                image_path = None

            tables.append(
                Table(
                    id=table_id,
                    source_page=page_index,
                    bbox=normalize_bbox((rect.x0, rect.y0, rect.x1, rect.y1), page.rect.width, page.rect.height),
                    representation="structured",
                    columns=rows[0],
                    rows=rows[1:],
                    image_path=image_path,
                )
            )


def _add_caption_fallback_tables(
    pdf: fitz.Document,
    body_blocks: list[BodyBlock],
    out_dir: Path,
    dpi: int,
    warnings: list[PaperWarning],
    tables: list[Table],
) -> None:
    caption_blocks = [block for block in body_blocks if block.type == "caption" and caption_kind(block.text) == "table"]
    for caption in caption_blocks:
        if any(item.source_page == caption.page_start and item.caption_block_id == caption.id for item in tables):
            continue
        if any(item.source_page == caption.page_start and item.caption is None for item in tables):
            continue

        page = pdf[caption.page_start - 1]
        rect = _fallback_rect(page, caption)
        table_id = f"table_{len(tables) + 1:03d}"
        try:
            image_path = crop_page_region(
                page,
                out_dir,
                "assets/tables",
                f"{table_id}_page_{caption.page_start:03d}.png",
                rect,
                dpi,
            )
        except Exception as exc:  # pragma: no cover - depends on malformed PDFs
            warnings.append(
                PaperWarning(
                    code="TABLE_CROP_FAILED",
                    message=f"Failed to crop fallback table {table_id}: {exc}",
                    page=caption.page_start,
                )
            )
            image_path = None

        tables.append(
            Table(
                id=table_id,
                label=caption_label(caption.text),
                source_page=caption.page_start,
                bbox=normalize_bbox((rect.x0, rect.y0, rect.x1, rect.y1), page.rect.width, page.rect.height),
                caption=caption.text,
                caption_block_id=caption.id,
                representation="image",
                image_path=image_path,
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
        top = max(0, y0 - page.rect.height * 0.25)
        bottom = max(top + 24, y0 - 4)
    else:
        top = min(page.rect.height - 24, y1 + 4)
        bottom = min(page.rect.height, y1 + page.rect.height * 0.25)
    return fitz.Rect(horizontal_margin, top, page.rect.width - horizontal_margin, bottom)


def _cell_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_useful_table(rows: list[list[str]]) -> bool:
    if len(rows) < 2:
        return False
    max_columns = max(len(row) for row in rows)
    if max_columns < 2:
        return False
    non_empty = sum(1 for row in rows for cell in row if cell.strip())
    return non_empty >= 4

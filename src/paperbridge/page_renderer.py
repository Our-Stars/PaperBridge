from __future__ import annotations

from pathlib import Path

import fitz

from paperbridge.utils.paths import relative_to_output


def render_page(page: fitz.Page, out_dir: Path, page_number: int, dpi: int) -> str:
    target = out_dir / "assets" / "pages" / f"page_{page_number:03d}.png"
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    pix.save(target)
    return relative_to_output(target, out_dir)


def crop_page_region(
    page: fitz.Page,
    out_dir: Path,
    relative_folder: str,
    file_name: str,
    rect: fitz.Rect,
    dpi: int,
) -> str:
    target = out_dir / relative_folder / file_name
    target.parent.mkdir(parents=True, exist_ok=True)
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
    pix.save(target)
    return relative_to_output(target, out_dir)


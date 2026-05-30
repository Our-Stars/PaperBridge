from __future__ import annotations

from paperbridge.models import BodyBlock, Figure, Table
from paperbridge.utils.bbox import bbox_center_y
from paperbridge.utils.text import caption_kind, caption_label


def bind_captions(body_blocks: list[BodyBlock], figures: list[Figure], tables: list[Table]) -> None:
    captions = [block for block in body_blocks if block.type == "caption"]
    for caption in captions:
        kind = caption_kind(caption.text)
        if kind == "figure":
            target = _nearest_figure(caption, figures)
            if target:
                target.label = target.label or caption_label(caption.text)
                target.caption = target.caption or caption.text
                target.caption_block_id = target.caption_block_id or caption.id
        elif kind == "table":
            target_table = _nearest_table(caption, tables)
            if target_table:
                target_table.label = target_table.label or caption_label(caption.text)
                target_table.caption = target_table.caption or caption.text
                target_table.caption_block_id = target_table.caption_block_id or caption.id


def _nearest_figure(caption: BodyBlock, figures: list[Figure]) -> Figure | None:
    candidates = [figure for figure in figures if figure.source_page == caption.page_start and figure.caption_block_id is None]
    if not candidates:
        return None
    return min(candidates, key=lambda figure: _vertical_distance(caption, figure.bbox))


def _nearest_table(caption: BodyBlock, tables: list[Table]) -> Table | None:
    candidates = [table for table in tables if table.source_page == caption.page_start and table.caption_block_id is None]
    if not candidates:
        return None
    return min(candidates, key=lambda table: _vertical_distance(caption, table.bbox))


def _vertical_distance(caption: BodyBlock, bbox: list[float] | None) -> float:
    if not caption.bbox or not bbox:
        return 1.0
    return abs(bbox_center_y(caption.bbox) - bbox_center_y(bbox))


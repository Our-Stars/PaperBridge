from __future__ import annotations

from paperbridge.models import BodyBlock, BodyMention, Figure, Table
from paperbridge.utils.text import FIGURE_MENTION_RE, TABLE_MENTION_RE


def bind_body_mentions(body_blocks: list[BodyBlock], figures: list[Figure], tables: list[Table]) -> None:
    figure_by_key = {_label_key(figure.label): figure for figure in figures if figure.label}
    table_by_key = {_label_key(table.label): table for table in tables if table.label}

    for block in body_blocks:
        if block.type not in {"paragraph", "abstract", "reference_item"}:
            continue
        for match in FIGURE_MENTION_RE.finditer(block.text):
            key = f"figure {match.group(1).lower()}"
            figure = figure_by_key.get(key)
            if figure:
                figure.body_mentions.append(
                    BodyMention(block_id=block.id, section_id=block.section_id, text=block.text)
                )
        for match in TABLE_MENTION_RE.finditer(block.text):
            key = f"table {match.group(1).lower()}"
            table = table_by_key.get(key)
            if table:
                table.body_mentions.append(BodyMention(block_id=block.id, section_id=block.section_id, text=block.text))


def _label_key(label: str | None) -> str:
    return " ".join((label or "").lower().replace(".", "").split())


from __future__ import annotations

from pathlib import Path

from paperbridge.models import Document, Figure, Table


def export_txt(document: Document, path: Path) -> None:
    path.write_text(to_txt(document), encoding="utf-8")


def to_txt(document: Document) -> str:
    lines: list[str] = []
    figures_by_caption = {figure.caption_block_id: figure for figure in document.figures if figure.caption_block_id}
    tables_by_caption = {table.caption_block_id: table for table in document.tables if table.caption_block_id}
    emitted_figures: set[str] = set()
    emitted_tables: set[str] = set()

    for block in document.body_blocks:
        if block.id in figures_by_caption:
            _append_figure(lines, figures_by_caption[block.id])
            emitted_figures.add(figures_by_caption[block.id].id)
            continue
        if block.id in tables_by_caption:
            _append_table(lines, tables_by_caption[block.id])
            emitted_tables.add(tables_by_caption[block.id].id)
            continue

        if block.type == "title":
            lines.extend([f"# {document.metadata.title or block.text}", ""])
        elif block.type == "abstract_heading":
            lines.extend(["## Abstract", ""])
        elif block.type == "heading_1":
            lines.extend([f"## {block.text}", ""])
        elif block.type == "heading_2":
            lines.extend([f"### {block.text}", ""])
        elif block.type == "heading_3":
            lines.extend([f"#### {block.text}", ""])
        elif block.type == "reference_heading":
            lines.extend(["## References", ""])
        elif block.type in {"paragraph", "abstract", "reference_item", "list_item", "equation", "unknown"}:
            lines.extend([block.text, ""])

    for figure in document.figures:
        if figure.id not in emitted_figures:
            _append_figure(lines, figure)
    for table in document.tables:
        if table.id not in emitted_tables:
            _append_table(lines, table)

    return "\n".join(lines).strip() + "\n"


def _append_figure(lines: list[str], figure: Figure) -> None:
    lines.extend(
        [
            f"[FIGURE {figure.id}]",
            f"Label: {figure.label or ''}",
            f"Image: {figure.image_path or ''}",
            f"Page: {figure.source_page}",
            f"Caption: {figure.caption or ''}",
            "[/FIGURE]",
            "",
        ]
    )


def _append_table(lines: list[str], table: Table) -> None:
    lines.extend(
        [
            f"[TABLE {table.id}]",
            f"Label: {table.label or ''}",
            f"Page: {table.source_page}",
            f"Caption: {table.caption or ''}",
        ]
    )
    if table.columns:
        lines.append("Columns: " + " | ".join(table.columns))
    for row in table.rows:
        lines.append("Row: " + " | ".join(row))
    if table.image_path:
        lines.append(f"Image: {table.image_path}")
    lines.extend(["[/TABLE]", ""])

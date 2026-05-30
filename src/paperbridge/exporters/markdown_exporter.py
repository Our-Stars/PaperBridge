from __future__ import annotations

from pathlib import Path

from paperbridge.models import Document, Figure, Table


def export_markdown(document: Document, path: Path) -> None:
    path.write_text(to_markdown(document), encoding="utf-8")


def to_markdown(document: Document) -> str:
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
        elif block.type == "subtitle":
            lines.extend([f"*{block.text}*", ""])
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
        elif block.type == "list_item":
            lines.append(f"- {block.text.lstrip('-*• ')}")
        elif block.type == "equation":
            lines.extend(["```text", block.text, "```", ""])
        elif block.type in {"paragraph", "abstract", "reference_item", "unknown"}:
            lines.extend([block.text, ""])

    for figure in document.figures:
        if figure.id not in emitted_figures:
            _append_figure(lines, figure)
    for table in document.tables:
        if table.id not in emitted_tables:
            _append_table(lines, table)

    return _compact_blank_lines(lines)


def _append_figure(lines: list[str], figure: Figure) -> None:
    label = figure.label or figure.id
    if figure.image_path:
        lines.extend([f"![{label}]({figure.image_path})", ""])
    if figure.caption:
        caption = figure.caption
        if figure.label and caption.lower().startswith(figure.label.lower()):
            remainder = caption[len(figure.label) :].lstrip(" .:-")
            lines.extend([f"**{figure.label}.** {remainder}".rstrip(), ""])
        else:
            lines.extend([f"**{label}.** {caption}", ""])


def _append_table(lines: list[str], table: Table) -> None:
    label = table.label or table.id
    if table.representation == "structured" and table.columns:
        lines.append("")
        lines.append(f"**{label}.** {table.caption or ''}".rstrip())
        lines.append("")
        lines.append("| " + " | ".join(_escape_cell(cell) for cell in table.columns) + " |")
        lines.append("| " + " | ".join("---" for _ in table.columns) + " |")
        for row in table.rows:
            padded = row + [""] * max(0, len(table.columns) - len(row))
            lines.append("| " + " | ".join(_escape_cell(cell) for cell in padded[: len(table.columns)]) + " |")
        lines.append("")
    elif table.image_path:
        lines.extend([f"![{label}]({table.image_path})", ""])
        if table.caption:
            lines.extend([f"**{label}.** {table.caption}", ""])
    elif table.caption:
        lines.extend([f"**{label}.** {table.caption}", ""])


def _escape_cell(value: str) -> str:
    return str(value).replace("|", "\\|").strip()


def _compact_blank_lines(lines: list[str]) -> str:
    output: list[str] = []
    blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and blank:
            continue
        output.append(line.rstrip())
        blank = is_blank
    return "\n".join(output).strip() + "\n"

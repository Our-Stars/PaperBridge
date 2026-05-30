from __future__ import annotations

import re
from collections import Counter, defaultdict
from statistics import median

from paperbridge.models import BodyBlock, Document, Metadata, PaperWarning, RawBlock, Reference, Section
from paperbridge.utils.text import (
    NUMBERED_HEADING_RE,
    REFERENCE_ITEM_RE,
    caption_kind,
    clean_text,
    fix_english_hyphenation,
    has_terminal_punctuation,
    is_probable_caption,
)

REFERENCE_CHUNK_RE = re.compile(r"(\d{1,3}\.\s+.*?)(?=\s+\d{1,3}\.\s+|$)")
REFERENCE_NUMBER_RE = re.compile(r"^(\d{1,3})\.\s+")


def build_document_structure(document: Document, raw_blocks: list[RawBlock]) -> Document:
    if not raw_blocks:
        return document

    raw_by_id = {block.id: block for block in raw_blocks}
    header_ids, footer_ids, page_number_ids = _detect_repeating_marginalia(raw_blocks, document.source.page_count)
    title_id = _pick_title_block(raw_blocks, header_ids | footer_ids | page_number_ids)
    font_sizes = [block.font_size for block in raw_blocks if block.font_size]
    median_font_size = median(font_sizes) if font_sizes else 10.0

    blocks: list[BodyBlock] = []
    headers: list[BodyBlock] = []
    footers: list[BodyBlock] = []
    references: list[Reference] = []
    sections: list[Section] = []
    reading_order = 1
    reference_mode = False
    abstract_mode = False
    current_section_id: str | None = None
    reference_index = 1

    for raw in _sort_raw_blocks_for_reading(raw_blocks):
        block_type = "paragraph"
        if raw.id in page_number_ids:
            block_type = "page_number"
        elif raw.id in header_ids:
            block_type = "header"
        elif raw.id in footer_ids:
            block_type = "footer"
        elif raw.id == title_id:
            block_type = "title"
        elif _is_abstract_heading(raw.text):
            block_type = "abstract_heading"
            abstract_mode = True
        elif _is_reference_heading(raw.text):
            block_type = "reference_heading"
            reference_mode = True
            abstract_mode = False
        elif reference_mode:
            block_type = "reference_item" if REFERENCE_ITEM_RE.match(raw.text) else "paragraph"
        elif is_probable_caption(raw.text):
            block_type = "caption"
            abstract_mode = False
        elif abstract_mode and not _looks_like_heading(raw, median_font_size):
            block_type = "abstract"
        elif _looks_like_heading(raw, median_font_size):
            block_type = _heading_type(raw.text)
            abstract_mode = False
        elif _looks_like_list_item(raw.text):
            block_type = "list_item"
        elif _looks_like_equation(raw.text):
            block_type = "equation"

        text = fix_english_hyphenation(raw.text)
        body_block = BodyBlock(
            id=f"b_{reading_order:04d}",
            type=block_type,
            text=text,
            page_start=raw.page,
            page_end=raw.page,
            source_block_ids=[raw.id],
            bbox=raw.bbox,
            section_id=current_section_id,
            reading_order=reading_order,
            confidence=0.86 if block_type in {"heading_1", "heading_2", "heading_3", "title"} else 0.78,
        )
        reading_order += 1

        if block_type in {"header", "page_number"}:
            headers.append(body_block)
            continue
        if block_type == "footer":
            footers.append(body_block)
            continue

        if block_type in {"heading_1", "heading_2", "heading_3", "reference_heading"}:
            level = {"heading_1": 1, "heading_2": 2, "heading_3": 3, "reference_heading": 1}[block_type]
            current_section_id = f"sec_{len(sections) + 1:03d}"
            body_block.section_id = current_section_id
            sections.append(
                Section(
                    id=current_section_id,
                    title=body_block.text,
                    level=level,
                    page_start=body_block.page_start,
                    block_id=body_block.id,
                )
            )
        elif current_section_id and block_type not in {"title", "abstract_heading", "abstract"}:
            body_block.section_id = current_section_id

        if block_type == "reference_item":
            references.append(
                Reference(
                    id=f"ref_{reference_index:04d}",
                    text=body_block.text,
                    source_block_ids=body_block.source_block_ids,
                )
            )
            reference_index += 1

        blocks.append(body_block)

    blocks, references = _split_inline_references(blocks)
    sections = _rebuild_sections(blocks)
    _merge_cross_page_paragraphs(blocks)
    _close_sections(sections, blocks)
    document.body_blocks = blocks
    document.headers = headers
    document.footers = footers
    document.sections = sections
    document.references = references
    document.metadata = _extract_metadata(document.metadata, blocks)

    mapped_ids = {raw_id for block in blocks + headers + footers for raw_id in block.source_block_ids}
    missing_ids = set(raw_by_id) - mapped_ids
    if missing_ids:
        document.warnings.append(
            PaperWarning(
                code="RAW_BLOCK_MAPPING_GAP",
                message=f"{len(missing_ids)} raw text blocks were not mapped into the document structure.",
                severity="warning",
            )
        )
    return document


def _detect_repeating_marginalia(raw_blocks: list[RawBlock], page_count: int) -> tuple[set[str], set[str], set[str]]:
    top_text_pages: dict[str, set[int]] = defaultdict(set)
    bottom_text_pages: dict[str, set[int]] = defaultdict(set)
    normalized_by_id: dict[str, str] = {}

    for block in raw_blocks:
        normalized = clean_text(block.text).lower()
        normalized_by_id[block.id] = normalized
        if block.bbox[1] <= 0.08:
            top_text_pages[normalized].add(block.page)
        if block.bbox[3] >= 0.92:
            bottom_text_pages[normalized].add(block.page)

    threshold = 2 if page_count > 1 else 999
    repeated_top = {text for text, pages in top_text_pages.items() if len(pages) >= threshold and len(text) > 2}
    repeated_bottom = {text for text, pages in bottom_text_pages.items() if len(pages) >= threshold and len(text) > 2}

    header_ids: set[str] = set()
    footer_ids: set[str] = set()
    page_number_ids: set[str] = set()
    for block in raw_blocks:
        normalized = normalized_by_id[block.id]
        if normalized.isdigit() and (block.bbox[1] <= 0.08 or block.bbox[3] >= 0.92):
            page_number_ids.add(block.id)
        elif block.bbox[1] <= 0.12 and normalized in (repeated_top | repeated_bottom):
            header_ids.add(block.id)
        elif block.bbox[3] >= 0.88 and normalized in (repeated_top | repeated_bottom):
            footer_ids.add(block.id)
    return header_ids, footer_ids, page_number_ids


def _sort_raw_blocks_for_reading(raw_blocks: list[RawBlock]) -> list[RawBlock]:
    by_page: dict[int, list[RawBlock]] = defaultdict(list)
    for block in raw_blocks:
        by_page[block.page].append(block)

    ordered: list[RawBlock] = []
    for page_number in sorted(by_page):
        page_blocks = by_page[page_number]
        if _is_two_column_page(page_blocks):
            ordered.extend(sorted(page_blocks, key=lambda item: (_column_index(item), item.bbox[1], item.bbox[0])))
        else:
            ordered.extend(sorted(page_blocks, key=lambda item: (item.bbox[1], item.bbox[0], item.bbox[3], item.bbox[2])))
    return ordered


def _is_two_column_page(blocks: list[RawBlock]) -> bool:
    content_blocks = [
        block
        for block in blocks
        if len(block.text) > 30 and block.bbox[0] < 0.95 and block.bbox[2] > 0.05 and block.bbox[2] - block.bbox[0] < 0.62
    ]
    left = [block for block in content_blocks if block.bbox[0] < 0.3 and block.bbox[2] < 0.62]
    right = [block for block in content_blocks if block.bbox[0] > 0.38]
    return len(left) >= 2 and len(right) >= 1


def _column_index(block: RawBlock) -> int:
    if block.bbox[0] > 0.38:
        return 1
    return 0


def _pick_title_block(raw_blocks: list[RawBlock], excluded_ids: set[str]) -> str | None:
    first_page_blocks = [
        block
        for block in raw_blocks
        if block.page == 1 and block.id not in excluded_ids and len(block.text) >= 5 and block.bbox[1] < 0.45
    ]
    if not first_page_blocks:
        return None
    return max(first_page_blocks, key=lambda block: (block.font_size or 0.0, len(block.text))).id


def _looks_like_heading(raw: RawBlock, median_font_size: float) -> bool:
    text = raw.text.strip()
    if len(text) > 120:
        return False
    if NUMBERED_HEADING_RE.match(text):
        return True
    if raw.is_bold and (raw.font_size or 0.0) >= median_font_size * 1.05 and not has_terminal_punctuation(text):
        return True
    if (raw.font_size or 0.0) >= median_font_size * 1.25 and not has_terminal_punctuation(text):
        return True
    return False


def _heading_type(text: str) -> str:
    match = NUMBERED_HEADING_RE.match(text)
    if match:
        depth = match.group(1).count(".") + 1
        return {1: "heading_1", 2: "heading_2"}.get(depth, "heading_3")
    return "heading_1"


def _looks_like_list_item(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith(("- ", "* ", "• ")) or bool(stripped[:3].lower() in {"(a)", "(b)", "(c)"})


def _looks_like_equation(text: str) -> bool:
    if len(text) > 140:
        return False
    math_chars = sum(1 for char in text if char in "=∑∏√≤≥±×÷")
    return math_chars >= 2


def _is_abstract_heading(text: str) -> bool:
    return clean_text(text).lower() in {"abstract", "summary"}


def _is_reference_heading(text: str) -> bool:
    cleaned = clean_text(text).lower()
    return cleaned in {"references", "bibliography", "reference"} or cleaned.startswith("references 1.")


def _split_inline_references(blocks: list[BodyBlock]) -> tuple[list[BodyBlock], list[Reference]]:
    new_blocks: list[BodyBlock] = []
    references: list[Reference] = []
    in_references = False
    expected_reference_number = 1

    for block in blocks:
        cleaned = clean_text(block.text)
        if cleaned.lower().startswith("references "):
            heading = block.model_copy(update={"type": "reference_heading", "text": "References"})
            new_blocks.append(heading)
            reference_text = cleaned[len("References") :].strip()
            expected_reference_number = _append_reference_items(new_blocks, block, reference_text, expected_reference_number)
            in_references = True
            continue

        if in_references and REFERENCE_ITEM_RE.match(cleaned):
            expected_reference_number = _append_reference_items(new_blocks, block, cleaned, expected_reference_number)
            continue

        if in_references and not REFERENCE_ITEM_RE.match(cleaned):
            if new_blocks and new_blocks[-1].type == "reference_item" and _looks_like_reference_continuation(cleaned):
                new_blocks[-1].text = clean_text(f"{new_blocks[-1].text} {cleaned}")
                new_blocks[-1].source_block_ids.extend(block.source_block_ids)
                continue
            in_references = False
        new_blocks.append(block)

    for index, block in enumerate(new_blocks, start=1):
        block.id = f"b_{index:04d}"
        block.reading_order = index
        if block.type == "reference_item":
            references.append(
                Reference(
                    id=f"ref_{len(references) + 1:04d}",
                    text=block.text,
                    source_block_ids=block.source_block_ids,
                )
            )

    return new_blocks, references


def _append_reference_items(
    new_blocks: list[BodyBlock],
    source_block: BodyBlock,
    text: str,
    expected_reference_number: int,
) -> int:
    appended = False
    for item in _reference_items_from_text(text):
        number = _reference_number(item)
        if number == expected_reference_number:
            new_blocks.append(source_block.model_copy(update={"type": "reference_item", "text": item}))
            expected_reference_number += 1
            appended = True
        elif new_blocks and new_blocks[-1].type == "reference_item":
            new_blocks[-1].text = clean_text(f"{new_blocks[-1].text} {item}")
            new_blocks[-1].source_block_ids.extend(source_block.source_block_ids)
            appended = True

    cleaned = clean_text(text)
    if not appended and cleaned and new_blocks and new_blocks[-1].type == "reference_item":
        new_blocks[-1].text = clean_text(f"{new_blocks[-1].text} {cleaned}")
        new_blocks[-1].source_block_ids.extend(source_block.source_block_ids)
    return expected_reference_number


def _reference_items_from_text(text: str) -> list[str]:
    items = [clean_text(match.group(1)) for match in REFERENCE_CHUNK_RE.finditer(text)]
    if items:
        return items
    cleaned = clean_text(text)
    return [cleaned] if REFERENCE_ITEM_RE.match(cleaned) else []


def _reference_number(text: str) -> int | None:
    match = REFERENCE_NUMBER_RE.match(clean_text(text))
    return int(match.group(1)) if match else None


def _looks_like_reference_continuation(text: str) -> bool:
    cleaned = clean_text(text)
    if not cleaned:
        return False
    if cleaned.lower().startswith(
        (
            "acknowledgements",
            "author contributions",
            "competing interests",
            "additional information",
            "correspondence",
            "peer review",
            "reprints",
            "publisher",
            "springer nature",
        )
    ):
        return False
    return True


def _rebuild_sections(blocks: list[BodyBlock]) -> list[Section]:
    sections: list[Section] = []
    current_section_id: str | None = None
    levels = {"heading_1": 1, "heading_2": 2, "heading_3": 3, "reference_heading": 1}

    for block in blocks:
        if block.type in levels:
            current_section_id = f"sec_{len(sections) + 1:03d}"
            block.section_id = current_section_id
            sections.append(
                Section(
                    id=current_section_id,
                    title=block.text,
                    level=levels[block.type],
                    page_start=block.page_start,
                    block_id=block.id,
                )
            )
        elif block.type in {"title", "abstract_heading", "abstract"}:
            block.section_id = None
        elif current_section_id:
            block.section_id = current_section_id
    return sections


def _merge_cross_page_paragraphs(blocks: list[BodyBlock]) -> None:
    index = 0
    while index < len(blocks) - 1:
        current = blocks[index]
        nxt = blocks[index + 1]
        if (
            current.type == "paragraph"
            and nxt.type == "paragraph"
            and current.page_end + 1 == nxt.page_start
            and not has_terminal_punctuation(current.text)
            and nxt.text[:1].islower()
        ):
            current.text = f"{current.text} {nxt.text}"
            current.page_end = nxt.page_end
            current.source_block_ids.extend(nxt.source_block_ids)
            blocks.pop(index + 1)
            continue
        index += 1


def _close_sections(sections: list[Section], blocks: list[BodyBlock]) -> None:
    by_section: dict[str, list[BodyBlock]] = defaultdict(list)
    for block in blocks:
        if block.section_id:
            by_section[block.section_id].append(block)
    for section in sections:
        section_blocks = by_section.get(section.id, [])
        if section_blocks:
            section.page_end = max(block.page_end for block in section_blocks)


def _extract_metadata(metadata: Metadata, blocks: list[BodyBlock]) -> Metadata:
    title = metadata.title
    abstract = metadata.abstract
    for block in blocks:
        if block.type == "title" and not title:
            title = block.text
        elif block.type == "abstract":
            abstract = f"{abstract} {block.text}".strip() if abstract else block.text
    return Metadata(
        title=title,
        authors=metadata.authors,
        abstract=abstract,
        keywords=metadata.keywords,
        doi=metadata.doi,
        arxiv_id=metadata.arxiv_id,
    )

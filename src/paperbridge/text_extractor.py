from __future__ import annotations

from statistics import median

import fitz

from paperbridge.models import RawBlock
from paperbridge.utils.bbox import normalize_bbox
from paperbridge.utils.text import clean_text


def extract_raw_blocks(page: fitz.Page, page_number: int) -> list[RawBlock]:
    data = page.get_text("dict")
    blocks: list[RawBlock] = []
    width = page.rect.width
    height = page.rect.height
    raw_index = 1

    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue

        lines_text: list[str] = []
        font_sizes: list[float] = []
        font_names: list[str] = []
        bold_votes = 0
        italic_votes = 0
        span_count = 0

        for line in block.get("lines", []):
            span_texts: list[str] = []
            for span in line.get("spans", []):
                text = span.get("text", "")
                if text.strip():
                    span_texts.append(text)
                    font_sizes.append(float(span.get("size", 0.0)))
                    font_name = str(span.get("font", ""))
                    font_names.append(font_name)
                    lowered = font_name.lower()
                    if "bold" in lowered or "black" in lowered or "semibold" in lowered:
                        bold_votes += 1
                    if "italic" in lowered or "oblique" in lowered:
                        italic_votes += 1
                    span_count += 1
            if span_texts:
                lines_text.append(clean_text(" ".join(span_texts)))

        text = clean_text(" ".join(lines_text))
        if not text:
            continue

        font_size = median(font_sizes) if font_sizes else None
        font_name = max(set(font_names), key=font_names.count) if font_names else None
        bbox = normalize_bbox(block.get("bbox", [0, 0, 0, 0]), width, height)
        blocks.append(
            RawBlock(
                id=f"p{page_number}_raw_{raw_index:03d}",
                page=page_number,
                text=text,
                bbox=bbox,
                font_size=font_size,
                font_name=font_name,
                is_bold=bool(span_count and bold_votes / span_count >= 0.35),
                is_italic=bool(span_count and italic_votes / span_count >= 0.35),
            )
        )
        raw_index += 1

    return sorted(blocks, key=lambda item: (item.bbox[1], item.bbox[0], item.bbox[3], item.bbox[2]))


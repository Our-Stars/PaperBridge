from __future__ import annotations

from paperbridge.models import RawBlock


def classify_page_layout(blocks: list[RawBlock]) -> str:
    content_blocks = [block for block in blocks if len(block.text) > 15 and block.bbox[2] - block.bbox[0] < 0.75]
    if len(content_blocks) < 6:
        return "single_column"

    left = [block for block in content_blocks if block.bbox[0] < 0.38 and block.bbox[2] < 0.62]
    right = [block for block in content_blocks if block.bbox[0] > 0.38]
    if len(left) >= 3 and len(right) >= 3:
        return "two_column"
    return "single_column"


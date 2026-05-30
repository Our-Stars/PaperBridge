from __future__ import annotations

from paperbridge.llm.base import LLMBlockMapping, LLMPageInput, PageStructureResponse


class MockProvider:
    def __init__(self, response: PageStructureResponse | None = None, fail: bool = False) -> None:
        self.response = response
        self.fail = fail
        self.calls = 0

    def structure_page(self, page_input: LLMPageInput, use_vlm: bool = False) -> PageStructureResponse:
        self.calls += 1
        if self.fail:
            raise RuntimeError("mock provider failure")
        if self.response is not None:
            return self.response
        return PageStructureResponse(
            blocks=[
                LLMBlockMapping(
                    raw_block_ids=[block.id],
                    type="paragraph",
                    text=block.text,
                    confidence=0.5,
                )
                for block in page_input.raw_blocks
            ]
        )


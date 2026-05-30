from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from paperbridge.models import BlockType, RawBlock


class LLMProviderError(RuntimeError):
    pass


class LLMConfigurationError(LLMProviderError):
    pass


class LLMBlockMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_block_ids: list[str] = Field(default_factory=list)
    type: BlockType
    text: str
    confidence: float = 0.5


class PageStructureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blocks: list[LLMBlockMapping] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class LLMPageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_number: int
    raw_blocks: list[RawBlock]
    page_image_path: str | None = None


class LLMProvider(Protocol):
    def structure_page(self, page_input: LLMPageInput, use_vlm: bool = False) -> PageStructureResponse:
        ...


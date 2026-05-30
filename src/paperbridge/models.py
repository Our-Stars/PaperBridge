from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


BlockType = Literal[
    "title",
    "subtitle",
    "abstract_heading",
    "abstract",
    "heading_1",
    "heading_2",
    "heading_3",
    "paragraph",
    "list_item",
    "equation",
    "figure",
    "caption",
    "table",
    "footnote",
    "reference_heading",
    "reference_item",
    "header",
    "footer",
    "page_number",
    "unknown",
]


class PaperBridgeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class SourceInfo(PaperBridgeModel):
    pdf_path: str
    file_name: str
    page_count: int


class Metadata(PaperBridgeModel):
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    keywords: list[str] = Field(default_factory=list)
    doi: str | None = None
    arxiv_id: str | None = None


class RawBlock(PaperBridgeModel):
    id: str
    page: int
    text: str
    bbox: list[float]
    font_size: float | None = None
    font_name: str | None = None
    is_bold: bool = False
    is_italic: bool = False

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, value: list[float]) -> list[float]:
        if len(value) != 4:
            raise ValueError("bbox must contain four numbers")
        return [round(float(v), 6) for v in value]


class Page(PaperBridgeModel):
    number: int
    width: float
    height: float
    has_text_layer: bool
    raw_block_ids: list[str] = Field(default_factory=list)
    page_image_path: str | None = None
    layout: Literal["single_column", "two_column", "unknown"] = "unknown"


class BodyBlock(PaperBridgeModel):
    id: str
    type: BlockType
    text: str
    page_start: int
    page_end: int
    source_block_ids: list[str] = Field(default_factory=list)
    bbox: list[float] | None = None
    section_id: str | None = None
    reading_order: int
    confidence: float = 1.0


class Section(PaperBridgeModel):
    id: str
    title: str
    level: int
    page_start: int
    page_end: int | None = None
    block_id: str


class BodyMention(PaperBridgeModel):
    block_id: str
    section_id: str | None = None
    text: str


class EmbeddedText(PaperBridgeModel):
    status: Literal["not_extracted", "extracted", "failed"] = "not_extracted"
    text: list[str] = Field(default_factory=list)
    confidence: float | None = None


class GeneratedDescription(PaperBridgeModel):
    status: Literal["not_generated", "generated", "failed"] = "not_generated"
    text: str | None = None


class ExtractedData(PaperBridgeModel):
    status: Literal["not_extracted", "extracted", "failed"] = "not_extracted"
    data: Any | None = None


class Figure(PaperBridgeModel):
    id: str
    label: str | None = None
    kind: str = "unknown"
    source_page: int
    bbox: list[float] | None = None
    image_path: str | None = None
    caption: str | None = None
    caption_block_id: str | None = None
    body_mentions: list[BodyMention] = Field(default_factory=list)
    embedded_text: EmbeddedText = Field(default_factory=EmbeddedText)
    description: GeneratedDescription = Field(default_factory=GeneratedDescription)
    extracted_data: ExtractedData = Field(default_factory=ExtractedData)
    subfigures: list[dict[str, Any]] = Field(default_factory=list)


class Table(PaperBridgeModel):
    id: str
    label: str | None = None
    source_page: int
    bbox: list[float] | None = None
    caption: str | None = None
    caption_block_id: str | None = None
    representation: Literal["structured", "image", "unknown"] = "unknown"
    columns: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    image_path: str | None = None
    body_mentions: list[BodyMention] = Field(default_factory=list)


class Reference(PaperBridgeModel):
    id: str
    text: str
    source_block_ids: list[str] = Field(default_factory=list)


class PaperWarning(PaperBridgeModel):
    code: str
    message: str
    page: int | None = None
    severity: Literal["info", "warning", "error"] = "warning"


class Document(PaperBridgeModel):
    schema_version: str = "0.1.0"
    source: SourceInfo
    metadata: Metadata = Field(default_factory=Metadata)
    pages: list[Page] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)
    body_blocks: list[BodyBlock] = Field(default_factory=list)
    figures: list[Figure] = Field(default_factory=list)
    tables: list[Table] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)
    headers: list[BodyBlock] = Field(default_factory=list)
    footers: list[BodyBlock] = Field(default_factory=list)
    warnings: list[PaperWarning] = Field(default_factory=list)


class SummaryStats(PaperBridgeModel):
    pages: int
    figures: int
    tables: int
    references: int
    warnings: int


class Summary(PaperBridgeModel):
    status: Literal["success", "warning", "error"]
    source_pdf: str
    outputs: dict[str, str]
    stats: SummaryStats
    warnings: list[PaperWarning] = Field(default_factory=list)


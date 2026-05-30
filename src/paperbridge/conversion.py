from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from paperbridge.caption_binder import bind_captions
from paperbridge.config import ConvertOptions, LLMConfig
from paperbridge.exporters.docx_exporter import export_docx
from paperbridge.exporters.json_exporter import export_json, export_summary
from paperbridge.exporters.markdown_exporter import export_markdown
from paperbridge.exporters.txt_exporter import export_txt
from paperbridge.figure_detector import detect_figures, remove_figure_overlap_blocks
from paperbridge.layout_analyzer import build_document_structure
from paperbridge.llm.base import LLMPageInput, LLMProvider, LLMProviderError, PageStructureResponse
from paperbridge.llm.openai_provider import OpenAICompatibleProvider
from paperbridge.mention_binder import bind_body_mentions
from paperbridge.models import Document, Metadata, Page, PaperWarning, SourceInfo, Summary, SummaryStats
from paperbridge.page_classifier import classify_page_layout
from paperbridge.page_renderer import render_page
from paperbridge.pdf_loader import open_pdf
from paperbridge.table_processor import detect_tables
from paperbridge.text_extractor import extract_raw_blocks
from paperbridge.utils.paths import prepare_output_dir
from paperbridge.utils.text import clean_text
from paperbridge.validators import validate_output


class ConversionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    output_dir: str
    json_path: str
    markdown_path: str | None = None
    txt_path: str | None = None
    docx_path: str | None = None
    summary_path: str
    warnings_count: int


def convert_pdf(
    input_pdf: Path,
    out_dir: Path,
    options: ConvertOptions,
    llm_provider: LLMProvider | None = None,
) -> ConversionResult:
    input_pdf = input_pdf.resolve()
    out_dir = out_dir.resolve()
    prepare_output_dir(out_dir, force=options.force)

    all_raw_blocks = []
    config = LLMConfig.from_env()

    with open_pdf(input_pdf) as pdf:
        processed_pages = options.max_pages or pdf.page_count
        processed_pages = min(processed_pages, pdf.page_count)
        metadata = _metadata_from_pdf(pdf.metadata or {})
        document = Document(
            source=SourceInfo(pdf_path=str(input_pdf), file_name=input_pdf.name, page_count=pdf.page_count),
            metadata=metadata,
        )

        for page_number in range(1, processed_pages + 1):
            page = pdf[page_number - 1]
            page_image_path = render_page(page, out_dir, page_number, options.dpi)
            raw_blocks = extract_raw_blocks(page, page_number)
            all_raw_blocks.extend(raw_blocks)
            if not raw_blocks:
                document.warnings.append(
                    PaperWarning(
                        code="NO_TEXT_LAYER",
                        message="Page appears to have no extractable text layer. OCR is not supported in v1.",
                        page=page_number,
                    )
                )
            document.pages.append(
                Page(
                    number=page_number,
                    width=page.rect.width,
                    height=page.rect.height,
                    has_text_layer=bool(raw_blocks),
                    raw_block_ids=[block.id for block in raw_blocks],
                    page_image_path=page_image_path,
                    layout=classify_page_layout(raw_blocks),
                )
            )

        build_document_structure(document, all_raw_blocks)
        _maybe_apply_llm(document, all_raw_blocks, out_dir, options, config, llm_provider)
        document.figures = detect_figures(pdf, document.body_blocks, out_dir, options.dpi, document.warnings)
        document.tables = detect_tables(pdf, document.body_blocks, out_dir, options.dpi, document.warnings)
        bind_captions(document.body_blocks, document.figures, document.tables)
        document.body_blocks = remove_figure_overlap_blocks(document.body_blocks, document.figures, document.tables)
        bind_body_mentions(document.body_blocks, document.figures, document.tables)

    if options.debug:
        _write_debug_files(document, all_raw_blocks, out_dir)

    paths = _export_outputs(document, out_dir, options.formats)
    validation = validate_output(
        document,
        out_dir,
        markdown_path=paths.get("markdown"),
        docx_path=paths.get("docx"),
    )
    for issue in validation.errors + validation.warnings:
        document.warnings.append(PaperWarning(code=issue.code, message=issue.message, severity=issue.severity))

    summary = _build_summary(document, input_pdf, paths, validation.status)
    export_json(document, out_dir / "paper.json")
    export_summary(summary, out_dir / "summary.json")

    return ConversionResult(
        status=summary.status,
        output_dir=str(out_dir),
        json_path=str(out_dir / "paper.json"),
        markdown_path=str(paths["markdown"]) if paths.get("markdown") else None,
        txt_path=str(paths["txt"]) if paths.get("txt") else None,
        docx_path=str(paths["docx"]) if paths.get("docx") else None,
        summary_path=str(out_dir / "summary.json"),
        warnings_count=len(document.warnings),
    )


def export_from_document(document: Document, out_dir: Path, formats: set[str]) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return _export_outputs(document, out_dir, formats)


def _metadata_from_pdf(metadata: dict[str, str]) -> Metadata:
    title = metadata.get("title") or None
    author = metadata.get("author") or ""
    authors = [item.strip() for item in author.replace(";", ",").split(",") if item.strip()]
    return Metadata(title=title, authors=authors)


def _maybe_apply_llm(
    document: Document,
    raw_blocks: list,
    out_dir: Path,
    options: ConvertOptions,
    config: LLMConfig,
    llm_provider: LLMProvider | None,
) -> None:
    if not options.use_llm and not options.use_vlm:
        return
    if llm_provider is None:
        if options.use_vlm and config.can_use_vlm():
            llm_provider = OpenAICompatibleProvider(config, output_dir=out_dir)
        elif options.use_llm and config.can_use_llm():
            llm_provider = OpenAICompatibleProvider(config, output_dir=out_dir)
        else:
            missing = "PAPERBRIDGE_OPENAI_API_KEY/PAPERBRIDGE_LLM_MODEL"
            if options.use_vlm:
                missing += " or PAPERBRIDGE_VLM_MODEL"
            document.warnings.append(
                PaperWarning(
                    code="LLM_CONFIG_MISSING",
                    message=f"LLM/VLM requested but configuration is incomplete ({missing}); using rule-based parsing.",
                )
            )
            return

    raw_by_page: dict[int, list] = {}
    for block in raw_blocks:
        raw_by_page.setdefault(block.page, []).append(block)
    page_image_by_number = {page.number: page.page_image_path for page in document.pages}

    for page_number, page_blocks in raw_by_page.items():
        page_input = LLMPageInput(
            page_number=page_number,
            raw_blocks=page_blocks,
            page_image_path=page_image_by_number.get(page_number),
        )
        response = _call_llm_with_retry(document, llm_provider, page_input, options.use_vlm)
        if response:
            _apply_llm_response(document, response, page_blocks)


def _call_llm_with_retry(
    document: Document,
    provider: LLMProvider,
    page_input: LLMPageInput,
    use_vlm: bool,
) -> PageStructureResponse | None:
    last_error: Exception | None = None
    for _ in range(2):
        try:
            return provider.structure_page(page_input, use_vlm=use_vlm)
        except Exception as exc:  # pragma: no cover - external API path is covered by mock tests
            last_error = exc
    document.warnings.append(
        PaperWarning(
            code="LLM_PAGE_STRUCTURE_FAILED",
            message=f"LLM/VLM page structure failed for page {page_input.page_number}: {last_error}",
            page=page_input.page_number,
        )
    )
    return None


def _apply_llm_response(document: Document, response: PageStructureResponse, page_blocks: list) -> None:
    raw_text_by_id = {block.id: clean_text(block.text) for block in page_blocks}
    body_by_raw = {
        tuple(block.source_block_ids): block
        for block in document.body_blocks
        if block.source_block_ids and block.type not in {"header", "footer", "page_number"}
    }
    for mapping in response.blocks:
        raw_ids = [raw_id for raw_id in mapping.raw_block_ids if raw_id in raw_text_by_id]
        if not raw_ids:
            continue
        source_text = clean_text(" ".join(raw_text_by_id[raw_id] for raw_id in raw_ids))
        mapped_text = clean_text(mapping.text)
        if mapped_text != source_text:
            continue
        target = body_by_raw.get(tuple(raw_ids))
        if target:
            target.type = mapping.type
            target.confidence = mapping.confidence


def _export_outputs(document: Document, out_dir: Path, formats: set[str]) -> dict[str, Path]:
    paths: dict[str, Path] = {"json": out_dir / "paper.json"}
    export_json(document, paths["json"])
    if "md" in formats or "markdown" in formats:
        paths["markdown"] = out_dir / "paper.md"
        export_markdown(document, paths["markdown"])
    if "txt" in formats:
        paths["txt"] = out_dir / "paper.txt"
        export_txt(document, paths["txt"])
    if "docx" in formats:
        paths["docx"] = out_dir / "paper.docx"
        export_docx(document, paths["docx"], out_dir)
    return paths


def _build_summary(document: Document, input_pdf: Path, paths: dict[str, Path], validation_status: str) -> Summary:
    outputs = {
        "json": paths["json"].name,
    }
    if "markdown" in paths:
        outputs["markdown"] = paths["markdown"].name
    if "txt" in paths:
        outputs["txt"] = paths["txt"].name
    if "docx" in paths:
        outputs["docx"] = paths["docx"].name

    status = "error" if validation_status == "error" else "warning" if document.warnings else "success"
    return Summary(
        status=status,
        source_pdf=str(input_pdf),
        outputs=outputs,
        stats=SummaryStats(
            pages=len(document.pages),
            figures=len(document.figures),
            tables=len(document.tables),
            references=len(document.references),
            warnings=len(document.warnings),
        ),
        warnings=document.warnings,
    )


def _write_debug_files(document: Document, raw_blocks: list, out_dir: Path) -> None:
    debug_dir = out_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "raw_blocks.json").write_text(
        json.dumps([block.model_dump() for block in raw_blocks], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (debug_dir / "page_layouts.json").write_text(
        json.dumps([page.model_dump() for page in document.pages], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from paperbridge.models import Document


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    severity: str = "warning"


class ValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]


def validate_output(
    document: Document,
    base_dir: Path,
    markdown_path: Path | None = None,
    docx_path: Path | None = None,
) -> ValidationReport:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    _validate_image_paths(document, base_dir, errors)
    if markdown_path:
        _validate_markdown_refs(markdown_path, base_dir, errors)
    if docx_path and not docx_path.exists():
        errors.append(ValidationIssue(code="DOCX_MISSING", message=f"DOCX was not generated: {docx_path}", severity="error"))
    _validate_raw_coverage(document, warnings)
    _validate_caption_binding(document, warnings)
    _validate_no_text_layer_warnings(document, warnings)
    _validate_marginalia_leak(document, warnings)

    status = "error" if errors else "warning" if warnings else "success"
    return ValidationReport(status=status, errors=errors, warnings=warnings)


def _validate_image_paths(document: Document, base_dir: Path, errors: list[ValidationIssue]) -> None:
    for figure in document.figures:
        if figure.image_path and not (base_dir / figure.image_path).exists():
            errors.append(
                ValidationIssue(
                    code="FIGURE_IMAGE_MISSING",
                    message=f"Figure image does not exist: {figure.image_path}",
                    severity="error",
                )
            )
    for table in document.tables:
        if table.image_path and not (base_dir / table.image_path).exists():
            errors.append(
                ValidationIssue(
                    code="TABLE_IMAGE_MISSING",
                    message=f"Table image does not exist: {table.image_path}",
                    severity="error",
                )
            )


def _validate_markdown_refs(markdown_path: Path, base_dir: Path, errors: list[ValidationIssue]) -> None:
    if not markdown_path.exists():
        errors.append(
            ValidationIssue(code="MARKDOWN_MISSING", message=f"Markdown was not generated: {markdown_path}", severity="error")
        )
        return
    markdown = markdown_path.read_text(encoding="utf-8")
    for ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", markdown):
        if ref.startswith(("http://", "https://")):
            continue
        if not (base_dir / ref).exists():
            errors.append(
                ValidationIssue(
                    code="MARKDOWN_IMAGE_MISSING",
                    message=f"Markdown image reference does not exist: {ref}",
                    severity="error",
                )
            )


def _validate_raw_coverage(document: Document, warnings: list[ValidationIssue]) -> None:
    raw_ids = {raw_id for page in document.pages for raw_id in page.raw_block_ids}
    if not raw_ids:
        return
    mapped_ids = {
        raw_id
        for block in document.body_blocks + document.headers + document.footers
        for raw_id in block.source_block_ids
    }
    coverage = len(raw_ids & mapped_ids) / len(raw_ids)
    if coverage < 0.8:
        warnings.append(
            ValidationIssue(
                code="LOW_RAW_BLOCK_COVERAGE",
                message=f"Only {coverage:.1%} of raw blocks are mapped into structured blocks.",
            )
        )


def _validate_caption_binding(document: Document, warnings: list[ValidationIssue]) -> None:
    for figure in document.figures:
        if not figure.caption_block_id:
            warnings.append(
                ValidationIssue(code="FIGURE_CAPTION_UNBOUND", message=f"Figure has no bound caption: {figure.id}")
            )
    for table in document.tables:
        if not table.caption_block_id:
            warnings.append(ValidationIssue(code="TABLE_CAPTION_UNBOUND", message=f"Table has no bound caption: {table.id}"))


def _validate_no_text_layer_warnings(document: Document, warnings: list[ValidationIssue]) -> None:
    warning_pages = {warning.page for warning in document.warnings if warning.code == "NO_TEXT_LAYER"}
    for page in document.pages:
        if not page.has_text_layer and page.number not in warning_pages:
            warnings.append(
                ValidationIssue(
                    code="NO_TEXT_LAYER_WARNING_MISSING",
                    message=f"Page {page.number} has no text layer but no warning was recorded.",
                )
            )


def _validate_marginalia_leak(document: Document, warnings: list[ValidationIssue]) -> None:
    marginalia = {block.text.lower() for block in document.headers + document.footers if len(block.text) > 4}
    if not marginalia:
        return
    leaked = [
        block.id
        for block in document.body_blocks
        if block.text.lower() in marginalia and block.type not in {"header", "footer", "page_number"}
    ]
    if leaked:
        warnings.append(
            ValidationIssue(
                code="MARGINALIA_IN_BODY",
                message=f"Possible repeated header/footer text found in body blocks: {', '.join(leaked[:5])}",
            )
        )


from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from paperbridge import __version__
from paperbridge.config import ConvertOptions
from paperbridge.conversion import convert_pdf, export_from_document
from paperbridge.exporters.json_exporter import load_document
from paperbridge.pdf_loader import inspect_pdf
from paperbridge.validators import validate_output

app = typer.Typer(help="PaperBridge PDF structured conversion CLI.")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Show PaperBridge version."),
    ] = None,
) -> None:
    return None


@app.command()
def convert(
    input_pdf: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    out: Annotated[Path, typer.Option("--out", "-o", help="Output directory.")],
    formats: Annotated[str, typer.Option("--formats", help="Comma-separated formats: json,md,txt,docx.")] = "json,md,txt,docx",
    profile: Annotated[str, typer.Option("--profile", help="Output profile: human, llm, full.")] = "full",
    dpi: Annotated[int, typer.Option("--dpi", min=72, max=600, help="Page render DPI.")] = 200,
    max_pages: Annotated[int | None, typer.Option("--max-pages", min=1, help="Only process the first N pages.")] = None,
    use_llm: Annotated[bool, typer.Option("--use-llm/--no-llm", help="Use LLM page structure enhancement.")] = True,
    use_vlm: Annotated[bool, typer.Option("--use-vlm", help="Allow VLM page image input.")] = False,
    debug: Annotated[bool, typer.Option("--debug", help="Write debug files.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Overwrite output directory.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Print machine-readable JSON result.")] = False,
    quiet: Annotated[bool, typer.Option("--quiet", help="Reduce terminal output.")] = False,
) -> None:
    result = convert_pdf(
        input_pdf=input_pdf,
        out_dir=out,
        options=ConvertOptions(
            formats=_parse_formats(formats),
            profile=profile,
            dpi=dpi,
            max_pages=max_pages,
            use_llm=use_llm,
            use_vlm=use_vlm,
            debug=debug,
            force=force,
            quiet=quiet,
        ),
    )
    if json_output:
        typer.echo(result.model_dump_json(indent=2))
    elif not quiet:
        typer.echo(f"status: {result.status}")
        typer.echo(f"output: {result.output_dir}")
        typer.echo(f"warnings: {result.warnings_count}")


@app.command()
def inspect(
    input_pdf: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    json_output: Annotated[bool, typer.Option("--json", help="Print machine-readable JSON.")] = False,
) -> None:
    info = inspect_pdf(input_pdf)
    if json_output:
        typer.echo(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        typer.echo(f"File: {info['file_name']}")
        typer.echo(f"Pages: {info['page_count']}")
        for page in info["pages"]:
            typer.echo(
                f"Page {page['page']}: text={page['has_text_layer']} "
                f"chars={page['text_length']} images={page['image_count']}"
            )


@app.command()
def validate(
    json_path: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    json_output: Annotated[bool, typer.Option("--json", help="Print machine-readable JSON.")] = False,
) -> None:
    document = load_document(json_path)
    base_dir = json_path.parent
    report = validate_output(
        document,
        base_dir,
        markdown_path=base_dir / "paper.md",
        docx_path=base_dir / "paper.docx",
    )
    if json_output:
        typer.echo(report.model_dump_json(indent=2))
    else:
        typer.echo(f"status: {report.status}")
        for issue in report.errors + report.warnings:
            typer.echo(f"{issue.severity.upper()} {issue.code}: {issue.message}")
    if report.status == "error":
        raise typer.Exit(1)


@app.command()
def export(
    json_path: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    formats: Annotated[str, typer.Option("--formats", help="Comma-separated formats: md,txt,docx.")] = "md,txt,docx",
    out: Annotated[Path | None, typer.Option("--out", "-o", help="Output directory.")] = None,
) -> None:
    document = load_document(json_path)
    output_dir = out or json_path.parent
    paths = export_from_document(document, output_dir, _parse_formats(formats))
    typer.echo(json.dumps({key: str(value) for key, value in paths.items()}, indent=2, ensure_ascii=False))


def _parse_formats(formats: str) -> set[str]:
    parsed = {item.strip().lower() for item in formats.split(",") if item.strip()}
    aliases = {"markdown": "md"}
    normalized = {aliases.get(item, item) for item in parsed}
    allowed = {"json", "md", "txt", "docx"}
    unknown = normalized - allowed
    if unknown:
        raise typer.BadParameter(f"Unknown format(s): {', '.join(sorted(unknown))}")
    return normalized or {"json", "md", "txt", "docx"}


if __name__ == "__main__":
    app()


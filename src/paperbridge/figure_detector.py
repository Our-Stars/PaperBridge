from __future__ import annotations

from pathlib import Path

import fitz

from paperbridge.models import BodyBlock, Figure, PaperWarning
from paperbridge.page_renderer import crop_page_region
from paperbridge.utils.bbox import denormalize_bbox, normalize_bbox
from paperbridge.utils.text import caption_kind, caption_label

# 内嵌图片的最小面积阈值（占页面面积比例）。部分图片在 PDF 中以较小
# 的内嵌图片形式存在，过高的阈值会导致子图被遗漏。
_MIN_IMAGE_PAGE_RATIO = 0.003
# 内嵌图片的最小边长（占页面高度比例），过滤过窄或过矮的装饰元素。
_MIN_IMAGE_DIMENSION_RATIO = 0.02


def detect_figures(
    pdf: fitz.Document,
    body_blocks: list[BodyBlock],
    out_dir: Path,
    dpi: int,
    warnings: list[PaperWarning],
) -> list[Figure]:
    figures: list[Figure] = []
    seen_rects: set[tuple[int, int, int, int, int]] = set()

    for page_index, page in enumerate(pdf, start=1):
        if not page.get_text("text").strip():
            continue
        page_area = page.rect.width * page.rect.height
        for image in page.get_images(full=True):
            xref = image[0]
            for rect in page.get_image_rects(xref):
                if rect.is_empty or rect.width * rect.height < page_area * _MIN_IMAGE_PAGE_RATIO:
                    continue
                if rect.height < page.rect.height * _MIN_IMAGE_DIMENSION_RATIO:
                    continue
                rect_key = (
                    page_index,
                    round(rect.x0),
                    round(rect.y0),
                    round(rect.x1),
                    round(rect.y1),
                )
                if rect_key in seen_rects:
                    continue
                seen_rects.add(rect_key)

                figure_id = f"fig_{len(figures) + 1:03d}"
                try:
                    image_path = crop_page_region(
                        page,
                        out_dir,
                        "assets/figures",
                        f"{figure_id}_page_{page_index:03d}.png",
                        rect,
                        dpi,
                    )
                except Exception as exc:  # pragma: no cover - depends on malformed PDFs
                    warnings.append(
                        PaperWarning(
                            code="FIGURE_CROP_FAILED",
                            message=f"Failed to crop figure candidate {figure_id}: {exc}",
                            page=page_index,
                        )
                    )
                    image_path = None

                figures.append(
                    Figure(
                        id=figure_id,
                        source_page=page_index,
                        bbox=normalize_bbox((rect.x0, rect.y0, rect.x1, rect.y1), page.rect.width, page.rect.height),
                        image_path=image_path,
                    )
                )

    _add_caption_fallback_figures(pdf, body_blocks, out_dir, dpi, warnings, figures)
    return figures


def _add_caption_fallback_figures(
    pdf: fitz.Document,
    body_blocks: list[BodyBlock],
    out_dir: Path,
    dpi: int,
    warnings: list[PaperWarning],
    figures: list[Figure],
) -> None:
    caption_blocks = [block for block in body_blocks if block.type == "caption" and caption_kind(block.text) == "figure"]
    # 按页面对 body blocks 排序，供扫描使用
    page_sorted: dict[int, list[BodyBlock]] = {}
    for b in body_blocks:
        page_sorted.setdefault(b.page_start, []).append(b)
    for blocks in page_sorted.values():
        blocks.sort(key=lambda b: (b.bbox[1] if b.bbox else 0, b.bbox[0] if b.bbox else 0))

    for caption in caption_blocks:
        if any(item.source_page == caption.page_start and item.caption_block_id == caption.id for item in figures):
            continue

        page = pdf[caption.page_start - 1]
        pg_blocks = page_sorted.get(caption.page_start, [])

        # 查找同一页上尚未绑定 caption 的内嵌图片
        unbound = [f for f in figures if f.source_page == caption.page_start and f.caption is None and f.caption_block_id is None]
        if unbound:
            nearest = min(unbound, key=lambda f: _distance_to_caption(f, caption, page))
            fig_rect = _figure_rect_from_fig(nearest, page)

            # 用 body block 扫描确定 figure 的完整 y 范围
            block_by_id = {b.id: b for b in body_blocks}
            region_top, region_bottom = _scan_figure_region(caption, nearest, pg_blocks, block_by_id)

            margin = page.rect.width * 0.04
            expanded_rect = fitz.Rect(
                min(fig_rect.x0, margin),
                max(0, region_top * page.rect.height),
                max(fig_rect.x1, page.rect.width - margin),
                min(page.rect.height, region_bottom * page.rect.height),
            )
            expanded_area = expanded_rect.width * expanded_rect.height
            fig_area = fig_rect.width * fig_rect.height

            if expanded_area > fig_area * 1.1:
                try:
                    nearest.image_path = crop_page_region(
                        page, out_dir, "assets/figures",
                        f"{nearest.id}_page_{caption.page_start:03d}.png",
                        expanded_rect, dpi,
                    )
                except Exception:
                    pass
                nearest.bbox = normalize_bbox(
                    (expanded_rect.x0, expanded_rect.y0, expanded_rect.x1, expanded_rect.y1),
                    page.rect.width, page.rect.height,
                )
            nearest.caption = nearest.caption or caption.text
            nearest.label = nearest.label or caption_label(caption.text)
            nearest.caption_block_id = nearest.caption_block_id or caption.id
        else:
            # 无内嵌图片 — 用 fallback rect 作为基础，再用扫描结果扩展
            fallback_rect = _fallback_rect(page, caption)
            block_by_id = {b.id: b for b in body_blocks}
            temp_fig = Figure(
                id="temp",
                source_page=caption.page_start,
                bbox=normalize_bbox(
                    (fallback_rect.x0, fallback_rect.y0, fallback_rect.x1, fallback_rect.y1),
                    page.rect.width, page.rect.height,
                ),
            )
            scan_top, scan_bottom = _scan_figure_region(caption, temp_fig, pg_blocks, block_by_id)
            final_rect = fitz.Rect(
                fallback_rect.x0,
                max(0, scan_top * page.rect.height),
                fallback_rect.x1,
                min(page.rect.height, scan_bottom * page.rect.height),
            )
            figure_id = f"fig_{len(figures) + 1:03d}"
            try:
                image_path = crop_page_region(
                    page, out_dir, "assets/figures",
                    f"{figure_id}_page_{caption.page_start:03d}.png",
                    final_rect, dpi,
                )
            except Exception as exc:  # pragma: no cover - depends on malformed PDFs
                warnings.append(
                    PaperWarning(
                        code="FIGURE_CROP_FAILED",
                        message=f"Failed to crop fallback figure {figure_id}: {exc}",
                        page=caption.page_start,
                    )
                )
                image_path = None

            figures.append(
                Figure(
                    id=figure_id,
                    label=caption_label(caption.text),
                    source_page=caption.page_start,
                    bbox=normalize_bbox(
                        (final_rect.x0, final_rect.y0, final_rect.x1, final_rect.y1),
                        page.rect.width, page.rect.height,
                    ),
                    image_path=image_path,
                    caption=caption.text,
                    caption_block_id=caption.id,
                )
            )


def _figure_rect_from_fig(fig: Figure, page: fitz.Page) -> fitz.Rect:
    if fig.bbox and len(fig.bbox) >= 4:
        x0, y0, x1, y1 = denormalize_bbox(fig.bbox, page.rect.width, page.rect.height)
        return fitz.Rect(x0, y0, x1, y1)
    return fitz.Rect(0, 0, 0, 0)


def _distance_to_caption(fig: Figure, caption: BodyBlock, page: fitz.Page) -> float:
    fig_mid = ((fig.bbox[1] + fig.bbox[3]) / 2) if fig.bbox else 0.5
    cap_mid = ((caption.bbox[1] + caption.bbox[3]) / 2) if caption.bbox else 0.5
    return abs(fig_mid - cap_mid)


def _scan_figure_region(
    caption: BodyBlock,
    fig: Figure,
    page_blocks_sorted: list[BodyBlock],
    block_by_id: dict[str, BodyBlock],
) -> tuple[float, float]:
    """通过扫描 body blocks 确定 figure 的完整 y 范围（归一化）。

    从 caption 双向扩展，短文本（图内标签）纳入，遇到正文段落或长标题停止。
    用于 figure 裁剪阶段（caption_block_id 尚未设置的时机）。
    """
    if not caption.bbox:
        return (fig.bbox[1], fig.bbox[3]) if (fig.bbox and len(fig.bbox) >= 4) else (0.4, 0.6)

    cap_y0, cap_y1 = caption.bbox[1], caption.bbox[3]
    blocked_types = {"header", "footer", "page_number", "reference_item", "caption"}

    region_top = cap_y0
    for b in page_blocks_sorted:
        if b.id == caption.id or not b.bbox:
            continue
        if b.bbox[1] >= cap_y0:
            continue
        if b.type in blocked_types:
            continue
        if b.type in {"paragraph", "abstract"} and len(b.text) > 200:
            break
        if b.type in {"heading_1", "heading_2", "heading_3"} and len(b.text) > 50:
            break
        region_top = min(region_top, b.bbox[1])

    # 向下仅覆盖到 caption 底或 figure bbox 底（取较大者），不扫描正文。
    # caption 下方的通常是讨论文字，而非图内元素。
    region_bottom = cap_y1

    if fig.bbox and len(fig.bbox) >= 4:
        region_top = min(region_top, fig.bbox[1])
        # 仅当 figure 确实在 caption 下方时才向下扩展。
        # 判断依据：向上扫描没找到内容（region_top 保持在 cap_y0 附近），
        # 且 figure bbox 的中心在 caption 下方。
        expanded_upward = (cap_y0 - region_top) > 0.10
        if not expanded_upward:
            fig_mid = (fig.bbox[1] + fig.bbox[3]) / 2
            cap_mid = (caption.bbox[1] + caption.bbox[3]) / 2
            if fig_mid > cap_mid:
                region_bottom = max(region_bottom, fig.bbox[3])

    return (region_top, region_bottom)


def _fallback_rect(page: fitz.Page, caption: BodyBlock) -> fitz.Rect:
    """纯 fallback（无内嵌图片时）的裁剪区域。"""
    if caption.bbox:
        x0, y0, x1, y1 = denormalize_bbox(caption.bbox, page.rect.width, page.rect.height)
    else:
        x0, y0, x1, y1 = (page.rect.width * 0.1, page.rect.height * 0.45, page.rect.width * 0.9, page.rect.height * 0.55)
    caption_mid = (y0 + y1) / 2
    horizontal_margin = page.rect.width * 0.04
    if caption_mid > page.rect.height * 0.5:
        top = max(0, y0 - page.rect.height * 0.50)
        bottom = max(top + 24, y0 - 4)
    else:
        top = min(page.rect.height - 24, y1 + 4)
        bottom = min(page.rect.height, y1 + page.rect.height * 0.50)
    return fitz.Rect(horizontal_margin, top, page.rect.width - horizontal_margin, bottom)


def remove_figure_overlap_blocks(
    body_blocks: list[BodyBlock],
    figures: list[Figure],
    tables: list[Figure] | None = None,
) -> list[BodyBlock]:
    """Remove body blocks that overlap with figure/table regions.

    以 caption 为锚点，从 caption 位置向上扫描找到 figure 的真正上边界，
    向下延伸到 caption 或 figure 的下边界，确保覆盖图内所有标签文本。
    """
    block_by_id = {b.id: b for b in body_blocks}
    caption_ids: set[str] = {fig.caption_block_id for fig in figures if fig.caption_block_id}
    if tables:
        caption_ids.update(t.caption_block_id for t in tables if t.caption_block_id)

    # 按页面分组，按 y 坐标排序
    page_sorted: dict[int, list[BodyBlock]] = {}
    for b in body_blocks:
        page_sorted.setdefault(b.page_start, []).append(b)
    for blocks in page_sorted.values():
        blocks.sort(key=lambda b: (b.bbox[1] if b.bbox else 0, b.bbox[0] if b.bbox else 0))

    page_figure_yranges: dict[int, list[tuple[float, float]]] = {}
    for fig in figures:
        if not fig.bbox or len(fig.bbox) < 4:
            continue
        top, bottom = _figure_region(fig, block_by_id, page_sorted.get(fig.source_page, []))
        page_figure_yranges.setdefault(fig.source_page, []).append((top, bottom))

    if tables:
        for tbl in tables:
            if not tbl.bbox or len(tbl.bbox) < 4:
                continue
            page_figure_yranges.setdefault(tbl.source_page, []).append((tbl.bbox[1], tbl.bbox[3]))

    kept: list[BodyBlock] = []
    for block in body_blocks:
        if block.id in caption_ids:
            kept.append(block)
            continue
        if block.type in {"header", "footer", "page_number", "reference_item"}:
            kept.append(block)
            continue
        yranges = page_figure_yranges.get(block.page_start, [])
        if not yranges:
            kept.append(block)
            continue
        block_mid_y = (block.bbox[1] + block.bbox[3]) / 2 if block.bbox else 0.5
        if any(r[0] <= block_mid_y <= r[1] for r in yranges):
            continue
        kept.append(block)

    return kept


def _figure_region(
    fig: Figure,
    block_by_id: dict[str, BodyBlock],
    page_blocks_sorted: list[BodyBlock],
) -> tuple[float, float]:
    """计算 figure 的 y 剔除范围（委托 _scan_figure_region）。"""
    if not fig.caption_block_id:
        return (fig.bbox[1], fig.bbox[3]) if (fig.bbox and len(fig.bbox) >= 4) else (0, 1)
    caption = block_by_id.get(fig.caption_block_id)
    if not caption or not caption.bbox:
        return (fig.bbox[1], fig.bbox[3]) if (fig.bbox and len(fig.bbox) >= 4) else (0, 1)
    return _scan_figure_region(caption, fig, page_blocks_sorted, block_by_id)

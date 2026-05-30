from __future__ import annotations

from collections.abc import Sequence


def normalize_bbox(rect: Sequence[float], width: float, height: float) -> list[float]:
    x0, y0, x1, y1 = [float(v) for v in rect]
    if width <= 0 or height <= 0:
        return [0.0, 0.0, 0.0, 0.0]
    return [
        max(0.0, min(1.0, x0 / width)),
        max(0.0, min(1.0, y0 / height)),
        max(0.0, min(1.0, x1 / width)),
        max(0.0, min(1.0, y1 / height)),
    ]


def denormalize_bbox(bbox: Sequence[float], width: float, height: float) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = [float(v) for v in bbox]
    return (x0 * width, y0 * height, x1 * width, y1 * height)


def bbox_center_x(bbox: Sequence[float]) -> float:
    return (float(bbox[0]) + float(bbox[2])) / 2


def bbox_center_y(bbox: Sequence[float]) -> float:
    return (float(bbox[1]) + float(bbox[3])) / 2


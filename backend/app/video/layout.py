"""Funções para ajustar a razão de aspecto."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LayoutTransform:
    filters: str
    width: int
    height: int


def build_scale_filter(width: int, height: int, target_aspect: str) -> LayoutTransform:
    """Retorna filtros FFmpeg para ajustar a razão sem distorção."""

    ratios = {
        "16:9": 16 / 9,
        "9:16": 9 / 16,
        "1:1": 1.0,
    }
    target_ratio = ratios.get(target_aspect, 16 / 9)
    source_ratio = width / height if height else target_ratio

    if abs(source_ratio - target_ratio) < 0.01:
        return LayoutTransform(filters="scale=-2:720", width=width, height=height)

    if source_ratio > target_ratio:
        new_height = 720
        new_width = int(new_height * target_ratio)
        filters = f"scale=-2:{new_height},crop={new_width}:{new_height}"
    else:
        new_width = 720
        new_height = int(new_width / target_ratio)
        filters = f"scale={new_width}:-2,crop={new_width}:{new_height}"
    return LayoutTransform(filters=filters, width=new_width, height=new_height)


__all__ = ["build_scale_filter", "LayoutTransform"]

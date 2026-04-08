# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""용지 및 네임태그 레이아웃 데이터 모델"""

from dataclasses import dataclass, field
from typing import Optional


# 용지 프리셋 (이름: (너비mm, 높이mm))
PAPER_PRESETS = {
    "A3": (297.0, 420.0),
    "A4": (210.0, 297.0),
    "A5": (148.0, 210.0),
    "B4": (250.0, 353.0),
    "B5": (176.0, 250.0),
    "Letter": (215.9, 279.4),
    "Legal": (215.9, 355.6),
    "Custom": (210.0, 297.0),
}


@dataclass
class PaperSize:
    """용지 크기"""
    name: str = "A4"
    width_mm: float = 210.0
    height_mm: float = 297.0

    @classmethod
    def from_preset(cls, name: str) -> "PaperSize":
        if name in PAPER_PRESETS:
            w, h = PAPER_PRESETS[name]
            return cls(name=name, width_mm=w, height_mm=h)
        return cls(name="A4", width_mm=210.0, height_mm=297.0)


@dataclass
class TagLayout:
    """네임태그 레이아웃 설정"""
    tag_width_mm: float = 90.0
    tag_height_mm: float = 54.0
    columns: int = 2
    rows: int = 5
    offset_x_mm: float = 15.0
    offset_y_mm: float = 13.5
    gap_x_mm: float = 0.0
    gap_y_mm: float = 0.0

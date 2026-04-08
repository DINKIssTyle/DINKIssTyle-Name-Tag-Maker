# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""텍스트 박스 및 태그 데이터 모델"""

from dataclasses import dataclass, field
from typing import List, Optional
import copy


from utils.fonts import get_default_korean_font


@dataclass
class TextBox:
    """네임태그 내 텍스트 박스"""
    label: str = "텍스트"
    x_mm: float = 5.0
    y_mm: float = 5.0
    width_mm: float = 80.0
    height_mm: float = 15.0
    font_family: str = field(default_factory=get_default_korean_font)
    font_size: float = 12.0
    line_spacing: float = 1.2
    letter_spacing: float = 0.0
    alignment: str = "center"  # left, center, right
    color: str = "#000000"
    bold: bool = False
    italic: bool = False

    def clone(self) -> "TextBox":
        return copy.deepcopy(self)


@dataclass
class TagTemplate:
    """네임태그 템플릿"""
    background_image: Optional[str] = None
    text_boxes: List[TextBox] = field(default_factory=list)

    def add_text_box(self, label: str = "텍스트") -> TextBox:
        tb = TextBox(label=label, y_mm=5.0 + len(self.text_boxes) * 18.0)
        self.text_boxes.append(tb)
        return tb

    def remove_text_box(self, index: int):
        if 0 <= index < len(self.text_boxes):
            self.text_boxes.pop(index)

    def move_text_box(self, from_idx: int, to_idx: int):
        if 0 <= from_idx < len(self.text_boxes) and 0 <= to_idx < len(self.text_boxes):
            tb = self.text_boxes.pop(from_idx)
            self.text_boxes.insert(to_idx, tb)

    def get_labels(self) -> List[str]:
        return [tb.label for tb in self.text_boxes]


@dataclass
class TagEntry:
    """스프레드시트의 한 행 (네임태그 하나의 데이터)"""
    checked: bool = True
    values: List[str] = field(default_factory=list)

    def get_value(self, index: int) -> str:
        if 0 <= index < len(self.values):
            return self.values[index]
        return ""

    def set_value(self, index: int, value: str):
        while len(self.values) <= index:
            self.values.append("")
        self.values[index] = value

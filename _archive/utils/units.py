# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""단위 변환 유틸리티 (mm, inch, px)"""


# 화면 표시용 기본 DPI
SCREEN_DPI = 96
# 인쇄용 DPI
PRINT_DPI = 300

MM_PER_INCH = 25.4


def mm_to_inch(mm: float) -> float:
    return mm / MM_PER_INCH


def inch_to_mm(inch: float) -> float:
    return inch * MM_PER_INCH


def mm_to_px(mm: float, dpi: float = SCREEN_DPI) -> float:
    return mm / MM_PER_INCH * dpi


def inch_to_px(inch: float, dpi: float = SCREEN_DPI) -> float:
    return inch * dpi


def px_to_mm(px: float, dpi: float = SCREEN_DPI) -> float:
    return px / dpi * MM_PER_INCH


def px_to_inch(px: float, dpi: float = SCREEN_DPI) -> float:
    return px / dpi


def to_px(value: float, unit: str, dpi: float = SCREEN_DPI) -> float:
    """주어진 단위의 값을 픽셀로 변환"""
    if unit == "mm":
        return mm_to_px(value, dpi)
    elif unit == "inch":
        return inch_to_px(value, dpi)
    return value


def from_px(px: float, unit: str, dpi: float = SCREEN_DPI) -> float:
    """픽셀 값을 주어진 단위로 변환"""
    if unit == "mm":
        return px_to_mm(px, dpi)
    elif unit == "inch":
        return px_to_inch(px, dpi)
    return px


def mm_to_pt(mm: float) -> float:
    """mm를 포인트(pt)로 변환 (1pt = 1/72 inch)"""
    return mm / MM_PER_INCH * 72


def pt_to_mm(pt: float) -> float:
    """포인트(pt)를 mm로 변환"""
    return pt / 72 * MM_PER_INCH

# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""PDF 생성 및 인쇄 유틸리티"""

import os
import sys
import subprocess
import tempfile
from typing import List, Optional

from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm as RL_MM
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from models.paper import PaperSize, TagLayout
from models.tag_data import TagTemplate, TagEntry, TextBox
from utils.fonts import get_default_korean_font, find_font_file


def generate_pdf(
    paper: PaperSize,
    layout: TagLayout,
    template: TagTemplate,
    entries: List[TagEntry],
    output_path: str,
    common_values: Optional[List[str]] = None,
):
    """PDF 파일 생성"""

    page_w = paper.width_mm * RL_MM
    page_h = paper.height_mm * RL_MM
    tag_w = layout.tag_width_mm * RL_MM
    tag_h = layout.tag_height_mm * RL_MM
    offset_x = layout.offset_x_mm * RL_MM
    offset_y = layout.offset_y_mm * RL_MM
    gap_x = layout.gap_x_mm * RL_MM
    gap_y = layout.gap_y_mm * RL_MM

    tags_per_page = layout.columns * layout.rows

    # 체크된 항목만 필터링
    checked_entries = [e for e in entries if e.checked]
    if not checked_entries:
        return

    c = canvas.Canvas(output_path, pagesize=(page_w, page_h))

    for idx, entry in enumerate(checked_entries):
        if idx > 0 and idx % tags_per_page == 0:
            c.showPage()

        pos_in_page = idx % tags_per_page
        col = pos_in_page % layout.columns
        row = pos_in_page // layout.columns

        x = offset_x + col * (tag_w + gap_x)
        y = page_h - offset_y - (row + 1) * tag_h - row * gap_y

        # 배경 이미지
        if template.background_image and os.path.isfile(template.background_image):
            try:
                c.drawImage(
                    template.background_image, x, y, tag_w, tag_h,
                    preserveAspectRatio=False, mask='auto'
                )
            except Exception:
                pass

        # 텍스트 박스 렌더링
        for tb_idx, tb in enumerate(template.text_boxes):
            # 공통 값이 있으면 공통 값 사용, 없으면 개별 값 사용
            text = ""
            if common_values and tb_idx < len(common_values) and common_values[tb_idx]:
                text = common_values[tb_idx]
            else:
                text = entry.get_value(tb_idx)

            if not text:
                continue

            # 텍스트 박스의 고정 좌표 (태그 좌상단 기준)
            box_x = x + tb.x_mm * RL_MM
            box_y_top = y + tag_h - tb.y_mm * RL_MM  # 박스 상단 Y (PDF 좌표계: 아래가 0)

            # 폰트 및 자동 크기 조절 (Auto-scaling)
            font_name = tb.font_family or get_default_korean_font()
            try:
                if font_name not in pdfmetrics.getRegisteredFontNames():
                    font_file = find_font_file(font_name)
                    if not font_file:
                        font_file = find_font_file(get_default_korean_font())
                        if font_file:
                            font_name = get_default_korean_font()
                            
                    if font_file:
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, font_file))
                        except Exception:
                            # TTC 파일의 경우 subfontIndex 지정 필요
                            if font_file.lower().endswith('.ttc'):
                                try:
                                    pdfmetrics.registerFont(TTFont(font_name, font_file, subfontIndex=0))
                                except Exception:
                                    # TTC도 실패하면 기본 폰트로 대체
                                    fallback = find_font_file(get_default_korean_font())
                                    if fallback and fallback != font_file:
                                        font_name = get_default_korean_font()
                                        if font_name not in pdfmetrics.getRegisteredFontNames():
                                            pdfmetrics.registerFont(TTFont(font_name, fallback))
                                    else:
                                        font_name = "Helvetica"
                            else:
                                font_name = "Helvetica"
                    else:
                        font_name = "Helvetica"
            except Exception:
                font_name = "Helvetica"

            box_w = tb.width_mm * RL_MM
            box_h = tb.height_mm * RL_MM
            
            # 텍스트 자동 축소 로직
            current_font_size = tb.font_size
            lines = text.split('\n')
            
            while current_font_size > 4: # 최소 폰트 사이즈 제한
                # 현재 폰트 크기로 줄 간격 계산
                line_h = current_font_size * tb.line_spacing
                total_h = len(lines) * line_h
                
                # 현재 폰트 크기로 최대 너비 계산
                max_w = 0
                for line in lines:
                    w = c.stringWidth(line, font_name, current_font_size)
                    if tb.letter_spacing > 0:
                        w += tb.letter_spacing * max(0, len(line) - 1)
                    if w > max_w:
                        max_w = w
                        
                # 박스 크기에 맞으면 종료
                if max_w <= box_w and total_h <= box_h:
                    break
                    
                # 크기가 넘치면 줄임
                current_font_size -= 0.5

            # 렌더링 설정
            c.setFont(font_name, current_font_size)
            c.setFillColor(HexColor(tb.color))

            # Y 좌표: 박스 상단 기준 고정 (폰트 크기와 무관하게 위치 통일)
            line_h = current_font_size * tb.line_spacing

            for line_idx, line in enumerate(lines):
                ly = box_y_top - current_font_size - line_idx * line_h

                if tb.letter_spacing > 0:
                    # 글자 간격 적용
                    cx = 0
                    if tb.alignment == "center":
                        total_w = sum(c.stringWidth(ch, font_name, current_font_size) for ch in line) + \
                                  tb.letter_spacing * (len(line) - 1)
                        cx = box_x + (box_w - total_w) / 2
                    elif tb.alignment == "right":
                        total_w = sum(c.stringWidth(ch, font_name, current_font_size) for ch in line) + \
                                  tb.letter_spacing * (len(line) - 1)
                        cx = box_x + box_w - total_w
                    else:
                        cx = box_x

                    for ch in line:
                        c.drawString(cx, ly, ch)
                        cx += c.stringWidth(ch, font_name, current_font_size) + tb.letter_spacing
                else:
                    lw = c.stringWidth(line, font_name, current_font_size)
                    if tb.alignment == "center":
                        lx = box_x + (box_w - lw) / 2
                    elif tb.alignment == "right":
                        lx = box_x + box_w - lw
                    else:
                        lx = box_x
                        
                    c.drawString(lx, ly, line)

    c.save()


def print_pdf(pdf_path: str):
    """시스템 기본 앱으로 PDF 열기 (인쇄용)"""
    if sys.platform == "darwin":
        subprocess.Popen(["open", pdf_path])
    elif sys.platform == "linux":
        subprocess.Popen(["xdg-open", pdf_path])
    elif sys.platform == "win32":
        os.startfile(pdf_path)

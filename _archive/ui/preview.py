# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""미리보기 창 (PyQt6 기반) — 용지에 네임태그 배치 표시"""

import os
import sys
import math
from typing import List, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image, ImageDraw, ImageFont, ImageQt

from models.paper import PaperSize, TagLayout
from models.tag_data import TagTemplate, TagEntry
from utils.fonts import get_default_korean_font, find_font_file
from utils.i18n import tr


class PreviewWindow(QDialog):
    """인쇄 미리보기 QDialog"""

    PREVIEW_DPI = 2.5  # 1mm → 2.5px

    def __init__(self, paper: PaperSize, layout: TagLayout,
                 template: TagTemplate, entries: List[TagEntry],
                 common_values: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("인쇄 미리보기"))
        
        self.paper = paper
        self.layout = layout
        self.template = template
        self.entries = entries
        self.common_values = common_values or []

        self._current_page = 0
        self._checked_entries = [e for e in entries if e.checked]
        self._total_pages = max(1, math.ceil(
            len(self._checked_entries) / max(1, layout.columns * layout.rows)))

        self._build_ui()
        self._render_page()

    def _build_ui(self):
        pw = int(self.paper.width_mm * self.PREVIEW_DPI) + 60
        ph = int(self.paper.height_mm * self.PREVIEW_DPI) + 120
        self.resize(min(pw, 1000), min(ph, 900))

        main_layout = QVBoxLayout(self)

        # 네비게이션
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton(tr("◀ 이전"))
        self.btn_next = QPushButton(tr("다음 ▶"))
        self.label_page = QLabel("1 / 1")
        
        self.btn_prev.clicked.connect(self._prev_page)
        self.btn_next.clicked.connect(self._next_page)
        
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.label_page, alignment=Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addStretch()
        
        main_layout.addLayout(nav_layout)

        # 캔버스
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setBackgroundBrush(Qt.GlobalColor.darkGray)
        
        main_layout.addWidget(self.view)

    def _prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._render_page()

    def _next_page(self):
        if self._current_page < self._total_pages - 1:
            self._current_page += 1
            self._render_page()

    def _render_page(self):
        self.label_page.setText(f"{self._current_page + 1} / {self._total_pages}")
        
        s = self.PREVIEW_DPI
        pw = int(self.paper.width_mm * s)
        ph = int(self.paper.height_mm * s)

        # Pillow 렌더링 (동일 모델 사용)
        img = Image.new("RGB", (pw, ph), "white")
        draw = ImageDraw.Draw(img)

        tag_w = self.layout.tag_width_mm * s
        tag_h = self.layout.tag_height_mm * s
        offset_x = self.layout.offset_x_mm * s
        offset_y = self.layout.offset_y_mm * s
        gap_x = self.layout.gap_x_mm * s
        gap_y = self.layout.gap_y_mm * s

        tags_per_page = self.layout.columns * self.layout.rows
        start_idx = self._current_page * tags_per_page

        bg_img = None
        if self.template.background_image and os.path.isfile(self.template.background_image):
            try:
                bg_img = Image.open(self.template.background_image)
                bg_img = bg_img.resize((int(tag_w), int(tag_h)), Image.LANCZOS)
            except Exception:
                pass

        for pos in range(tags_per_page):
            entry_idx = start_idx + pos
            if entry_idx >= len(self._checked_entries):
                break

            entry = self._checked_entries[entry_idx]
            col = pos % self.layout.columns
            row = pos // self.layout.columns

            x = offset_x + col * (tag_w + gap_x)
            y = offset_y + row * (tag_h + gap_y)

            if bg_img:
                img.paste(bg_img, (int(x), int(y)))

            draw.rectangle([x, y, x + tag_w, y + tag_h], outline="#CCCCCC", width=1)

            for tb_idx, tb in enumerate(self.template.text_boxes):
                text = ""
                if self.common_values and tb_idx < len(self.common_values) and self.common_values[tb_idx]:
                    text = self.common_values[tb_idx]
                else:
                    text = entry.get_value(tb_idx)

                if not text:
                    continue

                tx = x + tb.x_mm * s
                ty = y + tb.y_mm * s
                font_size = max(8, int(tb.font_size * s / 3))

                color = tb.color if tb.color.startswith("#") else "#000000"
                box_w = tb.width_mm * s
                box_h = tb.height_mm * s

                lines = text.split('\n')
                
                # --- Auto-scaling logic ---
                while font_size > 4:
                    pil_font = None
                    try:
                        font_path = find_font_file(tb.font_family)
                        if font_path:
                            pil_font = ImageFont.truetype(font_path, font_size)
                        else:
                            font_path = find_font_file(get_default_korean_font())
                            if font_path:
                                pil_font = ImageFont.truetype(font_path, font_size)
                    except Exception:
                        pass
                    
                    if not pil_font:
                        pil_font = ImageFont.load_default()
                        
                    max_w = 0
                    for line in lines:
                        try:
                            bbox = pil_font.getbbox(line)
                            w = bbox[2] - bbox[0]
                        except Exception:
                            w = len(line) * font_size * 0.6
                        if w > max_w:
                            max_w = w
                            
                    total_h = len(lines) * font_size * tb.line_spacing
                    
                    if max_w <= box_w and total_h <= box_h:
                        break
                        
                    font_size -= 0.5
                    font_size = int(font_size) # ImageFont.truetype requires integer font size
                
                line_h = font_size * tb.line_spacing
                for line_idx, line in enumerate(lines):
                    ly = ty + line_idx * line_h
                    try:
                        bbox = pil_font.getbbox(line)
                        text_w = bbox[2] - bbox[0]
                    except Exception:
                        text_w = len(line) * font_size * 0.6

                    if tb.alignment == "center":
                        lx = tx + (box_w - text_w) / 2
                    elif tb.alignment == "right":
                        lx = tx + box_w - text_w
                    else:
                        lx = tx

                    draw.text((lx, ly), line, fill=color, font=pil_font)

        # Pillow -> QImage -> QPixmap 변환
        qimage = ImageQt.ImageQt(img)
        pixmap = QPixmap.fromImage(qimage)
        
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(0, 0, pw, ph)

# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""네임태그 디자인 캔버스 (PyQt6 기반) — 배경 이미지 + 텍스트 박스 드래그/스냅"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import QBrush, QColor, QPen, QFont, QPixmap

from models.paper import TagLayout
from models.tag_data import TagTemplate, TextBox

CANVAS_SCALE = 3.0  # 1mm -> 3px (화면 표시 배율)
SNAP_THRESHOLD_MM = 2.0  # 스냅 발생 임계값 (mm)


class TextBoxGraphicsItem(QGraphicsRectItem):
    """QGraphicsScene 내에서 움직일 하나의 텍스트 박스 아이템"""

    # Scene이 아닌 외부로 신호를 보낼 방법이 제한적이므로
    # 캔버스 뷰를 통해 콜백을 호출하는 패턴 사용
    def __init__(self, index: int, tb: TextBox, layout: TagLayout, canvas_view, parent=None):
        super().__init__(parent)
        self.index = index
        self.tb = tb
        self.layout = layout
        self.canvas_view = canvas_view

        # 아이템 속성 설정
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        
        self.setAcceptHoverEvents(True)
        self._update_geometry()
        
        # 내부 텍스트 렌더링 아이템
        self.text_item = QGraphicsTextItem(self)
        self._update_style()

    def _update_geometry(self):
        w = self.tb.width_mm * CANVAS_SCALE
        h = self.tb.height_mm * CANVAS_SCALE
        self.setRect(0, 0, w, h)
        
        x = self.tb.x_mm * CANVAS_SCALE
        y = self.tb.y_mm * CANVAS_SCALE
        self.setPos(x, y)

    def _update_style(self):
        # 폰트 자동 크기 조절 (Auto-scaling)
        base_font_size = self.tb.font_size * CANVAS_SCALE / 4
        current_font_size = base_font_size
        
        box_w = self.tb.width_mm * CANVAS_SCALE
        box_h = self.tb.height_mm * CANVAS_SCALE
        
        font = QFont(self.tb.font_family, int(current_font_size))
        font.setBold(self.tb.bold)
        font.setItalic(self.tb.italic)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, self.tb.letter_spacing)
        
        self.text_item.setPlainText(self.tb.label)
        self.text_item.setFont(font)
        
        doc = self.text_item.document()
        opt = doc.defaultTextOption()
        # 자동 줄바꿈 방지 설정 (단어 단위 줄바꿈 X)
        opt.setWrapMode(opt.WrapMode.NoWrap)
        
        if self.tb.alignment == "center":
            opt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif self.tb.alignment == "right":
            opt.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            opt.setAlignment(Qt.AlignmentFlag.AlignLeft)
        doc.setDefaultTextOption(opt)
        
        # 폰트 크기 축소 루프
        while current_font_size > 4:
            # 현재 폰트를 적용한 상태에서 크기 확인
            ideal_width = doc.idealWidth()
            # 줄간격 고려한 높이 근사 계산 (QGraphicsTextItem 특성 반영)
            line_count = len(self.tb.label.split('\n'))
            ideal_height = current_font_size * 1.5 * line_count * self.tb.line_spacing
            
            if ideal_width <= box_w and ideal_height <= box_h:
                break
                
            current_font_size -= 0.5
            font.setPointSize(int(current_font_size))
            self.text_item.setFont(font)

        self.text_item.setDefaultTextColor(QColor(self.tb.color))
        self.text_item.setTextWidth(box_w)
        
        # 세로 중앙 정렬 보정 (QGraphicsTextItem 특성)
        actual_height = doc.size().height()
        if actual_height < box_h:
            y_offset = (box_h - actual_height) / 2
            self.text_item.setPos(0, y_offset)
        else:
            self.text_item.setPos(0, 0)
        
        # 박스 시각적 스타일 처리
        if self.isSelected():
            self.setPen(QPen(QColor("#0078D7"), 2, Qt.PenStyle.DashLine))
            self.setBrush(QBrush(QColor(229, 241, 251, 150))) # 살짝 투명한 파란색
        else:
            self.setPen(QPen(QColor("#888888"), 1, Qt.PenStyle.DashLine))
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemSelectedHasChanged:
            self._update_style()
            if self.isSelected():
                self.canvas_view.on_item_selected(self.index)
                
        elif change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange:
            # 드래그 중인 위치 (픽셀)
            new_pos = value
            
            # mm로 변환
            raw_x_mm = new_pos.x() / CANVAS_SCALE
            raw_y_mm = new_pos.y() / CANVAS_SCALE
            
            new_x_mm = max(0, raw_x_mm)
            new_y_mm = max(0, raw_y_mm)
            
            # --- 스마트 스냅 로직 ---
            center_x = (self.layout.tag_width_mm - self.tb.width_mm) / 2
            
            # X 중앙 스냅
            if abs(new_x_mm - center_x) < SNAP_THRESHOLD_MM:
                new_x_mm = center_x
            else:
                # X 1mm 단위 스냅
                grid_x = round(new_x_mm)
                if abs(new_x_mm - grid_x) < SNAP_THRESHOLD_MM * 0.5:
                    new_x_mm = grid_x
            
            # Y 1mm 단위 스냅
            grid_y = round(new_y_mm)
            if abs(new_y_mm - grid_y) < SNAP_THRESHOLD_MM * 0.5:
                new_y_mm = grid_y
            
            # 픽셀 좌표로 다시 변환
            snapped_pos = QPointF(new_x_mm * CANVAS_SCALE, new_y_mm * CANVAS_SCALE)
            
            return snapped_pos
            
        elif change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            # 최종 확정된 위치
            x_mm = self.pos().x() / CANVAS_SCALE
            y_mm = self.pos().y() / CANVAS_SCALE
            
            self.tb.x_mm = x_mm
            self.tb.y_mm = y_mm
            self.canvas_view.on_item_moved(self.index, x_mm, y_mm)
            
        return super().itemChange(change, value)


class TagCanvas(QGraphicsView):
    """네임태그 디자인 캔버스 (QGraphicsView)"""

    item_selected = pyqtSignal(int)
    item_moved = pyqtSignal(int, float, float)
    item_resized = pyqtSignal(int, float, float)

    def __init__(self, layout: TagLayout, template: TagTemplate, parent=None):
        super().__init__(parent)
        self.layout = layout
        self.template = template
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setBackgroundBrush(QBrush(QColor("#FFFFFF")))
        
        self._tb_items = []
        self._bg_item = None
        
        self.refresh()

    def refresh(self):
        # 씬 및 뷰 크기
        w = self.layout.tag_width_mm * CANVAS_SCALE
        h = self.layout.tag_height_mm * CANVAS_SCALE
        self.scene.setSceneRect(0, 0, w, h)
        
        # 배경 이미지 (QPixmap 사용)
        if self.template.background_image:
            pixmap = QPixmap(self.template.background_image)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(int(w), int(h), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                if self._bg_item is None:
                    self._bg_item = QGraphicsPixmapItem()
                    self._bg_item.setZValue(-1)
                    self.scene.addItem(self._bg_item)
                self._bg_item.setPixmap(pixmap)
        else:
            if self._bg_item is not None:
                self.scene.removeItem(self._bg_item)
                self._bg_item = None
                
        # 텍스트 박스 아이템 업데이트 (개수가 같으면 속성만 업데이트하여 상태 보존)
        if len(self._tb_items) == len(self.template.text_boxes):
            for i, item in enumerate(self._tb_items):
                item.tb = self.template.text_boxes[i]
                item._update_geometry()
                item._update_style()
        else:
            # 개수가 다르면 기존 항목 삭제 후 재생성 (선택 상태 복원)
            selected_idx = -1
            for i, item in enumerate(self._tb_items):
                if item.isSelected():
                    selected_idx = i
                    break
                    
            for item in self._tb_items:
                self.scene.removeItem(item)
            self._tb_items.clear()
            
            for i, tb in enumerate(self.template.text_boxes):
                item = TextBoxGraphicsItem(i, tb, self.layout, self)
                self.scene.addItem(item)
                self._tb_items.append(item)
                if i == selected_idx:
                    item.setSelected(True)

    def select_textbox(self, idx: int):
        """외부 패널에서 아이템이 선택되었을 때 캔버스에서 하이라이트"""
        if 0 <= idx < len(self._tb_items):
            self.scene.clearSelection()
            self._tb_items[idx].setSelected(True)

    def on_item_selected(self, idx: int):
        self.item_selected.emit(idx)
        
    def on_item_moved(self, idx: int, x_mm: float, y_mm: float):
        self.item_moved.emit(idx, x_mm, y_mm)

    def on_item_resized(self, idx: int, w_mm: float, h_mm: float):
        self.item_resized.emit(idx, w_mm, h_mm)

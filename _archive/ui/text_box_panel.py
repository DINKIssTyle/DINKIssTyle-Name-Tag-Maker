# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""텍스트 박스 속성 패널 (PyQt6 기반)"""

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QListWidget, QLabel, QLineEdit, QComboBox,
    QColorDialog, QCheckBox, QAbstractItemView, QFontComboBox, QDoubleSpinBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from models.tag_data import TagTemplate, TextBox
from utils.i18n import tr


class TextBoxPanel(QGroupBox):
    
    settings_changed = pyqtSignal()
    item_selected = pyqtSignal(int)
    
    def __init__(self, template: TagTemplate, parent=None):
        super().__init__(tr("텍스트 박스"), parent)
        self.template = template
        self._selected_idx = -1
        self._building = False
        
        self._build_ui()
        self.refresh_list()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 6, 4, 4)
        main_layout.setSpacing(2)
        
        # 버튼 프레임 (툴바 스타일)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        self.btn_add = QPushButton("+")
        self.btn_del = QPushButton("−")
        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        
        for btn in (self.btn_add, self.btn_del, self.btn_up, self.btn_down):
            btn.setFixedSize(32, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_add.clicked.connect(self._add_textbox)
        self.btn_del.clicked.connect(self._del_textbox)
        self.btn_up.clicked.connect(self._move_up)
        self.btn_down.clicked.connect(self._move_down)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_del)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        # 텍스트 박스 목록
        self.list_widget = QListWidget()
        self.list_widget.setFixedHeight(120)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.currentRowChanged.connect(self._on_list_select)
        main_layout.addWidget(self.list_widget)
        
        # 속성 편집 그룹
        prop_group = QGroupBox(tr("속성"))
        outer_prop_layout = QHBoxLayout(prop_group)
        outer_prop_layout.setContentsMargins(4, 6, 4, 4)
        
        prop_layout = QGridLayout()
        prop_layout.setContentsMargins(0, 0, 0, 0)
        prop_layout.setSpacing(2)
        # 0:Label, 1:Input, 2:Unit, 3:Label2, 4:Input2, 5:Unit2, 6:Stretch
        for c in range(6): prop_layout.setColumnStretch(c, 0)
        prop_layout.setColumnStretch(6, 1)
        
        # 위젯 생성 및 초기화
        self.edit_label = QLineEdit()
        self.edit_label.setFixedWidth(160)
        
        self.spin_x = QDoubleSpinBox()
        self.spin_y = QDoubleSpinBox()
        self.spin_w = QDoubleSpinBox()
        self.spin_h = QDoubleSpinBox()
        self.spin_size = QDoubleSpinBox()
        self.spin_line = QDoubleSpinBox()
        self.spin_letter = QDoubleSpinBox()
        
        for spin in (self.spin_x, self.spin_y, self.spin_w, self.spin_h, self.spin_size, self.spin_line, self.spin_letter):
            spin.setFixedWidth(65)
        
        self.spin_x.setRange(-50.0, 500.0)
        self.spin_y.setRange(-50.0, 500.0)
        self.spin_w.setRange(5.0, 500.0)
        self.spin_h.setRange(5.0, 500.0)
        self.spin_size.setRange(5.0, 150.0)
        self.spin_line.setRange(0.1, 5.0)
        self.spin_line.setSingleStep(0.1)
        self.spin_letter.setRange(-10.0, 50.0)
        
        self.combo_font = QFontComboBox()
        self.combo_font.setFixedWidth(160)
        
        self.combo_align = QComboBox()
        self.combo_align.addItem(tr("왼쪽"), "left")
        self.combo_align.addItem(tr("중앙"), "center")
        self.combo_align.addItem(tr("오른쪽"), "right")
        self.combo_align.setFixedWidth(80)

        # 그리드 배치
        # 행 0: 라벨
        lbl_l = QLabel(tr("라벨:"))
        lbl_l.setObjectName("prop_label")
        prop_layout.addWidget(lbl_l, 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.edit_label, 0, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
        
        # 공통 라벨들
        lbl_x = QLabel(tr("X:"))
        lbl_y = QLabel(tr("Y:"))
        lbl_w = QLabel(tr("너비:"))
        lbl_h = QLabel(tr("높이:"))
        lbl_font = QLabel(tr("폰트:"))
        lbl_size = QLabel(tr("크기:"))
        lbl_align = QLabel(tr("정렬:"))
        lbl_line = QLabel(tr("줄간격:"))
        lbl_letter = QLabel(tr("자간:"))
        for lbl in (lbl_x, lbl_y, lbl_w, lbl_h, lbl_font, lbl_size, lbl_align, lbl_line, lbl_letter):
            lbl.setObjectName("prop_label")

        # 행 1: X, Y
        prop_layout.addWidget(lbl_x, 1, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.spin_x, 1, 1)
        ux = QLabel(tr("mm")); ux.setObjectName("unit_label")
        prop_layout.addWidget(ux, 1, 2)
        prop_layout.addWidget(lbl_y, 1, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.spin_y, 1, 4)
        uy = QLabel(tr("mm")); uy.setObjectName("unit_label")
        prop_layout.addWidget(uy, 1, 5)

        # 행 2: 너비, 높이
        prop_layout.addWidget(lbl_w, 2, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.spin_w, 2, 1)
        uw = QLabel(tr("mm")); uw.setObjectName("unit_label")
        prop_layout.addWidget(uw, 2, 2)
        prop_layout.addWidget(lbl_h, 2, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.spin_h, 2, 4)
        uh = QLabel(tr("mm")); uh.setObjectName("unit_label")
        prop_layout.addWidget(uh, 2, 5)

        # 행 3: 폰트
        prop_layout.addWidget(lbl_font, 3, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.combo_font, 3, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)

        # 행 4: 크기, 정렬
        prop_layout.addWidget(lbl_size, 4, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.spin_size, 4, 1)
        us = QLabel(tr("pt")); us.setObjectName("unit_label")
        prop_layout.addWidget(us, 4, 2)
        prop_layout.addWidget(lbl_align, 4, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.combo_align, 4, 4, 1, 2, Qt.AlignmentFlag.AlignLeft)

        # 행 5: 줄간격, 자간
        prop_layout.addWidget(lbl_line, 5, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.spin_line, 5, 1)
        ul = QLabel(tr("배")); ul.setObjectName("unit_label")
        prop_layout.addWidget(ul, 5, 2)
        prop_layout.addWidget(lbl_letter, 5, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prop_layout.addWidget(self.spin_letter, 5, 4)
        ult = QLabel(tr("pt")); ult.setObjectName("unit_label")
        prop_layout.addWidget(ult, 5, 5)

        # 행 6: 색상, Bold/Italic
        lbl_color = QLabel(tr("색상:"))
        lbl_color.setObjectName("prop_label")
        prop_layout.addWidget(lbl_color, 6, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        color_layout = QHBoxLayout()
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(4)
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(40, 20)
        self.btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self._current_color = "#000000"
        self._update_color_btn()
        self.btn_color.clicked.connect(self._pick_color)
        color_layout.addWidget(self.btn_color)
        
        self.chk_bold = QCheckBox(tr("B"))
        self.chk_italic = QCheckBox(tr("I"))
        color_layout.addWidget(self.chk_bold)
        color_layout.addWidget(self.chk_italic)
        color_layout.addStretch()
        prop_layout.addLayout(color_layout, 6, 1, 1, 5)
        
        outer_prop_layout.addLayout(prop_layout)
        outer_prop_layout.addStretch()
        
        main_layout.addWidget(prop_group)
        
        # 실시간 속성 변경 이벤트 바인딩
        self.edit_label.textChanged.connect(self._auto_apply_props)
        self.spin_x.valueChanged.connect(self._auto_apply_props)
        self.spin_y.valueChanged.connect(self._auto_apply_props)
        self.spin_w.valueChanged.connect(self._auto_apply_props)
        self.spin_h.valueChanged.connect(self._auto_apply_props)
        self.combo_font.currentFontChanged.connect(self._auto_apply_props)
        self.spin_size.valueChanged.connect(self._auto_apply_props)
        self.combo_align.currentTextChanged.connect(self._auto_apply_props)
        self.spin_line.valueChanged.connect(self._auto_apply_props)
        self.spin_letter.valueChanged.connect(self._auto_apply_props)
        self.chk_bold.stateChanged.connect(self._auto_apply_props)
        self.chk_italic.stateChanged.connect(self._auto_apply_props)

    def _auto_apply_props(self, *args, **kwargs):
        if not self._building:
            self._apply_props()

    def refresh_list(self):
        self._building = True
        self.list_widget.clear()
        for i, tb in enumerate(self.template.text_boxes):
            self.list_widget.addItem(f"{i+1}. {tb.label}")
            
        if 0 <= self._selected_idx < len(self.template.text_boxes):
            self.list_widget.setCurrentRow(self._selected_idx)
        else:
            self._selected_idx = -1
            
        self._building = False

    def _add_textbox(self):
        tb = self.template.add_text_box(f"{tr('텍스트')}{len(self.template.text_boxes)+1}")
        self._selected_idx = len(self.template.text_boxes) - 1
        self.refresh_list()
        self._load_props(tb)
        self.settings_changed.emit()

    def _del_textbox(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            return
        self.template.remove_text_box(idx)
        if idx >= len(self.template.text_boxes):
            idx = len(self.template.text_boxes) - 1
            
        self._selected_idx = idx
        self.refresh_list()
        if idx >= 0:
            self._load_props(self.template.text_boxes[idx])
        self.settings_changed.emit()

    def _move_up(self):
        idx = self.list_widget.currentRow()
        if idx <= 0:
            return
        self.template.move_text_box(idx, idx - 1)
        self._selected_idx = idx - 1
        self.refresh_list()
        self.settings_changed.emit()

    def _move_down(self):
        idx = self.list_widget.currentRow()
        if idx < 0 or idx >= len(self.template.text_boxes) - 1:
            return
        self.template.move_text_box(idx, idx + 1)
        self._selected_idx = idx + 1
        self.refresh_list()
        self.settings_changed.emit()

    def _on_list_select(self, row: int):
        if self._building or row < 0:
            return
        self._selected_idx = row
        self._load_props(self.template.text_boxes[row])
        self.item_selected.emit(row)

    def _load_props(self, tb: TextBox):
        self._building = True
        self.edit_label.setText(tb.label)
        self.spin_x.setValue(tb.x_mm)
        self.spin_y.setValue(tb.y_mm)
        self.spin_w.setValue(tb.width_mm)
        self.spin_h.setValue(tb.height_mm)
        self.combo_font.setCurrentText(tb.font_family)
        self.spin_size.setValue(tb.font_size)
        
        idx = self.combo_align.findData(tb.alignment)
        if idx >= 0:
            self.combo_align.setCurrentIndex(idx)
            
        self.spin_line.setValue(tb.line_spacing)
        self.spin_letter.setValue(tb.letter_spacing)
        self._current_color = tb.color
        self._update_color_btn()
        self.chk_bold.setChecked(tb.bold)
        self.chk_italic.setChecked(tb.italic)
        self._building = False

    def _pick_color(self):
        col = QColor(self._current_color)
        color = QColorDialog.getColor(col, self, tr("색상 선택"))
        if color.isValid():
            self._current_color = color.name()
            self._update_color_btn()
            self._auto_apply_props()

    def _update_color_btn(self):
        self.btn_color.setStyleSheet(
            f"background-color: {self._current_color}; border: 1px solid #aaa;"
        )

    def _apply_props(self):
        if self._selected_idx < 0 or self._selected_idx >= len(self.template.text_boxes):
            return
            
        tb = self.template.text_boxes[self._selected_idx]
        tb.label = self.edit_label.text() or tr("텍스트")
        tb.x_mm = self.spin_x.value()
        tb.y_mm = self.spin_y.value()
        tb.width_mm = self.spin_w.value()
        tb.height_mm = self.spin_h.value()
        tb.font_family = self.combo_font.currentFont().family()
        tb.font_size = self.spin_size.value()
        tb.alignment = self.combo_align.currentData()
        tb.line_spacing = self.spin_line.value()
        tb.letter_spacing = self.spin_letter.value()
        tb.color = self._current_color
        tb.bold = self.chk_bold.isChecked()
        tb.italic = self.chk_italic.isChecked()
        
        # 목록의 텍스트만 선택 상실 없이 업데이트
        item = self.list_widget.item(self._selected_idx)
        if item:
            item.setText(f"{self._selected_idx+1}. {tb.label}")

        self.settings_changed.emit()

    def select_textbox(self, idx: int):
        """외부 캔버스 영역에서 터치 시 리스트 동기화"""
        if 0 <= idx < len(self.template.text_boxes):
            self._selected_idx = idx
            
            # 신호 중복을 방지하며 UI 업데이트
            self.list_widget.blockSignals(True)
            self.list_widget.setCurrentRow(idx)
            self.list_widget.blockSignals(False)
            
            self._load_props(self.template.text_boxes[idx])

    def update_position(self, idx: int, x_mm: float, y_mm: float):
        """드래그 후 좌표 동기화"""
        if 0 <= idx < len(self.template.text_boxes):
            tb = self.template.text_boxes[idx]
            tb.x_mm = x_mm
            tb.y_mm = y_mm
            if self._selected_idx == idx:
                self._building = True
                self.spin_x.setValue(x_mm)
                self.spin_y.setValue(y_mm)
                self._building = False

    def update_size(self, idx: int, w_mm: float, h_mm: float):
        """리사이즈 후 크기 동기화"""
        if 0 <= idx < len(self.template.text_boxes):
            tb = self.template.text_boxes[idx]
            tb.width_mm = w_mm
            tb.height_mm = h_mm
            if self._selected_idx == idx:
                self._building = True
                self.spin_w.setValue(w_mm)
                self.spin_h.setValue(h_mm)
                self._building = False

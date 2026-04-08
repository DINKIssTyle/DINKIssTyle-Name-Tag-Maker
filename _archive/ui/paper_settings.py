# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""용지 및 네임태그 설정 패널 (PyQt6 기반)"""

from PyQt6.QtWidgets import (
    QGroupBox, QFormLayout, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QRadioButton, QSpinBox, QDoubleSpinBox,
    QPushButton, QWidget
)
from PyQt6.QtCore import pyqtSignal, Qt

from models.paper import PaperSize, TagLayout, PAPER_PRESETS
from utils.units import mm_to_inch, inch_to_mm
from utils.i18n import tr


class PaperSettingsPanel(QGroupBox):
    
    settings_changed = pyqtSignal()
    
    def __init__(self, paper: PaperSize, layout: TagLayout, parent=None):
        super().__init__(tr("용지 / 네임태그 설정"), parent)
        self.paper = paper
        self.layout = layout
        self._unit_mode = "mm"  # "mm" or "inch"
        self._building = True
        
        self._build_ui()
        self._building = False

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 6, 4, 4)
        main_layout.setSpacing(2)
        
        # --- 단위 선택 ---
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel(tr("단위:")))
        self.radio_mm = QRadioButton(tr("mm"))
        self.radio_inch = QRadioButton(tr("inch"))
        self.radio_mm.setChecked(True)
        unit_layout.addWidget(self.radio_mm)
        unit_layout.addWidget(self.radio_inch)
        unit_layout.addStretch()
        main_layout.addLayout(unit_layout)
        
        self.radio_mm.toggled.connect(self._on_unit_change)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(2)
        # 0:PropLabel, 1:Spin1, 2:Unit1, 3:Sep/Label2, 4:Spin2, 5:Unit2, 6:Stretch
        for c in range(6): grid.setColumnStretch(c, 0)
        grid.setColumnStretch(6, 1)
        
        row = 0
        
        # --- 용지 프리셋 ---
        lbl_paper = QLabel(tr("용지:"))
        lbl_paper.setObjectName("prop_label")
        grid.addWidget(lbl_paper, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.combo_paper = QComboBox()
        self.combo_paper.setFixedWidth(160)
        for name in PAPER_PRESETS.keys():
            label = tr(name) if name != "Custom" else tr("사용자 정의")
            self.combo_paper.addItem(label, name)
        
        idx = self.combo_paper.findData(self.paper.name)
        if idx >= 0:
            self.combo_paper.setCurrentIndex(idx)
        grid.addWidget(self.combo_paper, row, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
        self.combo_paper.currentIndexChanged.connect(self._on_paper_preset)
        
        # --- 용지 크기 ---
        row += 1
        self.spin_paper_w = QDoubleSpinBox()
        self.spin_paper_h = QDoubleSpinBox()
        for spin in (self.spin_paper_w, self.spin_paper_h):
            spin.setRange(10.0, 5000.0)
            spin.setDecimals(1)
            spin.setFixedWidth(70)
        self.spin_paper_w.setValue(self.paper.width_mm)
        self.spin_paper_h.setValue(self.paper.height_mm)
        
        lbl_p_size = QLabel(tr("용지 크기:"))
        lbl_p_size.setObjectName("prop_label")
        grid.addWidget(lbl_p_size, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        grid.addWidget(self.spin_paper_w, row, 1)
        self.u_paper_w = QLabel(tr("mm"))
        self.u_paper_w.setObjectName("unit_label")
        grid.addWidget(self.u_paper_w, row, 2)

        sep_p = QLabel("×")
        sep_p.setFixedWidth(12)
        sep_p.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(sep_p, row, 3)
        
        grid.addWidget(self.spin_paper_h, row, 4)
        self.u_paper_h = QLabel(tr("mm"))
        self.u_paper_h.setObjectName("unit_label")
        grid.addWidget(self.u_paper_h, row, 5)

        # --- 태그 크기 ---
        row += 1
        self.spin_tag_w = QDoubleSpinBox()
        self.spin_tag_h = QDoubleSpinBox()
        for spin in (self.spin_tag_w, self.spin_tag_h):
            spin.setRange(5.0, 1000.0)
            spin.setDecimals(1)
            spin.setFixedWidth(70)
        self.spin_tag_w.setValue(self.layout.tag_width_mm)
        self.spin_tag_h.setValue(self.layout.tag_height_mm)
        
        lbl_t_size = QLabel(tr("태그 크기:"))
        lbl_t_size.setObjectName("prop_label")
        grid.addWidget(lbl_t_size, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        grid.addWidget(self.spin_tag_w, row, 1)
        self.u_tag_w = QLabel(tr("mm"))
        self.u_tag_w.setObjectName("unit_label")
        grid.addWidget(self.u_tag_w, row, 2)

        sep_t = QLabel("×")
        sep_t.setFixedWidth(12)
        sep_t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(sep_t, row, 3)
        
        grid.addWidget(self.spin_tag_h, row, 4)
        self.u_tag_h = QLabel(tr("mm"))
        self.u_tag_h.setObjectName("unit_label")
        grid.addWidget(self.u_tag_h, row, 5)

        # --- 배열 (열/행) ---
        row += 1
        self.spin_cols = QSpinBox()
        self.spin_rows = QSpinBox()
        for spin in (self.spin_cols, self.spin_rows):
            spin.setRange(1, 100)
            spin.setFixedWidth(70)
        self.spin_cols.setValue(self.layout.columns)
        self.spin_rows.setValue(self.layout.rows)
        
        lbl_cols = QLabel(tr("열:"))
        lbl_cols.setObjectName("prop_label")
        grid.addWidget(lbl_cols, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.spin_cols, row, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        lbl_rows = QLabel(tr("행:"))
        lbl_rows.setObjectName("prop_label")
        grid.addWidget(lbl_rows, row, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.spin_rows, row, 4, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # --- 여백 ---
        row += 1
        self.spin_off_x = QDoubleSpinBox()
        self.spin_off_y = QDoubleSpinBox()
        for spin in (self.spin_off_x, self.spin_off_y):
            spin.setRange(-500.0, 500.0)
            spin.setDecimals(1)
            spin.setFixedWidth(70)
        self.spin_off_x.setValue(self.layout.offset_x_mm)
        self.spin_off_y.setValue(self.layout.offset_y_mm)
        
        lbl_mx = QLabel(tr("여백X:"))
        lbl_mx.setObjectName("prop_label")
        grid.addWidget(lbl_mx, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.spin_off_x, row, 1)
        self.u_off_x = QLabel(tr("mm"))
        self.u_off_x.setObjectName("unit_label")
        grid.addWidget(self.u_off_x, row, 2)

        lbl_my = QLabel(tr("Y:"))
        lbl_my.setObjectName("prop_label")
        grid.addWidget(lbl_my, row, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.spin_off_y, row, 4)
        self.u_off_y = QLabel(tr("mm"))
        self.u_off_y.setObjectName("unit_label")
        grid.addWidget(self.u_off_y, row, 5)

        # --- 간격 ---
        row += 1
        self.spin_gap_x = QDoubleSpinBox()
        self.spin_gap_y = QDoubleSpinBox()
        for spin in (self.spin_gap_x, self.spin_gap_y):
            spin.setRange(0.0, 500.0)
            spin.setDecimals(1)
            spin.setFixedWidth(70)
        self.spin_gap_x.setValue(self.layout.gap_x_mm)
        self.spin_gap_y.setValue(self.layout.gap_y_mm)
        
        lbl_gx = QLabel(tr("간격X:"))
        lbl_gx.setObjectName("prop_label")
        grid.addWidget(lbl_gx, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.spin_gap_x, row, 1)
        self.u_gap_x = QLabel(tr("mm"))
        self.u_gap_x.setObjectName("unit_label")
        grid.addWidget(self.u_gap_x, row, 2)

        lbl_gy = QLabel(tr("Y:"))
        lbl_gy.setObjectName("prop_label")
        grid.addWidget(lbl_gy, row, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.spin_gap_y, row, 4)
        self.u_gap_y = QLabel(tr("mm"))
        self.u_gap_y.setObjectName("unit_label")
        grid.addWidget(self.u_gap_y, row, 5)

        grid_wrapper = QHBoxLayout()
        grid_wrapper.setContentsMargins(0, 0, 0, 0)
        grid_wrapper.addLayout(grid)
        grid_wrapper.addStretch()
        main_layout.addLayout(grid_wrapper)
        
        # 실시간 업데이트 바인딩
        for spin in [self.spin_paper_w, self.spin_paper_h, self.spin_tag_w, self.spin_tag_h,
                     self.spin_off_x, self.spin_off_y, self.spin_gap_x, self.spin_gap_y]:
            spin.valueChanged.connect(self._auto_apply)
            
        self.spin_cols.valueChanged.connect(self._auto_apply)
        self.spin_rows.valueChanged.connect(self._auto_apply)
        self.combo_paper.currentTextChanged.connect(self._auto_apply)

    def _auto_apply(self, *args, **kwargs):
        if not self._building:
            self._apply()

    def _on_paper_preset(self, index: int):
        if self._building:
            return
            
        text = self.combo_paper.currentData()
        if text in PAPER_PRESETS and text != "Custom":
            self._building = True
            w_mm, h_mm = PAPER_PRESETS[text]
            if self._unit_mode == "inch":
                self.spin_paper_w.setValue(mm_to_inch(w_mm))
                self.spin_paper_h.setValue(mm_to_inch(h_mm))
            else:
                self.spin_paper_w.setValue(w_mm)
                self.spin_paper_h.setValue(h_mm)
            self._building = False
            self._apply()

    def _on_unit_change(self):
        if self.radio_mm.isChecked():
            new_mode = "mm"
            unit_str = "mm"
        else:
            new_mode = "inch"
            unit_str = "inch"
            
        if self._unit_mode == new_mode:
            return
            
        self._building = True
        
        # 현재 값들을 기반으로 단위 변환 반영
        spins = [
            self.spin_paper_w, self.spin_paper_h,
            self.spin_tag_w, self.spin_tag_h,
            self.spin_off_x, self.spin_off_y,
            self.spin_gap_x, self.spin_gap_y
        ]
        
        for spin in spins:
            val = spin.value()
            if new_mode == "inch":
                spin.setDecimals(2)
                spin.setValue(mm_to_inch(val))
            else:
                spin.setDecimals(1)
                spin.setValue(inch_to_mm(val))
        
        # 라벨 업데이트
        unit_labels = [
            self.u_paper_w, self.u_paper_h, self.u_tag_w, self.u_tag_h,
            self.u_off_x, self.u_off_y, self.u_gap_x, self.u_gap_y
        ]
        for label in unit_labels:
            label.setText(tr("in") if new_mode == "inch" else tr("mm"))
                
        self._unit_mode = new_mode
        self._building = False

    def _to_mm(self, value):
        if self._unit_mode == "inch":
            return inch_to_mm(value)
        return value

    def _apply(self):
        # 모델 업데이트
        self.paper.name = self.combo_paper.currentText()
        self.paper.width_mm = self._to_mm(self.spin_paper_w.value())
        self.paper.height_mm = self._to_mm(self.spin_paper_h.value())
        
        self.layout.tag_width_mm = self._to_mm(self.spin_tag_w.value())
        self.layout.tag_height_mm = self._to_mm(self.spin_tag_h.value())
        self.layout.columns = self.spin_cols.value()
        self.layout.rows = self.spin_rows.value()
        self.layout.offset_x_mm = self._to_mm(self.spin_off_x.value())
        self.layout.offset_y_mm = self._to_mm(self.spin_off_y.value())
        self.layout.gap_x_mm = self._to_mm(self.spin_gap_x.value())
        self.layout.gap_y_mm = self._to_mm(self.spin_gap_y.value())

        self.settings_changed.emit()

    def refresh_ui_from_model(self):
        """저장 파일 불러오기 시 모델 갱신된 내역을 UI에 반영"""
        self._building = True
        
        self.combo_paper.setCurrentText(self.paper.name)
        
        # 내부적으로 모두 mm 기준 세팅 후 단위 컨버터 호출
        self.radio_mm.setChecked(True)
        self._unit_mode = "mm"
        
        self.spin_paper_w.setValue(self.paper.width_mm)
        self.spin_paper_h.setValue(self.paper.height_mm)
        self.spin_tag_w.setValue(self.layout.tag_width_mm)
        self.spin_tag_h.setValue(self.layout.tag_height_mm)
        self.spin_cols.setValue(self.layout.columns)
        self.spin_rows.setValue(self.layout.rows)
        self.spin_off_x.setValue(self.layout.offset_x_mm)
        self.spin_off_y.setValue(self.layout.offset_y_mm)
        self.spin_gap_x.setValue(self.layout.gap_x_mm)
        self.spin_gap_y.setValue(self.layout.gap_y_mm)
        
        self._building = False

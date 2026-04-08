# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""스프레드시트 (데이터 입력) 창 (PyQt6 기반)"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QCheckBox, QWidget, QAbstractItemView,
    QHeaderView, QApplication, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QKeySequence
from typing import List, Optional, Callable
import os

from models.tag_data import TagTemplate, TagEntry
from models.tag_data import TagTemplate, TagEntry
from utils.csv_handler import import_csv, export_csv
from utils.i18n import tr


class CheckBoxWidget(QWidget):
    """QTableWidget 내부에 넣을 중앙 정렬 체크박스 컨테이너"""
    def __init__(self, checked=True, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)
        layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

    def is_checked(self):
        return self.checkbox.isChecked()
        
    def set_checked(self, state):
        self.checkbox.setChecked(state)


class SpreadsheetWindow(QDialog):
    """네임태그 데이터 입력 QDialog"""
    
    data_updated = pyqtSignal()

    def __init__(self, template: TagTemplate, entries: List[TagEntry],
                 common_values: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("스프레드시트 데이터 입력"))
        self.resize(900, 550)
        
        self.template = template
        self.entries = entries
        self.common_values = common_values

        self._build_ui()
        self._populate()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 툴바
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton(tr("행 추가"))
        self.btn_del = QPushButton(tr("행 삭제"))
        self.btn_import = QPushButton(tr("CSV 가져오기"))
        self.btn_export = QPushButton(tr("CSV 내보내기"))
        self.btn_check_all = QPushButton(tr("전체 선택"))
        self.btn_uncheck_all = QPushButton(tr("전체 해제"))
        
        self.btn_add.clicked.connect(self._add_row)
        self.btn_del.clicked.connect(self._del_row)
        self.btn_import.clicked.connect(self._import_csv)
        self.btn_export.clicked.connect(self._export_csv)
        self.btn_check_all.clicked.connect(self._check_all)
        self.btn_uncheck_all.clicked.connect(self._uncheck_all)
        self.btn_apply.clicked.connect(self._apply)
        
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_del)
        toolbar.addSpacing(10)
        toolbar.addWidget(self.btn_import)
        toolbar.addWidget(self.btn_export)
        toolbar.addSpacing(10)
        toolbar.addWidget(self.btn_check_all)
        toolbar.addWidget(self.btn_uncheck_all)
        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        # QTableWidget
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        # 키보드 내비게이션 활성화
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        main_layout.addWidget(self.table)
        
        # 하단 텍스트 및 버튼
        bottom_layout = QVBoxLayout()
        instruction_label = QLabel(tr("엑셀이나 구글 시트에서 데이터를 복사(Ctrl+C)한 후, 아래 표에 붙여넣기(Ctrl+V) 하세요."))
        instruction_label.setStyleSheet("color: #666;")
        
        btn_layout = QHBoxLayout()
        self.btn_bottom_apply = QPushButton(tr("적용"))
        self.btn_bottom_cancel = QPushButton(tr("취소"))
        
        self.btn_bottom_apply.clicked.connect(self._apply)
        self.btn_bottom_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_bottom_apply)
        btn_layout.addWidget(self.btn_bottom_cancel)
        
        bottom_layout.addWidget(instruction_label)
        bottom_layout.addLayout(btn_layout)
        main_layout.addLayout(bottom_layout)

    def _populate(self):
        labels = self.template.get_labels()
        col_count = len(labels) + 2  # 체크박스 + 번호 + 텍스트박스들
        
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels([tr("체크"), "#"] + labels)
        
        # 열 너비 설정
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 40)
        
        row_count = len(self.entries) + 1  # 공통 값 행 + 데이터 행
        self.table.setRowCount(row_count)
        
        # 공통 값 행 (Index 0)
        self.table.setCellWidget(0, 0, QWidget()) # 빈 칸
        
        item_common_label = QTableWidgetItem(tr("공통"))
        item_common_label.setFlags(item_common_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item_common_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(0, 1, item_common_label)
        
        for j in range(len(labels)):
            val = self.common_values[j] if j < len(self.common_values) else ""
            item = QTableWidgetItem(val)
            item.setBackground(QColor(240, 240, 240))  # 공통 셀 배경 다르게
            self.table.setItem(0, j + 2, item)

        # 데이터 행 (Index 1 ~)
        for i, entry in enumerate(self.entries):
            r = i + 1
            
            # 체크박스
            cb_widget = CheckBoxWidget(entry.checked)
            self.table.setCellWidget(r, 0, cb_widget)
            
            # 번호
            item_num = QTableWidgetItem(str(i + 1))
            item_num.setFlags(item_num.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 1, item_num)
            
            # 데이터
            for j in range(len(labels)):
                val = entry.get_value(j)
                item = QTableWidgetItem(val)
                self.table.setItem(r, j + 2, item)
                
        # 클립보드 지원 이벤트 오버라이드 등록
        self.table.keyPressEvent = self._table_key_press_event

    def _table_key_press_event(self, event):
        if event.matches(QKeySequence.StandardKey.Paste):
            self._paste_from_clipboard()
        else:
            QTableWidget.keyPressEvent(self.table, event)

    def _paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return

        # TSV 형식 파싱
        rows = text.split('\n')
        # 마지막 빈 줄무시
        if rows and not rows[-1]:
            rows.pop()

        # 현재 선택된 셀 위치를 시작점으로 설정
        selected = self.table.selectedRanges()
        if selected:
            start_row = selected[0].topRow()
            start_col = selected[0].leftColumn()
        else:
            start_row = 1  # 0번 인덱스는 공통 행
            start_col = 2  # 0:체크박스, 1:번호, 2부터 데이터 시작

        # 데이터 행(1 이상), 데이터 열(2 이상) 영역에서만 붙여넣기 허용
        start_row = max(1, start_row)
        start_col = max(2, start_col)
        
        needed_rows = start_row + len(rows)
        if needed_rows > self.table.rowCount():
            # 필요한 만큼 행 추가
            for _ in range(needed_rows - self.table.rowCount()):
                self._add_row()

        for i, row in enumerate(rows):
            r = start_row + i
            cols = row.split('\t')
            for j, val in enumerate(cols):
                c = start_col + j
                if c < self.table.columnCount():
                    item = self.table.item(r, c)
                    if not item:
                        item = QTableWidgetItem(val)
                        self.table.setItem(r, c, item)
                    else:
                        item.setText(val)

    def _add_row(self):
        labels = self.template.get_labels()
        entry = TagEntry(checked=True, values=[""] * len(labels))
        self.entries.append(entry)
        self._populate()
        
        # 마지막 행으로 스크롤
        self.table.scrollToBottom()

    def _del_row(self):
        if not self.entries:
            return
            
        # 선택된 행(들) 찾기
        selected_rows = set(item.row() for item in self.table.selectedItems())
        
        # 공통 행(0) 선택 시 무시, 아무것도 선택 안됐으면 맨 아래 삭제
        rows_to_delete = [r - 1 for r in selected_rows if r > 0]
        
        if not rows_to_delete:
            self.entries.pop()
        else:
            # 뒷쪽 인덱스부터 삭제
            for idx in sorted(rows_to_delete, reverse=True):
                if 0 <= idx < len(self.entries):
                    self.entries.pop(idx)
                    
        self._populate()

    def _import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("CSV 파일 가져오기"), "", tr("CSV / TSV 파일 (*.csv *.tsv *.txt);;모든 파일 (*.*)")
        )
        if not path:
            return

        try:
            headers, data = import_csv(path)
        except Exception as e:
            QMessageBox.critical(self, tr("오류"), f"{tr('CSV 파일을 읽을 수 없습니다:')}\n{e}")
            return

        labels = self.template.get_labels()
        # 헤더 매핑
        col_map = {}
        for j, label in enumerate(labels):
            for k, header in enumerate(headers):
                if header.strip() == label.strip():
                    col_map[j] = k
                    break

        self.entries.clear()
        for row_data in data:
            vals = []
            for j in range(len(labels)):
                if j in col_map and col_map[j] < len(row_data):
                    vals.append(row_data[col_map[j]])
                else:
                    if j < len(row_data):
                        vals.append(row_data[j])
                    else:
                        vals.append("")
            self.entries.append(TagEntry(checked=True, values=vals))

        self._populate()

    def _export_csv(self):
        self._apply()
        path, _ = QFileDialog.getSaveFileName(
            self, tr("CSV 파일 내보내기"), "", tr("CSV 파일 (*.csv);;TSV 파일 (*.tsv)")
        )
        if not path:
            return

        labels = self.template.get_labels()
        data = []
        for entry in self.entries:
            row = [entry.get_value(j) for j in range(len(labels))]
            data.append(row)

        delimiter = '\t' if path.endswith('.tsv') else ','
        try:
            export_csv(path, labels, data, delimiter=delimiter)
            QMessageBox.information(self, tr("완료"), f"{tr('CSV 파일이 저장되었습니다:')}\n{os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, tr("오류"), f"{tr('저장 실패:')}\n{e}")

    def _check_all(self):
        for r in range(1, self.table.rowCount()):
            cb_widget = self.table.cellWidget(r, 0)
            if cb_widget:
                cb_widget.set_checked(True)

    def _uncheck_all(self):
        for r in range(1, self.table.rowCount()):
            cb_widget = self.table.cellWidget(r, 0)
            if cb_widget:
                cb_widget.set_checked(False)

    def _apply(self):
        labels = self.template.get_labels()
        
        # 공통 값 추출
        self.common_values.clear()
        for j in range(len(labels)):
            item = self.table.item(0, j + 2)
            self.common_values.append(item.text() if item else "")

        # 데이터(엔트리) 추출
        for i, entry in enumerate(self.entries):
            r = i + 1
            cb_widget = self.table.cellWidget(r, 0)
            if cb_widget:
                entry.checked = cb_widget.is_checked()
                
            for j in range(len(labels)):
                item = self.table.item(r, j + 2)
                entry.set_value(j, item.text() if item else "")

        self.data_updated.emit()
        self.accept()

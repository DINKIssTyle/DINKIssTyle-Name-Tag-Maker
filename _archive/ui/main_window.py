# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""메인 윈도우 (PyQt6 기반) — 전체 앱 레이아웃 및 기능 조합"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QToolBar, QSplitter, 
    QScrollArea, QFileDialog, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QComboBox, QSizePolicy

from models.paper import PaperSize, TagLayout
from models.tag_data import TagTemplate, TagEntry
from utils.i18n import tr, set_language, get_language
from ui.paper_settings import PaperSettingsPanel
from ui.text_box_panel import TextBoxPanel
from ui.tag_canvas import TagCanvas
from ui.spreadsheet import SpreadsheetWindow
from ui.preview import PreviewWindow
from utils.pdf_generator import generate_pdf, print_pdf
from utils.project_handler import save_project, load_project


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("DKST Name Tag Maker"))
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)

        # 데이터 모델 초기화
        self.paper = PaperSize.from_preset("A4")
        self.layout = TagLayout()
        self.template = TagTemplate()
        self.entries = []
        self.common_values = []

        self._spreadsheet_win = None
        self._current_file_path = None  # 현재 열려있는 프로젝트 파일 경로

        self._build_ui()
        self._load_styles()
        self._tag_canvas.refresh()

    def _load_styles(self):
        """QSS 스타일시트 로드"""
        qss_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _update_title(self):
        """타이틀바에 현재 파일명 표시"""
        if self._current_file_path:
            fname = os.path.basename(self._current_file_path)
            self.setWindowTitle(f"{tr('DINKIssTyle 명찰 제작기')} — {fname}")
        else:
            self.setWindowTitle(tr("DINKIssTyle 명찰 제작기"))

    def _build_ui(self):
        # ── 상단 툴바 ──
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        action_open = QAction("📂 " + tr("열기(&O)"), self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self._load_project)
        toolbar.addAction(action_open)

        action_save = QAction("💾 " + tr("저장(&S)"), self)
        action_save.setShortcut("Ctrl+S")
        action_save.triggered.connect(self._save_project)
        toolbar.addAction(action_save)

        action_save_as = QAction("💾 " + tr("다른 이름으로 저장(&A)"), self)
        action_save_as.setShortcut("Ctrl+Shift+S")
        action_save_as.triggered.connect(self._save_project_as)
        toolbar.addAction(action_save_as)

        toolbar.addSeparator()

        action_spreadsheet = QAction("📋 " + tr("스프레드시트"), self)
        action_spreadsheet.triggered.connect(self._open_spreadsheet)
        toolbar.addAction(action_spreadsheet)

        action_bg = QAction("🖼 " + tr("배경 이미지"), self)
        action_bg.triggered.connect(self._set_background)
        toolbar.addAction(action_bg)

        action_preview = QAction("👁 " + tr("미리보기"), self)
        action_preview.triggered.connect(self._open_preview)
        toolbar.addAction(action_preview)

        action_print = QAction("🖨 " + tr("인쇄"), self)
        action_print.triggered.connect(self._do_print)
        toolbar.addAction(action_print)

        toolbar.addSeparator()

        action_pdf = QAction(tr("PDF 저장"), self)
        action_pdf.triggered.connect(self._save_pdf)
        toolbar.addAction(action_pdf)
        
        #spacer
        empty = QWidget()
        empty.setSizePolicy(empty.sizePolicy().Policy.Expanding, empty.sizePolicy().Policy.Expanding)
        toolbar.addWidget(empty)
        
        # Language Selector
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["한국어", "English"])
        self.combo_lang.setCurrentText("한국어" if get_language() == "ko" else "English")
        self.combo_lang.currentTextChanged.connect(self._on_language_changed)
        toolbar.addWidget(self.combo_lang)

        # ── 메인 영역 (QSplitter) ──
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ── 좌측 설정 패널 (스크롤 가능) ──
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # scroll_area.setMinimumWidth(250)
        # scroll_area.setMaximumWidth(250)
        
        left_widget = QWidget()
        left_widget.setObjectName("sidebar")
        self.left_layout = QVBoxLayout(left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(2)
        
        # 용지 설정 패널
        self._paper_panel = PaperSettingsPanel(self.paper, self.layout)
        self._paper_panel.settings_changed.connect(self._on_settings_change)
        self.left_layout.addWidget(self._paper_panel)

        # 텍스트 박스 패널
        self._textbox_panel = TextBoxPanel(self.template)
        self._textbox_panel.settings_changed.connect(self._on_textbox_change)
        self._textbox_panel.item_selected.connect(self._on_textbox_select)
        self.left_layout.addWidget(self._textbox_panel)
        
        self.left_layout.addStretch()
        scroll_area.setWidget(left_widget)
        splitter.addWidget(scroll_area)

        # ── 우측 디자인 캔버스 영역 ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        canvas_label = QLabel(f"<b>{tr('네임태그 디자인')}</b>")
        right_layout.addWidget(canvas_label)

        self._tag_canvas = TagCanvas(self.layout, self.template)
        self._tag_canvas.item_selected.connect(self._on_canvas_select)
        self._tag_canvas.item_moved.connect(self._on_canvas_move)
        self._tag_canvas.item_resized.connect(self._on_canvas_resize)
        right_layout.addWidget(self._tag_canvas)
        
        splitter.addWidget(right_widget)
        # 초기 비율 설정 (좌측 260px 정도, 우측 나머지)
        splitter.setSizes([260, 800])

        # ── 하단 상태 표시줄 ──
        self.statusBar().showMessage(tr("준비"))

    def _on_language_changed(self, text):
        lang = "ko" if text == "한국어" else "en"
        set_language(lang)
        QMessageBox.information(self, tr("알림") if lang == "ko" else "Notice", 
                                "언어가 변경되었습니다. 앱을 재시작해야 적용됩니다." if lang == "ko" else "Language changed. Please restart the app for the changes to take effect.")

    def _refresh_canvas(self):
        self._tag_canvas.refresh()

    def _on_settings_change(self):
        self._refresh_canvas()
        self.statusBar().showMessage(tr("설정이 적용되었습니다."))

    def _on_textbox_change(self):
        self._refresh_canvas()

    def _on_textbox_select(self, idx: int):
        self._tag_canvas.select_textbox(idx)

    def _on_canvas_select(self, idx: int):
        self._textbox_panel.select_textbox(idx)

    def _on_canvas_move(self, idx: int, x_mm: float, y_mm: float):
        self._textbox_panel.update_position(idx, x_mm, y_mm)

    def _on_canvas_resize(self, idx: int, w_mm: float, h_mm: float):
        self._textbox_panel.update_size(idx, w_mm, h_mm)

    def _set_background(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("배경 이미지 선택"), "", tr("이미지 파일 (*.png *.jpg *.jpeg *.bmp *.gif);;모든 파일 (*.*)")
        )
        if path:
            self.template.background_image = path
            self._refresh_canvas()
            self.statusBar().showMessage(f"{tr('배경 이미지:')} {os.path.basename(path)}")

    def _open_spreadsheet(self):
        if not self.template.text_boxes:
            QMessageBox.warning(self, tr("경고"), tr("먼저 텍스트 박스를 추가해주세요."))
            return

        while len(self.common_values) < len(self.template.text_boxes):
            self.common_values.append("")

        if not self.entries:
            self.entries.append(
                TagEntry(checked=True,
                         values=[""] * len(self.template.text_boxes)))

        self._spreadsheet_win = SpreadsheetWindow(
            self.template, self.entries, self.common_values, self
        )
        self._spreadsheet_win.data_updated.connect(self._on_spreadsheet_update)
        self._spreadsheet_win.show()

    def _on_spreadsheet_update(self):
        self.statusBar().showMessage(f"데이터 {len(self.entries)}건 적용됨")

    def _open_preview(self):
        if not self.entries:
            QMessageBox.warning(self, tr("경고"), tr("스프레드시트에 데이터를 먼저 입력해주세요."))
            return

        checked = [e for e in self.entries if e.checked]
        if not checked:
            QMessageBox.warning(self, tr("경고"), tr("체크된 항목이 없습니다."))
            return

        preview_win = PreviewWindow(
            self.paper, self.layout, self.template, self.entries, self.common_values, self
        )
        preview_win.exec()

    def _do_print(self):
        checked = [e for e in self.entries if e.checked]
        if not checked:
            QMessageBox.warning(self, tr("경고"), tr("체크된 항목이 없습니다."))
            return

        import tempfile
        tmp_path = os.path.join(tempfile.gettempdir(), "nametag_print.pdf")
        try:
            generate_pdf(
                self.paper, self.layout, self.template,
                self.entries, tmp_path,
                common_values=self.common_values)
            print_pdf(tmp_path)
            self.statusBar().showMessage(tr("인쇄 다이얼로그가 열렸습니다."))
        except Exception as e:
            QMessageBox.critical(self, tr("오류"), f"{tr('PDF 생성 실패:')}\n{e}")

    def _save_pdf(self):
        checked = [e for e in self.entries if e.checked]
        if not checked:
            QMessageBox.warning(self, tr("경고"), tr("체크된 항목이 없습니다."))
            return

        path, _ = QFileDialog.getSaveFileName(
            self, tr("PDF 저장"), "", tr("PDF 파일 (*.pdf)")
        )
        if not path:
            return

        try:
            generate_pdf(
                self.paper, self.layout, self.template,
                self.entries, path,
                common_values=self.common_values)
            self.statusBar().showMessage(f"{tr('PDF 저장 완료:')} {os.path.basename(path)}")
            QMessageBox.information(self, tr("완료"), f"{tr('PDF가 저장되었습니다:')}\n{path}")
        except Exception as e:
            QMessageBox.critical(self, tr("오류"), f"{tr('PDF 생성 실패:')}\n{e}")

    def _save_project(self):
        """저장: 이미 경로가 있으면 덮어쓰기, 없으면 다른 이름으로 저장"""
        if self._current_file_path:
            self._do_save(self._current_file_path)
        else:
            self._save_project_as()

    def _save_project_as(self):
        """다른 이름으로 저장: 항상 파일 경로를 새로 묻기"""
        path, _ = QFileDialog.getSaveFileName(
            self, tr("프로젝트 저장"), "", tr("명찰 프로젝트 파일 (*.ntag)")
        )
        if not path:
            return
        self._do_save(path)

    def _do_save(self, path: str):
        """실제 저장 수행"""
        try:
            save_project(path, self.paper, self.layout, self.template, self.entries, self.common_values)
            self._current_file_path = path
            self._update_title()
            self.statusBar().showMessage(f"{tr('프로젝트 저장 완료:')} {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, tr("오류"), f"{tr('저장 실패:')}\n{e}")
            
    def _load_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("프로젝트 열기"), "", tr("명찰 프로젝트 파일 (*.ntag);;모든 파일 (*.*)")
        )
        if not path:
            return
            
        try:
            data = load_project(path)
            self.paper = data["paper"]
            self.layout = data["layout"]
            self.template = data["template"]
            self.entries = data["entries"]
            self.common_values = data["common_values"]
            
            # 현재 파일 경로 기억
            self._current_file_path = path
            self._update_title()
            
            # Reattach model to panels without recreating widget hierarchy
            self._paper_panel.paper = self.paper
            self._paper_panel.layout = self.layout
            self._paper_panel.refresh_ui_from_model()
            
            self._textbox_panel.template = self.template
            self._textbox_panel.refresh_list()
            
            self._tag_canvas.layout = self.layout
            self._tag_canvas.template = self.template
            
            self._refresh_canvas()
            self.statusBar().showMessage(f"{tr('프로젝트 불러오기 완료:')} {os.path.basename(path)}")
            
            if self._spreadsheet_win:
                self._spreadsheet_win.close()
                self._spreadsheet_win = None
                
        except Exception as e:
            QMessageBox.critical(self, tr("오류"), f"{tr('불러오기 실패:')}\n{e}")


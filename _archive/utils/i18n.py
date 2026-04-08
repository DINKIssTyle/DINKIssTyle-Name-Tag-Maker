# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""국제화(i18n) 및 언어 설정 유틸리티"""

import locale
from PyQt6.QtCore import QSettings

_current_lang = "ko"

_TRANSLATIONS = {
    "en": {
        # MainWindow
        "DKST Name Tag Maker": "DKST Name Tag Maker",
        "파일(&F)": "File(&F)",
        "열기(&O)": "Open(&O)",
        "저장(&S)": "Save(&S)",
        "다른 이름으로 저장(&A)": "Save As(&A)",
        "언어(Language)": "Language",
        "한국어": "Korean",
        "English": "English",
        "스프레드시트": "Spreadsheet",
        "배경 이미지": "Background",
        "미리보기": "Preview",
        "PDF 저장": "Save PDF",
        "인쇄": "Print",
        "준비": "Ready",
        "오류": "Error",
        "경고": "Warning",
        "성공": "Success",
        "저장 완료": "Saved successfully",
        "PDF 저장 완료": "PDF saved successfully.",
        "열기 실패": "Failed to open",
        "저장 실패": "Failed to save",
        "선택된 파일이 없습니다.": "No file selected.",
        
        # PaperSettingsPanel
        "용지 / 네임태그 설정": "Paper / Tag Settings",
        "단위:": "Unit:",
        "용지:": "Paper:",
        "용지 크기:": "Paper Size:",
        "태그:": "Tag:",
        "태그 크기:": "Tag Size:",
        "열:": "Cols:",
        "행:": "Rows:",
        "여백X:": "MarginX:",
        "Y:": "Y:",
        "간격X:": "GapX:",
        
        # TextBoxPanel
        "텍스트 박스": "Text Box",
        "+ 추가": "+ Add",
        "- 삭제": "- Del",
        "속성": "Properties",
        "라벨:": "Label:",
        "X:": "X:",
        "너비:": "Width:",
        "높이:": "Height:",
        "폰트:": "Font:",
        "크기:": "Size:",
        "정렬:": "Align:",
        "줄간격:": "Line Gap:",
        "자간:": "Letter Gap:",
        "색상:": "Color:",
        
        # SpreadsheetWindow
        "스프레드시트 데이터 입력": "Spreadsheet Data Entry",
        "데이터 붙여넣기": "Paste Data",
        "데이터 초기화": "Clear Data",
        "적용": "Apply",
        "취소": "Cancel",
        "데이터 지우기": "Clear Data",
        "모든 데이터를 지우시겠습니까?": "Are you sure you want to clear all data?",
        "엑셀이나 구글 시트에서 데이터를 복사(Ctrl+C)한 후, 아래 표에 붙여넣기(Ctrl+V) 하세요.": "Copy data from Excel or Google Sheets (Ctrl+C) and paste (Ctrl+V) into the table below.",
        "선택된 항목의 인쇄 여부를 결정합니다.": "Determine whether to print the selected item.",
        
        # PreviewWindow
        "인쇄 미리보기": "Print Preview",
        "◀ 이전": "◀ Prev",
        "다음 ▶": "Next ▶",
        "닫기": "Close",
        
        # MainWindow others
        "설정이 적용되었습니다.": "Settings applied.",
        "배경 이미지 선택": "Select Background Image",
        "이미지 파일 (*.png *.jpg *.jpeg *.bmp *.gif);;모든 파일 (*.*)": "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)",
        "배경 이미지:": "Background Image:",
        "먼저 텍스트 박스를 추가해주세요.": "Please add a text box first.",
        "스프레드시트에 데이터를 먼저 입력해주세요.": "Please enter data in the spreadsheet first.",
        "체크된 항목이 없습니다.": "No items are checked.",
        "인쇄 다이얼로그가 열렸습니다.": "Print dialog opened.",
        "PDF 생성 실패:": "Failed to generate PDF:",
        "PDF 저장 완료:": "PDF Save Complete:",
        "완료": "Complete",
        "PDF가 저장되었습니다:": "PDF has been saved:",
        "프로젝트 저장": "Save Project",
        "명찰 프로젝트 파일 (*.ntag)": "Name Tag Project File (*.ntag)",
        "프로젝트 저장 완료:": "Project saved:",
        "프로젝트 열기": "Open Project",
        "명찰 프로젝트 파일 (*.ntag);;모든 파일 (*.*)": "Name Tag Project File (*.ntag);;All Files (*.*)",
        "프로젝트 불러오기 완료:": "Project loaded:",
        "불러오기 실패:": "Load failed:",

        # SpreadsheetWindow others
        "행 추가": "Add Row",
        "행 삭제": "Delete Row",
        "CSV 가져오기": "Import CSV",
        "CSV 내보내기": "Export CSV",
        "전체 선택": "Check All",
        "전체 해제": "Uncheck All",
        "체크": "Check",
        "공통": "Common",
        "CSV 파일 가져오기": "Import CSV File",
        "CSV / TSV 파일 (*.csv *.tsv *.txt);;모든 파일 (*.*)": "CSV / TSV Files (*.csv *.tsv *.txt);;All Files (*.*)",
        "CSV 파일을 읽을 수 없습니다:": "Cannot read CSV file:",
        "CSV 파일 내보내기": "Export CSV File",
        "CSV 파일 (*.csv);;TSV 파일 (*.tsv)": "CSV Files (*.csv);;TSV Files (*.tsv)",
        "CSV 파일이 저장되었습니다:": "CSV file saved:",

        # TagCanvas
        "네임태그 디자인": "Name Tag Design",
        "새 텍스트": "New Text",
        "텍스트": "Text",
        
        # Units and Others
        "열": "Cols",
        "행": "Rows",
        "배": "x",
        "mm": "mm",
        "in": "in",
        "inch": "inch",
        "pt": "pt",
        "이미지": "Image",
        "사용자 정의": "Custom",
        "색상 선택": "Select Color",
        "x": "x",
        "X:": "X:",
        "Y:": "Y:",
        "왼쪽": "Left",
        "중앙": "Center",
        "오른쪽": "Right",
        "B": "B",
        "I": "I"
    }
}

def init_i18n():
    """QSettings에서 언어를 불러오거나 시스템 기본값을 설정합니다."""
    global _current_lang
    settings = QSettings("DINKIssTyle", "NameTagMaker")
    saved_lang = settings.value("language", "")
    
    if saved_lang in ["ko", "en"]:
        _current_lang = saved_lang
    else:
        # 시스템 기본 언어 확인
        try:
            sys_lang, _ = locale.getdefaultlocale()
            if sys_lang and not sys_lang.startswith('ko'):
                _current_lang = "en"
            else:
                _current_lang = "ko"
        except:
            _current_lang = "ko"

def set_language(lang: str):
    """현재 언어를 변경하고 QSettings에 저장합니다."""
    global _current_lang
    if lang in ["ko", "en"]:
        _current_lang = lang
        settings = QSettings("DINKIssTyle", "NameTagMaker")
        settings.setValue("language", lang)

def get_language() -> str:
    return _current_lang

def tr(text: str) -> str:
    """한국어 문자열을 입력받아 현재 언어 설정에 맞는 문자열을 반환합니다."""
    if _current_lang == "ko":
        return text
    
    # 영문(등록된 번역)이 있으면 반환, 없으면 원본 반환
    return _TRANSLATIONS.get(_current_lang, {}).get(text, text)

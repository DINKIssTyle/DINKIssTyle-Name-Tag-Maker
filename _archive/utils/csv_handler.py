# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""CSV 가져오기/내보내기 핸들러"""

import csv
import io
from typing import List, Tuple, Optional


def detect_delimiter(text: str) -> str:
    """텍스트에서 구분자 자동 감지 (탭 또는 쉼표)"""
    first_line = text.split('\n')[0] if text else ""
    tab_count = first_line.count('\t')
    comma_count = first_line.count(',')
    return '\t' if tab_count > comma_count else ','


def import_csv(file_path: str) -> Tuple[List[str], List[List[str]]]:
    """CSV 파일을 읽어서 헤더와 데이터 반환"""
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    delimiter = detect_delimiter(content)
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    rows = list(reader)

    if not rows:
        return [], []

    headers = rows[0]
    data = rows[1:]
    return headers, data


def import_csv_text(text: str) -> Tuple[List[str], List[List[str]]]:
    """CSV 텍스트를 파싱하여 헤더와 데이터 반환"""
    delimiter = detect_delimiter(text)
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)

    if not rows:
        return [], []

    headers = rows[0]
    data = rows[1:]
    return headers, data


def export_csv(file_path: str, headers: List[str], data: List[List[str]],
               delimiter: str = ','):
    """데이터를 CSV 파일로 내보내기"""
    with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)


def export_csv_text(headers: List[str], data: List[List[str]],
                    delimiter: str = ',') -> str:
    """데이터를 CSV 텍스트로 변환"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter)
    writer.writerow(headers)
    for row in data:
        writer.writerow(row)
    return output.getvalue()

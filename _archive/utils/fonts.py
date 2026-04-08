# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""폰트 관련 유틸리티"""

import sys
import os
import re
import unicodedata
from typing import Optional

def get_default_korean_font() -> str:
    """OS에 맞는 기본 한글 폰트 반환"""
    if sys.platform == "darwin":
        return "AppleGothic"
    elif sys.platform == "win32":
        return "Malgun Gothic"
    return "NanumGothic"

_FONT_CACHE = {}

# Qt에서 알려주는 폰트명(또는 한글명)과 실제 시스템에 저장된 영문 파일명의 매핑 (띄어쓰기/특수문자 제거된 형태 기준)
_FONT_NAME_MAP = {
    # 윈도우 기본 폰트들 (맥에 설치된 경우 대응)
    "맑은고딕": "malgun",
    "malgungothic": "malgun",
    "굴림": "gulim",
    "굴림체": "gulim",
    "돋움": "dotum",
    "돋움체": "dotum",
    "바탕": "batang",
    "바탕체": "batang",
    "궁서": "gungseo",
    "궁서체": "gungseo",
    
    # 무료 널리 쓰이는 폰트들
    "배달의민족주아": "bmjua",
    "배달의민족도현": "bmdohyeon",
    "배달의민족한나는열한살": "bmhanna",
    "배달의민족기랑해랑": "bmkiranghaerang",
    "배달의민족연성": "bmyenseong",
    "티몬몬소리": "tmonmonsori",
    "티몬몬소리체": "tmonmonsori",
    "야놀자야체": "yanolja",
    "나눔스퀘어": "nanumsquare",
    "나눔스퀘어라운드": "nanumsquareround",
    "나눔바른고딕": "nanumbarungothic",
    "본고딕": "notosanskr",
    "notosanscjk": "notosans",
    "본명조": "notoserifkr"
}

def _clean_font_name(name: str) -> str:
    """폰트 이름 비교를 위해 공백, 특수문자 제거 및 한글 NFC 정규화 수행"""
    # macOS NFD(자소 분리) 한글을 NFC(입력기 한글)로 병합
    normalized = unicodedata.normalize('NFC', name.lower())
    # 영문, 숫자, 완전한 한글 문자만 남김
    cleaned = re.sub(r'[^a-zA-Z0-9가-힣]', '', normalized)
    return _FONT_NAME_MAP.get(cleaned, cleaned)

def find_font_file(font_family: str) -> Optional[str]:
    """시스템에서 폰트 파일 경로(TTF/OTF) 찾기. PDF와 미리보기 모두 동일 로직 활용."""
    if not font_family:
        font_family = get_default_korean_font()
        
    if font_family in _FONT_CACHE:
        return _FONT_CACHE[font_family]
        
    font_dirs = []
    if sys.platform == "darwin":
        font_dirs = [
            "/System/Library/Fonts/Supplemental",
            "/System/Library/Fonts",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts"),
        ]
    elif sys.platform == "win32":
        font_dirs = [os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")]
    else:
        font_dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts")]

    target = _clean_font_name(font_family)
    if not target:
        target = "applegothic"

    # 1단계: 정확한 파일명 매치 (TTF/OTF 우선, TTC 후순위)
    ttc_fallback = None
    for font_dir in font_dirs:
        if not os.path.isdir(font_dir):
            continue
        for root, dirs, files in os.walk(font_dir):
            for fname in files:
                ext = fname.lower().rsplit('.', 1)[-1] if '.' in fname else ''
                if ext in ('ttf', 'otf', 'ttc'):
                    name = _clean_font_name(os.path.splitext(fname)[0])
                    if name and name == target:
                        path = os.path.join(root, fname)
                        if ext in ('ttf', 'otf'):
                            _FONT_CACHE[font_family] = path
                            return path
                        elif ttc_fallback is None:
                            ttc_fallback = path

    if ttc_fallback:
        _FONT_CACHE[font_family] = ttc_fallback
        return ttc_fallback

    # 2단계: 부분 문자열 매치 (TTF/OTF 우선)
    ttc_fallback = None
    for font_dir in font_dirs:
        if not os.path.isdir(font_dir):
            continue
        for root, dirs, files in os.walk(font_dir):
            for fname in files:
                ext = fname.lower().rsplit('.', 1)[-1] if '.' in fname else ''
                if ext in ('ttf', 'otf', 'ttc'):
                    name = _clean_font_name(os.path.splitext(fname)[0])
                    if name and target and (target in name or name in target):
                        path = os.path.join(root, fname)
                        if ext in ('ttf', 'otf'):
                            _FONT_CACHE[font_family] = path
                            return path
                        elif ttc_fallback is None:
                            ttc_fallback = path

    if ttc_fallback:
        _FONT_CACHE[font_family] = ttc_fallback
        return ttc_fallback

    # 부분 매치도 실패했을 경우 기본 폰트 파일 강제 지정
    if sys.platform == "darwin" and font_family != get_default_korean_font():
        return find_font_file(get_default_korean_font())
        
    return None

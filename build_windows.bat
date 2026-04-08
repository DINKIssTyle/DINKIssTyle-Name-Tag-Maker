@echo off
REM Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

echo ======================================
echo     윈도우(Windows)용 빌드를 시작합니다.
echo ======================================

REM clean 옵션과 함께 윈도우 amd64 바이너리 빌드 수행
wails build -platform windows/amd64 -clean

if %ERRORLEVEL% EQU 0 (
    echo ======================================
    echo   Windows 빌드가 성공적으로 완료되었습니다!
    echo   결과물은 build/bin 폴더를 확인해주세요.
    echo ======================================
) else (
    echo ======================================
    echo   Windows 빌드 중 오류가 발생했습니다.
    echo ======================================
    exit /b 1
)

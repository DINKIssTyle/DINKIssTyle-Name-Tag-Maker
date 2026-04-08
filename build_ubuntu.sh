#!/bin/bash
# Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

echo "======================================"
echo "    우분투(Linux)용 빌드를 시작합니다. "
echo "======================================"

# clean 옵션과 함께 리눅스 amd64 바이너리 빌드 수행
wails build -platform linux/amd64 -clean

if [ $? -eq 0 ]; then
    echo "======================================"
    echo "  Ubuntu 빌드가 성공적으로 완료되었습니다!"
    echo "  결과물은 build/bin 폴더를 확인해주세요."
    echo "======================================"
else
    echo "======================================"
    echo "  Ubuntu 빌드 중 오류가 발생했습니다."
    echo "======================================"
    exit 1
fi

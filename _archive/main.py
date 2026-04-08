# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""DINKIssTyle 명찰 제작기 — PyQt6 진입점"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from utils.i18n import init_i18n

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    init_i18n()
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

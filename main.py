import sys
from PyQt6.QtWidgets import QApplication

from ui.theme import build_stylesheet
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Prevenir warning de 'setPointSize <= 0 (-1)' forzando fuente base nativa
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    app.setStyleSheet(build_stylesheet())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

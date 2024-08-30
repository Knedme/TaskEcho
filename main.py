import sys
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6 import uic


class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        uic.loadUi('./ui/main.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

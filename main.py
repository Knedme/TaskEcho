import sys
from PyQt6.QtWidgets import QWidget, QApplication


class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

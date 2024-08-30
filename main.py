import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import uic, QtCore


class MainWindow(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('./ui/main.ui', self)

        # Add a flag to make the window stay on top
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.move(50, 50)  # Move the window to the side of the screen

        self.status_bar.showMessage('Loaded sample.rec')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

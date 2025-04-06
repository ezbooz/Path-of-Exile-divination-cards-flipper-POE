import sys
from PyQt6.QtWidgets import QApplication
from utils.utils import MainWindow
from __version__ import __version__


def main():
    app = QApplication(sys.argv)
    app.setApplicationVersion(__version__)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

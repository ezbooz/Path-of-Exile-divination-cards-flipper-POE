import sys

from PyQt6.QtWidgets import QApplication

from __version__ import __version__
from utils.utils import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationVersion(__version__)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

import sys

from PyQt6.QtWidgets import QApplication

from __version__ import __version__ as version
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationVersion(version)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

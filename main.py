import sys
from PyQt6.QtWidgets import QApplication

from poeNinja.ninjaAPI import poeNinja
from utils.utils import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    # ninja = poeNinja()
    # ninja.get_data("Standard")
    main()

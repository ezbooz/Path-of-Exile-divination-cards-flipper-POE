import json

from PyQt6.QtCore import QPropertyAnimation, Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
                             QLabel, QMainWindow, QMessageBox, QPushButton,
                             QStyle, QStyledItemDelegate, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from __version__ import __version__ as version
from gui.styles import (COMBO_BOX, COPY_LABEL, FOOTER, FOOTER_LABEL, HEADER,
                        HEADER_LABEL, MAIN_WINDOW, MESSAGE_BOX, START_BUTTON,
                        STATUS_LABEL, TABLE_WIDGET, UPDATE_BUTTON,
                        get_update_message)
from poeNinja.ninjaAPI import poeNinja
from utils.utils import Utils


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.utils = Utils()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle(
            f"Path of Exile Card Flipper v{version} | github.com/ezbooz"
        )
        self.setFixedSize(1070, 700)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.create_header()
        self.create_footer()
        self.create_table()
        self.create_controls()

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.table_widget, 1)
        main_layout.addLayout(self.controls_layout)
        main_layout.addWidget(self.copy_label)
        main_layout.addWidget(self.footer)

        self.setStyleSheet(MAIN_WINDOW)

    def create_header(self):
        self.header = QLabel(HEADER)
        self.header.setStyleSheet(HEADER_LABEL)

    def create_table(self):
        self.table_widget = QTableWidget()
        self.table_widget.setItemDelegate(NoFocusDelegate())
        self.table_widget.setStyleSheet(TABLE_WIDGET)
        self.table_widget.setShowGrid(False)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

    def create_controls(self):
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setSpacing(10)

        self.league_selector = QComboBox()
        self.league_selector.addItems(
            [league["name"] for league in self.utils.get_current_leagues()]
        )
        self.league_selector.setStyleSheet(COMBO_BOX)

        self.start_button = QPushButton(" Start ")
        self.start_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.start_button.setStyleSheet(START_BUTTON)

        self.status_label = QLabel("Select league")
        self.status_label.setStyleSheet(STATUS_LABEL)

        self.update_button = QPushButton(" Check for Updates ")
        self.update_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        )
        self.update_button.setStyleSheet(UPDATE_BUTTON)

        self.controls_layout.addWidget(self.league_selector)
        self.controls_layout.addWidget(self.start_button)
        self.controls_layout.addWidget(self.status_label)
        self.controls_layout.addStretch(1)
        self.controls_layout.addWidget(self.update_button)

        self.copy_label = QLabel("")
        self.copy_label.setStyleSheet(COPY_LABEL)
        self.copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.copy_label.setVisible(False)

    def create_footer(self):
        self.footer = QLabel(FOOTER)
        self.footer.setStyleSheet(FOOTER_LABEL)
        self.footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.footer.setOpenExternalLinks(True)
        self.footer.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

    def setup_connections(self):
        self.table_widget.cellClicked.connect(self.copy_card_name)
        self.start_button.clicked.connect(self.process_data)
        self.update_button.clicked.connect(self.check_for_updates)

    def process_data(self):
        self.status_label.setText("Processing data...")
        QApplication.processEvents()
        selected_league = self.league_selector.currentText()

        try:
            poe_ninja = poeNinja()
            poe_ninja.get_data(selected_league)
            divination_data, currency_data, unique_items = self.utils.load_data()

            highscores = self.utils.calculate_highscores(
                divination_data, currency_data, unique_items
            )
            highscores_sorted = sorted(
                highscores.values(), key=lambda x: x["Profit"], reverse=True
            )

            self.display_results(highscores_sorted)
            self.status_label.setText("Data loaded successfully")

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def display_results(self, highscores_sorted):
        with open("Data\\Currency.json", "r") as file:
            data = json.load(file)
            divine_orb_value = next(
                (
                    line["receive"]["value"]
                    for line in data["lines"]
                    if line["currencyTypeName"] == "Divine Orb"
                ),
                None,
            )

        if divine_orb_value is None:
            self.status_label.setText("Error: Divine Orb price not found!")
            return

        self.table_widget.setRowCount(len(highscores_sorted))
        self.table_widget.setColumnCount(8)

        headers = [
            "#",
            "Name",
            "Type",
            "Total profit",
            "Profit per card",
            "1 card price",
            "Total set price",
            "Reward price",
        ]
        self.table_widget.setHorizontalHeaderLabels(headers)
        header = self.table_widget.horizontalHeader()
        for col in range(self.table_widget.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)

        self.table_widget.setColumnWidth(0, 40)

        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHeight(row, 20)

        for row, item in enumerate(highscores_sorted):
            self.create_table_item(row, 0, str(row + 1))
            self.populate_table_row(row, item, divine_orb_value)

        for col in range(1, self.table_widget.columnCount()):
            self.table_widget.resizeColumnToContents(col)

    def populate_table_row(self, row, item, divine_orb_value):
        profit_in_divine = round(item["Profit"] / divine_orb_value, 2)
        profit_per_card_in_divine = round(item["Profitpercard"] / divine_orb_value, 2)
        total_in_divine = round(item["Total"] / divine_orb_value, 2)
        sellprice_in_divine = round(item["Sellprice"] / divine_orb_value, 2)
        cost_in_divine = round(item["Cost"] / divine_orb_value, 2)

        self.create_table_item(row, 1, item["Name"], align_left=True)
        self.create_table_item(row, 2, item["Type"], align_left=True)
        self.create_table_item(
            row, 3, f"{int(item['Profit'])} c ({profit_in_divine} d)"
        )
        self.create_table_item(
            row, 4, f"{int(item['Profitpercard'])} c ({profit_per_card_in_divine} d)"
        )
        self.create_table_item(row, 5, f"{int(item['Cost'])} c ({cost_in_divine} d)")
        self.create_table_item(row, 6, f"{int(item['Total'])} c ({total_in_divine} d)")
        self.create_table_item(
            row, 7, f"{int(item['Sellprice'])} c ({sellprice_in_divine} d)"
        )

    def create_table_item(self, row, col, text, align_left=False):
        item = QTableWidgetItem(text)
        item.setBackground(QColor(0, 0, 0, 0))
        if col == 3:
            self.set_item_foreground_color(item, text)
        if not align_left:
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
        self.table_widget.setItem(row, col, item)
        return item

    def set_item_foreground_color(self, item, text):
        try:
            value = float(text.split()[0])
            if value > 0:
                item.setForeground(QColor("#4CAF50"))
            elif value < 0:
                item.setForeground(QColor("#F44336"))
        except:
            pass

    def copy_card_name(self, row):
        item = self.table_widget.item(row, 1)
        QApplication.clipboard().setText(item.text())
        self.show_notification("Copied!")

    def show_notification(self, text, duration=2):
        if not hasattr(self, "copy_label"):
            return  # или создаем label, если его нет

        if hasattr(self, "_copy_timer"):
            self._copy_timer.stop()
        if hasattr(self, "fade_animation"):
            self.fade_animation.stop()

        label_width = 200
        label_height = 30
        label_x = (self.central_widget.width() - label_width) // 2  # По центру
        label_y = (
            self.central_widget.height() - label_height - 10
        )  # 10px от нижнего края

        self.copy_label.setGeometry(label_x, label_y, label_width, label_height)
        self.copy_label.setText(text)
        self.copy_label.setStyleSheet(COPY_LABEL)

        self.fade_animation = QPropertyAnimation(self.copy_label, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()

        self.copy_label.setVisible(True)

        self._copy_timer = QTimer()
        self._copy_timer.setSingleShot(True)
        self._copy_timer.timeout.connect(self._hide_copy_label)
        self._copy_timer.start(duration * 1000)

    def _hide_copy_label(self):
        if hasattr(self, "fade_animation"):
            self.fade_animation.stop()

        self.fade_animation = QPropertyAnimation(self.copy_label, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(lambda: self.copy_label.setVisible(False))
        self.fade_animation.start()

    def check_for_updates(self):
        remote_version = self.utils.check_for_updates()
        if remote_version:
            if remote_version != version:
                self.status_label.setText(f"Update available: v{remote_version}")
                self.show_notification("Update available!", 5)
                self.show_update_message(remote_version)
            else:
                self.status_label.setText("You have the latest version")
        else:
            self.status_label.setText("Failed to check for updates")

    def show_update_message(self, remote_version):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Update Available")
        msg_box.setTextFormat(Qt.TextFormat.RichText)

        update_message = get_update_message(remote_version, version)
        msg_box.setText(update_message)

        msg_box.setStyleSheet(MESSAGE_BOX)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        msg_box.exec()


class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)

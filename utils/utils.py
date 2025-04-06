import json
import os
import re
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QApplication,
    QLabel, QHBoxLayout, QStyle, QStyledItemDelegate, QComboBox,
)

from poeNinja.ninjaAPI import poeNinja


class Utils:
    def __init__(self):
        pass

    def create_directories(self, *directories):
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_item_name(self, url):
        temp = url.split("/")
        temp = temp[5].split("=")
        return temp[2]

    def fetch_url_data(self, url):
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        web_byte = urlopen(req).read()
        return json.loads(web_byte.decode())

    def save_data_to_file(self, data, file_path):
        with open(file_path, "w+") as outfile:
            json.dump(data, outfile)

    def load_data(self):
        with open("Data\\DivinationCard.json", "r") as read_file:
            divination_data = json.load(read_file)

        with open("Data\\Currency.json", "r") as read_file:
            currency_data = json.load(read_file)

        unique_items = {}
        for file in os.listdir("Uniquedata"):
            file_loc = os.path.join("Uniquedata", file)
            with open(file_loc, "r") as read_file:
                data = json.load(read_file)
                for item in data["lines"]:
                    unique_items[item["name"]] = item["chaosValue"]

        return divination_data, currency_data, unique_items

    def process_card(
        self,
        name,
        chaos_value,
        stack_size,
        explicit_modifiers,
        currency,
        unique_items,
        divination_data,
    ):
        total_cost = chaos_value * stack_size
        type_info = explicit_modifiers[0]["text"]
        match = re.match("<(.*)>{(.*)}", type_info)
        if match:
            if match.group(1) == "currencyitem":
                reward_type = "Currency"
                items = match.group(2).split("x ")
                if len(items) == 1:
                    items.insert(0, "1")
                if items[1] == "Master Cartographer's Sextant":
                    items[1] = "Awakened Sextant"
                try:
                    reward_value = currency.get(items[1], 0) * float(items[0])
                except KeyError:
                    print(
                        f"KeyError: Item '{items[1]}' not found in currency data for card '{name}'"
                    )
                    return None
            elif match.group(1) == "uniqueitem":
                reward_type = "Unique"
                item_reward = match.group(2)
                if item_reward == "Charan's Sword":
                    item_reward = "Oni-Goroshi"
                if name == "Azyran's Reward":
                    item_reward = "The Anima Stone"
                try:
                    reward_value = unique_items.get(item_reward, 0)
                except KeyError:
                    print(
                        f"KeyError: Item '{item_reward}' not found in unique items data for card '{name}'"
                    )
                    return None
            else:
                reward_type = "Divination"
                item_reward = match.group(2)
                try:
                    reward_value = divination_data.get(item_reward, 0)
                except KeyError:
                    print(
                        f"KeyError: Item '{item_reward}' not found in divination data for card '{name}'"
                    )
                    return None
            profit = round((reward_value - total_cost), 2)
            return {
                "Name": name,
                "Type": reward_type,
                "Profit": profit,
                "Cost": chaos_value,
                "Stack": stack_size,
                "Profitpercard": round(profit / stack_size, 2),
                "Total": total_cost,
                "Sellprice": reward_value,
            }
        return None

    def calculate_highscores(self, divination_data, currency_data, unique_items):
        highscores = {}
        for item in divination_data["lines"]:
            name = item["name"]
            chaos_value = item["chaosValue"]
            stack_size = item.get("stackSize", 1)
            explicit_modifiers = item.get("explicitModifiers", [])
            card_data = self.process_card(
                name,
                chaos_value,
                stack_size,
                explicit_modifiers,
                currency_data,
                unique_items,
                divination_data,
            )
            if card_data:
                highscores[name] = card_data
        return highscores

    def get_current_leagues(self):
        url = "https://api.pathofexile.com/leagues?type=main"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
        req = Request(url, headers=headers)

        with urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

        current_time = datetime.now(timezone.utc)
        active_leagues = []

        for league in data:
            end_at = league.get('endAt')
            if end_at is not None:
                end_date = datetime.fromisoformat(end_at.replace('Z', '+00:00'))
                if end_date < current_time:
                    continue

            name = league.get('name', '').lower()
            if any(word in name for word in ['hardcore', 'ssf', 'ruthless', 'solo self-found']):
                continue

            active_leagues.append(league)

        return active_leagues


class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.utils = Utils()
        self.setWindowTitle("Path of Exile Card Flipper | github.com/ezbooz")
        self.setFixedSize(1000, 700)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)


        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        header = QLabel("""
            <a href='https://github.com/ezbooz/Path-of-Exile-divination-cards-flipper-POE'
            style='text-decoration:none; color:#f0f0f0;'>
            Path of Exile Card Flipper
            </a>
        """)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 15px 0;
                color: #f0f0f0;
                border-bottom: 1px solid #444;
            }
            QLabel:hover {
                color: #aa9c39;
                text-shadow: 0 0 8px rgba(170, 156, 57, 0.3);
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setOpenExternalLinks(True)
        header.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        header.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(header)


        self.table_widget = QTableWidget(self)
        self.table_widget.setItemDelegate(NoFocusDelegate())
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                color: #e0e0e0;
                gridline-color: #444;
                font-size: 12px;
                alternate-background-color: #2a2a2a;
            }
           QTableWidget::item {
               padding: 5px;
               background: transparent;
               border: none;
           }
            QTableWidget::item:selected {
                background-color: #3a3a3a;
                color: white;
                border: none; 
                outline: none;
            }
            QTableWidget::item:focus {
            outline: none;
            }
            QHeaderView::section {
                background-color: #333;
                color: #f0f0f0;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #444;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """)
        main_layout.addWidget(self.table_widget, 1)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.league_selector = QComboBox()
        self.league_selector.addItems([
            league["name"] for league in self.utils.get_current_leagues()
        ])
        self.league_selector.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: #f0f0f0;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #4CAF50;
            }

            QComboBox QAbstractItemView {
                background-color: #333;
                color: #f0f0f0;
                border: 1px solid #444;
            }
            QComboBox::item {
                padding: 10px;
            }
            QComboBox::item:selected {
                background-color: #4CAF50;
            }
        """)
        button_layout.addWidget(self.league_selector)


        self.button = QPushButton(" Start ", self)
        self.button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(self.button)


        self.status_label = QLabel("Choose your league...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #aaa;
                font-size: 12px;
                padding: 5px;
            }
        """)
        button_layout.addWidget(self.status_label)

        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)


        self.copy_label = QLabel("")
        self.copy_label.setStyleSheet("""
            QLabel {
                background-color: rgba(76, 175, 80, 180);
                color: white;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                opacity: 0;
            }
        """)
        self.copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.copy_label.setVisible(False)
        main_layout.addWidget(self.copy_label)

        footer = QLabel(
            "<a href='https://github.com/ezbooz' style='text-decoration:none; color:#666;'>github.com/ezbooz</a>")
        footer.setStyleSheet("""
            QLabel {
                font-size: 11px;
                padding-top: 10px;
                border-top: 1px solid #444;
            }
            QLabel:hover {
                color: #999;
            }
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.setOpenExternalLinks(True)
        footer.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        main_layout.addWidget(footer)


        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_widget.cellClicked.connect(self.copy_card_name)


        self.button.clicked.connect(self.process_data)


        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
            }
        """)

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
        with open('Data\\Currency.json', 'r') as file:
            data = json.load(file)
            divine_orb_value = None
            for line in data["lines"]:
                if line["currencyTypeName"] == "Divine Orb":
                    divine_orb_value = line["receive"]["value"]
                    break

        if divine_orb_value is None:
            self.status_label.setText("Error: Divine Orb price not found!")
            return

        self.table_widget.setRowCount(len(highscores_sorted))
        self.table_widget.setColumnCount(7)

        headers = [
            "Name",
            "Type",
            "Total profit",
            "Profit per card",
            "1 card price",
            "Total set price",
            "Reward price",
        ]
        self.table_widget.setHorizontalHeaderLabels(headers)


        self.table_widget.setColumnWidth(0, 200)
        self.table_widget.setColumnWidth(1, 100)
        for col in range(2, 7):
            self.table_widget.setColumnWidth(col, 120)


        for row, item in enumerate(highscores_sorted):
            profit_in_divine = round(item["Profit"] / divine_orb_value, 2)
            profit_per_card_in_divine = round(item["Profitpercard"] / divine_orb_value, 2)
            total_in_divine = round(item["Total"] / divine_orb_value, 2)
            sellprice_in_divine = round(item["Sellprice"] / divine_orb_value, 2)
            cost_in_divine = round(item["Cost"] / divine_orb_value, 2)


            self.create_table_item(row, 0, item["Name"], align_left=True)
            self.create_table_item(row, 1, item["Type"], align_left=True)
            self.create_table_item(row, 2, f"{int(item['Profit'])} c ({profit_in_divine} d)")
            self.create_table_item(row, 3, f"{int(item['Profitpercard'])} c ({profit_per_card_in_divine} d)")
            self.create_table_item(row, 4, f"{int(item['Cost'])} c ({cost_in_divine} d)")
            self.create_table_item(row, 5, f"{int(item['Total'])} c ({total_in_divine} d)")
            self.create_table_item(row, 6, f"{int(item['Sellprice'])} c ({sellprice_in_divine} d)")


        self.highlight_top_rows()

    def create_table_item(self, row, col, text, align_left=False):
        item = QTableWidgetItem(text)
        item.setBackground(QColor(0, 0, 0, 0))
        if not align_left:
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table_widget.setItem(row, col, item)
        return item

    def highlight_top_rows(self):
        for row in range(min(3, self.table_widget.rowCount())):
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item:
                    item.setBackground(QColor(76, 175, 80, 50))

    def copy_card_name(self, row, column):
        item = self.table_widget.item(row, 0)
        if not item:
            return


        QApplication.clipboard().setText(item.text())


        if hasattr(self, '_copy_timer'):
            self._copy_timer.stop()
        if hasattr(self, 'fade_animation'):
            self.fade_animation.stop()


        rect = self.table_widget.visualItemRect(item)
        global_pos = self.table_widget.mapToGlobal(rect.topLeft())
        local_pos = self.central_widget.mapFromGlobal(global_pos)


        label_width = 80
        label_height = rect.height()
        label_x = local_pos.x() + rect.width() + 10
        label_y = local_pos.y()


        self.copy_label.setGeometry(label_x, label_y, label_width, label_height)
        self.copy_label.setText("Copied!")
        self.copy_label.setStyleSheet("""
            QLabel {
                background-color: rgba(76, 175, 80, 180);
                color: white;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                opacity: 0;
            }
        """)


        self.fade_animation = QPropertyAnimation(self.copy_label, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()

        self.copy_label.setVisible(True)


        self._copy_timer = QTimer()
        self._copy_timer.setSingleShot(True)
        self._copy_timer.timeout.connect(self._hide_copy_label)
        self._copy_timer.start(2000)

    def _hide_copy_label(self):
        if hasattr(self, 'fade_animation'):
            self.fade_animation.stop()

        self.fade_animation = QPropertyAnimation(self.copy_label, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(lambda: self.copy_label.setVisible(False))
        self.fade_animation.start()
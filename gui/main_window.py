import json
from typing import Dict, List, Optional

from PyQt6.QtCore import QPropertyAnimation, Qt, QTimer, QUrl
from PyQt6.QtGui import QColor, QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from __version__ import __version__ as version
from __version__ import __version_description__
from gui.styles import (
    COMBO_BOX,
    COPY_LABEL,
    FOOTER,
    FOOTER_LABEL,
    HEADER,
    HEADER_LABEL,
    MAIN_WINDOW,
    MESSAGE_BOX,
    START_BUTTON,
    STATUS_LABEL,
    TABLE_WIDGET,
    UPDATE_BUTTON,
    get_update_message,
)
from poeNinja.ninjaAPI import PoeNinja
from utils.utils import Utils


class NoFocusDelegate(QStyledItemDelegate):
    """Delegate that removes focus highlight from table items."""

    def paint(self, painter, option, index):
        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)


class MainWindow(QMainWindow):
    """Main application window for Path of Exile Card Flipper."""

    def __init__(self):
        super().__init__()
        self.utils = Utils()
        self._setup_ui()
        self._setup_connections()
        self._setup_animation_timers()

    def _setup_ui(self) -> None:
        """Initialize all UI components."""
        self._configure_main_window()
        self._create_widgets()
        self._setup_layout()
        self.setStyleSheet(MAIN_WINDOW)

    def _configure_main_window(self) -> None:
        """Configure main window properties."""
        self.setWindowTitle(
            f"Path of Exile Card Flipper v{version} | github.com/ezbooz"
        )
        self.setFixedSize(1070, 700)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

    def _create_widgets(self) -> None:
        """Create all widgets used in the UI."""
        self._create_header()
        self._create_table()
        self._create_controls()
        self._create_footer()

    def _setup_layout(self) -> None:
        """Set up the main layout structure."""
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.table_widget, 1)
        main_layout.addLayout(self.controls_layout)
        main_layout.addWidget(self.copy_label)
        main_layout.addWidget(self.footer)

    def _setup_connections(self) -> None:
        """Connect signals to slots."""
        self.table_widget.cellClicked.connect(self.copy_card_name)
        self.start_button.clicked.connect(self.process_data)
        self.update_button.clicked.connect(self.check_for_updates)
        self.table_widget.cellDoubleClicked.connect(self.generate_trade_link)

    def _setup_animation_timers(self) -> None:
        """Initialize animation timers."""
        self._copy_timer = QTimer()
        self._copy_timer.setSingleShot(True)
        self._copy_timer.timeout.connect(self._hide_copy_label)

    def _create_header(self) -> None:
        """Create the header widget."""
        self.header = QLabel(HEADER)
        self.header.setStyleSheet(HEADER_LABEL)

    def _create_table(self) -> None:
        """Create and configure the main table widget."""
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

    def _create_controls(self) -> None:
        """Create control widgets (buttons, combo boxes, labels)."""
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setSpacing(10)

        self._create_league_selector()
        self._create_start_button()
        self._create_status_label()
        self._create_update_button()
        self._create_copy_label()

    def _create_league_selector(self) -> None:
        """Create and populate the league selector combo box."""
        self.league_selector = QComboBox()
        self.league_selector.addItems(
            [league["name"] for league in self.utils.get_current_leagues()]
        )
        self.league_selector.setStyleSheet(COMBO_BOX)
        self.controls_layout.addWidget(self.league_selector)

    def _create_start_button(self) -> None:
        """Create the start/process data button."""
        self.start_button = QPushButton(" Start ")
        self.start_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.start_button.setStyleSheet(START_BUTTON)
        self.controls_layout.addWidget(self.start_button)

    def _create_status_label(self) -> None:
        """Create the status label."""
        self.status_label = QLabel("Select league")
        self.status_label.setStyleSheet(STATUS_LABEL)
        self.controls_layout.addWidget(self.status_label)
        self.controls_layout.addStretch(1)

    def _create_update_button(self) -> None:
        """Create the update check button."""
        self.update_button = QPushButton(" Check for Updates ")
        self.update_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        )
        self.update_button.setStyleSheet(UPDATE_BUTTON)
        self.controls_layout.addWidget(self.update_button)

    def _create_copy_label(self) -> None:
        """Create the copy notification label."""
        self.copy_label = QLabel("")
        self.copy_label.setStyleSheet(COPY_LABEL)
        self.copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.copy_label.setVisible(False)

    def _create_footer(self) -> None:
        """Create the footer widget."""
        self.footer = QLabel(FOOTER)
        self.footer.setStyleSheet(FOOTER_LABEL)
        self.footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.footer.setOpenExternalLinks(True)
        self.footer.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

    def process_data(self) -> None:
        """Process and display PoE card flipping data."""
        self.status_label.setText("Processing data...")
        QApplication.processEvents()

        try:
            data = self._fetch_and_process_data()
            if data:
                self._display_results(data)
                self.status_label.setText("Data loaded successfully")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def _fetch_and_process_data(self) -> Optional[List[Dict]]:
        """Fetch and process PoE Ninja data."""
        selected_league = self.league_selector.currentText()
        poe_ninja = PoeNinja()
        poe_ninja.get_data(selected_league)
        divination_data, currency_data, unique_items = self.utils.load_data()

        highscores = self.utils.calculate_highscores(
            divination_data, currency_data, unique_items
        )
        return sorted(highscores.values(), key=lambda x: x["Profit"], reverse=True)

    def _display_results(self, highscores_sorted: List[Dict]) -> None:
        """Display processed results in the table."""
        divine_orb_value = self._get_divine_orb_value()
        if divine_orb_value is None:
            self.status_label.setText("Error: Divine Orb price not found!")
            return

        self._setup_table_structure(highscores_sorted)
        self._populate_table_data(highscores_sorted, divine_orb_value)

    def _get_divine_orb_value(self) -> Optional[float]:
        """Get the current Divine Orb value from currency data."""
        try:
            with open("Data\\Currency.json", "r") as file:
                data = json.load(file)
                return next(
                    (
                        line["receive"]["value"]
                        for line in data["lines"]
                        if line["currencyTypeName"] == "Divine Orb"
                    ),
                    None,
                )
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _setup_table_structure(self, data: List[Dict]) -> None:
        """Configure table structure and headers."""
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels(
            [
                "#",
                "Name",
                "Type",
                "Total profit",
                "Profit per card",
                "1 card price",
                "Total set price",
                "Reward price",
            ]
        )

        header = self.table_widget.horizontalHeader()
        for col in range(self.table_widget.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)

        self.table_widget.setColumnWidth(0, 50)
        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHeight(row, 20)

    def _populate_table_data(self, data: List[Dict], divine_value: float) -> None:
        """Populate table with processed data."""
        for row, item in enumerate(data):
            self._add_table_row(row, item, divine_value)

        for col in range(1, self.table_widget.columnCount()):
            self.table_widget.resizeColumnToContents(col)

    def _add_table_row(self, row: int, item: Dict, divine_value: float) -> None:
        """Add a single row of data to the table."""

        # Create conversion functions for currency
        def to_divine(value: float) -> float:
            return round(value / divine_value, 2)

        # Convert values
        profit_divine = to_divine(item["Profit"])
        profit_per_card_divine = to_divine(item["Profitpercard"])
        total_divine = to_divine(item["Total"])
        sellprice_divine = to_divine(item["Sellprice"])
        cost_divine = to_divine(item["Cost"])

        # Add items to the row
        self._create_table_item(row, 0, str(row + 1))
        self._create_table_item(row, 1, item["Name"], align_left=True)
        self._create_table_item(row, 2, item["Type"], align_left=True)
        self._create_table_item(row, 3, f"{int(item['Profit'])} c ({profit_divine} d)")
        self._create_table_item(
            row, 4, f"{int(item['Profitpercard'])} c ({profit_per_card_divine} d)"
        )
        self._create_table_item(row, 5, f"{int(item['Cost'])} c ({cost_divine} d)")
        self._create_table_item(row, 6, f"{int(item['Total'])} c ({total_divine} d)")
        self._create_table_item(
            row, 7, f"{int(item['Sellprice'])} c ({sellprice_divine} d)"
        )

    def _create_table_item(
        self, row: int, col: int, text: str, align_left: bool = False
    ) -> QTableWidgetItem:
        """Create and configure a table widget item."""
        item = QTableWidgetItem(text)
        item.setBackground(QColor(0, 0, 0, 0))

        if col == 3:
            self._set_item_foreground_color(item, text)

        if not align_left:
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )

        self.table_widget.setItem(row, col, item)
        return item

    @staticmethod
    def _set_item_foreground_color(item: QTableWidgetItem, text: str) -> None:
        """Set item text color based on value (positive/negative)."""
        try:
            value = float(text.split()[0])
            color = "#4CAF50" if value > 0 else "#F44336" if value < 0 else None
            if color:
                item.setForeground(QColor(color))
        except (ValueError, IndexError):
            pass

    def copy_card_name(self, row: int) -> None:
        """Copy card name to clipboard from selected row."""
        item = self.table_widget.item(row, 1)
        QApplication.clipboard().setText(item.text())
        self.show_notification("Copied!")

    def show_notification(self, text: str, duration: int = 2) -> None:
        """Show a temporary notification message."""
        if not hasattr(self, "copy_label"):
            return

        # Stop any ongoing animations/timers
        self._copy_timer.stop()
        if hasattr(self, "fade_animation"):
            self.fade_animation.stop()

        # Position the label
        label_width = 200
        label_height = 30
        label_x = (self.central_widget.width() - label_width) // 2
        label_y = self.central_widget.height() - label_height - 10

        self.copy_label.setGeometry(label_x, label_y, label_width, label_height)
        self.copy_label.setText(text)
        self.copy_label.setStyleSheet(COPY_LABEL)

        # Set up fade-in animation
        self.fade_animation = QPropertyAnimation(self.copy_label, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()

        self.copy_label.setVisible(True)
        self._copy_timer.start(duration * 1000)

    def _hide_copy_label(self) -> None:
        """Hide the copy notification with fade-out animation."""
        if hasattr(self, "fade_animation"):
            self.fade_animation.stop()

        self.fade_animation = QPropertyAnimation(self.copy_label, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(lambda: self.copy_label.setVisible(False))
        self.fade_animation.start()

    def check_for_updates(self) -> None:
        """Check for application updates."""
        result = self.utils.check_for_updates()

        if not result:
            self.status_label.setText("Failed to check for updates")
            return

        remote_version, remote_description = result

        if remote_version != version:
            self.status_label.setText(f"Update available: v{remote_version}")
            self.show_notification("Update available!", 5)
            self._show_update_message(remote_version, remote_description)
        else:
            self.show_notification("You have the latest version")
            self.status_label.setText("You have the latest version")

    def _show_update_message(
        self, remote_version: str, remote_description: str
    ) -> None:
        """Show update available message box."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Update Available")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(get_update_message(remote_version, version, remote_description))
        msg_box.setStyleSheet(MESSAGE_BOX)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        msg_box.exec()

    def generate_trade_link(self, row: int, column: int) -> None:
        """Generate trade link for the selected item and copy to clipboard."""
        item_name = self.table_widget.item(row, 1).text()
        league = self.league_selector.currentText()

        trade_query = {
            "query": {
                "status": {"option": "online"},
                "type": item_name,
                "stats": [{"type": "and", "filters": []}],
            },
            "sort": {"price": "asc"},
        }

        encoded_query = json.dumps(trade_query)
        trade_url = (
            f"https://www.pathofexile.com/trade/search/{league}?q={encoded_query}"
        )

        QDesktopServices.openUrl(QUrl(trade_url))

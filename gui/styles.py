MAIN_WINDOW = """
    QMainWindow {
        background-color: #1a1a1a;
    }
    QWidget {
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
"""

HEADER_LABEL = """
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
"""

TABLE_WIDGET = """
    QTableWidget {
        background-color: #252525;
        border: 1px solid #333;
        border-radius: 6px;
        color: #e0e0e0;
        gridline-color: #333;
        font-size: 13px;
        alternate-background-color: #252525;
    }
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #333;
    }
    QTableWidget::item:selected {
        background-color: #3a3a3a;
        color: white;
        border: none;
    }
    QHeaderView::section {
        background-color: #2d2d2d;
        color: #f0f0f0;
        padding: 10px;
        border: none;
        font-weight: bold;
        font-size: 13px;
        border-bottom: 2px solid #4CAF50;
    }
    QScrollBar:vertical {
        background: #252525;
        width: 12px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: #4CAF50;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
        background: none;
    }
"""

COMBO_BOX = """
    QComboBox {
        background-color: #2d2d2d;
        color: #f0f0f0;
        border: 1px solid #444;
        border-radius: 5px;
        padding: 8px 15px;
        font-size: 14px;
        min-width: 100px;
    }
    QComboBox:hover {
        border: 1px solid #4CAF50;
    }
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        color: #f0f0f0;
        border: 1px solid #444;
        selection-background-color: #4CAF50;
        padding: 8px;
    }
"""

START_BUTTON = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 5px;
        min-width: 120px;
        transition: all 0.3s;
    }
    QPushButton:hover {
        background-color: #45a049;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
    }
    QPushButton:pressed {
        background-color: #3d8b40;
        transform: translateY(1px);
    }
    QPushButton:disabled {
        background-color: #333;
        color: #666;
    }
"""

UPDATE_BUTTON = """
    QPushButton {
        background-color: #2d2d2d;
        color: #f0f0f0;
        border: 1px solid #444;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 5px;
        min-width: 120px;
        transition: all 0.3s;
    }
    QPushButton:hover {
        background-color: #3a3a3a;
        border: 1px solid #4CAF50;
        transform: translateY(-1px);
    }
    QPushButton:pressed {
        background-color: #333;
        transform: translateY(1px);
    }
"""

STATUS_LABEL = """
    QLabel {
        color: #aaa;
        font-size: 13px;
        padding: 8px 12px;
        background-color: #2d2d2d;
        border-radius: 4px;
    }
"""

COPY_LABEL = """
    QLabel {
        background-color: rgba(76, 175, 80, 180);
        color: white;
        padding: 3px 8px;
        border-radius: 3px;
        font-size: 12px;
        opacity: 0;
    }
"""
FOOTER = "<a href='https://github.com/ezbooz' style='text-decoration:none; color:#666;'>github.com/ezbooz</a>"
FOOTER_LABEL = """
    QLabel {
        font-size: 11px;
        padding-top: 10px;
        border-top: 1px solid #444;
    }
    QLabel:hover {
        color: #999;
    }
"""

MESSAGE_BOX = """
    QMessageBox {
    }
    QLabel {
        color: #e0e0e0;
    }
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        min-width: 80px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
"""


def get_update_message(remote_version, version):
    return f"""
        <p style='font-size:14px;'>A new version (<b>v{remote_version}</b>) is available!</p>
        <p style='font-size:13px;'>Current version: v{version}</p><br>
        <p style='font-size:14px;'>Download update: 
        <a href='https://github.com/ezbooz/Path-of-Exile-divination-cards-flipper-POE' 
        style='color:#4CAF50; text-decoration:none;'>
        <b>GitHub Repository</b></a></p>
        </div>
    """


HEADER = """
            <div style='text-align: center;'>
                <h1 style='margin: 0; color: #f0f0f0; font-weight: bold;'>
                    <a href='https://github.com/ezbooz/Path-of-Exile-divination-cards-flipper-POE'
                    style='text-decoration: none; color: #f0f0f0;'>
                    Path of Exile Card Flipper
                    </a>
                </h1>
                <p style='margin: 5px 0 0; color: #aaa; font-size: 12px;'>
                    Click card name to copy | Select league and click Start
                </p>
            </div>
        """

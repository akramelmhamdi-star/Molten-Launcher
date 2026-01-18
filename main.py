import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Global Dark Theme Stylesheet
    app.setStyleSheet("""
    QMainWindow {
        background-color: #1e1e1e;
        color: #ecf0f1;
    }
    QWidget {
        background-color: #1e1e1e;
        color: #ecf0f1;
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }
    QLabel {
        color: #bdc3c7;
    }
    QPushButton {
        background-color: #34495e;
        color: #ecf0f1;
        border: 1px solid #2c3e50;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #3e5871;
    }
    QPushButton:pressed {
        background-color: #2c3e50;
    }
    QLineEdit, QSpinBox, QComboBox {
        background-color: #2c3e50;
        border: 1px solid #34495e;
        border-radius: 4px;
        padding: 6px;
        color: #ecf0f1;
        selection-background-color: #e67e22;
    }
    QListWidget {
        background-color: #252525;
        border: 1px solid #2c3e50;
        border-radius: 4px;
    }
    QScrollBar:vertical {
        border: none;
        background: #2c3e50;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #95a5a6;
        min-height: 20px;
        border-radius: 5px;
    }
    QGroupBox {
        border: 1px solid #34495e;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: #e67e22;
        font-weight: bold;
    }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

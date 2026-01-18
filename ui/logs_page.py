from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("""
            font-family: Consolas, monospace;
            background-color: #000;
            color: #0f0;
            border: 1px solid #333;
        """)
        layout.addWidget(self.log_view)

    def append_log(self, text):
        self.log_view.append(text)
        # Scroll to bottom
        sb = self.log_view.verticalScrollBar()
        sb.setValue(sb.maximum())

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QScrollArea, QFrame, QLabel, QPushButton, QGridLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
import requests
from app_state import state

class ModsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Modrinth mods...")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_mods)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # Results Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QGridLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.results_container)
        layout.addWidget(scroll)

    def search_mods(self):
        query = self.search_input.text()
        if not query: return
        
        # Clear previous
        for i in reversed(range(self.results_layout.count())): 
            self.results_layout.itemAt(i).widget().setParent(None)

        # Fetch (Mocking for stability/speed if API fails, but trying real first)
        try:
            # Modrinth API search
            url = f"https://api.modrinth.com/v2/search?query={query}&limit=10"
            resp = requests.get(url, timeout=5)
            hits = resp.json().get('hits', [])
            
            row = 0
            col = 0
            for hit in hits:
                card = self.create_mod_card(hit)
                self.results_layout.addWidget(card, row, col)
                col += 1
                if col > 1: # 2 columns
                    col = 0
                    row += 1

        except Exception as e:
            err_label = QLabel(f"Error fetching mods: {e}")
            self.results_layout.addWidget(err_label)

    def create_mod_card(self, data):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(frame)
        
        # Icon (skipped for now to avoid async image complexity in one file, just name)
        name = QLabel(data['title'])
        name.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(name)
        
        author = QLabel(f"by {data['author']}")
        author.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(author)
        
        desc = QLabel(data['description'])
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        btn = QPushButton("Install")
        btn.setStyleSheet("background-color: #2980b9; border: none; padding: 5px;")
        btn.clicked.connect(lambda: self.install_mod(data))
        layout.addWidget(btn)
        
        return frame

    def install_mod(self, data):
        if not state.active_modpack:
             print("No active modpack selected!")
             return
             
        # Real install logic would go here (fetch versions -> match mc version -> download jar)
        print(f"Installing {data['title']} to {state.active_modpack['name']}")

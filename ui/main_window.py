from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QStackedWidget, QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal
from .play_page import PlayPage
from .modpacks_page import ModpacksPage
from .mods_page import ModsPage
from .logs_page import LogsPage
from .skins_page import SkinsPage

class MainWindow(QMainWindow):
    modpack_updated = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoltenLauncher")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        logo_label = QLabel("MOLTEN\nLAUNCHER")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-weight: bold; font-size: 20px; padding: 20px; color: #e67e22;")
        sidebar_layout.addWidget(logo_label)

        self.nav_buttons = []
        self.add_nav_button("Play", 0, sidebar_layout)
        self.add_nav_button("Modpacks", 1, sidebar_layout)
        self.add_nav_button("Mods", 2, sidebar_layout)
        self.add_nav_button("Skins", 3, sidebar_layout)
        self.add_nav_button("Logs", 4, sidebar_layout)

        sidebar_layout.addStretch()
        
        user_label = QLabel("Player")
        user_label.setStyleSheet("padding: 15px; background-color: #1a1a1a;")
        sidebar_layout.addWidget(user_label)

        main_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        self.logs_page = LogsPage()
        self.play_page = PlayPage(self.logs_page)
        self.modpacks_page = ModpacksPage(self)
        self.mods_page = ModsPage()
        self.skins_page = SkinsPage()

        self.pages.addWidget(self.play_page)
        self.pages.addWidget(self.modpacks_page)
        self.pages.addWidget(self.mods_page)
        self.pages.addWidget(self.skins_page)
        self.pages.addWidget(self.logs_page)

        self.nav_buttons[0].setChecked(True)
        
        self.modpack_updated.connect(self.play_page.refresh_modpacks)

    def add_nav_button(self, text, index, layout):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.clicked.connect(lambda: self.pages.setCurrentIndex(index))
        layout.addWidget(btn)
        self.nav_buttons.append(btn)

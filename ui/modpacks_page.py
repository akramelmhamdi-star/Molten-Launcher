from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QListWidgetItem, QPushButton, QLineEdit, QComboBox, 
                               QLabel, QInputDialog, QMessageBox)
import requests
from app_state import state

class ModpacksPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        header.addWidget(QLabel("My Modpacks"))
        
        create_btn = QPushButton("+ New Instance")
        create_btn.clicked.connect(self.create_modpack)
        create_btn.setStyleSheet("background-color: #27ae60;")
        header.addWidget(create_btn)
        
        layout.addLayout(header)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget::item { 
                padding: 10px; 
                margin: 5px; 
                background-color: #34495e; 
                border-radius: 5px;
            }
            QListWidget::item:selected {
                border: 2px solid #e67e22;
            }
        """)
        layout.addWidget(self.list_widget)
        
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for mp in state.modpacks:
            item = QListWidgetItem(f"{mp['name']} - {mp['version']} ({mp['loader']})")
            self.list_widget.addItem(item)

    def create_modpack(self):
        try:
            versions_manifest = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()
            releases = [v['id'] for v in versions_manifest['versions'] if v['type'] == 'release']
        except:
            releases = ["1.20.4", "1.20.1", "1.19.4"]

        name, ok = QInputDialog.getText(self, "Create Modpack", "Modpack Name:")
        if not ok or not name: return

        version, ok = QInputDialog.getItem(self, "Select Version", "Minecraft Version:", releases, 0, False)
        if not ok: return

        loader, ok = QInputDialog.getItem(self, "Select Loader", "Mod Loader:", ["Vanilla", "Fabric", "Forge"], 0, False)
        if not ok: return

        state.add_modpack(name, version, loader)
        self.refresh_list()
        
        # Trigger refresh on play page
        self.main_window.modpack_updated.emit()
        
        QMessageBox.information(self, "Success", "Modpack created!")

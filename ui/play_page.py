from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, 
    QComboBox, QFileDialog, QProgressBar, QGroupBox, QFormLayout, 
    QHBoxLayout, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from app_state import state
from launcher.game import LaunchWorker, MSLoginWorker, MSLoginFinisher
import webbrowser

class PlayPage(QWidget):
    def __init__(self, logs_page):
        super().__init__()
        self.logs_page = logs_page
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        container = QWidget()
        container.setMaximumWidth(800)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)
        layout.addWidget(container, 0, Qt.AlignCenter)

        header = QLabel("Minecraft: Java Edition")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #e67e22;")
        container_layout.addWidget(header)

        self.banner = QLabel("Select a Modpack to Play")
        self.banner.setAlignment(Qt.AlignCenter)
        self.banner.setStyleSheet("""
            background-color: #2c3e50; 
            border-radius: 10px; 
            padding: 40px; 
            font-size: 18px;
            border: 2px solid #34495e;
            color: #ecf0f1;
        """)
        container_layout.addWidget(self.banner)

        # -------------------------
        # Launch Settings
        # -------------------------
        settings_group = QGroupBox("Launch Settings")
        settings_layout = QFormLayout()
        settings_layout.setSpacing(10)

        self.username_input = QLineEdit(state.username)
        self.username_input.setPlaceholderText("Enter username...")
        self.username_input.textChanged.connect(self.update_state)
        settings_layout.addRow("Username:", self.username_input)

        ms_layout = QHBoxLayout()
        self.ms_login_btn = QPushButton("Microsoft Login")
        self.ms_login_btn.clicked.connect(self.ms_login_init)
        self.ms_login_btn.setMinimumHeight(35)
        ms_layout.addWidget(self.ms_login_btn)
        ms_layout.addStretch()
        settings_layout.addRow("Account:", ms_layout)

        self.ram_input = QSpinBox()
        self.ram_input.setRange(1024, 32768)
        self.ram_input.setSingleStep(512)
        self.ram_input.setSuffix(" MB")
        self.ram_input.setValue(state.ram)
        self.ram_input.valueChanged.connect(self.update_state)
        settings_layout.addRow("RAM:", self.ram_input)

        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit(state.minecraft_dir)
        self.dir_input.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_dir)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_btn)
        settings_layout.addRow("Game Dir:", dir_layout)

        self.java_input = QLineEdit(state.java_path)
        self.java_input.setPlaceholderText("Auto-detect or path to javaw.exe")
        self.java_input.textChanged.connect(self.update_state)
        settings_layout.addRow("Java Path:", self.java_input)

        settings_group.setLayout(settings_layout)
        container_layout.addWidget(settings_group)

        # -------------------------
        # Play Controls
        # -------------------------
        controls_group = QGroupBox("Play")
        controls_vbox = QVBoxLayout()

        self.modpack_selector = QComboBox()
        self.modpack_selector.setMinimumHeight(35)
        self.modpack_selector.currentIndexChanged.connect(self.modpack_changed)
        controls_vbox.addWidget(QLabel("Selected Modpack:"))
        controls_vbox.addWidget(self.modpack_selector)

        self.launch_btn = QPushButton("PLAY")
        self.launch_btn.setMinimumHeight(60)
        self.launch_btn.clicked.connect(self.launch_game)
        controls_vbox.addWidget(self.launch_btn)

        controls_group.setLayout(controls_vbox)
        container_layout.addWidget(controls_group)

        # -------------------------
        # Status & Progress
        # -------------------------
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #e67e22; font-weight: bold;")
        container_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        container_layout.addWidget(self.progress_bar)

        layout.addStretch()
        self.refresh_modpacks()

    # -------------------------
    # Helper Functions
    # -------------------------
    def update_state(self):
        state.username = self.username_input.text()
        state.ram = self.ram_input.value()
        state.java_path = self.java_input.text()
        state.save()

    def browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Minecraft Directory", state.minecraft_dir)
        if d:
            self.dir_input.setText(d)
            state.minecraft_dir = d
            state.save()

    def refresh_modpacks(self):
        current_data = self.modpack_selector.currentData()
        self.modpack_selector.clear()
        self.modpack_selector.addItem("Vanilla (Latest)", "latest-release")
        for mp in state.modpacks:
            self.modpack_selector.addItem(f"{mp['name']} ({mp['version']})", mp)

        if current_data:
            index = self.modpack_selector.findData(current_data)
            if index >= 0:
                self.modpack_selector.setCurrentIndex(index)
        elif state.active_modpack:
            index = self.modpack_selector.findData(state.active_modpack)
            if index >= 0:
                self.modpack_selector.setCurrentIndex(index)

    def modpack_changed(self):
        data = self.modpack_selector.currentData()
        if data == "latest-release":
            self.banner.setText("Vanilla Minecraft\nLatest Release")
            state.active_modpack = None
        else:
            self.banner.setText(f"{data['name']}\nLoader: {data['loader']}")
            state.active_modpack = data
        state.save()

    # -------------------------
    # Launch Game
    # -------------------------
    def launch_game(self):
        version = "latest-release"
        data = self.modpack_selector.currentData()
        if data != "latest-release":
            version = data['version']
        else:
            import minecraft_launcher_lib
            version = minecraft_launcher_lib.utils.get_latest_version(state.minecraft_dir)["release"]

        self.launch_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.worker = LaunchWorker(
            state.username, version, state.minecraft_dir, state.ram, state.java_path, state.ms_auth_data
        )
        self.worker.progress_update.connect(self.update_progress)
        self.worker.log_output.connect(self.logs_page.append_log)
        self.worker.finished.connect(self.launch_finished)
        self.worker.error.connect(self.launch_error)
        self.worker.start()

    def update_progress(self, status, percent):
        self.status_label.setText(status)
        self.progress_bar.setValue(percent)

    def launch_finished(self):
        self.status_label.setText("Game Session Ended")
        self.launch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def launch_error(self, err):
        self.status_label.setText(f"Error: {err}")
        self.launch_btn.setEnabled(True)

    # -------------------------
    # Microsoft Device Code Login
    # -------------------------
    def ms_login_init(self):
        self.status_label.setText("Logging in with Microsoft...")
        self.ms_worker = MSLoginWorker()
        self.ms_worker.code_needed.connect(self.show_device_code)
        self.ms_worker.finished.connect(self.ms_login_success)
        self.ms_worker.error.connect(lambda e: QMessageBox.warning(self, "Login Error", e))
        self.ms_worker.start()

    def show_device_code(self, instructions):
        box = QMessageBox(self)
        box.setWindowTitle("Microsoft Login")
        box.setText("Open the link below in your browser and log in.\n\n"
                    "After login, copy the FULL redirect URL and paste it back into the launcher.")
        box.setDetailedText(instructions)

        copy_btn = box.addButton("Copy Login URL", QMessageBox.ActionRole)
        ok_btn = box.addButton("OK", QMessageBox.AcceptRole)

        def copy_link():
            # extract URL from instructions
            for line in instructions.splitlines():
                if line.startswith("http"):
                    QGuiApplication.clipboard().setText(line)
                    break

        copy_btn.clicked.connect(copy_link)
        box.exec()

        # Ask user to paste the redirect URL
        url_input, ok = QInputDialog.getText(
            self, "Enter Auth URL",
            "Paste the full redirect URL from browser after login:"
        )
        if ok and url_input:
            self.ms_finisher = MSLoginFinisher(url_input)
            self.ms_finisher.finished.connect(self.ms_login_success)
            self.ms_finisher.error.connect(lambda e: QMessageBox.warning(self, "Login Error", e))
            self.ms_finisher.start()

    def ms_login_success(self, auth_data):
        state.ms_auth_data = auth_data
        state.username = auth_data["name"]
        self.username_input.setText(auth_data["name"])
        state.save()
        self.status_label.setText(f"Logged in as {auth_data['name']}")
        QMessageBox.information(self, "Login Success", f"Logged in as {auth_data['name']}")

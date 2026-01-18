from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QFileDialog, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QImage, QPainter
from app_state import state
import os

class SkinsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        header = QLabel("Skin Customization")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #e67e22;")
        layout.addWidget(header)

        info = QLabel("Upload a custom skin for your offline account. This will be used when launching in offline mode.")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Skin Preview Area
        preview_container = QFrame()
        preview_container.setStyleSheet("background-color: #2c3e50; border-radius: 10px; border: 2px solid #34495e;")
        preview_container.setFixedSize(300, 450)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setAlignment(Qt.AlignCenter)
        
        self.preview_label = QLabel("No Skin Selected")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("color: #95a5a6;")
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_container, 0, Qt.AlignCenter)

        # Controls
        controls_layout = QHBoxLayout()
        
        upload_btn = QPushButton("Upload Skin (.png)")
        upload_btn.setMinimumHeight(40)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        upload_btn.clicked.connect(self.upload_skin)
        controls_layout.addWidget(upload_btn)
        
        clear_btn = QPushButton("Clear Skin")
        clear_btn.setMinimumHeight(40)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        clear_btn.clicked.connect(self.clear_skin)
        controls_layout.addWidget(clear_btn)
        
        layout.addLayout(controls_layout)
        layout.addStretch()
        
        self.refresh_preview()

    def upload_skin(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Skin", "", "Image Files (*.png)")
        if file_path:
            if state.set_skin(file_path):
                self.refresh_preview()

    def clear_skin(self):
        state.skin_path = ""
        state.save()
        self.refresh_preview()

    def get_preview_image(self, skin_path):
        try:
            img = QImage(skin_path)
            if img.isNull():
                return None
            
            # 64x64 or 64x32
            is_new_format = img.height() == 64
            
            # Helper to crop
            def crop(x, y, w, h):
                return img.copy(x, y, w, h)

            # Head (8,8) 8x8
            head = crop(8, 8, 8, 8)
            hat = crop(40, 8, 8, 8)
            
            # Body (20,20) 8x12
            body = crop(20, 20, 8, 12)
            
            # Right Arm (44,20) 4x12
            r_arm = crop(44, 20, 4, 12)
            
            # Left Arm
            if is_new_format:
                l_arm = crop(36, 52, 4, 12)
            else:
                l_arm = r_arm.mirrored(True, False)
                
            # Right Leg (4,20) 4x12
            r_leg = crop(4, 20, 4, 12)
            
            # Left Leg
            if is_new_format:
                l_leg = crop(20, 52, 4, 12)
            else:
                l_leg = r_leg.mirrored(True, False)

            # Composite dimensions: 16x32 (standard front view)
            # Head: 8x8 centered at x=4
            # Body: 8x12 centered at x=4
            # Arms: 4x12 at x=0 and x=12
            # Legs: 4x12 at x=4 and x=8
            composite = QImage(16, 32, QImage.Format_ARGB32)
            composite.fill(Qt.transparent)
            painter = QPainter(composite)
            
            # Draw Head & Hat
            painter.drawImage(4, 0, head)
            painter.drawImage(4, 0, hat)
            
            # Draw Torso
            painter.drawImage(4, 8, body)
            
            # Draw Arms
            painter.drawImage(0, 8, l_arm)
            painter.drawImage(12, 8, r_arm)
            
            # Draw Legs
            painter.drawImage(4, 20, l_leg)
            painter.drawImage(8, 20, r_leg)
            
            painter.end()
            return composite
        except Exception as e:
            print(f"Preview generation error: {e}")
            return None

    def refresh_preview(self):
        if state.skin_path and os.path.exists(state.skin_path):
            preview_img = self.get_preview_image(state.skin_path)
            if preview_img:
                pixmap = QPixmap.fromImage(preview_img)
                # Scale up to 160x320 for clear pixelated look
                scaled_pixmap = pixmap.scaled(160, 320, Qt.KeepAspectRatio, Qt.FastTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.setText("")
            else:
                self.preview_label.setPixmap(QPixmap())
                self.preview_label.setText("Error generating preview")
        else:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("No Skin Selected")

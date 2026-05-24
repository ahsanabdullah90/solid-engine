from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from app.core.hardware import HardwareManager
from app.database.db_session import SessionLocal
from app.database.models import Asset, AssetStatus

class StatCard(QFrame):
    def __init__(self, title, value, color="#2ecc71"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }}
            QLabel#title {{ color: #7f8c8d; font-size: 12px; font-weight: bold; }}
            QLabel#value {{ color: {color}; font-size: 24px; font-weight: bold; }}
        """)

        layout = QVBoxLayout(self)
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("title")
        self.value_lbl = QLabel(value)
        self.value_lbl.setObjectName("value")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)

class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(5000) # Every 5 seconds
        self.refresh_stats()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Business Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        # Hardware Stats Section
        hw_layout = QHBoxLayout()
        self.cpu_card = StatCard("CPU Cores", "0")
        self.ram_card = StatCard("RAM (GB)", "0")
        self.gpu_card = StatCard("VRAM (GB)", "0", "#3498db")
        hw_layout.addWidget(self.cpu_card)
        hw_layout.addWidget(self.ram_card)
        hw_layout.addWidget(self.gpu_card)
        layout.addLayout(hw_layout)

        # Asset Stats Section
        asset_layout = QGridLayout()
        self.total_card = StatCard("Total Assets", "0", "#34495e")
        self.pending_card = StatCard("Pending", "0", "#f1c40f")
        self.analyzed_card = StatCard("Analyzed", "0", "#27ae60")
        self.error_card = StatCard("Errors", "0", "#e74c3c")

        asset_layout.addWidget(self.total_card, 0, 0)
        asset_layout.addWidget(self.pending_card, 0, 1)
        asset_layout.addWidget(self.analyzed_card, 1, 0)
        asset_layout.addWidget(self.error_card, 1, 1)
        layout.addLayout(asset_layout)

        layout.addStretch()

    def refresh_stats(self):
        # Hardware
        caps = HardwareManager.get_capabilities()
        self.cpu_card.value_lbl.setText(str(caps['cpu_cores']))
        self.ram_card.value_lbl.setText(f"{caps['ram_gb']} GB")
        self.gpu_card.value_lbl.setText(f"{caps['vram_gb']} GB" if caps['has_nvidia_gpu'] else "N/A")

        # Database
        db = SessionLocal()
        try:
            total = db.query(Asset).count()
            pending = db.query(Asset).filter(Asset.status == AssetStatus.PENDING).count()
            analyzed = db.query(Asset).filter(Asset.status == AssetStatus.ANALYZED).count()
            error = db.query(Asset).filter(Asset.status == AssetStatus.ERROR).count()

            self.total_card.value_lbl.setText(str(total))
            self.pending_card.value_lbl.setText(str(pending))
            self.analyzed_card.value_lbl.setText(str(analyzed))
            self.error_card.value_lbl.setText(str(error))
        finally:
            db.close()

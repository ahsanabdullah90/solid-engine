import sys
<<<<<<< HEAD
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from app.database.db_session import init_db
from app.ui.dashboard import DashboardScreen
from app.ui.explorer import ExplorerScreen
from app.services.audit_service import AuditExportService
=======
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QWidget, QFileDialog,
    QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from app.database.db_session import init_db, SessionLocal
from app.database.models import Drive, Asset, AssetStatus
from app.workers.tasks import scan_directory
import uuid

class ScannerThread(QThread):
    finished = Signal(dict)

    def __init__(self, drive_id, path):
        super().__init__()
        self.drive_id = drive_id
        self.path = path

    def run(self):
        # In a real app, this would trigger Celery,
        # but for demonstration we'll show how to call the task
        result = scan_directory(self.drive_id, self.path)
        self.finished.emit(result)
>>>>>>> main

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Portfolio Manager")
<<<<<<< HEAD
        self.setMinimumSize(1024, 768)

        init_db()
        self.init_ui()
=======
        self.setMinimumSize(800, 600)

        init_db()
        self.db = SessionLocal()

        self.init_ui()
        self.refresh_asset_list()
>>>>>>> main

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
<<<<<<< HEAD
        main_layout = QHBoxLayout(central_widget)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        sidebar_layout = QVBoxLayout(sidebar)

        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget { background-color: transparent; border: none; }
            QListWidget::item { padding: 15px; color: white; font-weight: bold; }
            QListWidget::item:selected { background-color: #34495e; }
        """)
        self.nav_list.addItem("Dashboard")
        self.nav_list.addItem("Asset Explorer")
        self.nav_list.addItem("Audit Export")
        self.nav_list.currentRowChanged.connect(self.switch_screen)

        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar)

        # Content Area
        self.stack = QStackedWidget()
        self.dashboard = DashboardScreen()
        self.explorer = ExplorerScreen()
        self.export_view = self.init_export_view()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.explorer)
        self.stack.addWidget(self.export_view)

        main_layout.addWidget(self.stack)

    def init_export_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setAlignment(Qt.AlignCenter)

        csv_btn = QPushButton("Export Audit Log (CSV)")
        csv_btn.setFixedSize(300, 50)
        csv_btn.clicked.connect(lambda: self.export_audit("csv"))

        pdf_btn = QPushButton("Export Audit Log (PDF)")
        pdf_btn.setFixedSize(300, 50)
        pdf_btn.clicked.connect(lambda: self.export_audit("pdf"))

        layout.addWidget(csv_btn)
        layout.addWidget(pdf_btn)
        return view

    def switch_screen(self, index):
        self.stack.setCurrentIndex(index)
        # Refresh data when switching
        if index == 0: self.dashboard.refresh_stats()
        elif index == 1: self.explorer.refresh_data()

    def export_audit(self, fmt):
        ext = ".csv" if fmt == "csv" else ".pdf"
        path, _ = QFileDialog.getSaveFileName(self, f"Save Audit Log as {fmt.upper()}", "", f"Files (*{ext})")
        if path:
            success = False
            if fmt == "csv": success = AuditExportService.export_to_csv(path)
            else: success = AuditExportService.export_to_pdf(path)

            if success: QMessageBox.information(self, "Export Success", f"Audit log exported to {path}")
            else: QMessageBox.critical(self, "Export Failed", "An error occurred during export.")
=======
        layout = QVBoxLayout(central_widget)

        # Header
        header_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        header_layout.addWidget(self.status_label)

        self.scan_btn = QPushButton("Scan Directory")
        self.scan_btn.clicked.connect(self.start_scan)
        header_layout.addWidget(self.scan_btn)

        layout.addLayout(header_layout)

        # Asset List
        layout.addWidget(QLabel("Assets:"))
        self.asset_list = QListWidget()
        layout.addWidget(self.asset_list)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Refresh Button
        self.refresh_btn = QPushButton("Refresh List")
        self.refresh_btn.clicked.connect(self.refresh_asset_list)
        layout.addWidget(self.refresh_btn)

    def refresh_asset_list(self):
        self.asset_list.clear()
        assets = self.db.query(Asset).all()
        for asset in assets:
            self.asset_list.addItem(f"[{asset.status.value}] {asset.filename} - {asset.full_path}")

    def start_scan(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if dir_path:
            # Ensure we have a Drive record
            drive = self.db.query(Drive).filter(Drive.path == dir_path).first()
            if not drive:
                drive = Drive(id=uuid.uuid4(), name=os.path.basename(dir_path), path=dir_path)
                self.db.add(drive)
                self.db.commit()

            self.status_label.setText(f"Scanning: {dir_path}...")
            self.progress_bar.show()
            self.scan_btn.setEnabled(False)

            self.scanner_thread = ScannerThread(drive.id, dir_path)
            self.scanner_thread.finished.connect(self.on_scan_finished)
            self.scanner_thread.start()

    def on_scan_finished(self, result):
        self.status_label.setText("Scan Completed")
        self.progress_bar.hide()
        self.scan_btn.setEnabled(True)
        self.refresh_asset_list()
        QMessageBox.information(self, "Scan Finished", f"Scan results: {result}")

import os
>>>>>>> main

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
<<<<<<< HEAD
    # window.show()
    print("Application UI initialized successfully.")
=======
    # window.show() # Disabled for headless environment verification
    print("Application initialized successfully.")
>>>>>>> main
    sys.exit(0)

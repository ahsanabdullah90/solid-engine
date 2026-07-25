import sys
import os
import uuid
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from app.database.db_session import init_db, SessionLocal
from app.database.models import Drive, Asset, AssetStatus
from app.workers.tasks import scan_directory
from app.ui.dashboard import DashboardScreen
from app.ui.explorer import ExplorerScreen
from app.services.audit_service import AuditExportService

class ScannerThread(QThread):
    finished = Signal(dict)

    def __init__(self, drive_id, path):
        super().__init__()
        self.drive_id = drive_id
        self.path = path

    def run(self):
        result = scan_directory(self.drive_id, self.path)
        self.finished.emit(result)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Portfolio Manager")
        self.setMinimumSize(1024, 768)

        init_db()
        self.db = SessionLocal()

        self.init_ui()
        self.refresh_asset_list()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
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

        # Scan control panel at bottom of sidebar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #ecf0f1; font-size: 11px; padding: 5px;")
        self.status_label.setWordWrap(True)
        
        self.scan_btn = QPushButton("Scan Directory")
        self.scan_btn.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border: none; padding: 10px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #7f8c8d; }
        """)
        self.scan_btn.clicked.connect(self.start_scan)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.hide()
        
        sidebar_layout.addWidget(self.status_label)
        sidebar_layout.addWidget(self.progress_bar)
        sidebar_layout.addWidget(self.scan_btn)

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

    def refresh_asset_list(self):
        # Refresh data on active view components
        self.dashboard.refresh_stats()
        self.explorer.refresh_data()

    def start_scan(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if dir_path:
            # Ensure we have a Drive record in SQLite database
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.show() # Disabled for headless environment verification
    print("Application UI initialized successfully.")
    sys.exit(0)

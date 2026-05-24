import sys
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Portfolio Manager")
        self.setMinimumSize(1024, 768)

        init_db()
        self.init_ui()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.show()
    print("Application UI initialized successfully.")
    sys.exit(0)

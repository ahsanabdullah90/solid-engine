import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QHeaderView, QStyledItemDelegate,
    QStyleOptionViewItem, QLabel
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize
from PySide6.QtGui import QPixmap, QImageReader
from app.database.db_session import SessionLocal
from app.database.models import Asset

class AssetModel(QAbstractTableModel):
    def __init__(self, assets=None):
        super().__init__()
        self.assets = assets or []
        self.headers = ["Thumbnail", "Filename", "Size", "Status", "Path"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.assets)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        asset = self.assets[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 1: return asset.filename
            if col == 2: return f"{asset.size_bytes / 1024:.1f} KB"
            if col == 3: return asset.status.value
            if col == 4: return asset.full_path

        if role == Qt.UserRole: # For custom delegate
            return asset

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class AssetDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.placeholder = QPixmap(100, 100)
        self.placeholder.fill(Qt.lightGray)

    def paint(self, painter, option, index):
        if index.column() == 0:
            asset = index.data(Qt.UserRole)
            pixmap = self.placeholder
            if asset and asset.thumbnail_path and os.path.exists(asset.thumbnail_path):
                pixmap = QPixmap(asset.thumbnail_path)

            painter.drawPixmap(option.rect.x() + 5, option.rect.y() + 5,
                               pixmap.scaled(90, 90, Qt.KeepAspectRatio))
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        if index.column() == 0:
            return QSize(100, 100)
        return super().sizeHint(option, index)

class ExplorerScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableView()
        self.table.setItemDelegate(AssetDelegate())
        self.table.verticalHeader().setDefaultSectionSize(100)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 110)

        layout.addWidget(self.table)

    def refresh_data(self):
        db = SessionLocal()
        try:
            assets = db.query(Asset).all()
            self.model = AssetModel(assets)
            self.table.setModel(self.model)
        finally:
            db.close()

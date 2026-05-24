import os
import hashlib
import datetime
from pathlib import Path
from app.database.models import Drive, Asset, AssetStatus

class FileScanner:
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.jpg', '.jpeg', '.png'}

    def __init__(self, db_session):
        self.db = db_session

    def get_file_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (IOError, OSError):
            return None

    def scan_path(self, drive_id, root_path):
        drive = self.db.query(Drive).filter(Drive.id == drive_id).first()
        if not drive: return
        for path in Path(root_path).rglob('*'):
            if path.is_file() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self.process_file(drive, path)
        drive.last_scanned = datetime.datetime.utcnow()
        self.db.commit()

    def process_file(self, drive, file_path):
        full_path = str(file_path.absolute())
        file_stat = file_path.stat()
        asset = self.db.query(Asset).filter(Asset.full_path == full_path).first()
        mtime = datetime.datetime.fromtimestamp(file_stat.st_mtime)
        if not asset:
            file_hash = self.get_file_hash(full_path)
            asset = Asset(
                drive_id=drive.id, filename=file_path.name,
                extension=file_path.suffix.lower(), full_path=full_path,
                size_bytes=file_stat.st_size,
                created_at=datetime.datetime.fromtimestamp(file_stat.st_ctime),
                modified_at=mtime, hash_sha256=file_hash, status=AssetStatus.PENDING
            )
            self.db.add(asset)
        elif asset.modified_at < mtime:
            asset.size_bytes = file_stat.st_size
            asset.modified_at = mtime
            asset.hash_sha256 = self.get_file_hash(full_path)
            asset.status = AssetStatus.PENDING
        self.db.commit()

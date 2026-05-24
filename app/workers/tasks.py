import logging
from .celery_app import celery_app
from app.database.db_session import SessionLocal
from app.database.models import Asset, AssetStatus
from app.services.ai_pipeline import AIPipeline

logger = logging.getLogger(__name__)

@celery_app.task(name="app.workers.tasks.scan_directory")
def scan_directory(drive_id, path):
    from app.services.scanner import FileScanner
    db = SessionLocal()
    try:
        scanner = FileScanner(db)
        scanner.scan_path(drive_id, path)
        pending = db.query(Asset).filter(Asset.status == AssetStatus.PENDING).all()
        for asset in pending:
            analyze_asset.delay(str(asset.id))
    finally:
        db.close()
    return {"status": "success", "drive_id": str(drive_id)}

@celery_app.task(name="app.workers.tasks.analyze_asset")
def analyze_asset(asset_id, google_api_key=None):
    pipeline = AIPipeline(google_api_key=google_api_key)
    pipeline.process_asset(asset_id)
    return {"status": "completed", "asset_id": str(asset_id)}

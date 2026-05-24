import json
import logging
from app.database.db_session import SessionLocal
from app.database.models import Asset, AIMetadata, AssetStatus
from app.core.ai_providers import GoogleAIProvider, OllamaProvider
from app.core.hardware import HardwareManager
from app.core.config import config

logger = logging.getLogger(__name__)

class AIPipeline:
    def __init__(self, google_api_key=None):
        caps = HardwareManager.get_capabilities()
        if google_api_key or config.GOOGLE_API_KEY:
            self.provider = GoogleAIProvider(google_api_key or config.GOOGLE_API_KEY)
        else:
            self.provider = OllamaProvider(config.OLLAMA_MODEL)

    def process_asset(self, asset_id):
        db = SessionLocal()
        try:
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset: return
            asset.status = AssetStatus.PROCESSING
            db.commit()
            result = self._process_document(asset) if asset.extension in ['.pdf', '.docx'] else self._process_image(asset)
            if result:
                metadata = AIMetadata(
                    asset_id=asset.id, summary=result.get('summary'),
                    detected_topics=result.get('topics'), detected_entities=result.get('entities'),
                    image_description=result.get('description'), suggested_tags=result.get('tags')
                )
                db.add(metadata)
                asset.status = AssetStatus.ANALYZED
            db.commit()
        except Exception as e:
            logger.error(f"AI Pipeline error: {str(e)}")
            if asset: asset.status = AssetStatus.ERROR
            db.commit()
        finally:
            db.close()

    def _process_document(self, asset):
        extracted_text = f"Content of {asset.filename}..."
        response_text = self.provider.summarize_document(extracted_text)
        try:
            return json.loads(response_text)
        except:
            return {"summary": response_text, "topics": [], "entities": []}

    def _process_image(self, asset):
        description = self.provider.describe_image(asset.full_path)
        return {"description": description, "tags": ["AI-generated"]}

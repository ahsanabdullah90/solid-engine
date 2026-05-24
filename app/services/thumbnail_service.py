import os
from PIL import Image
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ThumbnailService:
    THUMBNAIL_SIZE = (128, 128)

    @staticmethod
    def get_thumbnail_dir(drive_path):
        thumb_dir = os.path.join(drive_path, ".thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        return thumb_dir

    @classmethod
    def generate_thumbnail(cls, asset):
        if asset.extension.lower() not in ['.jpg', '.jpeg', '.png', '.bmp']:
            return None

        try:
            drive_path = os.path.dirname(asset.full_path) # Simplified, should ideally get drive.path
            # Find the root drive path for the asset
            # For simplicity, we'll just use a subdirectory in the asset's current folder or a project global cache
            # Let's use a project-global cache for better management if drive path is complex
            cache_dir = os.path.abspath(".cache/thumbnails")
            os.makedirs(cache_dir, exist_ok=True)

            thumb_filename = f"{asset.id}.png"
            thumb_path = os.path.join(cache_dir, thumb_filename)

            if os.path.exists(thumb_path):
                return thumb_path

            with Image.open(asset.full_path) as img:
                img.thumbnail(cls.THUMBNAIL_SIZE)
                img.save(thumb_path, "PNG")

            return thumb_path
        except Exception as e:
            logger.error(f"Failed to generate thumbnail for {asset.full_path}: {e}")
            return None

from google.cloud import storage
from src.utils.logger import get_logger

logger = get_logger(__name__)

BUCKET_NAME = "hr-artifacts-unique-123"

class GCSService:
    def __init__(self):
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(BUCKET_NAME)
            self.online = True
        except Exception as e:
            logger.error(f"GCS Init Failed: {e}")
            self.online = False

    def upload_content(self, filename: str, content: str, content_type: str) -> str:
        if not self.online: return "GCS_OFFLINE"
        try:
            blob = self.bucket.blob(filename)
            blob.upload_from_string(content, content_type=content_type)
            return f"https://storage.cloud.google.com/{BUCKET_NAME}/{filename}"
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return "Upload Failed"
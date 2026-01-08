from src.models.employee import Employee
from src.services.gcs_service import GCSService
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

class DocumentAgent:
    def __init__(self):
        self.storage = GCSService()

    def run(self, employee: Employee) -> str:
        logger.info(f"Generating Contract for {employee.name}")
        
        # 1. Create Contract Text
        text = f"""
        OFFICIAL EMPLOYMENT OFFER
        Date: {datetime.now().strftime('%Y-%m-%d')}
        
        Candidate: {employee.name}
        Role: {employee.role}
        Start Date: {employee.start_date}
        Assets: {employee.assets}
        
        Welcome to the team!
        """
        
        # 2. Upload to GCS
        filename = f"contracts/{employee.name.replace(' ', '_')}_Contract.txt"
        link = self.storage.upload_content(filename, text, "text/plain")
        return link
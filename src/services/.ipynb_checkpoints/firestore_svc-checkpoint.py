from google.cloud import firestore
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FirestoreService:
    def __init__(self):
        self.db = firestore.Client()

    def save_payroll_record(self, employee_name: str, payroll_id: str, metadata: dict = None):
        data = {
            'name': employee_name,
            'payroll_id': payroll_id,
            'status': 'ACTIVE',
            'onboarded_at': firestore.SERVER_TIMESTAMP
        }
        
        if metadata:
            data.update(metadata)

        self.db.collection('payroll_records').document(employee_name).set(data)
        logger.info(f"Persisted record for {employee_name} in Firestore.")
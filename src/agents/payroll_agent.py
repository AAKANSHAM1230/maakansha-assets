import uuid
from src.models.employee import Employee
from src.services.firestore_svc import FirestoreService
from src.utils.retry_policy import with_retry
from src.utils.logger import get_logger

logger = get_logger(__name__)

class PayrollAgent:

    def __init__(self):
        self.db_svc = FirestoreService()

    @with_retry(max_retries=3, delay=1)
    def run(self, employee: Employee, doc_link: str = None, cal_link: str = None) -> str:
        logger.info(f"Registering {employee.name} in Payroll")

        payroll_id = f"PAY-{str(uuid.uuid4())[:8].upper()}"
        
        meta = {
            "role": employee.role,
            "start_date": employee.start_date,
            "email": employee.email,
            "doc_link": doc_link,      
            "cal_link": cal_link,       
            "assets": employee.assets
        }

        self.db_svc.save_payroll_record(employee.name, payroll_id, metadata=meta)

        return payroll_id
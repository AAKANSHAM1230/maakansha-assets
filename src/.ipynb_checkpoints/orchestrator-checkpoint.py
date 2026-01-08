import json
import vertexai
from vertexai.generative_models import GenerativeModel
from datetime import datetime

from src.models.employee import Employee
from src.agents.it_agent import ITProvisionAgent
from src.agents.pdf_document_agent import PDFDocumentAgent
#from src.agents.document_agent import DocumentAgent
from src.agents.scheduling_agent import SchedulingAgent
from src.agents.payroll_agent import PayrollAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self, project_id: str, location: str = "us-central1"):
        try:
            vertexai.init(project=project_id, location=location)
            self.model = GenerativeModel("gemini-2.5-pro")
        except:
            logger.error("Vertex Init Failed")

        self.it_agent = ITProvisionAgent()
        #self.doc_agent = DocumentAgent()
        self.doc_agent = PDFDocumentAgent() 
        self.sched_agent = SchedulingAgent()
        self.payroll_agent = PayrollAgent()

    def run(self, user_text: str):
        # 1. LLM Extraction
        prompt = f"""
        Extract to JSON: name, role, start_date (YYYY-MM-DD).
        Today: {datetime.now().strftime('%Y-%m-%d')}
        Text: "{user_text}"
        """
        res = self.model.generate_content(prompt)
        data = json.loads(res.text.replace("```json","").replace("```","").strip())
        
        employee = Employee(**data)
        
        employee.email = self.it_agent.generate_email(employee.name)
        asset_result = self.it_agent.run(employee)
        employee.assets = [asset_result]

        doc_link = self.doc_agent.run(employee)

        cal_link = self.sched_agent.run(employee)

        try: 
            payroll_id = self.payroll_agent.run(
                employee, 
                doc_link=doc_link, 
                cal_link=cal_link
            )
        except Exception as e: 
            logger.error(f"Payroll Failed: {e}")
            payroll_id = "Error"

        return {
            "status": "Success",
            "employee": employee.model_dump(),
            "contract": doc_link,
            "calendar": cal_link,
            "payroll": payroll_id
        }
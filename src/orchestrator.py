import json
import vertexai
from vertexai.generative_models import GenerativeModel
from datetime import datetime

# Models & Services
from src.models.employee import Employee
from src.utils.logger import get_logger

# Operational Agents
from src.agents.it_agent import ITProvisionAgent
from src.agents.pdf_document_agent import PDFDocumentAgent
from src.agents.scheduling_agent import SchedulingAgent
from src.agents.payroll_agent import PayrollAgent

# Analytical Agent (ADK)
from src.agents.analytics.agent import hr_analytics_agent

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self, project_id: str, location: str = "us-central1"):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-2.5-pro") 
        self.it_agent = ITProvisionAgent()
        self.doc_agent = PDFDocumentAgent() 
        self.sched_agent = SchedulingAgent()
        self.payroll_agent = PayrollAgent()
        self.analytics_agent = hr_analytics_agent

    def run(self, user_text: str):
        intent = self._route_intent(user_text)
        
        if intent == "ANALYTICS":
            return self._run_analytics(user_text)
        else:
            return self._run_onboarding(user_text)

    def _route_intent(self, user_text: str) -> str:
        prompt = f"""
        You are an Intent Router. Classify the User Input into one of two categories:
        
        1. ONBOARDING: The user is hiring someone, starting a process, or adding a new employee.
           Keywords: "hired", "start onboarding", "new employee", "starting on".
           
        2. ANALYTICS: The user is asking a question about data, salaries, counts, locations, or lists.
           Keywords: "how many", "average", "list", "who is", "what is".
           
        User Input: "{user_text}"
        
        Return ONLY the category name: ONBOARDING or ANALYTICS.
        """
        res = self.model.generate_content(prompt)
        intent = res.text.strip().upper()
        logger.info(f"Routed Intent: {intent}")
        return intent

    def _run_analytics(self, user_text: str):
        logger.info("Delegating to HR Analytics Agent")
        response_obj = self.analytics_agent.query(user_text)
        answer_text = str(response_obj) 
        
        return {
            "status": "Analytics Success",
            "type": "analytics",
            "summary": answer_text
        }

    def _run_onboarding(self, user_text: str):
        logger.info("Starting Onboarding Workflow...")

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
        payroll_id = self.payroll_agent.run(
            employee, 
            doc_link=doc_link, 
            cal_link=cal_link
        )

        return {
            "status": "Success",
            "type": "onboarding",
            "employee": employee.model_dump(),
            "contract": doc_link,
            "calendar": cal_link,
            "payroll": payroll_id,
            "summary": f"Onboarding started for {employee.name}"
        }
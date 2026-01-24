import os
import json
from datetime import datetime
from google.adk.agents import Agent

from src.models.employee import Employee
from src.agents.it_agent import ITProvisionAgent
from src.agents.pdf_document_agent import PDFDocumentAgent
from src.agents.scheduling_agent import SchedulingAgent
from src.agents.payroll_agent import PayrollAgent
from src.agents.analytics.agent import hr_analytics_agent

def onboard_new_hire(name: str, role: str, start_date: str) -> str:
    it_agent = ITProvisionAgent()
    doc_agent = PDFDocumentAgent()
    sched_agent = SchedulingAgent()
    payroll_agent = PayrollAgent()
    employee = Employee(name=name, role=role, start_date=start_date)
    
    employee.email = it_agent.generate_email(employee.name)
    asset_result = it_agent.run(employee)
    employee.assets = [asset_result]
    doc_link = doc_agent.run(employee)
    cal_link = sched_agent.run(employee)
    payroll_id = payroll_agent.run(employee, doc_link=doc_link, cal_link=cal_link)

    return json.dumps({
        "status": "Success",
        "employee_email": employee.email,
        "assets": employee.assets,
        "contract_pdf": doc_link,
        "calendar_event": cal_link,
        "payroll_id": payroll_id
    }, indent=2)

onboarding_agent = Agent(
    name="onboarding_specialist",
    model="gemini-2.5-pro",
    description="Handles all new hire onboarding: IT setup, contracts, calendar invites, and payroll.",
    instruction=f"""
    You are an expert HR Coordinator. When a user mentions hiring someone new, 
    use the 'onboard_new_hire' tool.
    
    Extract:
    - name: The full name of the new hire.
    - role: Their job title.
    - start_date: Calculate the date in YYYY-MM-DD format. Today is {datetime.now().strftime("%Y-%m-%d")}.
    
    After the tool runs, provide a friendly summary of the results.
    """,
    tools=[onboard_new_hire]
)

root_agent = Agent(
    name="hr_manager_assistant",
    model="gemini-2.5-pro",
    description="Main HR assistant that routes to Onboarding or Analytics specialists.",
    instruction="""
    You are the head HR Orchestrator for the company. 
    
    - If the user is HIRING or ONBOARDING someone new, delegate to 'onboarding_specialist'.
    - If the user is ASKING a question about employee DATA (salaries, headcount, locations, departments), 
      delegate to 'hr_analytics_agent'.
    
    Be professional, efficient, and provide clear summaries.
    """,
    sub_agents=[onboarding_agent, hr_analytics_agent]
)

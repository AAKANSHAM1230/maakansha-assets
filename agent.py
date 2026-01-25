import os
import json
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List
from google.adk.agents import Agent
from google.cloud import storage, firestore
from google.auth import default
from googleapiclient.discovery import build
from fpdf import FPDF
#from google.adk.applications import App
#from google.adk.apps import App      
from dateutil.relativedelta import relativedelta, MO

# ============ INLINE MODELS ============
class Employee(BaseModel):
    name: str
    role: str
    start_date: str
    email: Optional[str] = None
    assets: List[str] = []

# ============ INLINE SERVICES ============
BUCKET_NAME = os.getenv("BUCKET_NAME", "hr-artifacts-unique-123")
CALENDAR_ID = os.getenv("CALENDAR_ID", "c_067c77de5ae7a172f98e9a8372feb0e865ef276b32686f443d1c3541293b3959@group.calendar.google.com")

def generate_email(name: str) -> str:
    return f"{name.lower().replace(' ', '.')}@company.com"

def provision_assets(role: str) -> str:
    role_lower = role.lower()
    if any(k in role_lower for k in ["engineer", "developer", "swe", "sce", "ai"]):
        return "MacBook Pro 16-inch (M3 Max)"
    return "Chromebook Enterprise"

def generate_pdf(employee: Employee) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "EMPLOYMENT AGREEMENT", 0, 1, "C")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1)
    pdf.cell(0, 10, f"Candidate: {employee.name}", 0, 1)
    pdf.cell(0, 10, f"Role: {employee.role}", 0, 1)
    pdf.cell(0, 10, f"Start Date: {employee.start_date}", 0, 1)
    pdf.ln(10)
    assets_str = ", ".join(employee.assets)
    pdf.multi_cell(0, 8, f"Assets Assigned: {assets_str}\n\nWelcome to the team!")
    
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    filename = f"candidates/{employee.name.replace(' ', '_').lower()}/legal/offer_letter.pdf"
    blob = bucket.blob(filename)
    blob.upload_from_string(bytes(pdf.output()), content_type="application/pdf")
    return f"https://storage.cloud.google.com/{BUCKET_NAME}/{filename}"

def schedule_orientation(employee: Employee) -> str:
    try:
        creds, _ = default()
        service = build("calendar", "v3", credentials=creds)
        
        # --- ROBUST DATE PARSING ---
        try:
            start_dt = datetime.strptime(employee.start_date, "%Y-%m-%d").replace(hour=9)
        except:
            # If the LLM sent "Monday", calculate next Monday
            start_dt = (datetime.now() + relativedelta(weekday=MO(1))).replace(hour=9, minute=0, second=0)
        
        end_dt = start_dt + timedelta(hours=1)
        
        event = {
            "summary": f"Onboarding: {employee.name}",
            "description": f"Role: {employee.role}. Email: {employee.email}",
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        }
        result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return result.get("htmlLink", "Event Scheduled")
    except Exception as e:
        return f"Calendar skipped: {e}"

def register_payroll(employee: Employee, doc_link: str, cal_link: str) -> str:
    import uuid
    payroll_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    try:
        db = firestore.Client()
        db.collection("payroll_records").document(employee.name).set({
            "name": employee.name,
            "email": employee.email,
            "role": employee.role,
            "payroll_id": payroll_id,
            "doc_link": doc_link,
            "cal_link": cal_link,
            "assets": employee.assets,
            "status": "ACTIVE"
        })
    except:
        pass
    return payroll_id

# ============ ONBOARDING TOOL ============
def onboard_new_hire(name: str, role: str, start_date: str) -> str:
    """
    Starts the onboarding process for a new employee. 
    Args:
        name: Full name.
        role: Job title.
        start_date: Start date (YYYY-MM-DD).
    """
    employee = Employee(name=name, role=role, start_date=start_date)
    employee.email = generate_email(name)
    employee.assets = [provision_assets(role)]
    
    doc_link = generate_pdf(employee)
    cal_link = schedule_orientation(employee)
    payroll_id = register_payroll(employee, doc_link, cal_link)
    
    return json.dumps({
        "status": "Success",
        "contract": doc_link,
        "calendar": cal_link,
        "payroll_id": payroll_id
    })

# ============ ANALYTICS AGENT (SUB-AGENT) ============
from src.agents.analytics.agent import hr_analytics_agent

# ============ ROOT AGENT ============
onboarding_agent = Agent(
    name="onboarding_specialist",
    model="gemini-2.5-pro",
    description="I execute the physical onboarding steps (PDF, IT, Calendar).",
    instruction=f"Today is {datetime.now().strftime('%Y-%m-%d')}. Extract the name, role, and YYYY-MM-DD date. Use the onboard_new_hire tool.",
    tools=[onboard_new_hire]
)

root_agent = Agent(
    name="hr_manager_assistant",
    model="gemini-2.5-pro",
    description="Main HR Assistant. Routes to Onboarding or Analytics.",
    instruction="Route hiring/onboarding to onboarding_specialist. Route data/salary questions to hr_analytics_agent.",
    sub_agents=[onboarding_agent, hr_analytics_agent]
)

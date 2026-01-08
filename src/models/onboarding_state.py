from pydantic import BaseModel
from typing import Optional

class OnboardingState(BaseModel):
    employee_name: str
    docs_generated: bool = False
    it_provisioned: bool = False
    calendar_scheduled: bool = False
    payroll_registered: bool = False
    last_updated: Optional[str] = None
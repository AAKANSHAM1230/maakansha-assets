from pydantic import BaseModel
from typing import Optional, List

class Employee(BaseModel):
    name: str
    role: str
    start_date: str  # YYYY-MM-DD (String)
    email: Optional[str] = None
    assets: List[str] = []
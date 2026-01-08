from datetime import datetime, timedelta
from src.models.employee import Employee
from src.services.google_workspace import GoogleWorkspaceService
from src.utils.logger import get_logger

logger = get_logger(__name__)

CALENDAR_ID = "c_067c77de5ae7a172f98e9a8372feb0e865ef276b32686f443d1c3541293b3959@group.calendar.google.com"

class SchedulingAgent:
    def __init__(self):
        self.svc = GoogleWorkspaceService()

    def run(self, employee: Employee) -> str:
        logger.info(f"Scheduling for {employee.name}")

        try:
            dt = datetime.strptime(employee.start_date, "%Y-%m-%d")
            start = dt.replace(hour=9, minute=0)
            end = start + timedelta(hours=1)
        except:
            return "Invalid date"

        event = {
            'summary': f"Orientation: {employee.name}",
            'description': f"Onboarding for {employee.name}. Email: {employee.email}", 
            'start': {'dateTime': start.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end.isoformat(), 'timeZone': 'UTC'},
        }

        try:
            res = self.svc.calendar_service.events().insert(
                calendarId=CALENDAR_ID, 
                body=event
            ).execute()
            return res.get('htmlLink')
        except Exception as e:
            logger.error(f"Scheduling Failed: {e}")
            return f"Error: {e}"
        
        
        
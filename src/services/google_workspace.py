import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils.logger import get_logger

logger = get_logger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/calendar'
]

class GoogleWorkspaceService:
    def __init__(self):
        self.creds, _ = google.auth.default()

        if hasattr(self.creds, 'with_scopes'):
            self.creds = self.creds.with_scopes(SCOPES)

        try:
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)
            self.calendar_service = build('calendar', 'v3', credentials=self.creds)
            self.online = True
        except Exception as e:
            logger.warning(f"Google API Services failed to infit: {e}. Entering OFFLINE MOCK MODE.")
            self.online = False

    def copy_file(self, file_id: str, new_title: str) -> str:
        if not self.online:
            return f"mock_doc_id_for_{new_title.replace(' ', '_')}"

        try:
            body = {'name': new_title}
            drive_response = self.drive_service.files().copy(
                fileId=file_id, body=body
            ).execute()
            new_id = drive_response.get('id')
            logger.info(f"Created copy. New ID: {new_id}")
            return new_id
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning("PERMISSION DENIED (Scope Error). Returning MOCK ID.")
                return f"mock_doc_id_for_{new_title.replace(' ', '_')}"
            raise e

    def replace_text(self, doc_id: str, replacements: dict):
        if "mock_doc_id" in doc_id or not self.online:
            logger.info(f"[MOCK] Replaced text in doc {doc_id} with {replacements}")
            return

        try:
            requests = []
            for key, value in replacements.items():
                requests.append({
                    'replaceAllText': {
                        'containsText': {'text': key, 'matchCase': True},
                        'replaceText': str(value)
                    }
                })
            self.docs_service.documents().batchUpdate(
                documentId=doc_id, body={'requests': requests}
            ).execute()
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning("[MOCK] Permission denied during text replacement. Skipping.")
                return
            raise e

    def share_file_publicly(self, file_id: str):
        if "mock_doc_id" in file_id or not self.online:
            logger.info(f"[MOCK] Shared file {file_id} publicly.")
            return

        try:
            self.drive_service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
        except HttpError as e:
            logger.warning(f"Could not share file: {e}")

    def get_link(self, file_id: str) -> str:
        if "mock_doc_id" in file_id or not self.online:
            return f"https://docs.google.com/document/d/{file_id}/mock_view"

        try:
            file = self.drive_service.files().get(
                fileId=file_id, fields='webViewLink'
            ).execute()
            return file.get('webViewLink')
        except HttpError as e:
            if e.resp.status == 403:
                return f"https://docs.google.com/document/d/{file_id}/mock_view_permission_error"
            raise e

    def create_calendar_event(self, email: str, summary: str, start_time: str, end_time: str) -> str:
        if not self.online:
            return "https://calendar.google.com/mock_event"

        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
            'attendees': [{'email': email}],
        }

        try:
            created_event = self.calendar_service.events().insert(
                calendarId='primary', body=event
            ).execute()
            return created_event.get('htmlLink')
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning("Calendar Permission Denied. Returning Mock.")
                return "https://calendar.google.com/mock_permission_error"
            
            logger.error(f"Calendar API Error: {e}")
            raise e
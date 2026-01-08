from fpdf import FPDF
from datetime import datetime
from src.models.employee import Employee
from src.services.advanced_gcs_service import AdvancedGCSService
from src.utils.logger import get_logger

logger = get_logger(__name__)

class PDFDocumentAgent:
    def __init__(self):
        self.storage = AdvancedGCSService()

    def run(self, employee: Employee) -> str:
        logger.info(f"Generating PDF Contract for {employee.name}")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, "OFFICIAL EMPLOYMENT AGREEMENT", 0, 1, 'C')
        pdf.ln(10) 
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1)
        pdf.cell(0, 10, f"Candidate: {employee.name}", 0, 1)
        pdf.cell(0, 10, f"Role: {employee.role}", 0, 1)
        pdf.ln(10)

        pdf.set_font("Helvetica", size=11)
        body = (
            f"Dear {employee.name},\n\n"
            f"We are pleased to offer you the position of {employee.role}. "
            f"Your start date is scheduled for {employee.start_date}.\n\n"
            "This package includes:\n"
            f"- IT Assets: {', '.join(employee.assets)}\n"
            "- Full Health & Dental\n"
            "- Unlimited PTO\n\n"
            "Welcome to the team!"
        )
        pdf.multi_cell(0, 8, body)
        pdf.ln(20)
        pdf.cell(0, 10, "__________________________", 0, 1)
        pdf.cell(0, 10, f"Signed, {employee.name}", 0, 1)

        pdf_bytes = pdf.output() #fpdf2.output() = bytearr string
        clean_name = employee.name.replace(' ', '_').lower()
        filename = f"candidates/{clean_name}/legal/offer_letter.pdf"
        
        link = self.storage.upload_bytes(filename, bytes(pdf_bytes), "application/pdf")
        return link
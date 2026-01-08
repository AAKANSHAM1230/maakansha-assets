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

        # 1. Initialize PDF
        pdf = FPDF()
        pdf.add_page()
        
        # 2. Add Professional Header
        pdf.set_font("Helvetica", "B", 20)
        # Cell(width, height, text, border, newline, align)
        pdf.cell(0, 10, "OFFICIAL EMPLOYMENT AGREEMENT", 0, 1, 'C')
        pdf.ln(10) # Add vertical space
        
        # 3. Add Details
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1)
        pdf.cell(0, 10, f"Candidate: {employee.name}", 0, 1)
        pdf.cell(0, 10, f"Role: {employee.role}", 0, 1)
        pdf.ln(10)

        # 4. Add Body
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

        # 5. Add Signature Area
        pdf.cell(0, 10, "__________________________", 0, 1)
        pdf.cell(0, 10, f"Signed, {employee.name}", 0, 1)

        # 6. Generate Bytes
        # fpdf2 .output() returns a bytearray string
        pdf_bytes = pdf.output()

        # 7. Upload to Structured Folder
        # e.g., candidates/dwight_schrute/legal/offer_letter.pdf
        clean_name = employee.name.replace(' ', '_').lower()
        filename = f"candidates/{clean_name}/legal/offer_letter.pdf"
        
        link = self.storage.upload_bytes(filename, bytes(pdf_bytes), "application/pdf")
        return link
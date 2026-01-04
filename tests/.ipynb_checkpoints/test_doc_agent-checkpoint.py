import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.employee import Employee
from src.agents.document_agent import DocumentAgent

def test_doc_generation():
    print("=== Testing Document Agent ===")
    
    # 1. Create dummy data
    emp = Employee(
        name="Test User 001", 
        role="Senior AI SCE", 
        start_date=datetime.now()
    )

    # 2. Run Agent
    try:
        agent = DocumentAgent()
        link = agent.run(emp)
        
        print(f"✅ SUCCESS!")
        print(f"Generated Doc: {link}")
        print("Click the link above to verify the {{placeholders}} were replaced.")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test_doc_generation()
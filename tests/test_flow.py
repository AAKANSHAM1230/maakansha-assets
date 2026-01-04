import sys
import os
from datetime import datetime

# Setup path to find source code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Auto-detect Project ID
project_id = os.popen("gcloud config get-value project").read().strip()

from src.orchestrator import Orchestrator

def test_full_flow():
    print(f"=== Testing Full Agent Flow (Project: {project_id}) ===")
    
    # 1. Init
    orchestrator = Orchestrator(project_id=project_id)

    # 2. Input
    user_text = "We hired Jane Doe as a Senior AI SCE starting next Monday. Please onboard her."

    # 3. Run
    try:
        response = orchestrator.run(user_text)
        print("\n=== AGENT RESPONSE ===")
        print(response)
        print("======================")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_full_flow()
import vertexai
from vertexai import agent_engines

# Initialize
vertexai.init(project="maakansha-sandbox", location="us-central1")

# Get the deployed agent
ae = agent_engines.get("2719590334257430528")

print("--- Testing Onboarding ---")
try:
    print(ae.query(input="We hired Jim Halpert as Sales Rep starting Feb 1st 2026."))
except Exception as e:
    print(f"Onboarding Error: {e}")

print("\n--- Testing Analytics ---")
try:
    print(ae.query(input="How many employees are in the system?"))
except Exception as e:
    print(f"Analytics Error: {e}")

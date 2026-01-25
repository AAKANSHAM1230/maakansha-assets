import vertexai
from vertexai import agent_engines

# Initialize
vertexai.init(project="maakansha-sandbox", location="us-central1")

# Get the deployed agent
ae = agent_engines.get("2719590334257430528")

print("--- Testing Remote Agent (Onboarding) ---")
try:
    # Using .run() as per latest SDK
    response = ae.run(input="We hired Jim Halpert as Sales Rep starting Feb 1st 2026.")
    print(f"RESPONSE: {response}")
except Exception as e:
    print(f"CLOUD ERROR: {e}")

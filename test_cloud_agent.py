import vertexai
from vertexai import agent_engines

vertexai.init(project="maakansha-sandbox", location="us-central1")
ae = agent_engines.get("2719590334257430528")

print("--- Calling Remote Agent ---")
try:
    # Using the method we found in detect_methods.py
    responses = ae.stream_query(input="We hired Jim Halpert as Sales Rep starting Feb 1st 2026.")
    for response in responses:
        print(response)
except Exception as e:
    print(f"CLOUD EXECUTION ERROR: {e}")

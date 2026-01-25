import vertexai
from vertexai import agent_engines

vertexai.init(project="maakansha-sandbox", location="us-central1")
ae = agent_engines.get("3975531680340377600")

try:
    responses = ae.stream_query(
        message="How many employees do we currently have in new york?",
        user_id="test-admin"
    )
    for response in responses:
        print(response)
except Exception as e:
    print(f"ERROR: {e}")

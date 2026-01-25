import vertexai
from vertexai import agent_engines

vertexai.init(project="maakansha-sandbox", location="us-central1")

ae = agent_engines.get("3975531680340377600")

try:
    responses = ae.stream_query(
        message="We hired Stanley Hudson as a Sales Rep starting next Monday. Please onboard him.",
        user_id="test-user-001"
    )
    for response in responses:
        print(response)
except Exception as e:
    print(f"ERROR: {e}")

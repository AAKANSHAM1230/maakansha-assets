import vertexai
from vertexai import agent_engines

vertexai.init(project="maakansha-sandbox", location="us-central1")
ae = agent_engines.get("2719590334257430528")

print(f"Object Class: {type(ae)}")
print("\n--- Methods available on this agent ---")
for method in dir(ae):
    if not method.startswith("_"):
        print(f" - {method}")

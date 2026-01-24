import os
import google.auth
from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from . import prompt

AGENT_NAME = "hr_analytics_agent"
GEMINI_MODEL = "gemini-2.5-pro"
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "maakansha-sandbox") 

tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(credentials=credentials)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, 
    bigquery_tool_config=tool_config
)

hr_analytics_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description="An HR Analyst agent capable of querying an employee database for insights.",
    instruction=prompt.HR_ANALYST_PROMPT,
    tools=[bigquery_toolset],
)

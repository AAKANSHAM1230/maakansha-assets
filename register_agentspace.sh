#!/bin/bash

# Project detail
export GCP_PROJECT=394732309499
export LOCATION_RE="us-central1"
export LOCATION_APP="global"

# Reasoning Engine ID from your successful deployment
export ADK_DEPLOYMENT_ID=2719590334257430528

# The App ID for your Agent Space / Discovery Engine app
# You can find this in the Console under Search & Conversation
export APP_ID=hr-agent_1769321165055

# Metadata
export DISPLAY_NAME='HR Onboarding Agent'
export DESCRIPTION='Autonomous onboarding and HR analytics agent'
export TOOL_DESCRIPTION='Handles hiring workflows and BQ analytics'


curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: ${GCP_PROJECT}" \
"https://discoveryengine.googleapis.com/v1alpha/projects/${GCP_PROJECT}/locations/${LOCATION_APP}/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents" \
-d '{
  "displayName": "'"${DISPLAY_NAME}"'",
  "description": "'"${DESCRIPTION}"'",
  "adk_agent_definition": {
    "tool_settings": {
      "tool_description": "'"${TOOL_DESCRIPTION}"'"
    },
    "provisioned_reasoning_engine": {
      "reasoning_engine": "projects/'"${GCP_PROJECT}"'/locations/'"${LOCATION_RE}"'/reasoningEngines/'"${ADK_DEPLOYMENT_ID}"'"
    }
  }
}'

curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${GCP_PROJECT}"\
  "https://discoveryengine.googleapis.com/v1alpha/projects/${GCP_PROJECT}/locations/${LOCATION_APP}/collections/default_collection/engines/${APP_ID}"




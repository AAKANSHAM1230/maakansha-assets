#!/bin/bash
set -e

AGENT_NAME="maakansha_assets"

if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  set -a
  source .env
  set +a
fi

if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT environment variable is not set."
    exit 1
fi

if [ -z "$GOOGLE_CLOUD_LOCATION" ]; then
    echo "Error: GOOGLE_CLOUD_LOCATION environment variable is not set."
    exit 1
fi

echo "--- Configuration ---"
echo "Agent Name: $AGENT_NAME"
echo "Project: $GOOGLE_CLOUD_PROJECT"
echo "Location: $GOOGLE_CLOUD_LOCATION"
echo "---------------------"

echo "\n--- Building wheel file ---"
poetry build --format=wheel --output=dist

echo "\n--- Deploying agent ---"
poetry run python deployment/deploy.py --create --agent_name=$AGENT_NAME

echo "\n--- Deployment script finished ---"

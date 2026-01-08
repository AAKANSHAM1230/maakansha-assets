import os
from flask import Flask, request, jsonify
from src.orchestrator import Orchestrator
from src.utils.logger import get_logger

logger = get_logger("Main")
app = Flask(__name__)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "maakansha-sandbox")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

try:
    orchestrator = Orchestrator(project_id=PROJECT_ID, location=LOCATION)
except Exception as e:
    logger.error(f"Orchestrator failed to init: {e}")
    orchestrator = None

@app.route("/", methods=["POST"])
def onboard():
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized. Check logs."}), 500

    try:
        data = request.get_json(silent=True)
        if data and 'text' in data:
            user_input = data['text']
        else:
            user_input = request.get_data(as_text=True)

        if not user_input:
            return jsonify({"error": "Empty request"}), 400

        logger.info(f"Received request: {user_input[:50]}...")
        result = orchestrator.run(user_input)
        return jsonify({"status": "success", "summary": result}), 200

    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
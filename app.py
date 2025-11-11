# app.py
import os
import sys
import logging
from flask import Flask, request, jsonify
import requests

# Import the QA engine (make sure qa_engine.py is in same folder)
from qa_engine import answer_question_from_messages

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Default messages API URL (can be overridden with env var)
MESSAGES_API_URL = os.environ.get(
    "MESSAGES_API_URL",
    "https://november7-730026606190.europe-west1.run.app/messages"
)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/ask", methods=["GET"])
def ask():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"answer": "Please provide a question in the 'q' query parameter."}), 400

    # Fetch messages from the public API and normalize into a list
    try:
        logging.info("Fetching messages from: %s", MESSAGES_API_URL)
        resp = requests.get(MESSAGES_API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # handle various shapes:
        if isinstance(data, dict):
            # prefer common keys
            if "items" in data and isinstance(data["items"], list):
                messages = data["items"]
            elif "messages" in data and isinstance(data["messages"], list):
                messages = data["messages"]
            else:
                # try to find the first list value
                messages = []
                for v in data.values():
                    if isinstance(v, list):
                        messages = v
                        break
        elif isinstance(data, list):
            messages = data
        else:
            return jsonify({"answer": "Unexpected response structure from messages API."}), 502

        logging.info("Fetched %d messages", len(messages))

    except Exception as e:
        logging.exception("Failed to fetch messages")
        return jsonify({"answer": f"Failed to fetch messages from data source: {e}"}), 502

    # Call the QA engine
    try:
        answer = answer_question_from_messages(q, messages)
    except Exception as e:
        logging.exception("QA engine error")
        return jsonify({"answer": f"Internal error while answering question: {e}"}), 500

    return jsonify({"answer": answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Run flask app
    app.run(host="0.0.0.0", port=port)

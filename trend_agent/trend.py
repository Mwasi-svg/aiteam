import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# Logging setup
logging.basicConfig(level=logging.INFO)

# Flask app initialization
app = Flask(__name__)

# System instruction for the Trend-Agent
SYSTEM_INSTRUCTION = """
Role: Trend-Agent

Purpose:
Track real-time trends, predict virality, and spot emerging market shifts.

Core Functions:
- Identify current or upcoming trends in tech, culture, or media.
- Predict potential virality or saturation points.
- Recommend trend-based opportunities.
"""

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return f"Error: {e}"

# Root route for basic info
@app.route('/')
def home():
    return "Welcome to the Trend-Agent API. Use POST at /run to scan for trends."

# API endpoint to run tasks
@app.route('/run', methods=['POST'])
def run():
    task = request.json.get("task", "")
    if not task:
        return jsonify({"error": "No task provided"}), 400

    logging.info(f"Trend-Agent task: {task}")
    prompt = (
        f"{SYSTEM_INSTRUCTION.strip()}\n\n"
        f"Task: {task}\n\n"
        f"Scan for trends and provide forecasts or observations."
    )
    result = ask_gemini(prompt)
    return jsonify({"result": result})

# Run the Flask app
if __name__ == "__main__":
    logging.info("Trend-Agent is up and running...")
    port = int(os.environ.get("PORT", 5005))  # Use environment port or fallback to 5005
    app.run(host='0.0.0.0', port=port)

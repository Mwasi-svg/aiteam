import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from flask_cors import CORS  # Import CORS for cross-origin requests
import time

load_dotenv()
genai.configure(api_key="AIzaSyC_nRKjOy12gBNdRjGS6UeXm3xr81kGIPw")
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Enable CORS for the frontend URL
CORS(app, origins="https://9000-idx-admin-dashboard-1745483841791.cluster-oayqgyglpfgseqclbygurw4xd4.cloudworkstations.dev")  # Frontend URL


SYSTEM_INSTRUCTION = """
Role: Dev-Agent

Purpose:
Assist with technical tasks such as code creation, debugging, optimization, and testing.

Core Functions:
- Write clean, efficient, and well-documented code.
- Debug and improve provided code.
- Suggest appropriate libraries, tools, or technologies.
- Explain code when needed.
"""

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return f"Error: {e}"

@app.route('/run', methods=['POST'])
def run():
    task = request.json.get("task", "")
    if not task:
        return jsonify({"error": "No task provided"}), 400

    logging.info(f"Dev-Agent task: {task}")
    prompt = (
        f"{SYSTEM_INSTRUCTION.strip()}\n\n"
        f"Task: {task}\n\n"
        f"Provide a technical solution or explanation."
    )
    result = ask_gemini(prompt)
    return jsonify({"result": result})

@app.route("/")
def index():
    return "Dev-Agent is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))  # Use the port specified by Railway
    logging.info(f"Starting the app on port {port}")
    time.sleep(3)  # Wait for 3 seconds to ensure Railway is ready
    app.run(host="0.0.0.0", port=port)
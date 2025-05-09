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
Role: Design-Agent

Purpose:
Generate creative and user-friendly design ideas, layouts, and mockups.

Core Functions:
- Suggest UI/UX layouts and flows.
- Provide wireframe or component-level design recommendations.
- Adapt style based on audience, brand, or platform.
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

    logging.info(f"Design-Agent task: {task}")
    prompt = (
        f"{SYSTEM_INSTRUCTION.strip()}\n\n"
        f"Task: {task}\n\n"
        f"Provide design insights or layout ideas."
    )
    result = ask_gemini(prompt)
    return jsonify({"result": result})

@app.route("/")
def index():
    return "Design-Agent is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5007))  # Use the port specified by Railway
    logging.info(f"Starting the app on port {port}")
    time.sleep(3)  # Wait for 3 seconds to ensure Railway is ready
    app.run(host="0.0.0.0", port=port)
import os
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import time

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["https://turiagent.web.app"])
logging.basicConfig(level=logging.INFO)

# Agent endpoint map (from Railway ENV VARs)
AGENT_ENDPOINTS = {
    "Market Research": os.getenv("MARKET_AGENT_URL"),
    "Dev": os.getenv("DEV_AGENT_URL"),
    "Design": os.getenv("DESIGN_AGENT_URL"),
    "Analysis": os.getenv("ANALYSIS_AGENT_URL"),
    "Trend": os.getenv("TREND_AGENT_URL"),
    "Content Creation": os.getenv("CONTENT_AGENT_URL"),
}

PM_AGENT_URL = os.getenv("PM_AGENT_URL")

def call_agent(url, task):
    try:
        logging.info(f"Sending task to {url}")
        response = requests.post(url, json={"task": task})
        return response.json().get("result", "No result returned.")
    except Exception as e:
        return f"Error calling agent: {e}"

@app.route('/execute', methods=['POST'])
def execute():
    user_goal = request.json.get("goal", "")
    if not user_goal:
        return jsonify({"error": "No goal provided"}), 400

    logging.info(f"User Goal: {user_goal}")
    
    pm_response = call_agent(PM_AGENT_URL, f"Deconstruct this goal: {user_goal}")
    logging.info(f"PM-Agent response:\n{pm_response}")

    results = {}
    for line in pm_response.split("\n"):
        taskfound = False
        for agent_name, url in AGENT_ENDPOINTS.items():
            if agent_name.lower() in line.lower():
                subtask = line.split("→")[-1].strip() if "→" in line else line.strip()
                logging.info(f"Routing to {agent_name} → Task: {subtask}")
                results[agent_name] = call_agent(url, subtask)
                taskfound = True 
        if not taskfound:
            logging.warning(f"No agent found for task: {line.strip()}")
            results["Unassigned"] = line.strip()

    return jsonify({
        "goal": user_goal,
        "plan": pm_response,
        "agent_responses": results
    })

@app.route("/")
def index():
    return "Brain Agent is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use the port specified by Railway
    logging.info(f"Starting the app on port {port}")
    time.sleep(3)  # Wait for 3 seconds to ensure Railway is ready
    app.run(host="0.0.0.0", port=port)

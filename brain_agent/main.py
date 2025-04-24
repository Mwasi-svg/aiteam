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
    "Market Research": os.getenv("https://market-agent-f9q2.onrender.com"),
    "Dev": os.getenv("https://dev-agent-ai-agents.up.railway.app/"),
    "Design": os.getenv("https://design-agent-ai-agents.up.railway.app/"),
    "Analysis": os.getenv("https://analysis-agent-ai-agents.up.railway.app/"),
    "Trend": os.getenv("https://trend-agent.onrender.com"),
    "Content Creation": os.getenv("https://content-agent-ai-agents.up.railway.app/"),
}

PM_AGENT_URL = os.getenv("https://project-manager-agent.onrender.com")

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

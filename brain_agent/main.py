import os
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import time

load_dotenv()
app = Flask(__name__)

# Enable CORS for the frontend URL
CORS(app, origins="https://9000-idx-admin-dashboard-1745483841791.cluster-oayqgyglpfgseqclbygurw4xd4.cloudworkstations.dev")

logging.basicConfig(level=logging.INFO)

# Agent endpoint map (from Railway ENV VARs)
AGENT_ENDPOINTS = {
    "Market Research": "https://market-agent-f9q2.onrender.com",
    "Dev": "https://dev-agent-ai-agents.up.railway.app/",
    "Design": "https://design-agent-ai-agents.up.railway.app/",
    "Analysis": "https://analysis-agent-ai-agents.up.railway.app/",
    "Trend": "https://trend-agent.onrender.com",
    "Content Creation": "https://content-agent-ai-agents.up.railway.app/",
}

PM_AGENT_URL = "https://project-manager-agent.onrender.com/run"

def call_agent(url, task):
    try:
        logging.info(f"Sending task to {url} with task: {task}")
        response = requests.post(url, json={"task": task}, timeout=120)

        if response.status_code == 200:
            logging.info(f"Received response from {url}: {response.json()}")
            return {
                "result": response.json().get("result", "No result returned."),
                "status": "success"
            }
        else:
            logging.error(f"Error from {url}: {response.status_code} - {response.text}")
            return {
                "result": f"Error from {url}: {response.status_code} - {response.text}",
                "status": "error"
            }

    except requests.exceptions.Timeout:
        logging.error(f"Timeout while calling {url} for task: {task}")
        return {
            "result": "Timeout error: The agent took too long to respond.",
            "status": "timeout"
        }

    except Exception as e:
        logging.error(f"Error calling agent at {url} for task: {task}: {e}")
        return {
            "result": f"Error calling agent: {e}",
            "status": "error"
        }

@app.route('/execute', methods=['POST'])
def execute():
    user_goal = request.json.get("goal", "")
    if not user_goal:
        return jsonify({"error": "No goal provided"}), 400

    logging.info(f"User Goal: {user_goal}")

    pm_response = call_agent(PM_AGENT_URL, f"Deconstruct this goal: {user_goal}")
    logging.info(f"PM-Agent response:\n{pm_response['result']}")

    results = {}

    for line in pm_response["result"].split("\n"):
        taskfound = False
        logging.info(f"Processing line: {line.strip()}")
        for agent_name, url in AGENT_ENDPOINTS.items():
            if agent_name.lower() in line.lower():
                subtask = line.split("→")[-1].strip() if "→" in line else line.strip()
                logging.info(f"Routing to {agent_name} → Task: {subtask}")
                results[agent_name] = call_agent(url, subtask)
                taskfound = True

        if not taskfound:
            logging.warning(f"No agent found for task: {line.strip()}")
            results["Unassigned"] = {
                "result": line.strip(),
                "status": "unassigned"
            }

    return jsonify({
        "goal": user_goal,
        "plan": pm_response["result"],
        "agent_responses": results
    })

@app.route("/")
def index():
    return "Brain Agent is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5004))
    logging.info(f"Starting the app on port {port}")
    time.sleep(1)
    app.run(host="0.0.0.0", port=port)

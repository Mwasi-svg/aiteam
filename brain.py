import os
import logging
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Agent endpoint map
AGENT_ENDPOINTS = {
    "Market Research": "http://localhost:5001/run",
    "Dev": "http://localhost:5002/run",
    "Design": "http://localhost:5003/run",
    "Analysis": "http://localhost:5004/run",
    "Trend": "http://localhost:5005/run",
    "Content Creation": "http://localhost:5006/run",
}

PM_AGENT_URL = "http://localhost:5000/run"  # PM-Agent

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
    
    # Step 1: Ask PM-Agent to break down the goal
    pm_response = call_agent(PM_AGENT_URL, f"Deconstruct this goal: {user_goal}")
    logging.info(f"PM-Agent response:\n{pm_response}")

    # Step 2: Parse and route subtasks (basic parsing here)
    results = {}
    for line in pm_response.split("\n"):
        taskfound = False # Initialize for each line.
        for agent_name, url in AGENT_ENDPOINTS.items():
            if agent_name.lower() in line.lower():
                subtask = line.split("→")[-1].strip() if "→" in line else line.strip()
                logging.info(f"Routing to {agent_name} → Task: {subtask}")
                results[agent_name] = call_agent(url, subtask)
                taskfound=True 
        if not taskfound:
            logging.warning(f"No agent found for task: {line.strip()}")
            results["Unassigned"] = line.strip()

    return jsonify({
        "goal": user_goal,
        "plan": pm_response,
        "agent_responses": results
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5100))
    app.run(host="0.0.0.0", port=port)
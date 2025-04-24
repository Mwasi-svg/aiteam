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
CORS(app, origins="https://9000-idx-admin-dashboard-1745483841791.cluster-oayqgyglpfgseqclbygurw4xd4.cloudworkstations.dev")  # Frontend URL

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

PM_AGENT_URL = "https://project-manager-agent.onrender.com"

def call_agent(url, task):
    try:
        logging.info(f"Sending task to {url}")
        response = requests.post(url, json={"task": task})
        
        # Check if the response is successful
        if response.status_code == 200:
            return response.json().get("result", "No result returned.")
        else:
            logging.error(f"Error from {url}: {response.status_code} - {response.text}")
            return f"Error from {url}: {response.status_code} - {response.text}"

    except Exception as e:
        logging.error(f"Error calling agent at {url}: {e}")
        return f"Error calling agent: {e}"

@app.route('/execute', methods=['POST'])
def execute():
    user_goal = request.json.get("goal", "")
    if not user_goal:
        return jsonify({"error": "No goal provided"}), 400

    logging.info(f"User Goal: {user_goal}")
    
    # Send the user's goal to the PM Agent to deconstruct
    pm_response = call_agent(PM_AGENT_URL, f"Deconstruct this goal: {user_goal}")
    logging.info(f"PM-Agent response:\n{pm_response}")

    results = {}
    
    # Process the PM-Agent's response and assign tasks to agents
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
    port = int(os.environ.get("PORT", 5004))  # Use the port specified by Railway
    logging.info(f"Starting the app on port {port}")
    time.sleep(3)  # Wait for 3 seconds to ensure Railway is ready
    app.run(host="0.0.0.0", port=port)

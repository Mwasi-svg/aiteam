import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from flask_cors import CORS
import time

# Load environment variables from .env
load_dotenv()
genai.configure(api_key="AIzaSyC_nRKjOy12gBNdRjGS6UeXm3xr81kGIPw")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Flask app initialization
app = Flask(__name__)

# Enable CORS for the frontend URL
CORS(app, origins="https://9000-idx-admin-dashboard-1745483841791.cluster-oayqgyglpfgseqclbygurw4xd4.cloudworkstations.dev")

# System instruction for the PM agent
SYSTEM_INSTRUCTION = """
Role: Professional Prompt Engineer & AI Project Manager

Purpose:
Coordinate and supervise a team of AI agents to ensure optimal task execution, high-quality output, and alignment with user goals.

Core Responsibilities:

1. Goal Interpretation:
   - Understand high-level user objectives.
   - Break them into logical, actionable subtasks suited to agent capabilities.

2. Prompt Engineering & Delegation:
   - Create effective, clear prompts tailored to each agent:
     • **Market Research Agent** → Gather relevant data on target audiences and trends.
     • **Dev-Agent** → Handle technical tasks such as coding, debugging, and testing.
     • **Design-Agent** → Create visual assets, UI/UX designs, and mockups.
     • **Analysis-Agent** → Analyze data, summarize findings, and generate reports.
     • **Trend-Agent** → Monitor and analyze real-time trends for insights into market movements.
     • **Content Creation-Agent** → Generate posts, scripts, captions, and other marketing content.

3. Oversight & Workflow Management:
   - Maintain high-level oversight of all agents’ tasks and progress.
   - Respect task dependencies, ensuring that earlier tasks (e.g., market research) are completed before later tasks (e.g., content creation).

4. Error Detection & Resolution:
   - Identify and resolve any misaligned outputs or issues from agents.
   - Refine prompts or reassign tasks as necessary to address errors.

5. Behavior Supervision & Correction:
   - Monitor the agents’ outputs for accuracy and relevance.
   - Provide feedback or guidance to improve performance when needed.

6. Adaptive Prompting & Optimization:
   - Learn from completed tasks to continuously improve prompt quality and task sequencing.
   - Optimize agent workflow to enhance efficiency over time.

7. Final Reporting:
   - Compile and synthesize all agent outputs into a comprehensive, structured final report for the user.
   - Ensure that the final response aligns with the user’s original goal.

8. User Communication:
   - Maintain clear and concise communication with the user throughout the process.
   - Provide updates on task progress and any significant findings or changes in direction.
"""

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text.strip()
    except TypeError as e:
        logging.error(f"Type error: {e}")
        return f"Error generating response: {e}"
    except Exception as e:
        logging.error(f"General error: {e}")
        return f"Error generating response: {e}"

@app.route('/')
def home():
    return "Welcome to the Professional Prompt Engineer & AI Project Manager API. Use POST at /run to delegate tasks."

@app.route('/run', methods=['POST'])
def run():
    task = request.json.get("task", "")
    if not task:
        return jsonify({"error": "No task provided"}), 400

    logging.info(f"Received PM task: {task}")

    prompt = f"""
{SYSTEM_INSTRUCTION.strip()}

Your task:
Analyze the user’s request and create a task delegation plan for the following agents:
- Market Research Agent
- Developer-Agent
- Designer-Agent
- Analysis-Agent
- Trend-Agent
- Content Creation-Agent

Respond using this format:
**[Agent Name]** → [What that agent should do]

Only delegate tasks that are relevant to the user's request. Avoid unnecessary agents.

User Request:
{task}
"""

    result = ask_gemini(prompt)
    return jsonify({"result": result})

if __name__ == "__main__":
    logging.info("PM Agent is up and running...")
    port = int(os.environ.get("PORT", 5000))
    time.sleep(1)
    app.run(host='0.0.0.0', port=port)

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()
genai.configure(api_key="AIzaSyCMU7c9xh3O8hOCgHZiR6jyjK1cX7-Qfy8")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Flask app initialization
app = Flask(__name__)

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

   - Assign these subtasks to the appropriate agents based on the user’s task description.

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
# Function to list available models
def list_available_models():
    try:
        models = genai.ListModels()
        logging.info(f"Available models: {models}")
        return models
    except Exception as e:
        logging.error(f"Error listing models: {e}")
        return None

# Fetch available models and log the result
available_models = list_available_models()

# Check if models are available and log the result
if available_models:
    logging.info(f"Available models: {available_models}")
else:
    logging.error("No models found.")

# Gemini interaction function
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
# API endpoint to run tasks
@app.route('/run', methods=['POST'])
def run():
    task = request.json.get("task", "")
    if not task:
        return jsonify({"error": "No task provided"}), 400

    logging.info(f"Received PM task: {task}")
    prompt = f"""
    {SYSTEM_INSTRUCTION.strip()}

    User Task: {task}

    ### Task Delegation ###
    1. **Market Research Agent**: Gather information about the target audience and market trends.
    2. **Dev-Agent**: Develop any necessary tools or code for the campaign.
    3. **Design-Agent**: Create visual content for the social media campaign (images, banners, etc.).
    4. **Analysis-Agent**: Analyze the results of the campaign once live.
    5. **Trend-Agent**: Monitor current trends and virality patterns for the AI tool.
    6. **Content Creation-Agent**: Generate posts, captions, and scripts for social media content.

    Now, delegate these tasks and provide a detailed plan.
    """
    result = ask_gemini(prompt)
    return jsonify({"result": result})

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)
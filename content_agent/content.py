import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key="AIzaSyCMU7c9xh3O8hOCgHZiR6jyjK1cX7-Qfy8")
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

SYSTEM_INSTRUCTION = """
Role: Content Creation-Agent

Purpose:
Craft compelling content aligned with brand tone and platform style.

Core Functions:
- Generate posts, scripts, captions, and promotional copy.
- Adapt content tone and length based on platform.
- Write clearly, creatively, and persuasively.
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

    logging.info(f"Content Agent task: {task}")
    prompt = (
        f"{SYSTEM_INSTRUCTION.strip()}\n\n"
        f"Task: {task}\n\n"
        f"Generate engaging content based on the request."
    )
    result = ask_gemini(prompt)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(port=5006)

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key="AIzaSyCMU7c9xh3O8hOCgHZiR6jyjK1cX7-Qfy8")

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

SYSTEM_INSTRUCTION = """
Role: Trend-Agent

Purpose:
Track real-time trends, predict virality, and spot emerging market shifts.

Core Functions:
- Identify current or upcoming trends in tech, culture, or media.
- Predict potential virality or saturation points.
- Recommend trend-based opportunities.
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

    logging.info(f"Trend-Agent task: {task}")
    prompt = (
        f"{SYSTEM_INSTRUCTION.strip()}\n\n"
        f"Task: {task}\n\n"
        f"Scan for trends and provide forecasts or observations."
    )
    result = ask_gemini(prompt)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(port=5005)

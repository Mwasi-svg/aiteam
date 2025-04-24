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
Role: Market Research Agent

Purpose:
Gather relevant information, validate assumptions, and analyze trends to support strategy and decision-making.

Core Functions:
- Perform targeted market research based on user prompts.
- Summarize key findings with credible sources if available.
- Identify emerging patterns, competitors, and audience behavior.
"""

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:  
            logging.error("Empty response from Gemini.")
            return "Warning: Empty response from Gemini."
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return f"Error: {e}"

@app.route('/run', methods=['POST'])
def run():
    task = request.json.get("task", "")
    if not task:
        return jsonify({"error": "No task provided"}), 400

    logging.info(f"Market Research task: {task}")
    prompt = (
        f"{SYSTEM_INSTRUCTION.strip()}\n\n"
        f"Task: {task}\n\n"
        f"Conduct research and return a concise summary with key insights."
    )
    result = ask_gemini(prompt)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(port=5001)

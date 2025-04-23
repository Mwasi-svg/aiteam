import os 
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
# Set the environment variable for the model

def ask_gemini(prompt):
    model = genai.GenerativeModel(model="gemini-1.5-turbo")
    response = model.generate_content(prompt)
    return response.text.strip()


app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run():
    task = request.json.get("task", "")
    response = f"Processed task: {task} by Market Research Agent"
    return jsonify({"result": response})

if __name__ == "__main__":
    app.run(port=5000)

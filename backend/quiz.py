from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

print("🔍 Debug: Loaded API Key ->", GOOGLE_API_KEY)
if not GOOGLE_API_KEY:
    raise ValueError("Google Gemini API key is missing. Set it in a .env file.")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Update model name

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_quiz', methods=['GET'])
def generate_quiz():
    """Retrieves 10 Java quiz questions using Google Gemini API."""
    try:
        prompt = "Generate 10 mcq questions on Java. Give the output as only questions and options. No other content."
        response = model.generate_content(prompt)

        quiz_data = response.text.strip() if response else "Error generating quiz."
        return jsonify({"quiz": quiz_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    """Evaluates the quiz and returns a score."""
    try:
        data = request.json
        answers = data.get("answers", "")

        prompt = f"Evaluate the following quiz answers: {answers}. Only return the numerical score out of 10."
        response = model.generate_content(prompt)

        score = response.text.strip() if response else "Error evaluating score."
        return jsonify({"score": score})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

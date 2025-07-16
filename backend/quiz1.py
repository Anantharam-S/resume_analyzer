from flask import Flask, request, jsonify, render_template
import os
import pdfplumber
import mysql.connector
import google.generativeai as genai
import re

# Gemini API key setup
genai.configure(api_key="AIzaSyCfFhfqFomEefjAzeq0wF-ldBFC5xw49GY")  # Replace with your actual key
model = genai.GenerativeModel('gemini-1.5-pro-latest')

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="resume_analyzer"
    )

# Create table if not exists
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50),
            name VARCHAR(255),
            score INT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Extract text from resume PDF
def extract_resume_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

# Generate MCQs
def generate_mcqs(resume_text):
    prompt = f"""Analyze the following resume and generate 10 multiple choice questions (MCQs)to test the proficiency of applicant on the technical skills they claim to have on their resume. 
For example if the applicant has claimed to have java programming skills on their resume, ask general questions on jave. Each question should have 4 options and indicate the correct one clearly.

Resume Text:
{resume_text}

Format:
1. Question
A. Option 1
B. Option 2
C. Option 3
D. Option 4
Answer: [Correct Option Letter]

Repeat for 10 questions.
"""
    response = model.generate_content(prompt)
    full_text = response.text

    questions_only = re.sub(r'Answer:\s*[A-D]', '', full_text).strip()
    correct_answers = re.findall(r'Answer:\s*([A-D])', full_text)

    return questions_only, correct_answers

@app.route('/')
def quiz_page():
    return render_template('quiz.html')

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    file = request.files.get('resume')

    if not file or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid or missing PDF file."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, f"{user_id}_{file.filename}")
    file.save(file_path)

    resume_text = extract_resume_text(file_path)
    questions, correct_answers = generate_mcqs(resume_text)

    # Save questions
    with open(f'{user_id}_questions.txt', 'w', encoding='utf-8') as f:
        f.write(questions)

    # Save correct answers
    with open(f'{user_id}_answers.txt', 'w', encoding='utf-8') as f:
        f.write(' '.join(correct_answers))

    return jsonify({"questions": questions})

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    user_answers = request.form.get('answers').strip().split()

    try:
        with open(f'{user_id}_answers.txt', 'r', encoding='utf-8') as f:
            correct_answers = f.read().strip().split()
    except FileNotFoundError:
        return jsonify({"error": "Answer key not found for this user."}), 404

    score = sum(1 for u, c in zip(user_answers, correct_answers) if u.upper() == c.upper())

    # Save score
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quiz_scores (user_id, name, score) VALUES (%s, %s, %s)",
                   (user_id, name, score))
    conn.commit()
    conn.close()

    return jsonify({"score": score})

if __name__ == '__main__':
    app.run(debug=True)

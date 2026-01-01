from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import requests
import math
import re

app = Flask(__name__)
CORS(app)

# Manual TF-IDF and Cosine Similarity to save space
def get_cosine_sim(str1, str2):
    def get_vec(s):
        words = re.findall(r'\w+', s.lower())
        return {w: words.count(w) for w in set(words)}
    v1, v2 = get_vec(str1), get_vec(str2)
    common = set(v1.keys()) & set(v2.keys())
    numerator = sum(v1[x] * v2[x] for x in common)
    sum1 = sum(v1[x]**2 for x in v1.keys())
    sum2 = sum(v2[x]**2 for x in v2.keys())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    return (numerator / denominator) if denominator else 0.0

def fetch_real_jobs(skills_list):
    APP_ID = "8dbb7963"
    APP_KEY = "8f6ae7284b44a01cd9a5ba3527851870"
    query = " ".join(skills_list[:2]) if skills_list else "Software Developer"
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=6&what={query}"
    try:
        r = requests.get(url, timeout=5).json()
        return [{"title": j['title'].replace("<strong>","").replace("</strong>",""), 
                 "company": j['company']['display_name'], "link": j['redirect_url']} for j in r.get('results', [])]
    except: return []

@app.route('/match', methods=['POST'])
def match():
    resume = request.files['resume']
    job_desc = request.form.get('job_description', '')
    
    with pdfplumber.open(resume) as pdf:
        resume_text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    
    skill_bank = ["python", "sql", "java", "javascript", "html", "css", "react", "node", "flask", "aws", "git", "api"]
    found_in_resume = [s for s in skill_bank if s.lower() in resume_text.lower()]
    
    required = [s for s in skill_bank if s.lower() in job_desc.lower()]
    matched = [s for s in required if s in found_in_resume] if required else found_in_resume
    missing = [s for s in required if s not in found_in_resume]
    
    score = round(get_cosine_sim(resume_text, job_desc if job_desc else resume_text) * 100, 2)
    
    return jsonify({
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendations": fetch_real_jobs(matched)
    })

@app.route('/')
def home(): return "API is running!"

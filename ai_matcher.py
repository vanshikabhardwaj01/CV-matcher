import pdfplumber
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def fetch_real_jobs(skills_list):
    APP_ID = "8dbb7963"
    APP_KEY = "8f6ae7284b44a01cd9a5ba3527851870"
    query = " ".join(skills_list[:2]) if skills_list else "Software Developer"
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=6&what={query}"
    try:
        r = requests.get(url).json()
        return [{"title": j['title'], "company": j['company']['display_name'], "link": j['redirect_url']} for j in r.get('results', [])]
    except: return []

def match_resume(resume_path, job_description):
    with pdfplumber.open(resume_path) as pdf:
        text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()]).lower()
    
    skill_bank = ["python", "sql", "java", "javascript", "html", "css", "react", "node", "flask", "aws", "git", "c++"]
    found_in_resume = [s for s in skill_bank if s in text]
    
    jd_lower = job_description.lower().strip()
    required = [s for s in skill_bank if s in jd_lower] if jd_lower else []
    
    matched = [s for s in required if s in found_in_resume] if required else found_in_resume
    missing = [s for s in required if s not in found_in_resume]

    vec = TfidfVectorizer()
    target = job_description if jd_lower else " ".join(found_in_resume)
    matrix = vec.fit_transform([text, target])
    score = round(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100, 2)

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendations": fetch_real_jobs(matched)
    }

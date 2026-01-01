import pdfplumber
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def fetch_real_jobs(user_query, skills_list):
    APP_ID = "8dbb7963"
    APP_KEY = "8f6ae7284b44a01cd9a5ba3527851870"
    
    # LOGIC: Pehle Job Description (user_query) ko priority do
    # Agar user ne JD likha hai, toh wahi search query hogi.
    # Agar JD khali hai, toh resume ki top 2 skills use hongi.
    
    search_term = user_query.strip() if user_query.strip() else " ".join(skills_list[:2])
    if not search_term: search_term = "Software Developer"

    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=8&what={search_term}"
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return [{"title": j.get('title').replace("<strong>", "").replace("</strong>", ""), 
                 "company": j.get('company', {}).get('display_name', 'Tech Firm'), 
                 "link": j.get('redirect_url', '#')} for j in data.get('results', [])]
    except Exception as e:
        print(f"Fetch Error: {e}")
        return []

def match_resume(resume_path, job_description):
    with pdfplumber.open(resume_path) as pdf:
        text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()]).lower()
    
    skill_bank = ["python", "sql", "java", "javascript", "html", "css", "react", "node", "flask", "aws", "git", "c++", "c#"]
    found_in_resume = [s for s in skill_bank if s in text]
    
    jd_lower = job_description.lower().strip()
    required = [s for s in skill_bank if s in jd_lower] if jd_lower else []
    
    # Skills display logic
    matched = [s for s in required if s in found_in_resume] if required else found_in_resume
    missing = [s for s in required if s not in found_in_resume]

    # Contextual Score
    vec = TfidfVectorizer()
    target = job_description if jd_lower else " ".join(found_in_resume)
    matrix = vec.fit_transform([text, target])
    score = round(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100, 2)

    # SEARCH JOBS based on Job Description + Skills
    recommendations = fetch_real_jobs(job_description, found_in_resume)

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendations": recommendations
    }
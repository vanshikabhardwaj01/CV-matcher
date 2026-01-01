from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
from fpdf import FPDF
from ai_matcher import match_resume

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/match", methods=["POST"])
def match():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file"}), 400
        
        resume = request.files["resume"]
        jd = request.form.get("job_description", "")
        
        resume_path = os.path.join(UPLOAD_FOLDER, resume.filename)
        resume.save(resume_path)
        
        # ai_matcher se analysis lana
        result = match_resume(resume_path, jd)
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download_report", methods=["POST"])
def download_report():
    data = request.json
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(251, 113, 133) # Pink Color
    pdf.cell(200, 20, "AI Career Analysis Report", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"Match Score: {data.get('score', 0)}%", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Skills Found:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, ", ".join(data.get('matched_skills', [])).upper())
    
    pdf.ln(5)
    pdf.cell(200, 10, "Missing Skills:", ln=True)
    pdf.multi_cell(0, 10, ", ".join(data.get('missing_skills', [])).upper())

    output = io.BytesIO()
    pdf_content = pdf.output(dest='S').encode('latin-1')
    output.write(pdf_content)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="Report.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True, port=5000)

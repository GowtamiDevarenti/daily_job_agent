import os
import json
import requests

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def evaluate_and_generate_cover_letter(job, profile, config):
    """
    Evaluates job fit and generates summary + tailored cover letter.
    Uses Google Gemini API if GEMINI_API_KEY is available, or rule-based fallback.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    # 1. First quick keyword check for instant safety filter
    title_lower = job.get("title", "").lower()
    desc_lower = job.get("description", "").lower()

    # Never apply keywords filter
    for kw in config.get("never_apply_keywords", ["Senior", "Lead", "Architect", "Principal"]):
        if kw.lower() in title_lower:
            return {
                "match_score": 0,
                "reason": f"Skipped: Senior/Lead role ('{kw}')",
                "summary": "",
                "cover_letter": ""
            }

    if api_key and api_key != "your_gemini_api_key_here":
        return _evaluate_with_gemini(job, profile, config, api_key)
    else:
        return _evaluate_with_fallback(job, profile, config)


def _evaluate_with_gemini(job, profile, config, api_key):
    """Evaluates job using Google Gemini API."""
    prompt = f"""
You are an expert career agent evaluating a job description for candidate Gowtami Devarenti.

CANDIDATE PROFILE FACTS (STRICT RULES: Use ONLY these facts, NEVER invent extra skills or work experience):
{json.dumps(profile, indent=2, ensure_ascii=False)}

JOB DETAILS:
Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}
Description: {job.get('description')[:3000]}

TASK:
1. Evaluate if this job is suitable for a student/career changer looking for Junior, Trainee, or LIA roles in Python, AI/ML, Data or Business Analytics in Göteborg or Remote.
2. Check exclusion rules:
   - SKIP (Score 0) if it requires Senior/Lead/Architect experience.
   - SKIP (Score 0) if it strictly requires fluent native Swedish for technical work.
   - SKIP if the candidate lacks core requirements.
3. Assign a Match Score from 0 to 100.
4. Write a 2-3 sentence summary of the job.
5. If Match Score >= {config.get('min_match_score', 80)}, write a tailored English cover letter (max 250 words) highlight candidate's MBA in Finance, Lexicon Python AI/ML Developer studies, leadership of 40 people, Python/SQL skills, full right to work in Sweden, and enthusiasm for the role.

Return strictly a valid JSON object with format:
{{
  "match_score": <number 0-100>,
  "reason": "<short explanation>",
  "summary": "<2-3 sentence summary>",
  "cover_letter": "<tailored cover letter string or empty>"
}}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        res = requests.post(f"{GEMINI_API_URL}?key={api_key}", json=payload, headers=headers, timeout=15)
        if res.status_code == 200:
            result_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Extract JSON from response
            json_match = result_text[result_text.find("{"):result_text.rfind("}")+1]
            return json.loads(json_match)
    except Exception as e:
        print(f"Gemini API call failed: {e}. Using smart fallback rule evaluator.")

    return _evaluate_with_fallback(job, profile, config)


def _evaluate_with_fallback(job, profile, config):
    """Smart rule-based evaluator used when Gemini API key is not yet set up."""
    title = job.get("title", "")
    desc = job.get("description", "")
    text = (title + " " + desc).lower()

    # Positive match keywords
    pos_keywords = ["python", "ai", "machine learning", "data", "analyst", "junior", "trainee", "lia", "intern", "assistant"]
    score_points = sum(15 for kw in pos_keywords if kw in text)

    # Swedish fluency requirement check
    if "flytande svenska" in text or "svenska i tal och skrift" in text:
        # Candidate has basic Swedish, so penalize if high fluency required
        score_points -= 20

    final_score = min(max(score_points + 40, 30), 95)
    
    # Check if title matches junior/entry/LIA or general developer
    if any(k in title.lower() for kk in ["senior", "lead", "architect", "chef"] for k in [kk]):
        final_score = 0

    if final_score >= config.get("min_match_score", 80):
        summary = f"Opportunity for {title} at {job.get('company')} in {job.get('location')}. Fits Python/AI student profile."
        cover_letter = generate_fallback_cover_letter(job, profile)
    else:
        summary = f"Role: {title} at {job.get('company')}. Match score ({final_score}%) is below minimum threshold."
        cover_letter = ""

    return {
        "match_score": final_score,
        "reason": f"Rule-based match score: {final_score}%",
        "summary": summary,
        "cover_letter": cover_letter
    }


def generate_fallback_cover_letter(job, profile):
    """Generates a clean tailored cover letter using profile facts."""
    return f"""Dear Hiring Team at {job.get('company', 'the company')},

I am writing to express my enthusiastic interest in the {job.get('title')} position. As a dedicated student in the Python AI/ML Developer program at Lexicon IT-Proffs in Stockholm, combined with an MBA in Finance and proven business leadership experience, I am eager to contribute to your team.

My background includes leading a team of 40 in real-estate sales and business development, where I developed strong problem-solving and communication skills. Currently, I am expanding my technical capabilities in Python, SQL, Git, and Machine Learning. I am based in Göteborg and hold full right to work in Sweden (EU/EEA).

I am available for LIA internship and junior developer opportunities, and I am confident that my unique combination of business acumen and technical skills will bring immediate value to {job.get('company')}.

Thank you for your time and consideration.

Best regards,

Gowtami Devarenti
Göteborg, Sweden
GitHub: https://github.com/GowtamiDevarenti
"""

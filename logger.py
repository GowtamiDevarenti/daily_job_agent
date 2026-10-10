import json
import os
from datetime import datetime

LOG_FILE = "applied_jobs.json"

def load_log():
    """Loads the history log of applied jobs."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not read {LOG_FILE}: {e}")
            return {"applied_jobs": []}
    return {"applied_jobs": []}

def save_log(log_data):
    """Saves the history log to JSON file."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

def is_job_processed(job_id, company_name, config):
    """Checks if job ID or company is already applied to or in never-apply list."""
    log_data = load_log()
    never_apply_employers = [emp.lower() for emp in config.get("never_apply_to_employers", [])]

    if company_name and company_name.lower() in never_apply_employers:
        print(f"Skipping {company_name}: In excluded employers list.")
        return True

    for job in log_data.get("applied_jobs", []):
        if str(job.get("id")) == str(job_id):
            return True
        # Check if already applied to this company in past 30 days
        if job.get("company", "").lower() == (company_name or "").lower():
            print(f"Already applied to {company_name} previously on {job.get('date')}.")
            return True
    return False

def log_job_application(job_id, title, company, url, status, match_score, cover_letter=""):
    """Logs a newly processed job application."""
    log_data = load_log()
    entry = {
        "id": str(job_id),
        "title": title,
        "company": company,
        "url": url,
        "status": status,
        "match_score": match_score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cover_letter": cover_letter
    }
    log_data.setdefault("applied_jobs", []).append(entry)
    save_log(log_data)
    print(f"Logged job: {title} at {company} (Status: {status})")

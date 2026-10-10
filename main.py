import json
import os
import sys
from dotenv import load_dotenv

# Load .env file automatically if present
load_dotenv()

from logger import is_job_processed, log_job_application, load_log
from job_fetcher import fetch_all_jobs
from ai_agent import evaluate_and_generate_cover_letter
from notifier import send_email, send_daily_summary

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_agent():
    print("="*60)
    print("  DAILY JOB APPLICATION AGENT FOR SWEDEN")
    print("="*60)

    # Load configuration and profile
    config = load_json("config.json")
    profile = load_json("profile.json")

    test_mode = config.get("test_mode", True)
    user_email = os.getenv("MY_EMAIL", config.get("user_email"))
    max_apps = config.get("max_applications_per_day", 5)
    min_score = config.get("min_match_score", 80)

    print(f"Mode: {'[TEST MODE - Emails go to candidate]' if test_mode else '[LIVE MODE - Sending to employers]'}")
    print(f"Candidate Email: {user_email}")
    print(f"Max Applications / Day: {max_apps}")
    print(f"Min Match Score: {min_score}%\n")

    # 1. Fetch fresh jobs
    jobs = fetch_all_jobs(config)
    print(f"\nFetched {len(jobs)} total job candidates.")

    sent_applications = []
    manual_applications = []
    apps_count = 0

    # 2. Evaluate and process each job
    for job in jobs:
        if apps_count >= max_apps:
            print(f"Reached maximum daily application limit ({max_apps}). Stopping.")
            break

        job_id = job.get("id")
        company = job.get("company", "Unknown")

        # Skip if processed previously
        if is_job_processed(job_id, company, config):
            continue

        print(f"\nEvaluating: '{job.get('title')}' at '{company}'...")
        eval_res = evaluate_and_generate_cover_letter(job, profile, config)
        match_score = eval_res.get("match_score", 0)
        reason = eval_res.get("reason", "")
        summary = eval_res.get("summary", "")
        cover_letter = eval_res.get("cover_letter", "")

        print(f"  Match Score: {match_score}% ({reason})")

        if match_score >= min_score:
            contact_email = job.get("contact_email")
            apply_url = job.get("apply_url")
            
            if contact_email:
                # Direct email application
                target_email = user_email if test_mode else contact_email
                subject = f"{'[TEST MODE] ' if test_mode else ''}Application for {job.get('title')} - Gowtami Devarenti"
                
                body = f"Dear Hiring Manager,\n\n{cover_letter}\n\nAttached is my ATS-friendly CV for your review.\n\nBest regards,\nGowtami Devarenti\nhttps://github.com/GowtamiDevarenti"
                
                # Attachment priority: ATS-optimized CV
                attachment = "CV_Gowtami_Devarenti_ATS.txt" if os.path.exists("CV_Gowtami_Devarenti_ATS.txt") else "CV_Gowtami_Devarenti.txt"
                success = send_email(target_email, subject, body, attachment_path=attachment, config=config)

                status = "sent_test_email" if test_mode else "sent_employer_email"
                log_job_application(job_id, job.get('title'), company, apply_url, status, match_score, cover_letter)
                
                sent_applications.append({
                    "title": job.get('title'),
                    "company": company,
                    "url": apply_url,
                    "match_score": match_score,
                    "status": status
                })
                apps_count += 1
            else:
                # Online link application (e.g., LinkedIn / Employer Portal)
                status = "manual_apply_link"
                log_job_application(job_id, job.get('title'), company, apply_url, status, match_score, cover_letter)
                
                manual_applications.append({
                    "title": job.get('title'),
                    "company": company,
                    "url": apply_url,
                    "match_score": match_score,
                    "summary": summary,
                    "cover_letter": cover_letter
                })

    # 3. Send Daily Summary & generate report
    send_daily_summary(sent_applications, manual_applications, config)
    print("\nDaily Agent run completed successfully!")

if __name__ == "__main__":
    run_agent()

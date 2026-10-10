import requests
import re
import imaplib
import email
from email.header import decode_header
import json
import os

JOBTECH_API_URL = "https://jobsearch.api.jobtechdev.se/search"

def fetch_platsbanken_jobs(keywords, locations):
    """
    Fetches jobs from Arbetsförmedlingen's official public JobTech API.
    """
    jobs = []
    print("Fetching jobs from Arbetsförmedlingen Platsbanken API...")
    
    for keyword in keywords:
        for loc in locations:
            query = f"{keyword} {loc}"
            try:
                response = requests.get(JOBTECH_API_URL, params={"q": query, "limit": 15}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("hits", [])
                    for hit in hits:
                        job_id = hit.get("id")
                        headline = hit.get("headline", "Untitled Job")
                        company = hit.get("employer", {}).get("name", "Unknown Company")
                        municipality = hit.get("workplace_address", {}).get("municipality", loc)
                        desc = hit.get("description", {}).get("text", "")
                        
                        app_details = hit.get("application_details", {})
                        app_url = app_details.get("url") or f"https://platsbanken.arbetsformedlingen.se/lediga-jobb/jobb/{job_id}"
                        app_email = app_details.get("email")

                        jobs.append({
                            "id": f"pb_{job_id}",
                            "title": headline,
                            "company": company,
                            "location": municipality,
                            "description": desc,
                            "apply_url": app_url,
                            "contact_email": app_email,
                            "source": "Platsbanken API"
                        })
            except Exception as e:
                print(f"Error fetching Platsbanken jobs for '{query}': {e}")

    # Remove duplicates based on ID
    unique_jobs = {j["id"]: j for j in jobs}.values()
    print(f"Found {len(unique_jobs)} total jobs from Platsbanken.")
    return list(unique_jobs)


def fetch_linkedin_gmail_alerts(user_email, app_password):
    """
    Connects to Gmail via IMAP to read LinkedIn job-alert emails.
    Safety rule: Reads emails safely, extracts links, NEVER scrapes or logs into LinkedIn.
    """
    if not user_email or not app_password or app_password == "your_gmail_app_password_here":
        print("Gmail credentials not provided. Skipping Gmail LinkedIn alert fetch.")
        return []

    jobs = []
    print("Connecting to Gmail IMAP to check LinkedIn job alerts...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user_email, app_password)
        mail.select("inbox")

        # Search for recent LinkedIn Job Alert emails
        status, messages = mail.search(None, '(FROM "jobalerts-noreply@linkedin.com")')
        if status != "OK" or not messages[0]:
            status, messages = mail.search(None, '(SUBJECT "job alert")')

        email_ids = messages[0].split()
        # Fetch up to 5 latest alert emails
        for e_id in email_ids[-5:]:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type in ["text/plain", "text/html"]:
                                try:
                                    body += part.get_payload(decode=True).decode(errors="ignore")
                                except Exception:
                                    pass
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    # Extract job links and titles from email body using Regex
                    # Looking for links like https://www.linkedin.com/comm/jobs/view/...
                    links = re.findall(r'https://[a-zA-Z0-9\./\?=_-]*linkedin.com[a-zA-Z0-9\./\?=_-]*job[s]?[a-zA-Z0-9\./\?=_-]*', body)
                    for i, link in enumerate(set(links)):
                        jobs.append({
                            "id": f"li_alert_{hash(link)}",
                            "title": f"LinkedIn Alert Job #{i+1} from '{subject}'",
                            "company": "Company via LinkedIn Alert",
                            "location": "Göteborg / Remote",
                            "description": f"LinkedIn Job Alert listing found in email '{subject}'. Link: {link}",
                            "apply_url": link,
                            "contact_email": None,
                            "source": "LinkedIn Gmail Alert"
                        })
        mail.logout()
    except Exception as e:
        print(f"Notice: Gmail IMAP check skipped or error: {e}")

    print(f"Extracted {len(jobs)} jobs from LinkedIn alert emails.")
    return jobs


def fetch_all_jobs(config):
    """
    Fetches jobs from all configured sources.
    """
    keywords = config.get("search_keywords", ["Python", "AI", "Data Analyst"])
    locations = config.get("search_locations", ["Göteborg"])
    
    platsbanken_jobs = fetch_platsbanken_jobs(keywords, locations)
    
    user_email = os.getenv("MY_EMAIL", config.get("user_email"))
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    linkedin_jobs = fetch_linkedin_gmail_alerts(user_email, app_password)

    all_jobs = platsbanken_jobs + linkedin_jobs
    return all_jobs

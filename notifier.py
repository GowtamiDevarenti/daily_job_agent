import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

def send_email(to_email, subject, body, attachment_path=None, config=None):
    """
    Sends email via SMTP (Gmail). If credentials are missing, logs to console safely.
    """
    user_email = os.getenv("MY_EMAIL", config.get("user_email") if config else "")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not user_email or not app_password or app_password == "your_gmail_app_password_here":
        print(f"\n[SIMULATION EMAIL NOT SENT - NO GMAIL APP PASSWORD SET]")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body Preview:\n{body[:300]}...\n")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = user_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user_email, app_password)
        server.send_message(msg)
        server.quit()
        print(f"Email successfully sent to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False


def send_daily_summary(sent_apps, manual_jobs, config):
    """
    Sends daily summary email to Gowtami and writes local markdown report.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    user_email = os.getenv("MY_EMAIL", config.get("user_email"))

    subject = f"Daily Job Agent Summary - {today_str} ({len(sent_apps)} Sent, {len(manual_jobs)} Manual)"

    body = f"Hello Gowtami,\n\nHere is your Daily Job Application Agent report for {today_str}.\n\n"
    body += "="*50 + "\n"
    body += f"1. APPLICATIONS SENT DIRECTLY ({len(sent_apps)})\n"
    body += "="*50 + "\n"
    
    if sent_apps:
        for app in sent_apps:
            body += f"• {app['title']} at {app['company']} (Score: {app['match_score']}%)\n"
            body += f"  Status: {app['status']}\n"
            body += f"  Link: {app['url']}\n\n"
    else:
        body += "No direct email applications sent today.\n\n"

    body += "="*50 + "\n"
    body += f"2. JOBS TO APPLY FOR YOURSELF ({len(manual_jobs)})\n"
    body += "="*50 + "\n"
    
    if manual_jobs:
        for job in manual_jobs:
            body += f"• {job['title']} at {job['company']} (Score: {job['match_score']}%)\n"
            body += f"  Apply Link: {job['url']}\n"
            body += f"  Summary: {job.get('summary', '')}\n"
            body += f"  Draft Cover Letter:\n{job.get('cover_letter', '')}\n"
            body += "-"*40 + "\n\n"
    else:
        body += "No additional manual application links found today.\n\n"

    body += "Keep up the great work!\nBest regards,\nYour Daily Job Agent"

    # Send summary email
    send_email(user_email, subject, body, config=config)

    # Save detailed local report file
    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/daily_report_{today_str}.md"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(f"# Daily Job Agent Report - {today_str}\n\n")
        f.write(f"**Direct Applications Sent**: {len(sent_apps)}\n")
        f.write(f"**Manual Applications Suggested**: {len(manual_jobs)}\n\n")
        f.write("## 1. Sent Applications\n")
        for app in sent_apps:
            f.write(f"- **{app['title']}** at *{app['company']}* (Match: {app['match_score']}%)\n  [View Ad]({app['url']})\n")
        f.write("\n## 2. Recommended Manual Applications & Pre-drafted Cover Letters\n")
        for job in manual_jobs:
            f.write(f"### {job['title']} at {job['company']}\n")
            f.write(f"- **Match Score**: {job['match_score']}%\n")
            f.write(f"- **Apply URL**: {job['url']}\n")
            f.write(f"- **Summary**: {job.get('summary', '')}\n\n")
            f.write("```text\n" + job.get('cover_letter', '') + "\n```\n\n")

    print(f"Generated daily report file: {report_filename}")

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

def send_email(to_email, subject, text_body, html_body=None, attachment_path=None, config=None):
    """
    Sends multi-part (Plain Text + Rich HTML) email via SMTP.
    Catches errors gracefully if credentials are missing.
    """
    user_email = os.getenv("MY_EMAIL", config.get("user_email") if config else "")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not user_email or not app_password or app_password in ["your_gmail_app_password_here", "paste_your_16_character_app_password_here"]:
        print(f"\n[NOTICE: Simulation Mode] Gmail App Password not configured yet.")
        print(f"Target: {to_email} | Subject: {subject.encode('ascii', 'ignore').decode()}")
        print(f"Saving cover letter and HTML report locally...")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = user_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach Plain Text fallback
        msg.attach(MIMEText(text_body, "plain", "utf-8"))

        # Attach HTML version if provided
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(user_email, app_password)
        server.send_message(msg)
        server.quit()
        print(f"Successfully sent rich HTML email to {to_email}")
        return True
    except Exception as e:
        print(f"\n[SMTP NOTICE] Gmail connection skipped ({e}). Report saved locally.")
        return False


def send_daily_summary(sent_apps, manual_jobs, config):
    """
    Writes Markdown & HTML local report files, then sends rich HTML daily email digest.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    user_email = os.getenv("MY_EMAIL", config.get("user_email"))

    # 1. ALWAYS write Markdown report
    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/daily_report_{today_str}.md"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(f"# Daily Job Agent Report - {today_str}\n\n")
        f.write(f"**Direct Applications Sent**: {len(sent_apps)}\n")
        f.write(f"**Manual Applications Suggested**: {len(manual_jobs)}\n\n")
        f.write("## 1. Sent Applications\n")
        if sent_apps:
            for app in sent_apps:
                f.write(f"- **{app['title']}** at *{app['company']}* (Match: {app['match_score']}%)\n  [View Ad]({app['url']})\n")
        else:
            f.write("No direct email applications sent today.\n")
            
        f.write("\n## 2. Recommended Manual Applications & Pre-drafted Cover Letters\n")
        if manual_jobs:
            for job in manual_jobs:
                f.write(f"### {job['title']} at {job['company']}\n")
                f.write(f"- **Match Score**: {job['match_score']}%\n")
                f.write(f"- **Apply URL**: {job['url']}\n")
                f.write(f"- **Summary**: {job.get('summary', '')}\n\n")
                f.write("```text\n" + job.get('cover_letter', '') + "\n```\n\n")
        else:
            f.write("No manual application links found today.\n")

    # 2. Build Rich HTML Body for Email & Web Report
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f7f6; color: #333; margin:0; padding:20px; }}
        .container {{ max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }}
        .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 25px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header p {{ margin: 5px 0 0 0; opacity: 0.9; font-size: 14px; }}
        .stats {{ display: flex; background: #eef2f5; padding: 15px; border-bottom: 1px solid #e1e8ed; }}
        .stat-box {{ flex: 1; text-align: center; }}
        .stat-num {{ font-size: 22px; font-weight: bold; color: #1e3c72; }}
        .stat-label {{ font-size: 11px; text-transform: uppercase; color: #666; font-weight: 600; }}
        .section {{ padding: 20px; border-bottom: 1px solid #f0f0f0; }}
        .section-title {{ font-size: 18px; color: #1e3c72; border-bottom: 2px solid #1e3c72; padding-bottom: 6px; margin-top: 0; }}
        .job-card {{ background: #fafbfc; border: 1px solid #e1e8ed; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
        .job-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .job-title {{ font-size: 16px; font-weight: bold; color: #2c3e50; margin: 0; }}
        .company {{ font-size: 14px; color: #7f8c8d; font-weight: 500; margin: 2px 0 10px 0; }}
        .badge {{ background: #27ae60; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
        .btn {{ display: inline-block; background: #2980b9; color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; margin-top: 10px; }}
        .cover-box {{ background: #f8f9fa; border-left: 4px solid #2980b9; padding: 10px 15px; font-size: 12px; color: #444; margin-top: 10px; white-space: pre-line; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #888; background: #f9f9f9; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🇸🇪 Daily Job Agent Digest</h1>
          <p>Candidate: Gowtami Devarenti | {today_str}</p>
        </div>
        
        <div class="stats">
          <div class="stat-box">
            <div class="stat-num">{len(sent_apps) + len(manual_jobs)}</div>
            <div class="stat-label">Total Jobs</div>
          </div>
          <div class="stat-box">
            <div class="stat-num">{len(sent_apps)}</div>
            <div class="stat-label">Direct Emails</div>
          </div>
          <div class="stat-box">
            <div class="stat-num">{len(manual_jobs)}</div>
            <div class="stat-label">Manual Links</div>
          </div>
        </div>

        <div class="section">
          <h2 class="section-title">1. Direct Email Applications Sent ({len(sent_apps)})</h2>
    """

    if sent_apps:
        for app in sent_apps:
            html_body += f"""
            <div class="job-card">
              <div class="job-title">{app['title']}</div>
              <div class="company">{app['company']}</div>
              <span class="badge">Score: {app['match_score']}%</span>
              <br><a href="{app['url']}" class="btn" target="_blank">View Job Listing</a>
            </div>
            """
    else:
        html_body += "<p style='color:#777;'>No direct email applications sent today.</p>"

    html_body += f"""
        </div>

        <div class="section">
          <h2 class="section-title">2. Recommended Manual Applications & Draft Cover Letters ({len(manual_jobs)})</h2>
    """

    if manual_jobs:
        for job in manual_jobs:
            html_body += f"""
            <div class="job-card">
              <div class="job-title">{job['title']}</div>
              <div class="company">{job['company']}</div>
              <span class="badge">Match: {job['match_score']}%</span>
              <p style="font-size:13px; color:#555; margin:8px 0;">{job.get('summary', '')}</p>
              <a href="{job['url']}" class="btn" target="_blank">Apply Now on Portal</a>
              <div class="cover-box"><strong>Draft Cover Letter:</strong>\n{job.get('cover_letter', '')}</div>
            </div>
            """
    else:
        html_body += "<p style='color:#777;'>No additional manual application links today.</p>"

    html_body += """
        </div>
        <div class="footer">
          <p>Daily Job Agent for Sweden • Gowtami Devarenti</p>
        </div>
      </div>
    </body>
    </html>
    """

    # 3. Save HTML report
    html_report_filename = f"reports/daily_report_{today_str}.html"
    with open(html_report_filename, "w", encoding="utf-8") as f:
        f.write(html_body)
    print(f"Generated HTML report file: {html_report_filename}")

    # Plain text body fallback
    text_body = f"Daily Job Agent Report - {today_str}\nDirect Sent: {len(sent_apps)}\nManual Links: {len(manual_jobs)}\nCheck reports folder for HTML digest."

    # 4. Attempt Sending Email
    subject = f"Daily Job Agent Digest - {today_str} ({len(sent_apps)} Sent, {len(manual_jobs)} Manual)"
    send_email(user_email, subject, text_body, html_body=html_body, config=config)

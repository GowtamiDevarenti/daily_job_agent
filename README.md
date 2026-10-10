# Daily Job Application Agent (Sweden) 🇸🇪🤖

Automated daily job search agent built for **Gowtami Devarenti** to find, score, and apply for Python, AI/ML, Data & Business Analytics roles (Junior, Trainee, and LIA internships) in Göteborg and Remote.

---

## 🌟 How It Works

1. **Finds Fresh Jobs Daily**:
   - Searches official **Arbetsförmedlingen Platsbanken API**.
   - Extracts job listings from **LinkedIn Job Alert emails** in Gmail.
2. **AI Matching & Safety Filters**:
   - Scores jobs from 0% to 100% using **Google Gemini AI**.
   - Automatically skips Senior, Lead, Architect, or fluent Swedish-required jobs.
   - Ensures no candidate facts are invented—uses **ONLY** `profile.json`.
3. **Application & Draft Generation**:
   - **TEST MODE**: Sends test application emails to your own Gmail inbox with your CV attached.
   - **Manual Links**: Lists jobs requiring web portal submission with pre-drafted cover letters.
4. **Daily Email & Markdown Summary**:
   - Sends a single daily digest email every evening.
   - Saves a daily report in `reports/daily_report_YYYY-MM-DD.md`.
5. **No Duplicate Applications**:
   - Tracks processed jobs in `applied_jobs.json` to never apply to the same job or employer twice.

---

## 🔑 Setting Up Secrets & Credentials

To run the agent locally or in the cloud, you need two secret keys.

### 1. Google Gemini API Key (Free)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click **Create API Key**.
3. Copy your API Key.

### 2. Gmail App Password (Free)
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Ensure **2-Step Verification** is turned ON.
3. Search for **App Passwords** in the search bar.
4. Create a new App Password named `JobAgent` and copy the 16-character code.

---

## 💻 Local Testing

1. Create a `.env` file in this directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   MY_EMAIL=gowtamidevarenti@gmail.com
   GMAIL_APP_PASSWORD=your_16_character_app_password
   ```
2. Run the agent locally:
   ```bash
   python main.py
   ```

---

## ☁️ Setting Up Daily Cloud Automation (GitHub Actions)

1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Daily Job Application Agent"
   git branch -M main
   git remote add origin https://github.com/GowtamiDevarenti/daily_job_agent.git
   git push -u origin main
   ```
2. **Add Repository Secrets on GitHub**:
   - Go to your repository on GitHub: `https://github.com/GowtamiDevarenti/daily_job_agent`
   - Click **Settings** > **Secrets and variables** > **Actions**.
   - Click **New repository secret** and add:
     - `GEMINI_API_KEY`
     - `MY_EMAIL`
     - `GMAIL_APP_PASSWORD`
3. **Enable Workflow Permissions**:
   - Go to **Settings** > **Actions** > **General**.
   - Scroll down to **Workflow permissions** and select **Read and write permissions**.
   - Click **Save**.

Now your agent will automatically run every day at **19:00 CET**! 🚀

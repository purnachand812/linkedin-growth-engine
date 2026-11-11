# 🚀 Autonomous LinkedIn Growth Engine & Studio (White-Label OS)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Autonomous Scheduling](https://img.shields.io/badge/Autonomous-Scheduler-10B981.svg)]()
[![Voice Quality Gate](https://img.shields.io/badge/Voice%20Gate-5--Check%20Scoring-38BDF8.svg)]()

A practitioner-grade, **white-label autonomous LinkedIn content engine** designed for software engineers, systems architects, AI builders, and technical founders. 

This engine eliminates AI corporate fluff, enforces contrarian technical depth, automatically generates dark-mode Canva-style architecture graphics, and handles autonomous queue scheduling or one-click live publishing with official LinkedIn OAuth 2.0.

Run it locally with the included real-time dashboard or deploy it 100% serverless for **$0/month** on GitHub Actions.

---

## ⚡ Key Highlights

- **Interactive Setup Wizard (`setup.py`)**: Seamless onboarding in under 2 minutes. Configures author branding, technical niche, target timezone, and API credentials.
- **Dynamic Personal Branding**: All Canva graphics, visual comparison cards, and dashboard elements pull dynamically from `config.json`. Zero hardcoded names or credentials.
- **5-Check Voice & Quality Gate**:
  1. **Burstiness**: Prevents robotic, uniform sentence lengths.
  2. **Specificity**: Enforces concrete numbers, memory limits, and hardware metrics.
  3. **Anti-Slop Filter**: Flags and blocks corporate buzzwords (*delve, leverage, game-changer, unlock*).
  4. **AI Fingerprint Shield**: Blocks em-dashes (`—`), zero-width Unicode characters, and synthetic quotation formats.
  5. **Pragmatic Skepticism**: Enforces real-world trade-offs, gotchas, and test declaration.
- **Autonomous Timezone-Aware Scheduler**: Dispatches approved drafts strictly during prime-time audience windows (e.g., Morning Standup, Midday Catchup) with strict daily rate limits.
- **Canva Comparison Graphic Generator**: Uses headless Chromium to compile 1200x675 high-DPI side-by-side architecture benchmarks.
- **Autonomous Jobs Radar & ATS Resume Tailor**: Scrapes open engineering positions from LinkedIn and European employment boards without paid recruiter accounts. Analyzes job descriptions against your `profile_master.json`, scores match %, and generates tailored 2-page ATS resumes and custom cover letters in HTML & pixel-perfect vector PDF.
- **Real-Time Interactive Studio**: Dark-mode glassmorphic dashboard (`http://localhost:3000`) for queue management, draft editing, live quality scoring, and OAuth connection.

---

## 📋 System Prerequisites

Before running the engine, ensure your machine has:

1. **Python 3.10 or higher**:
   ```bash
   python --version
   ```
2. **Google Chrome or Chromium**:
   Required by `html2image` to render high-resolution PNG graphics.
   - *Windows / macOS*: Standard Google Chrome installation.
   - *Linux / Ubuntu*: `sudo apt-get install chromium-browser`
3. **LinkedIn Developer App** (Free, takes 3 minutes — see instructions below).

---

## 🚀 3-Minute Quickstart

### Step 1: Clone and Enter the Directory
```bash
git clone <your-repository-url>
cd white-label-linkedin-automation
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Interactive Setup Wizard
```bash
python setup.py
```
The wizard will prompt you for:
- Your Name, Initials, Professional Headline, and Location.
- Your primary content niche (e.g. AI Systems, Cloud & DevOps, Distributed Backends).
- Your target audience timezone (e.g. `Europe/Berlin`, `America/New_York`, `UTC`).
- (Optional) Your LinkedIn API credentials.

The wizard creates your customized `config.json`, initializes `.env`, seeds 3 starter breakthrough candidates, and renders their graphics!

---

## 🔑 Setting Up Your LinkedIn Developer App

To enable live publishing and OAuth token exchange:

1. Visit the [LinkedIn Developer Portal](https://www.linkedin.com/developers/) and click **Create App**.
2. Fill in your App Name and link your personal or company LinkedIn page.
3. In the **Products** tab of your app, add:
   - **Sign In with LinkedIn using OpenID Connect**
   - **Share on LinkedIn**
4. In the **Auth** tab:
   - Note your **Client ID** and **Client Secret**.
   - Under **Authorized redirect URLs for your app**, add:
     ```text
     http://localhost:3000/api/linkedin/callback
     ```
   - Verify that your app permissions include:
     - `w_member_social` (Post, comment, and like on your behalf)
     - `openid` (Authenticate using OpenID)
     - `profile` (Retrieve basic name and profile information)
     - `email` (Retrieve primary account email)
5. Add these credentials into your `.env` file:
   ```env
   LINKEDIN_CLIENT_ID=your_client_id_here
   LINKEDIN_CLIENT_SECRET=your_client_secret_here
   LINKEDIN_REDIRECT_URI=http://localhost:3000/api/linkedin/callback
   ```

---

## 🖥️ Running the Local Studio

Start both the interactive Studio UI and background scheduling daemon with a single command:

```bash
python run_hub.py
```

Then open your browser at:
👉 **[http://localhost:3000](http://localhost:3000)**

### Dashboard Features:
- **Active Queue Tab**: View all pending drafts, check scores, approve/unapprove, or click **Publish Now** to dispatch immediately.
- **100% Published Archive Tab**: Live history of all published posts with clickable links directly to LinkedIn.
- **Post Studio Tab**: Compose or paste custom copy to run real-time 5-check quality scoring and save drafts to the queue.
- **Jobs Radar Tab**: View real-time technical job openings matching your profile, match scores, and 1-click tailored ATS Resumes & Cover Letters (HTML/PDF).
- **Settings Tab**: Update your name, initials badge, headline, and target timezone in real time.
- **Connect LinkedIn Button**: One-click OAuth login to link your personal LinkedIn profile.

---

## 💼 Autonomous Jobs Radar & ATS Resume Tailor

The engine includes an autonomous career module that monitors real-time engineering positions and tailors customized application packets:

1. **Profile Master Template (`profile_master.json.example`)**:
   - Define your work experience, education, verified projects, skills, and CEFR language proficiencies.
   - The setup wizard automatically initializes your local `profile_master.json`.
2. **Multi-Source Job Scraper**:
   - Scrapes LinkedIn public guest postings and the official Bundesagentur für Arbeit API without requiring paid recruiter accounts.
   - Filters positions by your target role titles and location.
3. **1-Click Tailored ATS Resumes**:
   - Matches the job's required tech stack against your profile.
   - Dynamically reorganizes and highlights your most relevant projects and skills.
   - Generates authentic 2-page ATS-compliant resumes exported to both HTML and vector PDF.
4. **Custom Grounded Cover Letters**:
   - Generates an individualized cover letter addressing the employer's specific tech stack and challenges.
   - Exports to clean, printable A4 PDF.

---

## ☁️ Serverless Deployment via GitHub Actions ($0 Cloud Run)

You can run this automation entirely in the cloud for free using GitHub Actions without hosting any server:

1. Push this repository to a private GitHub repo.
2. In your GitHub repo, go to **Settings > Secrets and variables > Actions**.
3. Add the following Repository Secrets:
   - `LINKEDIN_CLIENT_ID`
   - `LINKEDIN_CLIENT_SECRET`
   - `LINKEDIN_ACCESS_TOKEN` (Obtained after authenticating once in your local studio from `history/credentials.json`)
   - `LINKEDIN_MEMBER_URN` (Found in `history/credentials.json`, e.g. `urn:li:person:abcdef123`)
4. Enable the workflow located at:
   `.github/workflows/scheduled_publishing.yml`
5. The workflow automatically runs every 30 minutes, checks if the current time matches your configured prime-time windows in `config.json`, dispatches approved posts, and commits the updated queue status back to the repository!

---

## 📁 Repository Structure

```text
white-label-linkedin-automation/
├── .github/
│   └── workflows/
│       └── scheduled_publishing.yml # Serverless GitHub Actions dispatcher
├── dashboard/
│   ├── index.html                   # Modern glassmorphic Studio UI
│   ├── style.css                    # Dark-mode responsive styles
│   ├── app.js                       # Reactive frontend application
│   └── server.py                    # White-label API & OAuth server
├── engine/
│   ├── designer.py                  # Dynamic Canva graphic generator
│   ├── detector.py                  # 5-Check quality gate & anti-slop engine
│   ├── publisher.py                 # LinkedIn API client (media upload & posts)
│   ├── scheduler.py                 # Autonomous prime-time scheduling daemon
│   └── trend_radar.py               # Breakthrough generator & starter seeder
├── history/
│   ├── credentials.json             # Local OAuth credentials (ignored by git)
│   ├── daemon_status.json           # Scheduler runtime telemetry
│   └── publishing_log.json          # Permanent record of all published posts
├── queue/
│   ├── candidates/                  # Individual post markdown files
│   └── queue_summary.json           # Active queue state
├── visuals/                         # Generated comparison graphics (.png)
├── .env.example                     # Environment variables template
├── .gitignore                       # Protects secrets and local credentials
├── config.json.example              # Profile branding and posting schedule template
├── requirements.txt                 # Python dependencies
├── run_hub.py                       # Unified 1-click local process manager
├── setup.py                         # Interactive onboarding wizard
└── README.md                        # Documentation
```

---

## ⚙️ Customizing Content Strategy & Voice Rules

All behaviors are controlled by `config.json`:

```json
{
  "profile": {
    "full_name": "Alex Rivera",
    "initials": "AR",
    "headline": "Senior AI Systems Engineer & Distributed Architect",
    "location": "Berlin, Germany"
  },
  "content_strategy": {
    "primary_niche": "AI Systems, LLM Inference & Open-Source Engineering",
    "target_timezone": "Europe/Berlin",
    "max_posts_per_day": 2,
    "posting_windows": [
      { "name": "Morning Standup (Prime)", "start": "08:30", "end": "10:00" },
      { "name": "Midday Tech Catchup", "start": "12:00", "end": "13:30" },
      { "name": "Evening Engineering Wrap", "start": "17:00", "end": "18:30" }
    ]
  },
  "voice_rules": {
    "forbid_em_dashes": true,
    "forbidden_buzzwords": [
      "delve", "leverage", "game-changer", "revolutionary", "unlock",
      "landscape", "groundbreaking", "transformative", "paradigm shift"
    ],
    "require_hardware_metrics": true,
    "require_tested_declaration": true
  }
}
```

---

## 🛡️ License

This project is licensed under the MIT License — free for personal and commercial adaptation.


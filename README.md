# TMCC Waitlist System / Peoplesoft Portal Alerter

An automated cloud scraping utility designed to track enrollment availability for a specific class on Oracle PeopleSoft portals, specifically I used TMCC (Truckee Meadows Community College) as they do not have a waitlist system. When an opening is detected, it pushes a high-frequency notification sequence directly to a user's phone via an Email-to-SMS gateway.

## Features
* **Playwright + BeautifulSoup4 Architecture**: Breaks through multi-layered iFrame DOM frameworks to securely extract deep structural text fields.
* **Anti-Bot Defenses**: Employs desktop browser user-agents and persistent data tracking to bypass PeopleSoft session cookie checks.
* **High-Frequency Spam Alert**: Stays completely silent during class downtime, but triggers a 5-blast notification text loop spaced 2 seconds apart the moment a seat opens.
* **Zero-Cost Serverless Execution**: Orchestrated via GitHub Actions workflows to query servers on an optimized schedule without server maintenance overhead.

---

## Directory Structure
```text
├── .github/
│   └── workflows/
│       └── scrape.yml  <-- GitHub Actions schedule blueprint
├── Dockerfile          <-- Containerized blueprint
├── README.md
├── main.py             <-- Single-execution scraping script
└── requirements.txt
```

---

## Deployment Option 1: GitHub Actions (Recommended / 100% Free)

This setup runs your scraper automatically once per hour on GitHub's secure, serverless infrastructure.

### 1. Configure GitHub Repository Secrets
To keep your credentials safe, **never** push a `.env` file to your repository. Instead, go to your GitHub repository web page and navigate to **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**. 

Inject these three keys:
*   `SENDER_EMAIL`: The bot's Gmail address (e.g., `tmccwaitlist@gmail.com`).
*   `APP_PASSWORD`: A unique 16-character Google App Password (not your primary password).
*   `RECIEVER_PHONE`: The target phone number with carrier SMS gateway (e.g., `1234567890@vtext.com`).

### 2. Tailor Your Monitoring Cadence
Open `.github/workflows/scrape.yml` and adjust the cron expression to choose how often the script checks for openings.

```yaml
on:
  schedule:
    # Runs once an hour at exactly 47 minutes past the hour
    - cron: '47 * * * *'
```

### 3. Execution Logs
Commit your files to your main repository branch. To review performance metrics or check historical results, click on the **Actions** tab on your GitHub repository page to watch the live console logs print out.

---

## Deployment Option 2: Local Container or Render (Alternative)

If you prefer to run the scraper inside a localized container or on a cloud platform like Render or Railway, a multi-stage `Dockerfile` is included in the root directory.

### Why this custom Dockerfile layout is necessary:
Standard slim Python images lack the video layers, system-level fonts, and display dependencies required to run a headless Chromium browser. This custom file skips fragile `apt-get` system scripts entirely and utilizes Playwright's native system binary engine to ensure smooth compilation.

### 1. Local Compilation & Verification
To test the container engine locally on your machine, create a local `.env` file containing your credentials and execute these terminal commands:

```bash
# Build the localized container image
docker build -t class-scraper-test .

# Spin up the image while injecting your local .env configuration 
docker run --env-file .env class-scraper-test
```

### 2. Render Deployment Workflow
1. Upload your code files to a private GitHub repository (ensure `.env` is listed inside your `.gitignore`).
2. Provision a new **Background Worker** on the Render dashboard.
3. Explicitly set the deployment environment **Runtime to Docker** (do not select Python). Render will read the Dockerfile rules and automatically provision the required browser environments.
4. Add your secrets (`SENDER_EMAIL`, `APP_PASSWORD`, `RECIEVER_PHONE`) and add `PYTHONUNBUFFERED=1` to the environment variables dashboard to see your logs stream live.
